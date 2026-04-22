import { QUESTIONS } from '../data/chatbot-questions.js';
import { scoringEngine, type AnswerRecord, type ScoringResult } from '../lib/scoring-engine.js';

const GOOGLE_FORM_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLScGbvgjRJBzo9UjxF9YDJbIwv-aru2qy1QX3zPlSBLBIDf60w/formResponse';

const REPORT_ICON_CLASSES: Record<'High' | 'Medium' | 'Low', string> = {
  High: 'fa-shield-halved',
  Medium: 'fa-triangle-exclamation',
  Low: 'fa-circle-exclamation',
};

type ChatState =
  | 'IDLE'
  | 'GREETING'
  | 'COLLECT_LEAD'
  | 'QUESTIONING'
  | 'SCORING'
  | 'REPORT';

interface LeadData {
  name: string;
  email: string;
  company: string;
}

interface ChatbotState {
  phase: ChatState;
  currentQuestionIndex: number;
  answers: AnswerRecord[];
  lead: LeadData | null;
  result: ScoringResult | null;
  leadCollectionStep: 'name' | 'email' | 'company' | 'done';
}

interface ChatbotElements {
  widget: HTMLElement;
  fab: HTMLButtonElement;
  panel: HTMLElement;
  messagesContainer: HTMLElement;
  inputArea: HTMLElement;
  progressBar: HTMLElement;
  progressLabel: HTMLElement;
  closeBtn: HTMLButtonElement;
  minimizeBtn: HTMLButtonElement;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

async function submitLeadToGoogleForms(
  name: string,
  email: string,
  company: string,
  maturity: string,
  score: string
): Promise<void> {
  const params = new URLSearchParams({
    'entry.285505795': name,
    'entry.283005138': email,
    // Google Forms subject values must match the live contact form options.
    'entry.154599738': 'General Inquiry',
    'entry.1712408064':
      `Source: Compliance Assessment Chatbot | Company: ${company} | ` +
      `Maturity: ${maturity} | Score: ${score}%`,
  });

  try {
    await fetch(GOOGLE_FORM_URL, { method: 'POST', mode: 'no-cors', body: params });
  } catch {
    // no-cors fetches only fail for network-level issues
  }
}

function renderBotMessage(container: HTMLElement, html: string, delay = 0): void {
  const wrapper = document.createElement('div');
  wrapper.className = 'cbot-msg cbot-msg--bot cbot-msg--entering';
  wrapper.innerHTML = `
    <div class="cbot-avatar" aria-hidden="true">
      <img src="/favicon.png" alt="Cyberfyx" width="28" height="28" />
    </div>
    <div class="cbot-bubble">${html}</div>
  `;

  if (delay > 0) {
    wrapper.style.opacity = '0';
    wrapper.style.transform = 'translateY(8px)';
    setTimeout(() => {
      container.appendChild(wrapper);
      scrollToBottom(container);
      requestAnimationFrame(() => {
        wrapper.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        wrapper.style.opacity = '1';
        wrapper.style.transform = 'translateY(0)';
      });
    }, delay);
    return;
  }

  container.appendChild(wrapper);
  scrollToBottom(container);
}

function renderUserMessage(container: HTMLElement, text: string): void {
  const wrapper = document.createElement('div');
  wrapper.className = 'cbot-msg cbot-msg--user';

  const bubble = document.createElement('div');
  bubble.className = 'cbot-bubble';
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  scrollToBottom(container);
}

function renderTypingIndicator(container: HTMLElement): HTMLElement {
  const el = document.createElement('div');
  el.className = 'cbot-msg cbot-msg--bot cbot-typing';
  el.innerHTML = `
    <div class="cbot-avatar" aria-hidden="true">
      <img src="/favicon.png" alt="" width="28" height="28" />
    </div>
    <div class="cbot-bubble cbot-bubble--typing">
      <span></span><span></span><span></span>
    </div>
  `;
  container.appendChild(el);
  scrollToBottom(container);
  return el;
}

function scrollToBottom(container: HTMLElement): void {
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

function clearInputArea(inputArea: HTMLElement): void {
  inputArea.innerHTML = '';
}

function renderAnswerButtons(
  inputArea: HTMLElement,
  onAnswer: (value: 'yes' | 'partial' | 'no') => void
): void {
  clearInputArea(inputArea);

  const buttons: Array<{ value: 'yes' | 'partial' | 'no'; label: string; iconClass: string }> = [
    { value: 'yes', label: 'Yes', iconClass: 'fa-check' },
    { value: 'partial', label: 'Partial', iconClass: 'fa-minus' },
    { value: 'no', label: 'No', iconClass: 'fa-xmark' },
  ];

  const row = document.createElement('div');
  row.className = 'cbot-answer-row';

  buttons.forEach(({ value, label, iconClass }) => {
    const btn = document.createElement('button');
    btn.className = `cbot-answer-btn cbot-answer-btn--${value}`;
    btn.type = 'button';
    btn.innerHTML = `
      <i class="fa-solid ${iconClass} cbot-answer-icon" aria-hidden="true"></i>
      <span>${label}</span>
    `;
    btn.addEventListener('click', () => {
      row.querySelectorAll('button').forEach(button => {
        (button as HTMLButtonElement).disabled = true;
      });
      btn.classList.add('cbot-answer-btn--selected');
      onAnswer(value);
    });
    row.appendChild(btn);
  });

  inputArea.appendChild(row);
}

function renderTextInput(
  inputArea: HTMLElement,
  placeholder: string,
  onSubmit: (value: string) => void,
  type: 'text' | 'email' = 'text'
): void {
  clearInputArea(inputArea);

  const row = document.createElement('div');
  row.className = 'cbot-text-row';

  const input = document.createElement('input');
  input.type = type;
  input.className = 'cbot-text-input';
  input.placeholder = placeholder;
  input.autocomplete = type === 'email' ? 'email' : 'on';

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'cbot-send-btn';
  btn.innerHTML = '<i class="fa-solid fa-arrow-right" aria-hidden="true"></i>';
  btn.setAttribute('aria-label', 'Submit');

  const submit = () => {
    const val = input.value.trim();
    if (!val) {
      input.classList.add('cbot-text-input--error');
      input.focus();
      return;
    }

    if (type === 'email' && !val.includes('@')) {
      input.classList.add('cbot-text-input--error');
      input.focus();
      return;
    }

    input.disabled = true;
    btn.disabled = true;
    onSubmit(val);
  };

  input.addEventListener('input', () => input.classList.remove('cbot-text-input--error'));
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter') submit();
  });
  btn.addEventListener('click', submit);

