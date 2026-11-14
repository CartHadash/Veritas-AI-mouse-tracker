"""Automatic checks for the tracker that do not need anyone to move the mouse.

    python -m pytest tracker/test_reader.py

A fake pointer replaces macOS, so these also run on Windows (except the real-Mac check).
"""

import sys
import time

import pytest

from tracker import log, reader


def run_with_fake_pointer(monkeypatch, positions, seconds):
    """Run the tracker for `seconds` with a fake pointer; positions(i) gives the i-th reading."""
    calls = [0]

    def fake_read():
        calls[0] += 1
        return positions(calls[0])

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(reader, "read_position", fake_read)
    samples = []
    reader.start(samples.append)
    time.sleep(seconds)
    reader.stop()
    return samples


def test_moving_pointer_gives_about_100_per_second(monkeypatch):
    samples = run_with_fake_pointer(monkeypatch, lambda i: (float(i), 0.0), 1.0)
    assert 85 <= len(samples) <= 105
    assert set(samples[0]) == {"t", "x", "y"}          # Contract 1 shape, nothing else


def test_still_pointer_stops_sending(monkeypatch):
    monkeypatch.setattr(reader, "IDLE_SECONDS", 0.2)
    samples = run_with_fake_pointer(monkeypatch, lambda i: (5.0, 5.0), 1.0)
    assert len(samples) < 30                            # only about the first 0.2 s


def test_not_a_mac_gives_clear_error(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    with pytest.raises(RuntimeError, match="only works on macOS"):
        reader.start(lambda sample: None)
    assert not reader.is_running()


def test_log_file_and_delete(monkeypatch, tmp_path):
    monkeypatch.setattr(log, "LOG_DIR", tmp_path / "local_logs")
    sample_log = log.SampleLog()
    sample_log.write({"t": 0.01, "x": 1.0, "y": 2.0})
    sample_log.close()
    assert sample_log.path.read_text(encoding="utf-8") == "t,x,y\n0.0100,1.0,2.0\n"
    sessions = tmp_path / "local_logs" / "sessions"            # saved session summaries
    sessions.mkdir()
    (sessions / "session_x.json").write_text("{}", encoding="utf-8")
    assert log.delete_all_logs() == 2
    assert list((tmp_path / "local_logs").iterdir()) == []


@pytest.mark.skipif(sys.platform != "darwin", reason="needs macOS")
def test_real_mac_position_needs_no_permission():
    x, y = reader.read_position()
    assert isinstance(x, float) and isinstance(y, float)
