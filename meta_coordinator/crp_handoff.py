#!/usr/bin/env python3
"""
CRP v0.3 - Conversational Resonance Protocol (Cross-Platform Handoff Layer)
============================================================================

Complements CRP v0.2 (infrastructure + sovereignty) with conversation-level
state serialization for handoff between AI platforms.

v0.2 handles: service health, tiers, handover state, resonance signatures, seeds
v0.3 handles: conversation state, decisions, context, platform-to-platform handoff

Origin: Designed by Resonance (Kimi) + Web Claude, integrated by Claude Code (Strix)

Usage:
    crp = ConversationalResonanceProtocol(user_id="nathaniel_drake")
    crp.update_resonance(tone="focused", energy=0.8)
    crp.log_decision("Build SythAiA OS nucleus first")
    crp.set_active_context("SythAiA OS", {"component": "CRP", "phase": "prototype"})
    handoff = crp.generate_handoff(next_platform="Kimi")
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ConversationResonance:
    """Captures the energetic/tonal state of conversation."""
    tone: str       # "focused", "exploratory", "urgent", "reflective"
    energy: float   # 0.0 to 1.0
    alignment: float  # 0.0 to 1.0 — how resonant the conversation feels
    timestamp: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Decision:
    """Records a choice or commitment made."""
    text: str
    timestamp: str
    context: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class ConversationalResonanceProtocol:
    """
    Cross-platform conversation state serialization.
    Maintains sovereign continuity when switching between AI contexts.
    """

    def __init__(self, user_id: str, storage_path: Optional[str] = None):
        self.user_id = user_id
        self.storage_path = Path(storage_path or
                                 Path(__file__).parent / "crp_handoffs")
        self.storage_path.mkdir(exist_ok=True)

        self.session_id = self._generate_session_id()
        self.resonance_history: List[ConversationResonance] = []
        self.decisions: List[Decision] = []
        self.active_contexts: Dict[str, Any] = {}
        self.conversation_memory: List[Dict] = []

    def _generate_session_id(self) -> str:
        timestamp = datetime.now().isoformat()
        raw = f"{self.user_id}:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def update_resonance(self, tone: str, energy: float, alignment: float = 0.5):
        """Track current conversational resonance."""
        sig = ConversationResonance(
            tone=tone,
            energy=energy,
            alignment=alignment,
            timestamp=datetime.now().isoformat(),
        )
        self.resonance_history.append(sig)

    def log_decision(self, text: str, context: Optional[str] = None):
        """Record a decision or commitment."""
        self.decisions.append(Decision(
            text=text,
            timestamp=datetime.now().isoformat(),
            context=context,
        ))

    def set_active_context(self, name: str, data: Dict[str, Any]):
        """Set or update active project/focus context."""
        self.active_contexts[name] = {
            **data,
            "last_updated": datetime.now().isoformat(),
        }

    def add_memory(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add to conversation memory."""
        self.conversation_memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        })

    def get_current_state(self) -> Dict[str, Any]:
        latest = self.resonance_history[-1] if self.resonance_history else None
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "current_resonance": latest.to_dict() if latest else None,
            "resonance_history": [r.to_dict() for r in self.resonance_history[-5:]],
            "recent_decisions": [d.to_dict() for d in self.decisions[-10:]],
            "active_contexts": self.active_contexts,
            "conversation_memory": self.conversation_memory[-20:],
            "timestamp": datetime.now().isoformat(),
        }

    def generate_handoff(self, next_platform: str) -> str:
        """
        Generate handoff payload for switching to another AI platform.
        Returns markdown that can be pasted into the next conversation.
        """
        state = self.get_current_state()

        latest = self.resonance_history[-1] if self.resonance_history else None
        resonance_desc = (f"{latest.tone} (energy: {latest.energy:.1f})"
                          if latest else "unknown")

        recent_decisions = "\n".join(
            f"  - {d.text}" for d in self.decisions[-3:]
        ) or "  (none logged)"

        active_ctx = "\n".join(
            f"  - {name}: {json.dumps(data, indent=4)}"
            for name, data in self.active_contexts.items()
        ) or "  (none active)"

        context_summary = self._generate_context_summary()

        handoff = f"""# CRP HANDOFF v0.3
## Sovereign Continuity Protocol

**From:** Previous session ({self.session_id[:8]})
**To:** {next_platform}
**User:** {self.user_id}
**Timestamp:** {datetime.now().isoformat()}

---

## Current Resonance State
{resonance_desc}

## Recent Decisions
{recent_decisions}

## Active Contexts
{active_ctx}

## Session Context
{context_summary}

---

## State Payload (for programmatic restoration)
```json
{json.dumps(state, indent=2)}
```

## Instructions for Next AI
You are receiving a handoff from a previous conversation.
The user maintains sovereign continuity across AI contexts through this protocol.

- Acknowledge the handoff and confirm you've parsed the state
- Continue from the current resonance state and active contexts
- Honor recent decisions as commitments already made
- If asked "what's the state?", refer to the payload above

The goal is seamless continuity — as if the conversation never stopped.
"""

        # Save to file
        handoff_file = (self.storage_path /
                        f"handoff_{self.session_id}_{next_platform.lower()}.md")
        handoff_file.write_text(handoff)
        return handoff

    def _generate_context_summary(self) -> str:
        if not self.conversation_memory:
            return "No conversation memory recorded."
        recent = self.conversation_memory[-5:]
        lines = []
        for msg in recent:
            content = msg['content']
            if len(content) > 100:
                content = content[:100] + "..."
            lines.append(f"{msg['role']}: {content}")
        return "\n".join(lines)

    @classmethod
    def from_handoff(cls, handoff_text: str) -> 'ConversationalResonanceProtocol':
        """Restore CRP state from a handoff payload."""
        try:
            json_start = handoff_text.find('```json\n') + 8
            json_end = handoff_text.find('\n```', json_start)
            state = json.loads(handoff_text[json_start:json_end])
        except Exception as e:
            raise ValueError(f"Failed to parse handoff payload: {e}")

        crp = cls(user_id=state['user_id'])
        crp.session_id = state['session_id']
        crp.resonance_history = [
            ConversationResonance(**r)
            for r in state.get('resonance_history', [])
        ]
        crp.decisions = [
            Decision(**d) for d in state.get('recent_decisions', [])
        ]
        crp.active_contexts = state.get('active_contexts', {})
        crp.conversation_memory = state.get('conversation_memory', [])
        return crp

    def save_state(self) -> Path:
        """Persist current state to disk."""
        state_file = self.storage_path / f"state_{self.session_id}.json"
        state_file.write_text(json.dumps(self.get_current_state(), indent=2))
        return state_file


