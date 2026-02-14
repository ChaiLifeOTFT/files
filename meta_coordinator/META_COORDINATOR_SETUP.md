# Meta-Coordinator Setup & Usage

## Quick Start

1. Create directory and download files:
```bash
mkdir -p ~/Desktop/files/meta_coordinator
cd ~/Desktop/files/meta_coordinator
# Move downloaded files here: config.yaml, state_input.py, engine.py, meta_coordinator.py
```

2. Make executable:
```bash
chmod +x *.py
```

3. Install PyYAML:
```bash
pip3 install pyyaml
```

4. Run:
```bash
python3 meta_coordinator.py
```

## How It Works

The Meta-Coordinator breaks the recursion of "which project should I work on?" by making the choice itself a system.

**Input:** Your current state (energy, time, emotional weather)
**Process:** Evaluates which Pillar needs activation + which project serves that Pillar
**Output:** Recommendation with reasoning + alternative path

## The Four Pillars

- **ARTISAN**: Build something tangible (high energy, focused state, 1-3 hours)
- **NODE**: Strengthen connections (medium energy, calm state, <1 hour)  
- **ALCHEMIST**: Transform stuck energy (any energy, stormy state, 3+ hours)
- **GARDENER**: Tend living systems (low-medium energy, any state, flexible time)

## Customizing

Edit `config.yaml` to:
- Add new projects
- Update momentum/urgency of existing projects
- Mark blockers resolved
- Adjust time sweet spots
- Update pillar history (which pillars you've activated recently)

## Integration with DigiUs

This tool is part of the DigiUs infrastructure:
- Uses persistent state (`history.log`)
- Can be called by other coordinators
- Feeds into daily build logs
- Supports distributed decision-making

The recursion is broken. The choice is now a system.

∞
