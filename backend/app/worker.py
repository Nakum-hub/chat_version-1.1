from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.notifications import get_outbox_handlers
from app.services.outbox import process_pending_outbox_events


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def run_pending_outbox_batch(batch_size: int = 25) -> int:
    with session_scope() as session:
        events = process_pending_outbox_events(
            session,
            handlers=get_outbox_handlers(),
            batch_size=batch_size,
        )
        return len(events)


if __name__ == "__main__":
    processed = run_pending_outbox_batch()
    print(f"Processed {processed} outbox event(s).")
