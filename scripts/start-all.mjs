import { copyFileSync, existsSync, mkdirSync, unlinkSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import net from 'node:net';
import { spawn, spawnSync } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = resolve(__dirname, '..');
const backendDir = join(rootDir, 'backend');
const frontendDir = join(rootDir, 'frontend-astro');
const pidFile = join(rootDir, '.runall.pids');

const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const taskKillCommand = process.platform === 'win32' ? 'taskkill' : null;

const children = [];
let shuttingDown = false;

function log(message) {
  process.stdout.write(`${message}\n`);
}

function commandExists(command, args = ['--version']) {
  const result = spawnSync(command, args, { stdio: 'ignore', shell: false });
  return result.status === 0;
}

function resolveSystemPython() {
  const candidates = process.platform === 'win32'
    ? ['py', 'python']
    : ['python3', 'python'];

  for (const candidate of candidates) {
    const args = candidate === 'py' ? ['-3', '--version'] : ['--version'];
    if (commandExists(candidate, args)) {
      return {
        command: candidate,
        baseArgs: candidate === 'py' ? ['-3'] : [],
      };
    }
  }

  throw new Error('Python was not found on PATH. Install Python 3.10+ and retry.');
}

function resolveBackendPython() {
  return process.platform === 'win32'
    ? join(backendDir, '.venv', 'Scripts', 'python.exe')
    : join(backendDir, '.venv', 'bin', 'python');
}

function backendHasPip(backendPython) {
  return existsSync(backendPython) && commandExists(backendPython, ['-m', 'pip', '--version']);
}

async function tryRun(command, args, options = {}) {
  try {
    await run(command, args, options);
    return true;
  } catch {
    return false;
  }
}

async function ensureBackendVirtualEnv(python, backendPython) {
  if (!existsSync(backendPython)) {
    log('[backend] Creating virtual environment...');
    await run(python.command, [...python.baseArgs, '-m', 'venv', '.venv'], { cwd: backendDir });
  }

  if (backendHasPip(backendPython)) {
    return;
  }

  log('[backend] Virtual environment is missing pip. Repairing...');

  try {
    await run(backendPython, ['-m', 'ensurepip', '--upgrade'], { cwd: backendDir });
  } catch {
    // Fall back to recreating the environment below.
  }

  if (backendHasPip(backendPython)) {
    return;
  }

  log('[backend] Recreating virtual environment with pip...');
  await run(python.command, [...python.baseArgs, '-m', 'venv', '--clear', '.venv'], { cwd: backendDir });

  if (!backendHasPip(backendPython)) {
    try {
      await run(backendPython, ['-m', 'ensurepip', '--upgrade'], { cwd: backendDir });
    } catch {
      // Let the explicit error below explain the next step.
    }
  }

  if (!backendHasPip(backendPython)) {
    const activateHint = process.platform === 'win32'
      ? 'In PowerShell: .\\backend\\.venv\\Scripts\\Activate.ps1'
      : 'On Linux/macOS: source backend/.venv/bin/activate';
    throw new Error(
      `The backend virtual environment was created without pip. Repair the Python installation used by npm start and retry. ${activateHint}`,
    );
  }
}

async function installBackendDependencies(backendPython) {
  log('[backend] Upgrading packaging tools...');
  const upgradedPackaging = await tryRun(
    backendPython,
    ['-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'],
    { cwd: backendDir },
  );

  if (!upgradedPackaging) {
    log('[backend] Packaging tool upgrade failed. Continuing with the existing pip environment.');
  }

  log('[backend] Installing Python dependencies...');
  const editableInstalled = await tryRun(
    backendPython,
    ['-m', 'pip', 'install', '-e', '.[dev]'],
    { cwd: backendDir },
  );

  if (editableInstalled) {
    return;
  }

  log('[backend] Editable install failed. Falling back to a standard install...');
  await run(backendPython, ['-m', 'pip', 'install', '.[dev]'], { cwd: backendDir });
}

function ensureFileFromExample(targetPath, examplePath) {
  if (!existsSync(targetPath) && existsSync(examplePath)) {
    copyFileSync(examplePath, targetPath);
  }
}

function shouldUseShell(command) {
  return process.platform === 'win32' && command.toLowerCase().endsWith('.cmd');
}

function quoteForCmd(arg) {
  if (!/[\s"&()^<>|]/.test(arg)) {
    return arg;
  }

  return `"${arg.replace(/"/g, '""')}"`;
}

function spawnProcess(command, args, options = {}) {
  const cwd = options.cwd ?? rootDir;
  const env = options.env ?? process.env;
  const stdio = options.stdio ?? 'inherit';

  if (shouldUseShell(command)) {
    const commandLine = [quoteForCmd(command), ...args.map(arg => quoteForCmd(String(arg)))].join(' ');
    return spawn(process.env.ComSpec || 'cmd.exe', ['/d', '/s', '/c', commandLine], {
      cwd,
      env,
      stdio,
      shell: false,
    });
  }

  return spawn(command, args, {
    cwd,
    env,
    stdio,
    shell: false,
  });
}

function run(command, args, options = {}) {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawnProcess(command, args, {
      cwd: options.cwd ?? rootDir,
      env: options.env ?? process.env,
      stdio: 'inherit',
    });

    child.on('error', rejectPromise);
    child.on('exit', code => {
      if (code === 0) {
        resolvePromise();
      } else {
        rejectPromise(new Error(`${command} ${args.join(' ')} failed with exit code ${code ?? 'unknown'}.`));
      }
    });
  });
}

