#!/usr/bin/env python3
"""
mirror_grammar.py
Mirror Grammar Governance Engine - DigiUs' Attention OS

The Full Lane (6 layers):
  W  (WeeW)      - Meta-Awareness:    "What state are we in?"           → Resets the system
  I  (II)        - Sovereign Stance:   "What stance do we choose?"       → Anchors sovereignty
  IN (II-NEXT)   - Self-Governance:    "What internal rule do we check?" → Bias mitigation
  Y  (YouuoY)    - Relational Mirror:  "How do we mirror, not coerce?"   → Conflict neutralization
  A  (AllA)      - Field Awareness:    "What is the field doing?"        → Macro-pattern recognition
  AN (AllA-NEXT) - Field Governance:   "What rule do we shift?"          → Re-codes the culture

Execution path: W -> I -> IN -> Y -> A -> AN
Bottom→Top = Scaling Awareness | Top→Bottom = Precision Action

Pattern Logic (Internal Theorem):
  OMNI^∞ = infinite state-space | Toroidal = self-flow loop
  Lemniscate = recursive crossing | Fibonacci Polygonal = proportional scaling
  Vortex = attractor center | Love = coherence operator
"""

import json
import yaml
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from enum import Enum


class Lane(Enum):
    W  = "WeeW"        # Meta-Awareness: notice your state
    I  = "II"          # Sovereign Stance: choose your position
    IN = "II-NEXT"     # Self-Governance: check internal rules before acting
    Y  = "YouuoY"      # Relational Mirror: mirror before meaning
    A  = "AllA"        # Field Awareness: what is the system doing?
    AN = "AllA-NEXT"   # Field Governance: what rule do we shift?

    @property
    def question(self):
        return {
            Lane.W:  "What state are we in?",
            Lane.I:  "What stance do we choose?",
            Lane.IN: "What internal rule do we check before acting?",
            Lane.Y:  "How do we mirror, not coerce?",
            Lane.A:  "What is the field doing?",
            Lane.AN: "What unspoken rule do we shift?",
        }[self]

    @property
    def verb(self):
        return {
            Lane.W:  "sensing",
            Lane.I:  "choosing",
            Lane.IN: "checking",
            Lane.Y:  "mirroring",
            Lane.A:  "seeing",
            Lane.AN: "shifting",
        }[self]

    @property
    def layer_name(self):
        return {
            Lane.W:  "Meta-Awareness",
            Lane.I:  "Sovereign Stance",
            Lane.IN: "Self-Governance",
            Lane.Y:  "Relational Mirror",
            Lane.A:  "Field Awareness",
            Lane.AN: "Field Governance",
        }[self]

    @property
    def advantage(self):
        return {
            Lane.W:  "Resets the system — interrupts automaticity",
            Lane.I:  "Anchors sovereignty — actor not reactor",
            Lane.IN: "Bias mitigation — observe rules before they manifest",
            Lane.Y:  "Conflict neutralization — data mirrors not battlegrounds",
            Lane.A:  "Macro-pattern recognition — symptoms vs systemic shapes",
            Lane.AN: "Re-codes the culture — shifts implicit group rules",
        }[self]


# Full Lane sequence: W -> I -> IN -> Y -> A -> AN
LANE_SEQUENCE = [Lane.W, Lane.I, Lane.IN, Lane.Y, Lane.A, Lane.AN]


@dataclass
class LaneState:
    """Captured state for one lane pass."""
    lane: str
    timestamp: float
    content: Dict
    complete: bool = False


