"""Unit tests for ActivityLogger."""

from tool.core.activity_logger import ActivityLogger


def test_activity_event_fields():
    logger = ActivityLogger()
    event = logger.info(stage="test", event="hello", message="world", details={"k": 1})
    assert event.timestamp
    assert event.level == "info"
    assert event.stage == "test"
    assert event.event == "hello"
    assert event.message == "world"
    assert event.details == {"k": 1}
    assert event.id
    assert len(logger.events) == 1


def test_logger_levels_and_clear():
    logger = ActivityLogger()
    logger.debug(stage="s", event="d", message="d")
    logger.warning(stage="s", event="w", message="w")
    logger.error(stage="s", event="e", message="e")
    assert len(logger.events) == 3
    logger.clear()
    assert logger.events == []


def test_logger_listener():
    seen: list[str] = []
    logger = ActivityLogger(on_event=lambda event: seen.append(event.event))
    logger.info(stage="s", event="first", message="one")
    logger.set_listener(lambda event: seen.append(event.event))
    logger.info(stage="s", event="second", message="two")
    logger.set_listener(None)
    logger.info(stage="s", event="third", message="three")
    assert seen == ["first", "second"]