  row.appendChild(input);
  row.appendChild(btn);
  inputArea.appendChild(row);
  input.focus();
}

function renderStartButton(inputArea: HTMLElement, onStart: () => void): void {
  clearInputArea(inputArea);

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'cbot-start-btn';
  btn.innerHTML = '<i class="fa-solid fa-shield-halved" aria-hidden="true"></i> Start assessment';
  btn.addEventListener('click', () => {
    btn.disabled = true;
    onStart();
  });

  inputArea.appendChild(btn);
}

function renderCtaButtons(
  inputArea: HTMLElement,
  onConsult: () => void,
  onRestart: () => void
): void {
  clearInputArea(inputArea);

  const row = document.createElement('div');
  row.className = 'cbot-cta-row';

  const consultBtn = document.createElement('button');
  consultBtn.type = 'button';
  consultBtn.className = 'cbot-cta-btn cbot-cta-btn--primary';
  consultBtn.innerHTML = '<i class="fa-solid fa-calendar-check" aria-hidden="true"></i> Talk to Cyberfyx';
  consultBtn.addEventListener('click', onConsult);

  const restartBtn = document.createElement('button');
  restartBtn.type = 'button';
  restartBtn.className = 'cbot-cta-btn cbot-cta-btn--ghost';
  restartBtn.innerHTML = '<i class="fa-solid fa-rotate-left" aria-hidden="true"></i> Restart assessment';
  restartBtn.addEventListener('click', onRestart);

  row.appendChild(consultBtn);
  row.appendChild(restartBtn);
  inputArea.appendChild(row);
}

