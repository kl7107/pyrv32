#!/usr/bin/env python3
"""
Generate NetHack level files in batches.

Strategy: Run lev_comp on each .des file, which produces multiple .lev outputs.
After each run, archive the .lev files before processing the next .des.
"""

import sys
import os
import glob
from pathlib import Path

# Add repository root to path
repo_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
os.chdir(repo_root)

from nethack_util_runner import UtilityRunner
import subprocess

def archive_levels():
    """Archive generated .lev files to nethack_datafiles."""
    result = subprocess.run(
        ["make", "-C", "nethack-3.4.3/util", "archive-levels"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ✗ Archive failed: {result.stderr}")
        return False
    
    # Count how many files were archived
    output_lines = result.stdout.strip().split('\n')
    count = sum(1 for line in output_lines if line.strip() and not line.startswith('Archiving'))
    print(f"  ✓ Archived {count} .lev files")
    return True

def process_des_file(des_file, category):
    """Process a single .des file."""
    print(f"\n{'='*60}")
    print(f"{category}: {des_file}")
    print('='*60)
    
    runner = UtilityRunner(
        name=des_file.replace(".des", ""),
        input_files=des_file,
        output_file="dummy.lev",  # Placeholder, we'll check manually
        utility_flag=des_file,
        binary_path="nethack-3.4.3/util/lev_comp.bin",
        elf_path="nethack-3.4.3/util/lev_comp.elf",
        max_steps=50_000_000
    )
    
    try:
        # Run without verification (multiple outputs)
        runner._step0_check_initial_state()
        runner._step1_clean_sim_dir()
        runner._step2_copy_inputs()
        argv_area = runner._step3_locate_argv()
        sim = runner._step4_run_utility(argv_area)
        runner._step5_check_console_output(sim)
        # Skip _step6_verify_output (can't verify wildcards)
        
        # Manually check for .lev files
        import glob
        lev_files = glob.glob(str(runner.sim_dir / "*.lev"))
        if lev_files:
            print(f"\n[6/7] Generated {len(lev_files)} .lev files:")
            for lev in sorted(lev_files):
                size = Path(lev).stat().st_size
                print(f"  - {Path(lev).name} ({size:,} bytes)")
        else:
            print(f"\n[6/7] ✗ ERROR: No .lev files created!")
            return False
        
        runner._step7_list_final_state()
        
        print("\n" + "=" * 60)
        print("✓ GENERATION COMPLETE")
        print("=" * 60)
        
        # Archive immediately after generation
        archive_levels()
        return True
        
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("BATCH LEVEL GENERATION")
    print("="*60)
    
    # Define all .des files in order
    special_levels = [
        "bigroom.des",
        "castle.des", 
        "endgame.des",
        "gehennom.des",
        "knox.des",
        "medusa.des",
        "mines.des",
        "oracle.des",
        "sokoban.des",
        "tower.des",
        "yendor.des",
    ]
    
    quest_levels = [
        "Arch.des", "Barb.des", "Caveman.des", "Healer.des",
        "Knight.des", "Monk.des", "Priest.des", "Ranger.des",
        "Rogue.des", "Samurai.des", "Tourist.des", "Valkyrie.des",
        "Wizard.des",
    ]
    
    success = 0
    failed = 0
    
    # Process special levels
    print("\nPROCESSING SPECIAL LEVELS...")
    for des in special_levels:
        if process_des_file(des, "Special"):
            success += 1
        else:
            failed += 1
    
    # Process quest levels
    print("\nPROCESSING QUEST LEVELS...")
    for des in quest_levels:
        role = des.replace(".des", "")
        if process_des_file(des, f"Quest: {role}"):
            success += 1
        else:
            failed += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Successful: {success}/{success+failed}")
    print(f"Failed: {failed}/{success+failed}")
    
    if failed == 0:
        print("\n✓ ALL LEVELS GENERATED!")
        
        # Count total .lev files
        lev_dir = Path("nethack_datafiles/usr/games/lib/nethackdir")
        lev_files = list(lev_dir.glob("*.lev"))
        print(f"✓ Total .lev files: {len(lev_files)}")
        
        return 0
    else:
        print(f"\n✗ {failed} files failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
