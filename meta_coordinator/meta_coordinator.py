#!/usr/bin/env python3
"""
meta_coordinator.py
Unified entry point for the Meta-Coordinator system.
Now runs through Mirror Grammar governance lanes.
Integrates CRP (Constraint Response Protocol) for health-aware operation.

Usage:
  python3 meta_coordinator.py           # Full governance flow (W->I->Y->A)
  python3 meta_coordinator.py legacy    # Original engine-only mode
  python3 meta_coordinator.py map       # Show lane map
  python3 meta_coordinator.py status    # Show lane status as JSON
  python3 meta_coordinator.py crp       # CRP status (tier + service health)
  python3 meta_coordinator.py heartbeat # Run CRP heartbeat loop
  python3 meta_coordinator.py bootstrap # Zero-knowledge bootstrap
  python3 meta_coordinator.py handover  # Show/change handover state
  python3 meta_coordinator.py resonance # Emit/set resonance signature
  python3 meta_coordinator.py seed      # Generate/verify fork seed
  python3 meta_coordinator.py eko       # Eko invocation layer (status/invoke/respond)
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add parent dir for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from engine import (
    load_config, evaluate_pillar_need, generate_recommendations,
    select_top_recommendations, format_output, get_engine_results,
)
from mirror_grammar import (
    run_governance_flow, print_lane_map, quick_lane_status,
    lane_check, Lane,
)
from state_input import capture_state
from crp import (
    HealthAssessor, Heartbeat, Tier,
    Handover, HandoverState, HANDOVER_TRIGGERS,
    ResonanceSignature,
    bootstrap, write_checkpoint, read_checkpoint,
    generate_seed, write_seed, read_seed,
    _print_tier_status, _print_handover_status, _print_resonance,
)


def run_legacy():
    """Original mode: state_input -> engine -> recommendation."""
    print(">_ META-COORDINATOR v0.1 (legacy mode)")
    print(">_ BUILD PROTOCOL ENGAGED")

    print("\n>_ INITIATING DAILY CALIBRATION...")
    state = capture_state()
    state['timestamp'] = datetime.now().isoformat()

    print(">_ STATE CAPTURED")
    print(">_ RUNNING DECISION ENGINE...")

    results = get_engine_results(state)
    primary = results['primary']
    alternative = results['alternative']

    if not primary:
        print("No viable recommendations. Check project configurations.")
        sys.exit(1)

    output = format_output(
        primary, alternative,
        results['pillar_scores'], state,
    )
    print(output)


def run_governed():
    """
    Mirror Grammar mode: W -> I -> Y -> A governance pass
    with the Meta-Coordinator engine feeding into II and AllA lanes.
    CRP-aware: probes services first and adapts to current tier.
    """
    print("\n>_ META-COORDINATOR v0.3")
    print(">_ MIRROR GRAMMAR GOVERNANCE MODE (CRP-AWARE)")
    print(">_ W -> I -> Y -> A\n")

    # CRP pre-check: assess service health and operating tier
    assessor = HealthAssessor()
    assessor.probe_all(force=True)
    tier = assessor.assess_tier()
    summary = assessor.summary()

    # Check handover state
    handover = Handover()

    print(f"CRP Tier:    {tier.label}")
    print(f"Services:    {summary['healthy']}/{summary['total']} healthy")
    print(f"Handover:    {handover.state.label}")

    if tier == Tier.CHECKPOINT:
        print("\n  ALL SERVICES DOWN — entering checkpoint mode.")
        print("  Run 'meta_coordinator.py bootstrap' when services recover.")
        write_checkpoint(assessor, extra_residue={"event": "governance_aborted"})
        sys.exit(1)

    if tier == Tier.MINIMAL:
        print("\n  WARNING: Minimal tier — essential services may be down.")
        print("  Governance will proceed but results may be degraded.\n")

    # Write checkpoint at governance start (residue: session beginning)
    write_checkpoint(assessor, extra_residue={"event": "governance_start"},
                     handover=handover)

    # Pre-check: show which lane we should start at
    check = lane_check(Lane.W)
    print(f"Starting at: {check['current_lane']}")
    print(f"Question:    {check['current_question']}")
    print(f"W-lane services: {', '.join(check['services_active'])}")

    # Step 1: Capture raw state (WeeW input)
    state = capture_state()
    state['timestamp'] = datetime.now().isoformat()

    # Step 2: Run engine to get pillar scores and recommendations
    # (These feed into II and AllA lanes)
    results = get_engine_results(state)

    # Step 3: Run the full governance flow
    # Mirror Grammar uses engine results for II (pillar scores)
    # and AllA (project recommendations)
    gp = run_governance_flow(
        pre_state=state,
        pillar_scores=results['pillar_scores'],
        recommendations=results['recommendations'],
    )

    # Step 4: Show what the engine would have recommended vs what was chosen
    primary = results['primary']
    if primary:
        engine_pick = primary.project['name']
        governed_pick = gp.decision

        if engine_pick != governed_pick:
            print(f"\n  Note: Engine recommended '{engine_pick}', "
                  f"governance chose '{governed_pick}'.")
            print("  The lane flow may surface context the engine misses.")
        else:
            print(f"\n  Engine and governance aligned on: {governed_pick}")

    # Log the combined entry
    log_path = script_dir / "history.log"
    log_entry = {
        'timestamp': state.get('timestamp', ''),
        'mode': 'governed',
        'state': state,
        'governance_pass_id': gp.pass_id,
        'engine_recommendation': primary.project['key'] if primary else None,
        'governed_decision': gp.decision,
        'pillar': gp.lane_states.get('I', {}).content.get('pillar', 'unknown')
                  if 'I' in gp.lane_states else 'unknown',
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

    # Post-governance checkpoint (residue: session complete)
    write_checkpoint(assessor, extra_residue={
        "event": "governance_complete",
        "decision": gp.decision,
        "pass_id": gp.pass_id,
    }, handover=handover)

    print("\nConstruction begins with your next breath.")


def run_crp_status():
    """Show CRP tier and service health."""
    assessor = HealthAssessor()
    assessor.probe_all(force=True)
    tier = assessor.assess_tier()
    _print_tier_status(assessor, tier)


def run_heartbeat():
    """Run the CRP heartbeat loop."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    assessor, tier, boot_info = bootstrap()
    print(f"\n  Bootstrap: {boot_info['method']}")
    if boot_info['parent_id']:
        print(f"  Parent: {boot_info['parent_id'][:8]}...")
    _print_tier_status(assessor, tier)
    print(f"  Heartbeat starting (interval={interval}s, Ctrl+C to stop)\n")
    hb = Heartbeat(assessor=assessor, interval=interval)
    hb.run()


