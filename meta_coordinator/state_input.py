#!/usr/bin/env python3
"""
state_input.py
Daily state capture for Meta-Coordinator
The first structure is always internal.
"""

import sys
from datetime import datetime


def get_energy_level():
    """Capture current energy as 1-10 scale."""
    while True:
        try:
            energy = input("Energy level (1-10, 10=peak): ").strip()
            energy = int(energy)
            if 1 <= energy <= 10:
                return energy
            print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")


def get_time_available():
    """Capture available hours."""
    while True:
        try:
            time_input = input("Hours available (e.g., 2, 0.5): ").strip()
            hours = float(time_input)
            if 0 < hours <= 24:
                return hours
            print("Please enter a positive number up to 24.")
        except ValueError:
            print("Please enter a valid number.")


def get_emotional_weather():
    """Capture emotional state as weather metaphor."""
    weather_options = {
        '1': ('clear', 'Clear/Focused - Precision work ready'),
        '2': ('stormy', 'Stormy/Chaotic - Energy for transformation'),
        '3': ('foggy', 'Foggy/Uncertain - Gentle tending needed'),
        '4': ('calm', 'Calm/Peaceful - Connection available'),
        '5': ('bright', 'Bright/Energized - Creation mode')
    }

    print("\nEmotional weather:")
    for key, (code, desc) in weather_options.items():
        print(f"  [{key}] {desc}")

    while True:
        choice = input("Select (1-5): ").strip()
        if choice in weather_options:
            return weather_options[choice][0]
        print("Please select 1-5.")


def capture_state():
    """Full state vector capture."""
    print("\n" + "="*50)
    print("DAILY CALIBRATION")
    print("What world are you building from today?")
    print("="*50 + "\n")

    state = {
        'timestamp': datetime.now().isoformat(),
        'energy': get_energy_level(),
        'time_available': get_time_available(),
        'emotional_weather': get_emotional_weather()
    }

    # Quick confirmation
    print(f"\nState captured:")
    print(f"  Energy: {state['energy']}/10")
    print(f"  Time: {state['time_available']} hours")
    print(f"  Weather: {state['emotional_weather']}")

    confirm = input("\nConfirm? [Y/n]: ").strip().lower()
    if confirm in ('n', 'no'):
        print("Restarting calibration...")
        return capture_state()

    return state


if __name__ == "__main__":
    state = capture_state()
    # Output as JSON for pipe to engine
    import json
    print(f"\nJSON_STATE:{json.dumps(state)}")