function pickPort(preferredPort, host = '127.0.0.1', maxAttempts = 25) {
  return new Promise((resolvePromise, rejectPromise) => {
    let port = preferredPort;

    const tryListen = () => {
      const server = net.createServer();
      server.unref();
      server.once('error', error => {
        server.close();
        if (['EADDRINUSE', 'EACCES'].includes(error.code) && port < preferredPort + maxAttempts) {
          port += 1;
          tryListen();
          return;
        }
        rejectPromise(error);
      });
      server.listen(port, host, () => {
        const chosenPort = port;
        server.close(() => resolvePromise(chosenPort));
      });
    };

    tryListen();
  });
}

async function waitForHttp(url, timeoutMs = 30000) {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch {
      // Server is still starting.
    }

    await new Promise(resolvePromise => setTimeout(resolvePromise, 500));
  }

  throw new Error(`Timed out waiting for ${url}`);
}

function registerChild(child, label) {
  children.push({ child, label });

  child.on('error', error => {
    if (!shuttingDown) {
      console.error(`[${label}] failed to start.`, error);
      void shutdown(1);
    }
  });

  child.on('exit', code => {
    if (!shuttingDown) {
      log(`[${label}] exited with code ${code ?? 'unknown'}. Shutting down the stack.`);
      void shutdown(code ?? 1);
    }
  });
}

function writePidFile() {
  const pids = children
    .map(entry => entry.child.pid)
    .filter(pid => typeof pid === 'number');

  writeFileSync(pidFile, `${pids.join(' ')}\n`, 'utf8');
}

async function terminateChild(child) {
  if (!child.pid || child.killed) return;

  if (process.platform === 'win32' && taskKillCommand) {
    await new Promise(resolvePromise => {
      const killer = spawn(taskKillCommand, ['/pid', String(child.pid), '/t', '/f'], {
        stdio: 'ignore',
        shell: false,
      });
      killer.on('exit', () => resolvePromise());
      killer.on('error', () => resolvePromise());
    });
    return;
  }

  child.kill('SIGTERM');
}

async function shutdown(exitCode = 0) {
  if (shuttingDown) return;
  shuttingDown = true;

  try {
    if (existsSync(pidFile)) {
      unlinkSync(pidFile);
    }
  } catch {
    // Ignore cleanup failures.
  }

  await Promise.all(children.map(entry => terminateChild(entry.child)));
  process.exit(exitCode);
}