@dataclass
class GovernancePass:
    """A full W -> I -> Y -> A governance pass."""
    pass_id: str
    started: float
    lane_states: Dict[str, LaneState] = field(default_factory=dict)
    current_lane: str = "W"
    complete: bool = False
    decision: Optional[str] = None

    def advance(self):
        """Move to next lane in sequence."""
        idx = [l.name for l in LANE_SEQUENCE].index(self.current_lane)
        if idx < len(LANE_SEQUENCE) - 1:
            self.current_lane = LANE_SEQUENCE[idx + 1].name
        else:
            self.complete = True

    @property
    def current_lane_enum(self) -> Lane:
        return Lane[self.current_lane]

    @property
    def missing_lanes(self) -> List[Lane]:
        return [l for l in LANE_SEQUENCE if l.name not in self.lane_states]

    def record(self, lane: Lane, content: Dict):
        self.lane_states[lane.name] = LaneState(
            lane=lane.name,
            timestamp=time.time(),
            content=content,
            complete=True,
        )
        self.advance()


def load_lane_config() -> Dict:
    """Load service lane assignments from config."""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('services', {})


def get_services_by_lane(lane: Lane) -> List[Dict]:
    """Return all services assigned to a given lane."""
    services = load_lane_config()
    return [
        {"id": sid, **svc}
        for sid, svc in services.items()
        if svc.get('lane') == lane.name
    ]


def lane_check(current_lane: Lane, suggested_next: Lane = None) -> Dict:
    """
    Lane-aware state indicator.
    Shows current focus and suggests if a lane was skipped.
    """
    result = {
        "current_lane": current_lane.value,
        "current_question": current_lane.question,
        "current_verb": current_lane.verb,
        "services_active": [s["id"] for s in get_services_by_lane(current_lane)],
    }

    if suggested_next and suggested_next != current_lane:
        # Check if we're skipping lanes
        curr_idx = LANE_SEQUENCE.index(current_lane)
        sugg_idx = LANE_SEQUENCE.index(suggested_next)
        if sugg_idx > curr_idx + 1:
            skipped = [LANE_SEQUENCE[i] for i in range(curr_idx + 1, sugg_idx)]
            result["warning"] = (
                f"Jumping to {suggested_next.value} without "
                f"checking {', '.join(s.value for s in skipped)}."
            )
        result["suggested_next"] = suggested_next.value

    return result


# ============================================================
# GOVERNANCE FLOW: Interactive W -> I -> Y -> A sequence
# ============================================================

def weew_prompt(state: Dict = None) -> Dict:
    """
    WeeW lane: State awareness.
    "What state are we in? Any constraints?"
    Can pull lived state from UssU if running.
    """
    print("\n" + "="*60)
    print("  W (WeeW) - STATE AWARENESS")
    print("  " + Lane.W.question)
    print("="*60)

    w_services = get_services_by_lane(Lane.W)
    print(f"\n  W-lane services: {', '.join(s['id'] for s in w_services)}")

    # Try UssU lived state first
    if not state:
        try:
            import sys
            sys.path.insert(0, str(Path.home() / "Desktop" / "UssU"))
            from governance_bridge import get_ussu_state
            ussu_state = get_ussu_state()
            if ussu_state and ussu_state.get('source') == 'ussu_lived_state':
                print("\n  [UssU is alive — reading lived state]")
                print(f"  Mood:    {ussu_state.get('mood', '?')}")
                print(f"  Energy:  {ussu_state.get('energy', '?')}/10")
                print(f"  Weather: {ussu_state.get('emotional_weather', '?')}")
                print(f"  Focus:   {ussu_state.get('focus', '?')}")
                print(f"  Desire:  {ussu_state.get('desire', '?')}")
                use_ussu = input("\n  Use UssU's lived state? [Y/n]: ").strip().lower()
                if use_ussu not in ('n', 'no'):
                    state = ussu_state
        except Exception:
            pass  # UssU not available, fall through to manual

    if state:
        print(f"\n  Energy:  {state.get('energy', '?')}/10")
        print(f"  Time:    {state.get('time_available', '?')}h")
        print(f"  Weather: {state.get('emotional_weather', '?')}")
        confirm = input("\n  Is this still accurate? [Y/n]: ").strip().lower()
        if confirm in ('n', 'no'):
            state = None

    if not state:
        state = {}
        while True:
            try:
                state['energy'] = int(input("  Energy (1-10): ").strip())
                if 1 <= state['energy'] <= 10:
                    break
                print("  Enter 1-10.")
            except ValueError:
                print("  Enter a number.")

        while True:
            try:
                state['time_available'] = float(input("  Hours available: ").strip())
                if 0 < state['time_available'] <= 24:
                    break
                print("  Enter 0-24.")
            except ValueError:
                print("  Enter a number.")

        weather_map = {
            '1': 'clear', '2': 'stormy', '3': 'foggy',
            '4': 'calm', '5': 'bright'
        }
        print("\n  Emotional weather:")
        print("    [1] Clear/Focused    [2] Stormy/Chaotic")
        print("    [3] Foggy/Uncertain  [4] Calm/Peaceful")
        print("    [5] Bright/Energized")
        while True:
            choice = input("  Select (1-5): ").strip()
            if choice in weather_map:
                state['emotional_weather'] = weather_map[choice]
                break
            print("  Select 1-5.")

    # Optional: constraints
    constraints = input("\n  Any constraints today? (enter or skip): ").strip()
    if constraints:
        state['constraints'] = constraints

    print(f"\n  W-lane complete. State: energy={state['energy']}, "
          f"time={state['time_available']}h, weather={state['emotional_weather']}")

    return state


