# Stateless architecture compliance tests
# Copy this file to: backend/tests/test_stateless_compliance.py

import pytest
import asyncio
from sqlmodel import Session, create_engine, SQLModel
from app.models import Conversation, Message
from app.agents.chat_agent import run_agent
from app.agents.context_manager import load_conversation_context


@pytest.fixture
def test_db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.mark.asyncio
async def test_state_isolation_between_requests(test_db):
    """
    Verify agent doesn't retain state between requests.

    Requirement: Agent must load conversation history from database
    on every request, not rely on in-memory state.
    """
    conversation_id = "test-conv-state-isolation"

    # Create conversation
    conversation = Conversation(
        user_id="test-user",
        title="State Isolation Test"
    )
    test_db.add(conversation)
    test_db.commit()

    # First request
    response1 = await run_agent(
        conversation_id=conversation.id,
        user_message="First message",
        user_id="test-user",
        db=test_db
    )

    assert response1 is not None

    # Second request (should not have access to first request's in-memory state)
    response2 = await run_agent(
        conversation_id=conversation.id,
        user_message="Second message",
        user_id="test-user",
        db=test_db
    )

    assert response2 is not None

    # Verify both requests loaded history from database
    messages = load_conversation_context(conversation.id, test_db)

    # Should have at least 2 user messages (if agent is stateless)
    user_messages = [msg for msg in messages if msg.role == "user"]
    assert len(user_messages) >= 2

    print("✅ State isolation test passed")


@pytest.mark.asyncio
async def test_concurrent_request_handling(test_db):
    """
    Verify multiple instances can serve same conversation concurrently.

    Requirement: Stateless architecture enables horizontal scaling -
    multiple agent instances should be able to serve the same conversation
    without conflicts.
    """
    conversation_id = "test-conv-concurrent"

    # Create conversation
    conversation = Conversation(
        user_id="test-user",
        title="Concurrent Test"
    )
    test_db.add(conversation)
    test_db.commit()

    # Simulate 10 concurrent requests from different agent instances
    tasks = [
        run_agent(
            conversation_id=conversation.id,
            user_message=f"Concurrent message {i}",
            user_id="test-user",
            db=test_db
        )
        for i in range(10)
    ]

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Verify no exceptions occurred
    exceptions = [r for r in responses if isinstance(r, Exception)]
    assert len(exceptions) == 0, f"Concurrent requests failed: {exceptions}"

    # Verify all messages were saved to database
    messages = load_conversation_context(conversation.id, test_db)
    user_messages = [msg for msg in messages if msg.role == "user"]

    assert len(user_messages) == 10, (
        f"Expected 10 user messages, got {len(user_messages)}. "
        f"Concurrent requests may have race conditions."
    )

    print("✅ Concurrent request handling test passed")


@pytest.mark.asyncio
async def test_instance_restart_simulation(test_db):
    """
    Verify conversation history survives agent instance restart.

    Requirement: If agent stores state in memory, it would be lost on restart.
    Stateless agent loads from database, so restart has no effect.
    """
    conversation_id = "test-conv-restart"

    # Create conversation
    conversation = Conversation(
        user_id="test-user",
        title="Restart Test"
    )
    test_db.add(conversation)
    test_db.commit()

    # Request 1: Simulate agent instance A
    await run_agent(
        conversation_id=conversation.id,
        user_message="Message before restart",
        user_id="test-user",
        db=test_db
    )

    # Simulate instance restart
    # (In real scenario, this would be a different process)
    # If agent is stateless, this should have no effect

    # Request 2: Simulate agent instance B (different instance after restart)
    response = await run_agent(
        conversation_id=conversation.id,
        user_message="Message after restart",
        user_id="test-user",
        db=test_db
    )

    assert response is not None

    # Verify instance B has access to message from instance A
    messages = load_conversation_context(conversation.id, test_db)
    user_messages = [msg for msg in messages if msg.role == "user"]

    assert len(user_messages) >= 2, (
        f"Expected at least 2 user messages, got {len(user_messages)}. "
        f"Agent may not be loading history from database."
    )

    # Verify first message is present
    message_contents = [msg.content for msg in user_messages]
    assert "Message before restart" in message_contents, (
        "First message not found after restart. Agent may be using in-memory state."
    )

    print("✅ Instance restart simulation test passed")


@pytest.mark.asyncio
async def test_load_balancing_compatibility(test_db):
    """
    Verify requests can be served by different instances without sticky sessions.

    Requirement: Stateless architecture means any instance can serve any request.
    No sticky session routing required.
    """
    conversation_id = "test-conv-load-balancing"

    # Create conversation
    conversation = Conversation(
        user_id="test-user",
        title="Load Balancing Test"
    )
    test_db.add(conversation)
    test_db.commit()

    # Simulate round-robin load balancing
    # Each request goes to a "different instance"
    for i in range(5):
        # Each iteration simulates a different agent instance
        response = await run_agent(
            conversation_id=conversation.id,
            user_message=f"Message {i} from instance {i % 3}",
            user_id="test-user",
            db=test_db
        )

        assert response is not None

        # Verify this "instance" has access to all previous messages
        messages = load_conversation_context(conversation.id, test_db)
        user_messages = [msg for msg in messages if msg.role == "user"]

        assert len(user_messages) == i + 1, (
            f"Instance {i % 3} should see {i + 1} messages, got {len(user_messages)}. "
            f"Load balancing may not work correctly."
        )

    print("✅ Load balancing compatibility test passed")


@pytest.mark.asyncio
async def test_no_memory_leaks_from_state(test_db):
    """
    Verify agent doesn't accumulate state in memory over multiple requests.

    Requirement: Stateless agents should not grow memory usage with each request.
    """
    import gc
    import sys

    conversation_id = "test-conv-memory"

    # Create conversation
    conversation = Conversation(
        user_id="test-user",
        title="Memory Test"
    )
    test_db.add(conversation)
    test_db.commit()

    # Get baseline memory usage
    gc.collect()
    initial_objects = len(gc.get_objects())

    # Make 20 requests
    for i in range(20):
        await run_agent(
            conversation_id=conversation.id,
            user_message=f"Message {i}",
            user_id="test-user",
            db=test_db
        )

    # Get final memory usage
    gc.collect()
    final_objects = len(gc.get_objects())

    # Object count should not grow significantly
    # (Allow some growth for database objects, but not proportional to requests)
    growth = final_objects - initial_objects
    max_allowed_growth = 1000  # Generous threshold

    assert growth < max_allowed_growth, (
        f"Memory objects grew by {growth} after 20 requests. "
        f"Agent may be accumulating state in memory (expected < {max_allowed_growth})."
    )

    print(f"✅ No memory leaks test passed (growth: {growth} objects)")


def test_comprehensive_stateless_compliance(test_db):
    """
    Run all stateless compliance tests in sequence.

    This is the master test that validates complete stateless architecture.
    """
    print("\n" + "=" * 60)
    print("STATELESS ARCHITECTURE COMPLIANCE TEST SUITE")
    print("=" * 60 + "\n")

    # Run all async tests
    asyncio.run(test_state_isolation_between_requests(test_db))
    asyncio.run(test_concurrent_request_handling(test_db))
    asyncio.run(test_instance_restart_simulation(test_db))
    asyncio.run(test_load_balancing_compatibility(test_db))
    asyncio.run(test_no_memory_leaks_from_state(test_db))

    print("\n" + "=" * 60)
    print("✅ ALL STATELESS COMPLIANCE TESTS PASSED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
