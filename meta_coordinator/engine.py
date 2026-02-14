#!/usr/bin/env python3
"""
engine.py
Meta-Coordinator Decision Engine
Integrates pillar evaluation with project matching.
"""

import yaml
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Recommendation:
    project: Dict
    pillar: str
    score: float
    reasoning: List[str]
    time_commitment: str


def load_config(config_path: str = None) -> Dict:
    """Load project registry and pillar history."""
    if config_path is None:
        config_path = str(Path(__file__).parent / "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def evaluate_pillar_need(state: Dict, history: Dict) -> Dict[str, int]:
    """
    Determine which pillar needs activation based on state and history.
    """
    scores = {
        'artisan': 0,
        'node': 0,
        'alchemist': 0,
        'gardener': 0
    }

    # ENERGY MAPPING
    energy = state['energy']
    if energy >= 8:
        scores['artisan'] += 2
        scores['alchemist'] += 2
    elif energy >= 5:
        scores['node'] += 2
        scores['gardener'] += 2
    else:
        scores['gardener'] += 3

    # TIME MAPPING
    hours = state['time_available']
    if hours < 1:
        scores['node'] += 2
    elif hours <= 3:
        scores['artisan'] += 2
    else:
        scores['alchemist'] += 2
    scores['gardener'] += 1

    # WEATHER MAPPING
    weather = state['emotional_weather'].lower()
    if 'clear' in weather or 'focus' in weather:
        scores['artisan'] += 2
    elif 'storm' in weather or 'chaos' in weather:
        scores['alchemist'] += 3
    elif 'fog' in weather or 'uncertain' in weather:
        scores['gardener'] += 2
    elif 'calm' in weather or 'peace' in weather:
        scores['node'] += 2
    elif 'bright' in weather or 'energ' in weather:
        scores['artisan'] += 2
        scores['alchemist'] += 1

    # HISTORICAL BALANCE (neglected pillars get boost)
    total_activations = sum(history.values())
    if total_activations > 0:
        for pillar in scores:
            ratio = history.get(pillar, 0) / total_activations
            if ratio < 0.15:  # Severely neglected
                scores[pillar] += 3
            elif ratio < 0.20:  # Slightly neglected
                scores[pillar] += 1

    return scores


def parse_time_range(time_str: str) -> Tuple[float, float]:
    """Parse '1-4 hours' into (1.0, 4.0)."""
    clean = time_str.replace('hours', '').replace('hr', '').strip()
    parts = clean.split('-')
    if len(parts) == 2:
        return float(parts[0]), float(parts[1])
    else:
        val = float(parts[0])
        return val, val


def match_project_to_pillar(project: Dict, pillar: str, state: Dict) -> Tuple[float, List[str]]:
    """
    Calculate fitness score for project-pillar match.
    Returns (score, reasoning_list).
    """
    fitness = 0.0
    reasoning = []

    # Primary pillar alignment
    if project.get('primary_pillar') == pillar:
        fitness += 5
        reasoning.append(f"Primary pillar match ({pillar})")

    # Momentum dynamics
    momentum = project.get('momentum', 'medium')
    if momentum == 'high':
        if pillar == 'gardener':
            fitness += 2
            reasoning.append("High momentum needs tending")
        elif pillar == 'artisan':
            fitness += 1
            reasoning.append("Can build on existing momentum")
    elif momentum == 'low':
        if pillar == 'alchemist':
            fitness += 2
            reasoning.append("Low momentum needs transformation")
        elif pillar == 'artisan':
            fitness += 1
            reasoning.append("Creation can restart momentum")
    elif momentum == 'passive':
        if pillar == 'gardener':
            fitness += 1
            reasoning.append("Passive project needs gentle check-in")

    # Urgency alignment
    urgency = project.get('urgency', 'medium')
    if urgency == 'high':
        if pillar == 'artisan':
            fitness += 3
            reasoning.append("High urgency requires building")
    elif urgency == 'low':
        if pillar == 'gardener':
            fitness += 2
            reasoning.append("Low urgency suits patient tending")

    # Time feasibility
    min_hrs, max_hrs = parse_time_range(project.get('time_sweet_spot', '1-2 hours'))
    available = state['time_available']

    if min_hrs <= available <= max_hrs:
        fitness += 2
        reasoning.append(f"Time fit: {available}h in range {min_hrs}-{max_hrs}h")
    elif available < min_hrs:
        fitness -= 2
        reasoning.append(f"Insufficient time (need {min_hrs}h, have {available}h)")
    elif available > max_hrs * 1.5:
        fitness += 1
        reasoning.append("Abundant time available")

    # Blocker penalty
    blockers = project.get('blockers', [])
    if blockers:
        fitness -= 3
        reasoning.append(f"Blockers present: {', '.join(blockers)}")

    # Energy match for project type
    if project.get('complexity') == 'high' and state['energy'] < 6:
        fitness -= 1
        reasoning.append("High complexity needs more energy")

    final_score = max(0, fitness)
    return final_score, reasoning


def generate_recommendations(state: Dict, config: Dict) -> List[Recommendation]:
    """Generate ranked recommendations for all project-pillar combinations."""
    history = config.get('pillar_history', {})
    projects = config.get('projects', {})

    # Step 1: Which pillar needs activation?
    pillar_scores = evaluate_pillar_need(state, history)
    sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)

    recommendations = []

    # Step 2: Match projects to top pillars
    for pillar, pillar_score in sorted_pillars:
        for proj_key, proj_data in projects.items():
            proj_data = dict(proj_data)  # Copy
            proj_data['key'] = proj_key

            fitness, reasoning = match_project_to_pillar(proj_data, pillar, state)

            # Combined score: pillar need * project fitness
            combined_score = (pillar_score * 0.3) + (fitness * 0.7)

            if fitness > 0:  # Only viable matches
                rec = Recommendation(
                    project=proj_data,
                    pillar=pillar,
                    score=combined_score,
                    reasoning=reasoning,
                    time_commitment=proj_data.get('time_sweet_spot', 'unknown')
                )
                recommendations.append(rec)

    # Sort by combined score
    recommendations.sort(key=lambda x: x.score, reverse=True)
    return recommendations