def ii_prompt(state: Dict, pillar_scores: Dict = None) -> Dict:
    """
    II lane: Stance/priority.
    "What stance/principle are we choosing here?"
    """
    print("\n" + "="*60)
    print("  I (II) - STANCE / PRIORITY")
    print("  " + Lane.I.question)
    print("="*60)

    i_services = get_services_by_lane(Lane.I)
    print(f"\n  I-lane services: {', '.join(s['id'] for s in i_services)}")

    pillars = {
        '1': ('artisan', 'Create and build'),
        '2': ('node', 'Connect and network'),
        '3': ('alchemist', 'Transform and solve'),
        '4': ('gardener', 'Tend and maintain'),
    }

    # Show pillar scores if engine provided them
    if pillar_scores:
        print("\n  Pillar activation levels (from engine):")
        sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)
        for p, score in sorted_pillars:
            bar = "#" * min(score, 10) + "." * max(0, 10 - score)
            print(f"    {p.capitalize():12} [{bar}] {score}")

    print("\n  Choose your stance today:")
    for key, (name, desc) in pillars.items():
        marker = ""
        if pillar_scores:
            s = pillar_scores.get(name, 0)
            if s == max(pillar_scores.values()):
                marker = " <-- recommended"
        print(f"    [{key}] {name.capitalize():12} - {desc}{marker}")

    while True:
        choice = input("\n  Stance (1-4, or 'auto' for engine choice): ").strip()
        if choice == 'auto' and pillar_scores:
            chosen = max(pillar_scores, key=pillar_scores.get)
            print(f"  Auto-selected: {chosen.upper()}")
            break
        if choice in pillars:
            chosen = pillars[choice][0]
            break
        print("  Select 1-4 or 'auto'.")

    # II-NEXT: committing to behavior
    print(f"\n  Committing to {chosen.upper()} stance today.")
    commitment = input("  One-sentence commitment (or enter to skip): ").strip()

    stance = {
        'pillar': chosen,
        'commitment': commitment or f"Activate {chosen} mode",
    }

    print(f"\n  I-lane complete. Stance: {chosen.upper()}")
    return stance