function renderReport(
  container: HTMLElement,
  result: ScoringResult,
  lead: LeadData
): void {
  const config = result.maturityConfig;
  const reportTone = result.maturityLevel.toLowerCase();
  const safeCompany = escapeHtml(lead.company);

  const gapItemsHtml = result.gaps
    .slice(0, 6)
    .map(gap => {
      const severityClass = `cbot-gap--${gap.severity}`;
      const tierLabel = ['', 'Critical', 'High Impact', 'Operational'][gap.tier];
      return `
        <li class="cbot-gap-item ${severityClass}">
          <div class="cbot-gap-header">
            <strong>${gap.domain}</strong>
            <span class="cbot-gap-tier">Tier ${gap.tier} &middot; ${tierLabel}</span>
          </div>
          <p class="cbot-gap-text">${gap.gap}</p>
          <p class="cbot-gap-rec"><i class="fa-solid fa-lightbulb" aria-hidden="true"></i> ${gap.recommendation}</p>
        </li>
      `;
    })
    .join('');

  const moreGapsNote =
    result.gaps.length > 6
      ? `<p class="cbot-gaps-more">+${result.gaps.length - 6} additional gaps identified in this assessment.</p>`
      : '';

  const statsHtml = `
    <div class="cbot-stats-row">
      <div class="cbot-stat cbot-stat--yes">
        <span class="cbot-stat-num">${result.totalYes}</span>
        <span class="cbot-stat-lbl">Implemented</span>
      </div>
      <div class="cbot-stat cbot-stat--partial">
        <span class="cbot-stat-num">${result.totalPartial}</span>
        <span class="cbot-stat-lbl">Partial</span>
      </div>
      <div class="cbot-stat cbot-stat--no">
        <span class="cbot-stat-num">${result.totalNo}</span>
        <span class="cbot-stat-lbl">Gap</span>
      </div>
    </div>
  `;

  const reportHtml = `
    <div class="cbot-report cbot-report--${reportTone}">
      <div class="cbot-report-header">
        <span class="cbot-report-badge" aria-hidden="true">
          <i class="fa-solid ${REPORT_ICON_CLASSES[result.maturityLevel]}"></i>
        </span>
        <div>
          <div class="cbot-report-title">${config.label}</div>
          <div class="cbot-report-score">${result.percentage}% Compliance Score</div>
        </div>
      </div>
      <div class="cbot-score-bar-wrap">
        <div class="cbot-score-bar">
          <div class="cbot-score-fill" style="width:${result.percentage}%"></div>
        </div>
        <div class="cbot-score-markers">
          <span style="left:50%">50%</span>
          <span style="left:85%">85%</span>
        </div>
      </div>
      ${statsHtml}
      <p class="cbot-report-desc">${config.description}</p>
      ${result.gaps.length > 0 ? `
        <div class="cbot-gaps-section">
          <h4 class="cbot-gaps-title">Priority Gaps Identified</h4>
          <ul class="cbot-gaps-list">${gapItemsHtml}</ul>
          ${moreGapsNote}
        </div>
      ` : `
        <div class="cbot-report-clean">
          <i class="fa-solid fa-circle-check" aria-hidden="true"></i>
          <span>No critical gaps were identified in this assessment.</span>
        </div>
      `}
      <div class="cbot-report-cta-box">
        <p>${config.cta}</p>
      </div>
    </div>
  `;

  renderBotMessage(container, `Assessment summary for <strong>${safeCompany}</strong>.`);

  setTimeout(() => {
    const wrapper = document.createElement('div');
    wrapper.className = 'cbot-msg cbot-msg--bot cbot-msg--report';
    wrapper.innerHTML = `<div class="cbot-bubble cbot-bubble--report">${reportHtml}</div>`;
    container.appendChild(wrapper);
    scrollToBottom(container);
  }, 600);

  setTimeout(() => {
    renderBotMessage(
      container,
      'Would you like to review these results with a Cyberfyx ISO 27001 specialist?'
    );
  }, 1000);
}

export class ComplianceChatbot {
  private state: ChatbotState = {
    phase: 'IDLE',
    currentQuestionIndex: 0,
    answers: [],
    lead: null,
    result: null,
    leadCollectionStep: 'name',
  };

  private els!: ChatbotElements;

