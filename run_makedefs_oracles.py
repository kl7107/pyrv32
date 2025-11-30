#!/usr/bin/env python3
"""
Generate oracles file using makedefs -h with clean workflow.

Clean workflow:
1. Clean pyrv32_sim_fs/dat/
2. Copy oracles.txt from nethack-3.4.3/dat/
3. Run makedefs -h
4. Verify oracles file created
"""

import subprocess
import sys
import shutil
from pathlib import Path
from pyrv32_system import RV32System
import struct

# Paths
SIM_DAT = Path("pyrv32_sim_fs/dat")
SOURCE_DAT = Path("nethack-3.4.3/dat")
INPUT_FILE = "oracles.txt"
OUTPUT_FILE = "oracles"

print("=" * 60)
print("CLEAN GENERATION: oracles")
print("=" * 60)

# Step 0: Check initial state
print(f"\n[0/7] Checking initial state...")
print(f"  Source directory: {SOURCE_DAT}")
if SOURCE_DAT.exists():
    print(f"  ✓ Source directory exists")
    if (SOURCE_DAT / INPUT_FILE).exists():
        size = (SOURCE_DAT / INPUT_FILE).stat().st_size
        print(f"    - {INPUT_FILE} ({size} bytes)")
    else:
        print(f"    ✗ {INPUT_FILE} NOT FOUND")
        sys.exit(1)
else:
    print(f"  ✗ Source directory not found!")
    sys.exit(1)

print(f"\n  Simulator filesystem: {SIM_DAT}")
if SIM_DAT.exists():
    items = list(SIM_DAT.iterdir())
    if items:
        print(f"  Current contents ({len(items)} items):")
        for item in sorted(items)[:10]:  # Show first 10
            print(f"    - {item.name}")
        if len(items) > 10:
            print(f"    ... and {len(items) - 10} more")
    else:
        print(f"  ✓ Directory is empty")
else:
    print(f"  Directory does not exist (will be created)")

# Step 1: Clean sim dat directory
print(f"\n[1/7] Cleaning {SIM_DAT}/")
if SIM_DAT.exists():
    for item in SIM_DAT.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    print(f"  ✓ Cleaned {SIM_DAT}/")
else:
    SIM_DAT.mkdir(parents=True)
    print(f"  ✓ Created {SIM_DAT}/")

# Step 2: Copy input file
print(f"\n[2/7] Copying {INPUT_FILE} from source...")
shutil.copy2(SOURCE_DAT / INPUT_FILE, SIM_DAT / INPUT_FILE)
input_size = (SIM_DAT / INPUT_FILE).stat().st_size
print(f"  ✓ Copied {INPUT_FILE} ({input_size} bytes)")

# Step 3: Get argv area address
print(f"\n[3/7] Locating argv area...")
result = subprocess.run(
    ['riscv64-unknown-elf-nm', 'nethack-3.4.3/util/makedefs.elf'],
    capture_output=True, text=True, check=True
)
ARGV_AREA = None
for line in result.stdout.splitlines():
    if '__argv_envp_start' in line:
        ARGV_AREA = int(line.split()[0], 16)
        break

if ARGV_AREA is None:
    print("  ✗ ERROR: Could not find __argv_envp_start symbol")
    sys.exit(1)

print(f"  ✓ Using argv area at 0x{ARGV_AREA:08x}")

# Step 4: Run makedefs in simulator
print(f"\n[4/7] Running makedefs -h in simulator...")
sim = RV32System(fs_root="pyrv32_sim_fs")
sim.syscall_handler.cwd = "/dat"  # Set working directory
sim.load_binary("nethack-3.4.3/util/makedefs.bin")

# Set up argv
for i, byte in enumerate(b'makedefs\x00'):
    sim.memory.write_byte(ARGV_AREA + i, byte)
for i, byte in enumerate(b'-h\x00'):
    sim.memory.write_byte(ARGV_AREA + 0x0c + i, byte)

argv_array = struct.pack('<III', ARGV_AREA, ARGV_AREA + 0x0c, 0)
for i, byte in enumerate(argv_array):
    sim.memory.write_byte(ARGV_AREA + 0x100 + i, byte)

sim.cpu.regs[10] = 2  # argc
sim.cpu.regs[11] = ARGV_AREA + 0x100  # argv

exec_result = sim.run(max_steps=10_000_000)
print(f"  Status: {exec_result.status}")
print(f"  Instructions: {exec_result.instruction_count:,}")

# Step 5: Check console output
print(f"\n[5/7] Checking for console output...")
console_output = sim.console_uart_read_all()
if console_output:
    print(f"  Console output from makedefs ({len(console_output)} bytes):")
    for line in console_output.split('\n')[:20]:  # Show first 20 lines
        if line.strip():
            print(f"    {line}")
    if console_output.count('\n') > 20:
        print(f"    ... ({console_output.count('\n') - 20} more lines)")
else:
    print(f"  No console output (makedefs ran silently)")

# Step 6: Verify output file created
print(f"\n[6/7] Verifying output file...")
output_path = SIM_DAT / OUTPUT_FILE
if not output_path.exists():
    print(f"  ✗ ERROR: {OUTPUT_FILE} not created!")
    sys.exit(1)

output_size = output_path.stat().st_size
print(f"  ✓ Created {OUTPUT_FILE} ({output_size} bytes)")

# Step 7: List final state of sim dat directory
print(f"\n[7/7] Final state of {SIM_DAT}/:")
for item in sorted(SIM_DAT.iterdir()):
    size = item.stat().st_size
    print(f"  - {item.name} ({size:,} bytes)")

print("\n" + "=" * 60)
print("✓ GENERATION COMPLETE")
print("=" * 60)
print(f"\nNext step: cd nethack-3.4.3/util && make archive-data")