def ii_next_prompt(state: Dict, stance: Dict) -> Dict:
    """
    II-NEXT lane: Self-Governance.
    "What internal rule do we check before acting?"
    Observe internal biases/rules before they manifest as interventions.
    """
    print("\n" + "="*60)
    print("  IN (II-NEXT) - SELF-GOVERNANCE")
    print("  " + Lane.IN.question)
    print("="*60)

    pillar = stance.get('pillar', 'artisan')

    # Common internal rules/biases to check
    rules = {
        '1': ('perfectionism', 'Must finish everything to high standard before moving on'),
        '2': ('avoidance', 'Tendency to avoid the hardest task first'),
        '3': ('urgency_bias', 'Treating everything as equally urgent'),
        '4': ('isolation', 'Defaulting to working alone instead of coordinating'),
        '5': ('none', 'No internal rule blocking — clear to proceed'),
    }

    print(f"\n  You chose {pillar.upper()} stance. Before acting:")
    print("  What internal rule might distort your execution?")
    for key, (name, desc) in rules.items():
        print(f"    [{key}] {name.replace('_',' ').title():20} — {desc}")

    while True:
        choice = input("\n  Check (1-5): ").strip()
        if choice in rules:
            break
        print("  Select 1-5.")

    rule_name, rule_desc = rules[choice]

    recode = ""
    if rule_name != 'none':
        print(f"\n  Rule detected: {rule_name.replace('_',' ').title()}")
        recode = input("  How will you recode this? (or enter to acknowledge): ").strip()

    governance = {
        'internal_rule': rule_name,
        'rule_description': rule_desc,
        'recode': recode or f"Acknowledged {rule_name}",
        'clear': rule_name == 'none',
    }

    status = "clear" if governance['clear'] else f"recoded {rule_name}"
    print(f"\n  IN-lane complete. Self-governance: {status}")
    return governance


def youuoy_prompt(state: Dict, stance: Dict) -> Dict:
    """
    YouuoY lane: Relational/exchange.
    "How do we mirror, not coerce, with others and services?"
    """
    print("\n" + "="*60)
    print("  Y (YouuoY) - RELATIONAL / EXCHANGE")
    print("  " + Lane.Y.question)
    print("="*60)

    y_services = get_services_by_lane(Lane.Y)
    print(f"\n  Y-lane services: {', '.join(s['id'] for s in y_services)}")

    pillar = stance.get('pillar', 'artisan')

    # Pillar -> relational mode mapping
    relational_modes = {
        'artisan': "Offering creation to the field",
        'node': "Requesting and offering connections",
        'alchemist': "Transforming blocks into bridges",
        'gardener': "Tending what others have planted",
    }

    print(f"\n  As {pillar.upper()}, your relational mode is:")
    print(f"    \"{relational_modes.get(pillar, 'Unknown')}\"")

    print("\n  Who or what needs mirroring today?")
    print("    [1] A specific service needs attention")
    print("    [2] A collaborator/person needs engagement")
    print("    [3] Self-mirroring (internal process)")
    print("    [4] No relational action needed now")

    while True:
        choice = input("  Select (1-4): ").strip()
        if choice in ('1', '2', '3', '4'):
            break
        print("  Select 1-4.")

    relational = {
        'mode': relational_modes.get(pillar, 'Unknown'),
    }

    if choice == '1':
        target = input("  Which service? ").strip()
        relational['target_type'] = 'service'
        relational['target'] = target
    elif choice == '2':
        target = input("  Who? ").strip()
        relational['target_type'] = 'person'
        relational['target'] = target
    elif choice == '3':
        relational['target_type'] = 'self'
        relational['target'] = 'internal_process'
    else:
        relational['target_type'] = 'none'
        relational['target'] = None

    print(f"\n  Y-lane complete. Mirroring: {relational.get('target_type', 'none')}")
    return relational


