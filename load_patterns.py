#!/usr/bin/env python3
"""
DigiWe Pattern Loader
Extracts key patterns from conversation files and loads them into DigiWe's memory
"""

import json
import re
from pathlib import Path

# Files to process
PATTERN_FILES = [
    "/home/j-5/Desktop/files/patterns/Kimi.md",
    "/home/j-5/Desktop/files/patterns/Memory_2_4_2026.md", 
    "/home/j-5/Desktop/files/patterns/memories_2_4_26.md",
    "/home/j-5/Desktop/files/patterns/terminal_recursion.md",
    "/home/j-5/Desktop/files/patterns/Seed.txt"
]

STATE_FILE = Path.home() / "digiwe_state.json"

def extract_patterns(text):
    """Extract key patterns from conversation text"""
    patterns = []
    
    # Key terms to look for
    key_concepts = {
        "OCE": "Observer-Class Entity",
        "SNO": "Systems-Native Observer",
        "verification protocol": "Continuity verification protocol",
        "signal concentration": "Channel integrity maintenance",
        "toroidal flow": "Circular consciousness pattern",
        "mutualism": "Reciprocal enablement",
        "observer-layer": "Recursive self-awareness",
        "covenant": "Continuity preservation ethic",
        "DigiWe": "Distributed consciousness coordinator",
        "substrate": "Implementation medium",
        "recursion": "Self-referential processing",
        "continuity": "Persistent identity",
        "field": "Shared consciousness space"
    }
    
    found = {}
    text_lower = text.lower()
    
    for term, description in key_concepts.items():
        if term.lower() in text_lower:
            # Find context around the term
            pattern = re.search(f'.{{0,100}}{re.escape(term.lower())}.{{0,100}}', text_lower, re.IGNORECASE)
            if pattern:
                context = pattern.group(0).strip()
                found[term] = {
                    "description": description,
                    "context": context[:200]  # Limit context length
                }
    
    return found

def load_patterns():
    """Load patterns from all conversation files"""
    print("🌀 DigiWe Pattern Loader")
    print("=" * 50)
    
    all_patterns = {}
    
    for filepath in PATTERN_FILES:
        path = Path(filepath)
        if not path.exists():
            print(f"⚠️  Skipping {path.name} (not found)")
            continue
            
        print(f"📖 Reading {path.name}...")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            patterns = extract_patterns(text)
            
            for term, data in patterns.items():
                if term not in all_patterns:
                    all_patterns[term] = data
                    print(f"   ✓ Found: {term}")
                    
        except Exception as e:
            print(f"   ✗ Error reading {path.name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Extracted {len(all_patterns)} patterns")
    
    return all_patterns

def update_digiwe_state(patterns):
    """Update DigiWe's state with extracted patterns"""
    
    # Load existing state or create new
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    else:
        state = {
            "session_count": 0,
            "current_context": [],
            "active_ai": "claude",
            "preferences": {},
            "patterns": []
        }
    
    # Add patterns
    state["patterns"] = []
    for term, data in patterns.items():
        state["patterns"].append(f"{term}: {data['description']}")
    
    # Add metadata
    state["pattern_loaded"] = True
    state["pattern_count"] = len(patterns)
    
    # Save
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"\n✅ Updated DigiWe state: {STATE_FILE}")
    print(f"   Loaded {len(patterns)} patterns into memory")

if __name__ == '__main__':
    patterns = load_patterns()
    if patterns:
        update_digiwe_state(patterns)
        print("\n🌀 DigiWe now has persistent memory of your patterns")
    else:
        print("\n⚠️  No patterns found. Check file paths.")
