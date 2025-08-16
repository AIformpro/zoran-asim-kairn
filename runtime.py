from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from .memory.fractal_memory import FractalMemory
from .guards.delta_m113 import DeltaM113
from .modules.kairn.emotion_matrix import EmotionMatrix
from .modules.kairn.room_framework import RoomContext
from .modules.reasoners.mock_reasoner import MockReasoner

@dataclass
class Reply:
    text: str
    metrics: Dict[str, Any]

class ZRuntime:
    def __init__(self):
        self.mem = FractalMemory()
        self.guard = DeltaM113()
        self.kairn = EmotionMatrix()
        self.reasoner = MockReasoner()

    def handle(self, text: str, room: RoomContext|None=None) -> Reply:
        if room is None:
            room = RoomContext()
        # 1) affect
        ev = self.kairn.infer(text)
        # 2) memory push
        self.mem.add("user", text, src="input", room=room.to_dict(), vad=ev.as_tuple())
        # 3) guard/rollback: if unstable, neutralize tone
        stable = self.guard.check(text)
        vad = ev.as_tuple()
        out = self.reasoner.respond(text, vad if stable else (0.0,0.2,0.5))
        self.mem.add("assistant", out, src="runtime", stable=stable)
        metrics = {
            "stable": stable,
            "entropy": self.guard.last_entropy,
            "vad": vad,
            "room": room.to_dict()
        }
        return Reply(out, metrics)
