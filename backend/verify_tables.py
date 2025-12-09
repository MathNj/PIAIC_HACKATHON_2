"""Verify database tables exist."""
from sqlmodel import Session, text
from app.database import engine

with Session(engine) as session:
    result = session.exec(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).all()
    tables = [r[0] for r in result]

    print(f"[OK] Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")

    # Verify required tables
    required = ['users', 'tasks', 'conversations', 'messages', 'alembic_version']
    missing = [t for t in required if t not in tables]

    if missing:
        print(f"\n[ERROR] Missing tables: {missing}")
    else:
        print("\n[OK] All required tables exist!")

    # Check indexes on conversations table
    result = session.exec(text("PRAGMA index_list('conversations')")).all()
    print(f"\n[OK] Conversations table indexes:")
    for idx in result:
        print(f"  - {idx[1]}")

    # Check indexes on messages table
    result = session.exec(text("PRAGMA index_list('messages')")).all()
    print(f"\n[OK] Messages table indexes:")
    for idx in result:
        print(f"  - {idx[1]}")