def select_top_recommendations(recs: List[Recommendation]) -> Tuple[Recommendation, Recommendation]:
    """Select primary and alternative recommendations."""
    if not recs:
        return None, None

    primary = recs[0]

    # Alternative should be different project or different pillar
    alternative = None
    for rec in recs[1:]:
        if rec.project['key'] != primary.project['key']:
            alternative = rec
            break
        elif rec.pillar != primary.pillar:
            alternative = rec
            break

    return primary, alternative


def format_output(primary: Recommendation, alternative: Recommendation,
                  pillar_scores: Dict, state: Dict) -> str:
    """Format recommendation for human readability."""
    lines = []
    lines.append("\n" + "="*60)
    lines.append("META-COORDINATOR RECOMMENDATION")
    lines.append("="*60)

    # State summary
    lines.append(f"\nYour State:")
    lines.append(f"  Energy: {state['energy']}/10 | Time: {state['time_available']}h | Weather: {state['emotional_weather']}")

    # Pillar activation levels
    lines.append(f"\nPillar Activation Levels:")
    for pillar, score in sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * score + "░" * (10 - score)
        lines.append(f"  {pillar.capitalize():12} [{bar}] {score}")

    # Primary recommendation
    lines.append(f"\n{'─'*60}")
    lines.append(f"PRIMARY RECOMMENDATION")
    lines.append(f"{'─'*60}")
    lines.append(f"Project: {primary.project['name']}")
    lines.append(f"Pillar:  {primary.pillar.upper()}")
    lines.append(f"Time:    {primary.time_commitment}")
    lines.append(f"\nWhy this matters:")
    for reason in primary.reasoning[:4]:  # Top 4 reasons
        lines.append(f"  • {reason}")

    # Alternative
    if alternative:
        lines.append(f"\n{'─'*60}")
        lines.append(f"ALTERNATIVE PATH (if blocked)")
        lines.append(f"{'─'*60}")
        lines.append(f"Project: {alternative.project['name']}")
        lines.append(f"Pillar:  {alternative.pillar.upper()}")
        lines.append(f"Reason:  {alternative.reasoning[0] if alternative.reasoning else 'Diversification'}")

    # Daily build log prompt
    lines.append(f"\n{'='*60}")
    lines.append("DAILY BUILD LOG")
    lines.append(f"{'='*60}")
    lines.append(f"Today you will activate: {primary.pillar.upper()}")
    lines.append(f"On project: {primary.project['name']}")
    lines.append(f"\nAt day's end, log:")
    lines.append(f"  1. What did I create today? (Artisan check)")
    lines.append(f"  2. What did I connect today? (Node check)")
    lines.append(f"  3. What did I transmute today? (Alchemist check)")
    lines.append(f"  4. What did I tend today? (Gardener check)")

    lines.append(f"\n{'='*60}")
    lines.append("Construction begins with your next breath.")
    lines.append(f"{'='*60}\n")

    return "\n".join(lines)


def get_engine_results(state: Dict) -> Dict:
    """
    Lane-native engine interface.
    Returns pillar_scores, recommendations, primary, alternative
    for consumption by Mirror Grammar governance flow.
    """
    config = load_config()
    pillar_scores = evaluate_pillar_need(state, config.get('pillar_history', {}))
    recommendations = generate_recommendations(state, config)
    primary, alternative = select_top_recommendations(recommendations)
    return {
        'pillar_scores': pillar_scores,
        'recommendations': recommendations,
        'primary': primary,
        'alternative': alternative,
        'config': config,
    }


def main():
    """Main entry point."""
    # Load state from JSON argument or stdin
    if len(sys.argv) > 1:
        state = json.loads(sys.argv[1])
    else:
        # Check for JSON_STATE: prefix from state_input.py
        for line in sys.stdin:
            if line.startswith("JSON_STATE:"):
                state = json.loads(line.replace("JSON_STATE:", ""))
                break
        else:
            print("Error: No state provided. Run: python3 state_input.py | python3 engine.py")
            sys.exit(1)

    config = load_config()
    recommendations = generate_recommendations(state, config)
    primary, alternative = select_top_recommendations(recommendations)

    if not primary:
        print("No viable recommendations. Check project configurations.")
        sys.exit(1)

    pillar_scores = evaluate_pillar_need(state, config.get('pillar_history', {}))
    output = format_output(primary, alternative, pillar_scores, state)
    print(output)

    # Log this recommendation for history tracking
    log_entry = {
        'timestamp': state.get('timestamp', ''),
        'state': state,
        'recommended_project': primary.project['key'],
        'recommended_pillar': primary.pillar,
        'alternative_project': alternative.project['key'] if alternative else None
    }

    # Append to history log
    log_path = Path(__file__).parent / "history.log"
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    main()
