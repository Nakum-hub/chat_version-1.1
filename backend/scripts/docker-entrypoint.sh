#!/bin/sh
set -eu

if [ "${CYBERFYX_RUN_MIGRATIONS_ON_START:-true}" = "true" ]; then
  python -m alembic -c alembic/alembic.ini upgrade head
fi

if [ "${CYBERFYX_RUN_SEED_ON_START:-true}" = "true" ]; then
  python -m app.db.seed
fi

exec "$@"