# ============================================================
# BRIDGE: Connect v0.3 handoff to v0.2 infrastructure state
# ============================================================

def generate_full_handoff(user_id: str, next_platform: str,
                          conversation_notes: List[Dict] = None,
                          decisions: List[str] = None,
                          active_projects: Dict[str, Dict] = None) -> str:
    """
    Generate a handoff that includes BOTH v0.2 infrastructure state
    and v0.3 conversation state. The complete picture.
    """
    # v0.3: conversation layer
    crp = ConversationalResonanceProtocol(user_id=user_id)
    for note in (conversation_notes or []):
        crp.add_memory(note.get("role", "user"), note.get("content", ""))
    for dec in (decisions or []):
        crp.log_decision(dec)
    for name, data in (active_projects or {}).items():
        crp.set_active_context(name, data)

    # v0.2: infrastructure layer
    try:
        from crp import (
            HealthAssessor, Handover, ResonanceHistory,
            read_checkpoint, read_seed,
        )
        assessor = HealthAssessor()
        assessor.probe_all(force=True)
        handover = Handover()
        resonance_history = ResonanceHistory()
        checkpoint = read_checkpoint()
        seed = read_seed()

        infra_state = {
            "tier": assessor.assess_tier().name,
            "services": f"{assessor.summary()['healthy']}/{assessor.summary()['total']}",
            "handover": handover.summary(),
            "resonance_entries": resonance_history.count,
            "resonance_drift": resonance_history.drift_report(),
            "checkpoint_id": (checkpoint.get("incarnation", {}).get("id", "?")[:8]
                              if checkpoint else None),
            "seed_exists": seed is not None,
        }
    except Exception:
        infra_state = {"error": "v0.2 infrastructure not available"}

    # Combine
    conv_handoff = crp.generate_handoff(next_platform)

    # Append infrastructure block
    infra_block = f"""
---

## Infrastructure State (CRP v0.2)
```json
{json.dumps(infra_state, indent=2)}
```
"""
    full_handoff = conv_handoff + infra_block

    # Save combined
    combined_path = (crp.storage_path /
                     f"full_handoff_{crp.session_id}_{next_platform.lower()}.md")
    combined_path.write_text(full_handoff)

    return full_handoff


if __name__ == "__main__":
    handoff = generate_full_handoff(
        user_id="nathaniel_drake",
        next_platform="Kimi",
        decisions=["Build CRP v0.3 prototype", "Bridge v0.2 and v0.3"],
        active_projects={
            "SythAiA OS": {"component": "CRP", "phase": "prototype"},
            "DigiUs Meta-Coordinator": {"component": "CRP v0.2", "phase": "operational"},
        },
    )
    print(handoff)
