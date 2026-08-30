from app.patching.attempt_history import RepairAttemptHistory


def test_record_attempt():

    history = RepairAttemptHistory()

    repair = {
        "file": "calculator.py",
        "replacement": "return a + b",
    }

    attempt = history.record(
        repair=repair,
        provider="ollama",
        model="qwen2.5-coder:14b",
    )

    assert attempt["attempt_number"] == 1
    assert attempt["provider"] == "ollama"
    assert attempt["model"] == "qwen2.5-coder:14b"
    assert attempt["repair"] == repair


def test_attempt_numbers_increment():

    history = RepairAttemptHistory()

    history.record(
        repair={"file": "a.py"},
    )

    history.record(
        repair={"file": "b.py"},
    )

    attempts = history.get_all()

    assert len(attempts) == 2
    assert attempts[0]["attempt_number"] == 1
    assert attempts[1]["attempt_number"] == 2


def test_latest_attempt():

    history = RepairAttemptHistory()

    history.record(
        repair={"file": "a.py"},
    )

    history.record(
        repair={"file": "b.py"},
    )

    latest = history.get_latest()

    assert latest["attempt_number"] == 2
    assert latest["repair"]["file"] == "b.py"


def test_empty_history():

    history = RepairAttemptHistory()

    assert history.count() == 0
    assert history.get_latest() is None
    assert history.get_all() == []


def test_clear_history():

    history = RepairAttemptHistory()

    history.record(
        repair={"file": "a.py"},
    )

    history.clear()

    assert history.count() == 0
    assert history.get_latest() is None