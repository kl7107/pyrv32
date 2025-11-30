#!/usr/bin/env python3
"""
Generate dungeon file via two-step process with clean workflow.

Step 1: makedefs -e (dungeon.def → dungeon.pdf)
Step 2: dgn_comp (dungeon.pdf → dungeon)
"""

import sys
from pathlib import Path

# Add repository root to path (5 levels up from this file)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from nethack_util_runner import UtilityRunner

def main():
    print("=" * 60)
    print("TWO-STEP DUNGEON GENERATION")
    print("=" * 60)
    print()
    
    # Step 1: makedefs -e (dungeon.def → dungeon.pdf)
    print("STEP 1: makedefs -e (dungeon.def → dungeon.pdf)")
    print("-" * 60)
    
    makedefs_runner = UtilityRunner(
        name="dungeon.pdf",
        input_files="dungeon.def",
        output_file="dungeon.pdf",
        utility_flag="-e",
        binary_path="nethack-3.4.3/util/makedefs.bin",
        elf_path="nethack-3.4.3/util/makedefs.elf",
        max_steps=10_000_000
    )
    makedefs_runner.run()
    
    print()
    print("=" * 60)
    
    # Step 2: dgn_comp (dungeon.pdf → dungeon)
    print("STEP 2: dgn_comp (dungeon.pdf → dungeon)")
    print("-" * 60)
    
    # For step 2, the input file (dungeon.pdf) is in pyrv32_sim_fs/dat/ from step 1
    # We DON'T clean the directory - we keep dungeon.pdf from step 1
    # We use a custom runner that skips the clean step
    
    dgn_runner = UtilityRunner(
        name="dungeon",
        input_files="dungeon.pdf",  # Already in pyrv32_sim_fs/dat/ from step 1
        output_file="dungeon",
        utility_flag="dungeon.pdf",  # dgn_comp takes filename as argument, not a flag
        binary_path="nethack-3.4.3/util/dgn_comp.bin",
        elf_path="nethack-3.4.3/util/dgn_comp.elf",
        max_steps=10_000_000
    )
    
    # Override the run method to skip cleaning (keep dungeon.pdf)
    print(f"\n[1/7] Skipping clean (keeping dungeon.pdf from step 1)")
    print(f"  ✓ Retained dungeon.pdf")
    
    # Skip steps 0-2 (check, clean, copy) and go straight to step 3
    print(f"\n[2/7] Skipping input verification (dungeon.pdf already present)")
    print(f"  ✓ dungeon.pdf available from step 1")
    
    argv_area = dgn_runner._step3_locate_argv()
    sim = dgn_runner._step4_run_utility(argv_area)  # This sets cwd = "/dat"
    dgn_runner._step5_check_console_output(sim)
    dgn_runner._step6_verify_output()
    dgn_runner._step7_list_final_state()
    
    print()
    print("=" * 60)
    print("✓ TWO-STEP DUNGEON GENERATION COMPLETE")
    print("=" * 60)
    print()
    print("Next step: cd nethack-3.4.3/util && make archive-data")

if __name__ == "__main__":
    main()