  init(): void {
    const widget = document.getElementById('cbot-widget');
    if (!widget) return;

    this.els = {
      widget,
      fab: document.getElementById('cbot-fab') as HTMLButtonElement,
      panel: document.getElementById('cbot-panel') as HTMLElement,
      messagesContainer: document.getElementById('cbot-messages') as HTMLElement,
      inputArea: document.getElementById('cbot-input-area') as HTMLElement,
      progressBar: document.getElementById('cbot-progress-fill') as HTMLElement,
      progressLabel: document.getElementById('cbot-progress-label') as HTMLElement,
      closeBtn: document.getElementById('cbot-close') as HTMLButtonElement,
      minimizeBtn: document.getElementById('cbot-minimize') as HTMLButtonElement,
    };

    this.els.fab.addEventListener('click', () => this.openPanel());
    this.els.closeBtn.addEventListener('click', () => this.closePanel());
    this.els.minimizeBtn.addEventListener('click', () => this.closePanel());
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && this.els.panel.classList.contains('cbot-panel--open')) {
        this.closePanel();
      }
    });

    this.els.panel.setAttribute('aria-hidden', 'true');
  }

  private openPanel(): void {
    this.els.panel.classList.add('cbot-panel--open');
    this.els.fab.classList.add('cbot-fab--hidden');
    this.els.fab.setAttribute('aria-expanded', 'true');
    this.els.panel.setAttribute('aria-hidden', 'false');
    document.body.classList.add('cbot-open');

    if (this.state.phase === 'IDLE') {
      this.state.phase = 'GREETING';
      this.runGreeting();
    }
  }

  private closePanel(): void {
    this.els.panel.classList.remove('cbot-panel--open');
    this.els.fab.classList.remove('cbot-fab--hidden');
    this.els.fab.setAttribute('aria-expanded', 'false');
    this.els.panel.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('cbot-open');
    this.els.fab.focus();
  }

  private updateProgress(answered: number): void {
    const pct = Math.round((answered / QUESTIONS.length) * 100);
    this.els.progressBar.style.width = `${pct}%`;
    this.els.progressBar.setAttribute('aria-valuenow', String(pct));
    this.els.progressBar.setAttribute(
      'aria-valuetext',
      answered > 0
        ? `${answered} of ${QUESTIONS.length} questions answered`
        : 'Assessment not started'
    );

    this.els.progressLabel.textContent = answered > 0
      ? `${answered} / ${QUESTIONS.length} answered`
      : 'Compliance Evaluation';
  }

  private botDelayedSequence(messages: Array<{ html: string; delay: number }>): void {
    messages.forEach(({ html, delay }) => {
      renderBotMessage(this.els.messagesContainer, html, delay);
    });
  }

  private runGreeting(): void {
    this.botDelayedSequence([
      {
        html: 'You are speaking with the <strong>Cyberfyx Compliance Advisor</strong>.',
        delay: 0,
      },
      {
        html: 'This assessment reviews <strong>16 ISO 27001 control domains</strong> and returns a maturity score with prioritised gaps.',
        delay: 500,
      },
      {
        html: 'It takes about <strong>3 minutes</strong>. To personalise your report, enter your <strong>full name</strong>.',
        delay: 1200,
      },
    ]);

    setTimeout(() => {
      this.state.phase = 'COLLECT_LEAD';
      this.state.leadCollectionStep = 'name';
      renderTextInput(
        this.els.inputArea,
        'Your full name...',
        value => this.handleLeadInput(value)
      );
    }, 1500);
  }

  private handleLeadInput(value: string): void {
    renderUserMessage(this.els.messagesContainer, value);

    if (this.state.leadCollectionStep === 'name') {
      this.state.lead = { name: value, email: '', company: '' };
      this.state.leadCollectionStep = 'email';
      renderBotMessage(
        this.els.messagesContainer,
        `Thank you, <strong>${escapeHtml(value)}</strong>. What is your <strong>work email address</strong>?`,
        400
      );
      setTimeout(() => {
        renderTextInput(
          this.els.inputArea,
          'your@company.com',
          nextValue => this.handleLeadInput(nextValue),
          'email'
        );
      }, 800);
      return;
    }

    if (this.state.leadCollectionStep === 'email') {
      this.state.lead!.email = value;
      this.state.leadCollectionStep = 'company';
      renderBotMessage(
        this.els.messagesContainer,
        'Thank you. What is the name of your <strong>organisation</strong>?',
        400
      );
      setTimeout(() => {
        renderTextInput(
          this.els.inputArea,
          'Your organisation name...',
          nextValue => this.handleLeadInput(nextValue)
        );
      }, 800);
      return;
    }

    if (this.state.leadCollectionStep === 'company') {
      this.state.lead!.company = value;
      this.state.leadCollectionStep = 'done';
      renderBotMessage(
        this.els.messagesContainer,
        `We are ready to assess <strong>${escapeHtml(value)}</strong>. I will ask 16 questions about your current controls. Choose <strong>Yes</strong>, <strong>Partial</strong>, or <strong>No</strong> for each item.`,
        400
      );
      setTimeout(() => {
        this.state.phase = 'QUESTIONING';
        this.state.currentQuestionIndex = 0;
        this.updateProgress(0);
        renderStartButton(this.els.inputArea, () => this.askQuestion(0));
      }, 1000);
    }
  }

  private askQuestion(index: number): void {
    const question = QUESTIONS[index];
    if (!question) {
      this.runScoring();
      return;
    }

    const tierLabel = ['', 'Tier 1 Critical', 'Tier 2 High Impact', 'Tier 3 Operational'][question.tier];
    const questionHtml = `
      <div class="cbot-question-meta">
        <span class="cbot-q-num">Q${question.id} of ${QUESTIONS.length}</span>
        <span class="cbot-q-domain">${question.domain}</span>
        <span class="cbot-q-tier cbot-q-tier--${question.tier}">${tierLabel}</span>
      </div>
      <p class="cbot-q-text">${question.question}</p>
      <p class="cbot-q-hint"><i class="fa-solid fa-circle-info" aria-hidden="true"></i> ${question.hint}</p>
    `;

    const typing = renderTypingIndicator(this.els.messagesContainer);
    setTimeout(() => {
      typing.remove();
      renderBotMessage(this.els.messagesContainer, questionHtml);
      renderAnswerButtons(this.els.inputArea, answer => this.handleAnswer(index, answer));
    }, 300);
  }

  private handleAnswer(index: number, answer: 'yes' | 'partial' | 'no'): void {
    const question = QUESTIONS[index];
    const labels = { yes: 'Yes', partial: 'Partial', no: 'No' };
    renderUserMessage(this.els.messagesContainer, labels[answer]);

    this.state.answers.push({ questionId: question.id, answer });
    this.updateProgress(this.state.answers.length);

    const next = index + 1;
    this.state.currentQuestionIndex = next;

    if (next < QUESTIONS.length) {
      this.askQuestion(next);
      return;
    }

    this.runScoring();
  }

  private runScoring(): void {
    this.state.phase = 'SCORING';
    clearInputArea(this.els.inputArea);

    const typing = renderTypingIndicator(this.els.messagesContainer);
    renderBotMessage(
      this.els.messagesContainer,
      '<i class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Reviewing your responses and calculating the assessment score...',
      400
    );

    setTimeout(() => {
      typing.remove();
      this.state.result = scoringEngine.compute(this.state.answers);
      this.state.phase = 'REPORT';

      if (this.state.lead) {
        submitLeadToGoogleForms(
          this.state.lead.name,
          this.state.lead.email,
          this.state.lead.company,
          this.state.result.maturityLevel,
          String(this.state.result.percentage)
        );
      }

      this.renderFinalReport();
    }, 1800);
  }

  private renderFinalReport(): void {
    if (!this.state.result || !this.state.lead) return;

    renderReport(this.els.messagesContainer, this.state.result, this.state.lead);

    setTimeout(() => {
      renderCtaButtons(
        this.els.inputArea,
        () => this.handleConsultCta(),
        () => this.restartChatbot()
      );
    }, 1600);
  }

  private handleConsultCta(): void {
    const safeEmail = escapeHtml(this.state.lead?.email ?? '');
    renderUserMessage(this.els.messagesContainer, 'I want to speak with a Cyberfyx expert');
    renderBotMessage(
      this.els.messagesContainer,
      `You can contact us at <a href="mailto:sales@cyberfyx.net">sales@cyberfyx.net</a> or use the <a href="/contact">Contact page</a> to schedule a consultation.<br><br>We will follow up with <strong>${safeEmail}</strong> within one business day.`,
      400
    );

    clearInputArea(this.els.inputArea);
    setTimeout(() => {
      const restartBtn = document.createElement('button');
      restartBtn.className = 'cbot-cta-btn cbot-cta-btn--ghost';
      restartBtn.innerHTML = '<i class="fa-solid fa-rotate-left" aria-hidden="true"></i> Start new assessment';
      restartBtn.addEventListener('click', () => this.restartChatbot());
      this.els.inputArea.appendChild(restartBtn);
    }, 600);
  }

  private restartChatbot(): void {
    this.state = {
      phase: 'GREETING',
      currentQuestionIndex: 0,
      answers: [],
      lead: null,
      result: null,
      leadCollectionStep: 'name',
    };

    this.els.messagesContainer.innerHTML = '';
    clearInputArea(this.els.inputArea);
    this.updateProgress(0);
    this.runGreeting();
  }
}

let chatbotInstance: ComplianceChatbot | null = null;

function initChatbot() {
  if (chatbotInstance) return;
  if (!document.getElementById('cbot-widget')) return;
  chatbotInstance = new ComplianceChatbot();
  chatbotInstance.init();
}

document.addEventListener('DOMContentLoaded', initChatbot);
document.addEventListener('astro:page-load', () => {
  chatbotInstance = null;
  initChatbot();
});