process.on('SIGINT', () => {
  void shutdown(0);
});

process.on('SIGTERM', () => {
  void shutdown(0);
});

process.on('uncaughtException', error => {
  console.error(error);
  void shutdown(1);
});

process.on('unhandledRejection', error => {
  console.error(error);
  void shutdown(1);
});

async function main() {
  mkdirSync(join(rootDir, 'scripts'), { recursive: true });

  const preferredBackendPort = Number.parseInt(process.env.BACKEND_PORT ?? process.env.CYBERFYX_BACKEND_PORT ?? '8000', 10);
  const preferredFrontendPort = Number.parseInt(process.env.FRONTEND_PORT ?? process.env.CYBERFYX_FRONTEND_PORT ?? '4321', 10);

  const backendPort = await pickPort(preferredBackendPort);
  const frontendPort = await pickPort(preferredFrontendPort);

  if (backendPort !== preferredBackendPort) {
    log(`[start] Port ${preferredBackendPort} is busy. Using backend port ${backendPort}.`);
  }
  if (frontendPort !== preferredFrontendPort) {
    log(`[start] Port ${preferredFrontendPort} is busy. Using frontend port ${frontendPort}.`);
  }

  const python = resolveSystemPython();
  const backendPython = resolveBackendPython();
  const backendBaseUrl = `http://127.0.0.1:${backendPort}`;
  const backendRuntimeEnv = {
    ...process.env,
    CYBERFYX_ENVIRONMENT: process.env.CYBERFYX_ENVIRONMENT ?? 'development',
    CYBERFYX_DATABASE_URL: process.env.CYBERFYX_DATABASE_URL ?? 'sqlite:///./cyberfyx.db',
  };

  await ensureBackendVirtualEnv(python, backendPython);

  ensureFileFromExample(join(backendDir, '.env'), join(backendDir, '.env.example'));
  ensureFileFromExample(join(frontendDir, '.env'), join(frontendDir, '.env.example'));

  await installBackendDependencies(backendPython);

  log('[backend] Running migrations...');
  await run(backendPython, ['-m', 'alembic', '-c', 'alembic/alembic.ini', 'upgrade', 'head'], {
    cwd: backendDir,
    env: backendRuntimeEnv,
  });

  log('[backend] Seeding database...');
  await run(backendPython, ['-m', 'app.db.seed'], {
    cwd: backendDir,
    env: backendRuntimeEnv,
  });

  log('[frontend] Installing npm dependencies...');
  await run(npmCommand, ['install', '--no-fund', '--no-audit'], { cwd: frontendDir });

  log(`[backend] Starting FastAPI on ${backendBaseUrl} ...`);
  const backendChild = spawn(
    backendPython,
    ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', String(backendPort)],
    {
      cwd: backendDir,
      env: backendRuntimeEnv,
      stdio: 'inherit',
      shell: false,
    },
  );
  registerChild(backendChild, 'backend');

  await waitForHttp(`${backendBaseUrl}/health/live`);

  log(`[frontend] Starting Astro on http://127.0.0.1:${frontendPort} ...`);
  const frontendChild = spawnProcess(
    npmCommand,
    ['run', 'dev', '--', '--host', '127.0.0.1', '--port', String(frontendPort)],
    {
      cwd: frontendDir,
      env: {
        ...process.env,
        PUBLIC_API_BASE: backendBaseUrl,
        API_PROXY_TARGET: backendBaseUrl,
      },
      stdio: 'inherit',
    },
  );
  registerChild(frontendChild, 'frontend');

  writePidFile();

  log('');
  log('Running:');
  log(`  Backend  -> ${backendBaseUrl}`);
  log(`  Frontend -> http://127.0.0.1:${frontendPort}`);
  log('');
  log('Press Ctrl+C to stop both processes.');
}

try {
  await main();
} catch (error) {
  console.error(error);
  await shutdown(1);
}