def run_bootstrap():
    """Zero-knowledge bootstrap."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    assessor, tier, boot_info = bootstrap()
    print(f"\n  Bootstrap method: {boot_info['method']}")
    if boot_info['parent_id']:
        print(f"  Parent incarnation: {boot_info['parent_id'][:8]}...")
    _print_tier_status(assessor, tier)


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "legacy":
            run_legacy()
        elif cmd == "map":
            print_lane_map()
        elif cmd == "status":
            status = quick_lane_status()
            print(json.dumps(status, indent=2))
        elif cmd == "crp":
            run_crp_status()
        elif cmd == "heartbeat":
            run_heartbeat()
        elif cmd == "bootstrap":
            run_bootstrap()
        elif cmd == "handover":
            # Pass remaining args to crp.py handover
            import crp as crp_mod
            sys.argv = ["crp.py", "handover"] + sys.argv[2:]
            crp_mod.main()
        elif cmd == "resonance":
            import crp as crp_mod
            sys.argv = ["crp.py", "resonance"] + sys.argv[2:]
            crp_mod.main()
        elif cmd == "seed":
            import crp as crp_mod
            sys.argv = ["crp.py", "seed"] + sys.argv[2:]
            crp_mod.main()
        elif cmd == "eko":
            import eko_invocation
            sys.argv = ["eko_invocation.py"] + sys.argv[2:]
            eko_invocation.main()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: meta_coordinator.py [legacy|map|status|crp|heartbeat|bootstrap|handover|resonance|seed|eko]")
            sys.exit(1)
    else:
        run_governed()


if __name__ == "__main__":
    main()
