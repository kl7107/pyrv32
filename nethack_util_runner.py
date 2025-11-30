#!/usr/bin/env python3
"""
Common library for running NetHack utilities with clean workflow.

Provides a standardized 7-step process:
0. Check initial state (source files + sim filesystem)
1. Clean sim directory
2. Copy input files
3. Locate argv area
4. Run utility in simulator
5. Check console output
6. Verify output files
7. List final state
"""

import subprocess
import sys
import shutil
from pathlib import Path
from pyrv32_system import RV32System
import struct
from typing import Union, List


class UtilityRunner:
    """Run NetHack utilities with clean, verified workflow."""
    
    def __init__(self, 
                 name: str,
                 input_files: Union[str, List[str]],
                 output_file: str,
                 utility_flag: str,
                 binary_path: str = "nethack-3.4.3/util/makedefs.bin",
                 elf_path: str = "nethack-3.4.3/util/makedefs.elf",
                 max_steps: int = 10_000_000,
                 sim_dir: str = "pyrv32_sim_fs/dat",
                 source_dir: str = "nethack-3.4.3/dat"):
        """
        Initialize utility runner.
        
        Args:
            name: Display name (e.g., "data", "oracles", "rumors")
            input_files: Input file(s) - string or list of strings
            output_file: Expected output file name
            utility_flag: Command-line flag (e.g., "-d", "-h", "-r")
            binary_path: Path to .bin file
            elf_path: Path to .elf file (for argv lookup)
            max_steps: Maximum simulation steps
            sim_dir: Simulator filesystem directory
            source_dir: Source file directory
        """
        self.name = name
        self.input_files = [input_files] if isinstance(input_files, str) else input_files
        self.output_file = output_file
        self.utility_flag = utility_flag
        self.binary_path = binary_path
        self.elf_path = elf_path
        self.max_steps = max_steps
        self.sim_dir = Path(sim_dir)
        self.source_dir = Path(source_dir)
        
    def run(self):
        """Execute the complete workflow."""
        print("=" * 60)
        print(f"CLEAN GENERATION: {self.name}")
        print("=" * 60)
        
        self._step0_check_initial_state()
        self._step1_clean_sim_dir()
        self._step2_copy_inputs()
        argv_area = self._step3_locate_argv()
        sim = self._step4_run_utility(argv_area)
        self._step5_check_console_output(sim)
        self._step6_verify_output()
        self._step7_list_final_state()
        
        print("\n" + "=" * 60)
        print("✓ GENERATION COMPLETE")
        print("=" * 60)
        print(f"\nNext step: cd nethack-3.4.3/util && make archive-data")
        
    def _step0_check_initial_state(self):
        """Step 0: Check source files and current sim filesystem state."""
        print(f"\n[0/7] Checking initial state...")
        
        if self.input_files:
            print(f"  Source directory: {self.source_dir}")
            
            if not self.source_dir.exists():
                print(f"  ✗ Source directory not found!")
                sys.exit(1)
                
            print(f"  ✓ Source directory exists")
            
            # Check input files
            for input_file in self.input_files:
                source_path = self.source_dir / input_file
                if source_path.exists():
                    size = source_path.stat().st_size
                    print(f"    - {input_file} ({size} bytes)")
                else:
                    print(f"    ✗ {input_file} NOT FOUND")
                    sys.exit(1)
        else:
            print(f"  No input files required (generated from compile-time config)")
        
        # Show current sim filesystem state
        print(f"\n  Simulator filesystem: {self.sim_dir}")
        if self.sim_dir.exists():
            items = list(self.sim_dir.iterdir())
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
    
    def _step1_clean_sim_dir(self):
        """Step 1: Clean simulator directory."""
        print(f"\n[1/7] Cleaning {self.sim_dir}/")
        
        if self.sim_dir.exists():
            for item in self.sim_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print(f"  ✓ Cleaned {self.sim_dir}/")
        else:
            self.sim_dir.mkdir(parents=True)
            print(f"  ✓ Created {self.sim_dir}/")
    
    def _step2_copy_inputs(self):
        """Step 2: Copy input files."""
        if not self.input_files:
            print(f"\n[2/7] Skipping input copy (no files required)")
            return
            
        if len(self.input_files) == 1:
            print(f"\n[2/7] Copying {self.input_files[0]} from source...")
        else:
            print(f"\n[2/7] Copying input files from source...")
        
        for input_file in self.input_files:
            source_path = self.source_dir / input_file
            dest_path = self.sim_dir / input_file
            shutil.copy2(source_path, dest_path)
            size = dest_path.stat().st_size
            print(f"  ✓ Copied {input_file} ({size} bytes)")
    
    def _step3_locate_argv(self) -> int:
        """Step 3: Get argv area address from ELF symbols."""
        print(f"\n[3/7] Locating argv area...")
        
        result = subprocess.run(
            ['riscv64-unknown-elf-nm', self.elf_path],
            capture_output=True, text=True, check=True
        )
        
        argv_area = None
        for line in result.stdout.splitlines():
            if '__argv_envp_start' in line:
                argv_area = int(line.split()[0], 16)
                break
        
        if argv_area is None:
            print("  ✗ ERROR: Could not find __argv_envp_start symbol")
            sys.exit(1)
        
        print(f"  ✓ Using argv area at 0x{argv_area:08x}")
        return argv_area
    
    def _step4_run_utility(self, argv_area: int) -> RV32System:
        """Step 4: Run utility in simulator."""
        print(f"\n[4/7] Running makedefs {self.utility_flag} in simulator...")
        
        sim = RV32System(fs_root="pyrv32_sim_fs")
        sim.syscall_handler.cwd = "/dat"
        sim.load_binary(self.binary_path)
        
        # Set up argv: program name and flag
        # Write "makedefs\0" at ARGV_AREA
        for i, byte in enumerate(b'makedefs\x00'):
            sim.memory.write_byte(argv_area + i, byte)
        
        # Write flag (e.g., "-d\0") at ARGV_AREA + 0x0c
        flag_bytes = (self.utility_flag + '\x00').encode()
        for i, byte in enumerate(flag_bytes):
            sim.memory.write_byte(argv_area + 0x0c + i, byte)
        
        # Create argv array at ARGV_AREA + 0x100
        argv_array = struct.pack('<III', argv_area, argv_area + 0x0c, 0)
        for i, byte in enumerate(argv_array):
            sim.memory.write_byte(argv_area + 0x100 + i, byte)
        
        # Set argc=2, argv pointer
        sim.cpu.regs[10] = 2
        sim.cpu.regs[11] = argv_area + 0x100
        
        # Run simulation
        exec_result = sim.run(max_steps=self.max_steps)
        print(f"  Status: {exec_result.status}")
        print(f"  Instructions: {exec_result.instruction_count:,}")
        
        return sim
    
    def _step5_check_console_output(self, sim: RV32System):
        """Step 5: Check for console output."""
        print(f"\n[5/7] Checking for console output...")
        
        console_output = sim.console_uart_read_all()
        if console_output:
            print(f"  Console output from makedefs ({len(console_output)} bytes):")
            lines = console_output.split('\n')
            for line in lines[:20]:  # Show first 20 lines
                if line.strip():
                    print(f"    {line}")
            if len(lines) > 20:
                print(f"    ... ({len(lines) - 20} more lines)")
        else:
            print(f"  No console output (makedefs ran silently)")
    
    def _step6_verify_output(self):
        """Step 6: Verify output file was created."""
        print(f"\n[6/7] Verifying output file...")
        
        output_path = self.sim_dir / self.output_file
        if not output_path.exists():
            print(f"  ✗ ERROR: {self.output_file} not created!")
            sys.exit(1)
        
        output_size = output_path.stat().st_size
        print(f"  ✓ Created {self.output_file} ({output_size} bytes)")
    
    def _step7_list_final_state(self):
        """Step 7: List final state of sim directory."""
        print(f"\n[7/7] Final state of {self.sim_dir}/:")
        
        for item in sorted(self.sim_dir.iterdir()):
            size = item.stat().st_size
            print(f"  - {item.name} ({size:,} bytes)")


def run_makedefs(name: str, 
                 input_files: Union[str, List[str]], 
                 output_file: str,
                 flag: str,
                 max_steps: int = 10_000_000):
    """
    Convenience function to run makedefs with standard settings.
    
    Args:
        name: Display name
        input_files: Input file(s)
        output_file: Output file name
        flag: makedefs flag (-d, -h, -r, etc.)
        max_steps: Maximum simulation steps
    """
    runner = UtilityRunner(
        name=name,
        input_files=input_files,
        output_file=output_file,
        utility_flag=flag,
        binary_path="nethack-3.4.3/util/makedefs.bin",
        elf_path="nethack-3.4.3/util/makedefs.elf",
        max_steps=max_steps
    )
    runner.run()
