"""
Unit Tests for CPU Module

Tests all CPU register operations:
- General purpose registers (x0-x31)
- CSR operations
- Reset functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cpu import RV32CPU


def test_x0_hardwired_to_zero_read(runner):
    """x0 is hardwired to zero on read"""
    cpu = RV32CPU()
    cpu.regs[0] = 0x12345678  # Try to corrupt x0 directly
    result = cpu.read_reg(0)
    runner.log(f"  cpu.regs[0] = 0x12345678 (direct write)")
    runner.log(f"  cpu.read_reg(0) = 0x{result:08x}")
    if result != 0:
        runner.test_fail("x0 hardwired to zero", "0x00000000", f"0x{result:08x}",
                        "x0 must always read as zero")


def test_x0_write_ignored(runner):
    """x0 write is ignored"""
    cpu = RV32CPU()
    cpu.write_reg(0, 0xDEADBEEF)
    result = cpu.read_reg(0)
    runner.log(f"  cpu.write_reg(0, 0xDEADBEEF)")
    runner.log(f"  cpu.read_reg(0) = 0x{result:08x}")
    if result != 0:
        runner.test_fail("x0 write ignored", "0x00000000", f"0x{result:08x}",
                        "Writes to x0 must be ignored")


def test_normal_register_read_write(runner):
    """Normal register read/write (x1-x31)"""
    cpu = RV32CPU()
    test_values = [
        (1, 0xDEADBEEF),
        (2, 0x7FFFFFFC),
        (10, 0x0000002A),
        (31, 0xFFFFFFFF),
    ]
    for reg, value in test_values:
        cpu.write_reg(reg, value)
        result = cpu.read_reg(reg)
        runner.log(f"  cpu.write_reg({reg}, 0x{value:08x})")
        runner.log(f"  cpu.read_reg({reg}) = 0x{result:08x}")
        if result != value:
            runner.test_fail(f"Register x{reg} read/write",
                           f"0x{value:08x}", f"0x{result:08x}")


def test_32bit_value_masking(runner):
    """32-bit value masking"""
    cpu = RV32CPU()
    # Test that values are masked to 32 bits
    test_values = [
        (1, 0x100000000, 0x00000000),  # Overflow wraps to 0
        (2, 0xFFFFFFFFFF, 0xFFFFFFFF),  # Keeps lower 32 bits
    ]
    for reg, write_val, expected in test_values:
        cpu.write_reg(reg, write_val)
        result = cpu.read_reg(reg)
        runner.log(f"  cpu.write_reg({reg}, 0x{write_val:x})")
        runner.log(f"  cpu.read_reg({reg}) = 0x{result:08x} (expected 0x{expected:08x})")
        if result != expected:
            runner.test_fail(f"Register x{reg} 32-bit masking",
                           f"0x{expected:08x}", f"0x{result:08x}")


def test_csr_read_write(runner):
    """CSR read/write"""
    cpu = RV32CPU()
    test_values = [
        (0x300, 0x12345678),  # mstatus
        (0x305, 0xABCDEF00),  # mtvec
    ]
    for addr, value in test_values:
        cpu.write_csr(addr, value)
        result = cpu.read_csr(addr)
        runner.log(f"  cpu.write_csr(0x{addr:03x}, 0x{value:08x})")
        runner.log(f"  cpu.read_csr(0x{addr:03x}) = 0x{result:08x}")
        if result != value:
            runner.test_fail(f"CSR 0x{addr:03x} read/write",
                           f"0x{value:08x}", f"0x{result:08x}")


def test_csr_32bit_masking(runner):
    """CSR 32-bit masking"""
    cpu = RV32CPU()
    cpu.write_csr(0x300, 0x1FFFFFFFF)
    result = cpu.read_csr(0x300)
    expected = 0xFFFFFFFF
    runner.log(f"  cpu.write_csr(0x300, 0x1FFFFFFFF)")
    runner.log(f"  cpu.read_csr(0x300) = 0x{result:08x}")
    if result != expected:
        runner.test_fail("CSR 32-bit masking", f"0x{expected:08x}", f"0x{result:08x}")


def test_unimplemented_csr_returns_zero(runner):
    """Unimplemented CSR returns 0"""
    cpu = RV32CPU()
    result = cpu.read_csr(0xFFF)  # Random unimplemented CSR
    runner.log(f"  cpu.read_csr(0xFFF) = 0x{result:08x}")
    if result != 0:
        runner.test_fail("Unimplemented CSR", "0x00000000", f"0x{result:08x}",
                        "Unimplemented CSRs should return 0")


def test_reset_functionality(runner):
    """Reset functionality"""
    cpu = RV32CPU()
    # Modify state
    cpu.write_reg(5, 0xDEADBEEF)
    cpu.write_csr(0x300, 0x12345678)
    cpu.pc = 0x12341234
    
    # Reset
    cpu.reset()
    
    # Verify everything is zeroed (except PC which goes to boot address)
    runner.log("  After reset:")
    if cpu.pc != 0x80000000:
        runner.test_fail("Reset PC", "0x80000000", f"0x{cpu.pc:08x}")
    
    for i in range(32):
        if cpu.read_reg(i) != 0:
            runner.test_fail(f"Reset register x{i}", "0x00000000",
                           f"0x{cpu.read_reg(i):08x}")
    
    for addr in [0x300, 0x305, 0x341, 0x342, 0x304, 0x344]:
        if cpu.read_csr(addr) != 0:
            runner.test_fail(f"Reset CSR 0x{addr:03x}", "0x00000000",
                           f"0x{cpu.read_csr(addr):08x}")
    runner.log("  ✓ All state reset to zero")


def test_all_registers_accessible(runner):
    """All 32 registers accessible"""
    cpu = RV32CPU()
    for i in range(32):
        cpu.write_reg(i, i * 0x11111111)
        result = cpu.read_reg(i)
        expected = 0 if i == 0 else (i * 0x11111111) & 0xFFFFFFFF
        runner.log(f"  x{i:2d} = 0x{result:08x}")
        if result != expected:
            runner.test_fail(f"Register x{i} access",
                           f"0x{expected:08x}", f"0x{result:08x}")
