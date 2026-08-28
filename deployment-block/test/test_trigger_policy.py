#!/usr/bin/env python3
"""Unit tests for TriggerPolicy (plain python, no pytest needed)."""
import os
import sys
import time
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scaffold"))
from agent import TriggerPolicy  # noqa: E402

CFG = {
    "classes": ["hardhat", "no_hardhat"],
    "ignore_classes": ["background"],
    "min_confidence": 0.6,
    "consecutive_inferences": 2,
    "cooldown_seconds": 10,
}


def test_needs_consecutive_frames():
    p = TriggerPolicy(CFG)
    assert p.update([("no_hardhat", 0.9)]) is None, "must not fire on first frame"
    assert p.update([("no_hardhat", 0.9)]) == ("no_hardhat", 0.9), "fires on second"


def test_cooldown_blocks_then_allows():
    p = TriggerPolicy(CFG)
    p.update([("no_hardhat", 0.9)])
    assert p.update([("no_hardhat", 0.9)]) is not None
    p.update([("no_hardhat", 0.9)])
    assert p.update([("no_hardhat", 0.9)]) is None, "cooldown must block refire"
    with patch("time.monotonic", return_value=time.monotonic() + 11):
        # streak persisted through the cooldown, so the next update fires
        assert p.update([("no_hardhat", 0.9)]) is not None, "fires again after cooldown"


def test_ignored_and_unwatched_never_fire():
    p = TriggerPolicy(CFG)
    for _ in range(5):
        assert p.update([("background", 0.99)]) is None
        assert p.update([("someone_elses_class", 0.99)]) is None


def test_low_confidence_never_fires():
    p = TriggerPolicy(CFG)
    for _ in range(5):
        assert p.update([("no_hardhat", 0.59)]) is None


def test_streak_resets_when_label_drops_out():
    p = TriggerPolicy(CFG)
    assert p.update([("no_hardhat", 0.9)]) is None
    assert p.update([]) is None
    assert p.update([("no_hardhat", 0.9)]) is None, "streak must reset after a gap"
    assert p.update([("no_hardhat", 0.9)]) is not None


def test_empty_watchlist_watches_everything():
    p = TriggerPolicy({**CFG, "classes": []})
    p.update([("anything", 0.9)])
    assert p.update([("anything", 0.9)]) == ("anything", 0.9)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"  ok: {fn.__name__}")
    print(f"{len(fns)} trigger-policy tests passed")