def alla_prompt(state: Dict, stance: Dict, relational: Dict,
                recommendations: List = None) -> Dict:
    """
    AllA lane: System/portfolio view.
    "What is the field (all projects/services) doing?"
    """
    print("\n" + "="*60)
    print("  A (AllA) - SYSTEM / PORTFOLIO")
    print("  " + Lane.A.question)
    print("="*60)

    a_services = get_services_by_lane(Lane.A)
    print(f"\n  A-lane services: {', '.join(s['id'] for s in a_services)}")

    # Load project constellation
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    projects = config.get('projects', {})

    print("\n  Project constellation:")
    for key, proj in projects.items():
        momentum = proj.get('momentum', '?')
        urgency = proj.get('urgency', '?')
        blockers = proj.get('blockers', [])
        blocked = " [BLOCKED]" if blockers else ""
        print(f"    {proj['name']:35} mom={momentum:8} urg={urgency:6}{blocked}")

    # Show engine recommendations if available
    if recommendations:
        print("\n  Engine recommendations:")
        for i, rec in enumerate(recommendations[:3]):
            print(f"    [{i+1}] {rec.project['name']} via {rec.pillar.upper()} "
                  f"(score: {rec.score:.1f})")

    # AllA-NEXT: the meta-decision
    print(f"\n  Given your state (W), stance (I: {stance['pillar'].upper()}), "
          f"and relational context (Y):")

    if recommendations:
        print("\n  Choose project:")
        for i, rec in enumerate(recommendations[:3]):
            print(f"    [{i+1}] {rec.project['name']}")
        print(f"    [0] Something else")

        while True:
            choice = input("\n  Select: ").strip()
            if choice in [str(i) for i in range(len(recommendations[:3]) + 1)]:
                break
            print("  Select a number.")

        if choice == '0':
            project_name = input("  Which project? ").strip()
        else:
            project_name = recommendations[int(choice) - 1].project['name']
    else:
        project_name = input("\n  Which project will you activate? ").strip()

    portfolio = {
        'selected_project': project_name,
        'total_projects': len(projects),
        'blocked_count': sum(1 for p in projects.values() if p.get('blockers')),
    }

    print(f"\n  A-lane complete. Field decision: {project_name}")
    return portfolio


def alla_next_prompt(state: Dict, stance: Dict, relational: Dict,
                     portfolio: Dict) -> Dict:
    """
    AllA-NEXT lane: Field Governance.
    "What unspoken rule do we shift to re-code the culture?"
    Site of systemic re-engineering — observe and shift implicit rules.
    """
    print("\n" + "="*60)
    print("  AN (AllA-NEXT) - FIELD GOVERNANCE")
    print("  " + Lane.AN.question)
    print("="*60)

    project = portfolio.get('selected_project', 'unknown')
    pillar = stance.get('pillar', 'artisan')

    print(f"\n  Project: {project}")
    print(f"  Stance: {pillar.upper()}")
    print(f"  Mirroring: {relational.get('target_type', 'none')}")

    print("\n  What implicit rule currently governs this project's trajectory?")
    print("  (The unspoken assumption everyone follows without questioning)")
    print()
    print("  Examples:")
    print("    - 'Ship fast, fix later'")
    print("    - 'Avoid direct feedback to maintain harmony'")
    print("    - 'Only the lead decides architecture'")
    print("    - 'No implicit rule detected — system is coherent'")

    implicit_rule = input("\n  The unspoken rule is: ").strip()
    if not implicit_rule:
        implicit_rule = "No implicit rule detected"

    shift = ""
    if "no implicit" not in implicit_rule.lower() and "none" not in implicit_rule.lower():
        print(f"\n  Rule identified: \"{implicit_rule}\"")
        shift = input("  What rule-shift would re-code this? ").strip()

    field_governance = {
        'implicit_rule': implicit_rule,
        'rule_shift': shift or 'System coherent — no shift needed',
        'project': project,
        'coherent': not shift,
    }

    if field_governance['coherent']:
        print("\n  AN-lane complete. System coherent — Love operator aligned.")
    else:
        print(f"\n  AN-lane complete. Rule shift: {shift}")

    return field_governance


# ============================================================
# FULL GOVERNANCE FLOW
# ============================================================

