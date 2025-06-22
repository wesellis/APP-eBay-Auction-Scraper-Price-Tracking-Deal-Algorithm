"""
Test the GBA filtering function
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils import is_gba_related
from config import GBA_KEYWORDS

def test_filtering():
    print("Testing GBA filtering function...")
    print("=" * 50)
    
    # Test titles from the debug output
    test_titles = [
        "Nintendo Gameboy Advance SP AGS001 Onyx Black Handheld System Console",
        "Nintendo Game Boy Advance SP Console - Cobalt Blue",
        "Tested! NINTENDO Game Boy Advance SP Black Handheld Console with case",
        "Gameboy Advance SP Handheld Console Aqua Blue",
        "gameboy advance console silver",
        "Nintendo 2002 Game Boy Advance Super MonkeyBall Jr",
        "Game Boy Advance Manuals Warioware Twisted Wario Land 4",
        "Mario Bros.-e (Nintendo Game Boy Advance, 2002) Sealed Pack",
        "Nintendo Game Boy Advance E-Reader AGB-014 Authentic With 3 Games",
        "Nintendo Gameboy Advance NAMCO MUSEUM Galaga Ms. PAC Man",
        "Xtreme Green Gameboy Advance Sp Modded With Adjustable Brightness IPS",
        "Gameboy Advance SP Silver Metal Case And Accessories Very Good",
        "Gameboy Advance SP in Pink With Charger",
        "Nintendo Game Boy Advance SP Graphite Black System AGS-101",
        "Used working Nintendo Gameboy Advance SP With Charger And Case",
        "Nintendo Gameboy Advance SP AGS-001 Cobalt Blue Console Tested",
        # Non-GBA items
        "Nintendo Switch Console",
        "PlayStation 5 Console",
        "Xbox Series X"
    ]
    
    gba_count = 0
    non_gba_count = 0
    
    for title in test_titles:
        is_gba = is_gba_related(title, GBA_KEYWORDS)
        status = "✅ GBA" if is_gba else "❌ FILTERED"
        
        if is_gba:
            gba_count += 1
        else:
            non_gba_count += 1
            
        print(f"{status} | {title[:60]}...")
    
    print("=" * 50)
    print(f"Results: {gba_count} GBA items, {non_gba_count} filtered out")
    
    if gba_count > 0:
        print("✅ Filtering is working - should find GBA items now!")
    else:
        print("❌ Filtering still too strict")

if __name__ == "__main__":
    test_filtering()
