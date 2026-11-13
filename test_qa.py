"""Tests for the SQLite Q&A cache. Run with: pytest"""
import app


def setup_db(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "DB_PATH", str(tmp_path / "test_qa.db"))


def test_missing_question_not_found(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    assert app.query_qa("Where do you study?") == {"found": False}


def test_upsert_then_query(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    app.upsert_qa("Where do you study?", "At FAU Erlangen-Nürnberg.")
    assert app.query_qa("Where do you study?") == {"found": True, "answer": "At FAU Erlangen-Nürnberg."}


def test_upsert_updates_existing_answer(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    app.upsert_qa("Where do you study?", "Old answer")
    app.upsert_qa("Where do you study?", "New answer")
    assert app.query_qa("Where do you study?")["answer"] == "New answer"


def test_normalization_matches_variants(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    app.upsert_qa("What is your favorite color?", "Blue")
    for variant in ["what is your favorite color", "What is your favorite color ?", "  WHAT IS YOUR  FAVORITE COLOR?? "]:
        assert app.query_qa(variant) == {"found": True, "answer": "Blue"}


def test_unknown_tool_returns_error():
    class Fn:
        name, arguments = "does_not_exist", "{}"

    class Call:
        id, function = "call_1", Fn()

    result = app.Me.handle_tool_call(None, [Call()])
    assert "Unknown tool" in result[0]["content"]