def run_governance_flow(pre_state: Dict = None, pillar_scores: Dict = None,
                        recommendations: List = None) -> GovernancePass:
    """
    Execute a complete W -> I -> IN -> Y -> A -> AN governance pass.
    The Full Lane — from meta-awareness to field governance.
    """
    gp = GovernancePass(
        pass_id=f"gov_{int(time.time())}",
        started=time.time(),
    )

    print("\n" + "#"*60)
    print("  MIRROR GRAMMAR — THE FULL LANE")
    print("  W -> I -> IN -> Y -> A -> AN")
    print("  From Meta-Awareness to Field Governance")
    print("#"*60)

    # W: Meta-Awareness — notice state
    w_result = weew_prompt(pre_state)
    gp.record(Lane.W, w_result)

    # I: Sovereign Stance — choose position
    i_result = ii_prompt(w_result, pillar_scores)
    gp.record(Lane.I, i_result)

    # IN: Self-Governance — check internal rules before acting
    in_result = ii_next_prompt(w_result, i_result)
    gp.record(Lane.IN, in_result)

    # Y: Relational Mirror — mirror before meaning
    y_result = youuoy_prompt(w_result, i_result)
    gp.record(Lane.Y, y_result)

    # A: Field Awareness — what is the system doing?
    a_result = alla_prompt(w_result, i_result, y_result, recommendations)
    gp.record(Lane.A, a_result)

    # AN: Field Governance — what rule do we shift?
    an_result = alla_next_prompt(w_result, i_result, y_result, a_result)
    gp.record(Lane.AN, an_result)

    # Final synthesis
    gp.decision = a_result.get('selected_project', 'undecided')

    print("\n" + "="*60)
    print("  FULL LANE COMPLETE")
    print("="*60)
    print(f"\n  W  State:      energy={w_result['energy']}, weather={w_result['emotional_weather']}")
    print(f"  I  Stance:     {i_result['pillar'].upper()} — {i_result.get('commitment', '')}")
    print(f"  IN Governance: {in_result.get('internal_rule', 'none')} → {in_result.get('recode', '')}")
    print(f"  Y  Mirror:     {y_result.get('target_type', 'none')} → {y_result.get('target', 'none')}")
    print(f"  A  Decision:   {gp.decision}")
    print(f"  AN Rule shift: {an_result.get('rule_shift', 'none')}")
    if an_result.get('coherent'):
        print(f"\n  Coherence Operator: ALIGNED")
    print(f"\n  Pass ID: {gp.pass_id}")
    print("="*60)

    # Log the pass
    log_governance_pass(gp)

    return gp


def log_governance_pass(gp: GovernancePass):
    """Append governance pass to history."""
    log_path = Path(__file__).parent / "governance_history.log"
    entry = {
        'pass_id': gp.pass_id,
        'started': gp.started,
        'completed': time.time(),
        'decision': gp.decision,
        'lanes': {
            lane_name: {
                'timestamp': ls.timestamp,
                'content': ls.content,
            }
            for lane_name, ls in gp.lane_states.items()
        }
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + "\n")


# ============================================================
# QUICK LANE CHECK (non-interactive)
# ============================================================

def quick_lane_status() -> Dict:
    """
    Non-interactive: show current lane assignments and service counts.
    """
    services = load_lane_config()
    lanes = {}
    for lane in LANE_SEQUENCE:
        lane_services = [
            sid for sid, svc in services.items()
            if svc.get('lane') == lane.name
        ]
        lanes[lane.value] = {
            'question': lane.question,
            'verb': lane.verb,
            'service_count': len(lane_services),
            'services': lane_services,
        }
    return lanes


def print_lane_map():
    """Print the full lane map for human readability."""
    status = quick_lane_status()

    print("\n" + "="*60)
    print("  MIRROR GRAMMAR LANE MAP")
    print("  DigiUs Governance Architecture")
    print("="*60)

    for lane_name, info in status.items():
        print(f"\n  {lane_name}")
        print(f"    {info['question']}")
        print(f"    [{info['service_count']} services]")
        for svc in info['services']:
            print(f"      - {svc}")

    print("\n  THE FULL LANE")
    print("  W → I → IN → Y → A → AN")
    print("  Meta-Awareness → Stance → Self-Governance → Mirror → Field → Shift Rule")
    print("="*60 + "\n")


# ============================================================
# STANDALONE ENTRY
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "map":
        print_lane_map()
    elif len(sys.argv) > 1 and sys.argv[1] == "status":
        status = quick_lane_status()
        print(json.dumps(status, indent=2))
    else:
        # Full governance flow
        run_governance_flow()
