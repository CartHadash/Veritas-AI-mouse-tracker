"""Automatic checks for the session history (no API key or server needed).

    python -m pytest assistant/test_history.py
"""

import json

from assistant import history


def make_summary(started, share=0.3):
    return {"session": {"started": started, "minutes_active": 10.0},
            "tremor": {"detected_share": share, "typical_frequency_hz": 5.0, "typical_strength_px": 6.0},
            "usage": {"steadiness_score": 0.6, "click_accuracy": 0.8},
            "filter": {"mode": "learned", "strength": 0.7},
            "notes": ["Tremor replay (demo mode) was ON for part of this session."]}


def test_save_and_read_back_newest_first(monkeypatch, tmp_path):
    monkeypatch.setattr(history, "SESSIONS_DIR", tmp_path)
    for day in ("2026-11-12T09:00:00", "2026-11-13T09:00:00", "2026-11-14T09:00:00"):
        assert history.save(make_summary(day))
    past = history.past_sessions(exclude_started="2026-11-14T09:00:00", folder=tmp_path)
    assert [p["started"] for p in past] == ["2026-11-13T09:00:00", "2026-11-12T09:00:00"]
    assert past[0]["day"] == "Fri 13 Nov, 09:00"
    assert past[0]["demo_tremor_was_on"] is True
    assert "by_time" not in past[0]                      # only the short version


def test_nothing_analysed_is_not_saved(monkeypatch, tmp_path):
    monkeypatch.setattr(history, "SESSIONS_DIR", tmp_path)
    assert not history.save(make_summary("2026-11-14T10:00:00", share=None))
    assert list(tmp_path.iterdir()) == []


def test_deleted_session_is_never_saved_again(monkeypatch, tmp_path):
    monkeypatch.setattr(history, "SESSIONS_DIR", tmp_path)
    history.do_not_save("2026-11-14T11:00:00")
    assert not history.save(make_summary("2026-11-14T11:00:00"))


def test_damaged_file_is_skipped(monkeypatch, tmp_path):
    monkeypatch.setattr(history, "SESSIONS_DIR", tmp_path)
    history.save(make_summary("2026-11-14T12:00:00"))
    (tmp_path / "session_2026-11-15_00-00-00.json").write_text("{not json", encoding="utf-8")
    past = history.past_sessions(folder=tmp_path)
    assert [p["started"] for p in past] == ["2026-11-14T12:00:00"]


def test_saved_file_holds_summary_numbers_only(monkeypatch, tmp_path):
    monkeypatch.setattr(history, "SESSIONS_DIR", tmp_path)
    history.save(make_summary("2026-11-14T13:00:00"))
    saved = json.loads(next(tmp_path.glob("session_*.json")).read_text(encoding="utf-8"))
    assert set(saved) == {"session", "tremor", "usage", "filter", "notes"}
