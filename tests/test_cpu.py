"""
Unit Tests for CPU Module

Tests all CPU register operations:
- General purpose registers (x0-x31)
- CSR operations
- Reset functionality
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cpu import RV32CPU


def run_cpu_tests():
    """
    Run comprehensive unit tests for the RV32CPU.
    Tests run at program start to catch any regressions.
    Logs verbose output to a temp file for debugging.
    Exits immediately on first failure.
    """
    # Create temp file for test logging
    log_file = tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                           prefix='pyrv32_test_cpu_', suffix='.log')
    log_path = log_file.name
    
    def log(msg):
        """Write to log file only"""
        log_file.write(msg + '\n')
        log_file.flush()
    
    def test_fail(test_name, expected, actual, context=""):
        """Handle test failure - log details and exit"""
        log(f"\n{'=' * 60}")
        log(f"TEST FAILED: {test_name}")
        log(f"Expected: {expected}")
        log(f"Actual:   {actual}")
        if context:
            log(f"Context:  {context}")
        log(f"Log file: {log_path}")
        log(f"{'=' * 60}\n")
        log_file.close()
        print(f"\n{'=' * 60}")
        print(f"TEST FAILED: {test_name}")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        if context:
            print(f"Context:  {context}")
        print(f"Log file: {log_path}")
        print(f"{'=' * 60}\n")
        sys.exit(1)
    
    log("=" * 60)
    log("Running RV32CPU Unit Tests")
    log(f"Log file: {log_path}")
    log("=" * 60)
    
    cpu = RV32CPU()
    
    # Test 1: x0 is hardwired to zero on read
    log("\nTest 1: x0 hardwired to zero on read")
    cpu.regs[0] = 0x12345678  # Try to corrupt x0 directly
    result = cpu.read_reg(0)
    log(f"  cpu.regs[0] = 0x12345678 (direct write)")
    log(f"  cpu.read_reg(0) = 0x{result:08x}")
    if result != 0:
        test_fail("x0 hardwired to zero", "0x00000000", f"0x{result:08x}",
                 "x0 must always read as zero")
    log("  ✓ PASS")
    
    # Test 2: x0 write is ignored
    log("\nTest 2: x0 write is ignored")
    cpu.write_reg(0, 0xDEADBEEF)
    result = cpu.read_reg(0)
    log(f"  cpu.write_reg(0, 0xDEADBEEF)")
    log(f"  cpu.read_reg(0) = 0x{result:08x}")
    if result != 0:
        test_fail("x0 write ignored", "0x00000000", f"0x{result:08x}",
                 "Writes to x0 must be ignored")
    log("  ✓ PASS")
    
    # Test 3: Normal register read/write
    log("\nTest 3: Normal register read/write (x1-x31)")
    test_values = [
        (1, 0xDEADBEEF),
        (2, 0x7FFFFFFC),
        (10, 0x0000002A),
        (31, 0xFFFFFFFF),
    ]
    for reg, value in test_values:
        cpu.write_reg(reg, value)
        result = cpu.read_reg(reg)
        log(f"  cpu.write_reg({reg}, 0x{value:08x})")
        log(f"  cpu.read_reg({reg}) = 0x{result:08x}")
        if result != value:
            test_fail(f"Register x{reg} read/write", 
                     f"0x{value:08x}", f"0x{result:08x}")
    log("  ✓ PASS")
    
    # Test 4: 32-bit value masking
    log("\nTest 4: 32-bit value masking")
    test_cases = [
        (5, 0x123456789ABCDEF0, 0x9ABCDEF0),  # Upper bits stripped
        (6, 0x1FFFFFFFF, 0xFFFFFFFF),          # Just over 32 bits
        (7, -1, 0xFFFFFFFF),                   # Negative number
        (8, -42, 0xFFFFFFD6),                  # Small negative
    ]
    for reg, write_val, expected in test_cases:
        cpu.write_reg(reg, write_val)
        result = cpu.read_reg(reg)
        log(f"  cpu.write_reg({reg}, 0x{write_val:X})")
        log(f"  cpu.read_reg({reg}) = 0x{result:08x} (expected 0x{expected:08x})")
        if result != expected:
            test_fail(f"32-bit masking for x{reg}", 
                     f"0x{expected:08x}", f"0x{result:08x}")
    log("  ✓ PASS")
    
    # Test 5: CSR read/write
    log("\nTest 5: CSR read/write")
    csr_tests = [
        (0x300, 0x00001800),  # mstatus
        (0x305, 0x80000000),  # mtvec
        (0x341, 0x80001234),  # mepc
        (0x342, 0x00000002),  # mcause
    ]
    for addr, value in csr_tests:
        cpu.write_csr(addr, value)
        result = cpu.read_csr(addr)
        log(f"  cpu.write_csr(0x{addr:03x}, 0x{value:08x})")
        log(f"  cpu.read_csr(0x{addr:03x}) = 0x{result:08x}")
        if result != value:
            test_fail(f"CSR 0x{addr:03x} read/write",
                     f"0x{value:08x}", f"0x{result:08x}")
    log("  ✓ PASS")
    
    # Test 6: CSR 32-bit masking
    log("\nTest 6: CSR 32-bit masking")
    cpu.write_csr(0x300, 0x123456789ABCDEF0)
    result = cpu.read_csr(0x300)
    expected = 0x9ABCDEF0
    log(f"  cpu.write_csr(0x300, 0x123456789ABCDEF0)")
    log(f"  cpu.read_csr(0x300) = 0x{result:08x} (expected 0x{expected:08x})")
    if result != expected:
        test_fail("CSR 32-bit masking", f"0x{expected:08x}", f"0x{result:08x}")
    log("  ✓ PASS")
    
    # Test 7: Unimplemented CSR returns 0
    log("\nTest 7: Unimplemented CSR returns 0")
    result = cpu.read_csr(0x999)  # Non-existent CSR
    log(f"  cpu.read_csr(0x999) = 0x{result:08x}")
    if result != 0:
        test_fail("Unimplemented CSR read", "0x00000000", f"0x{result:08x}")
    log("  ✓ PASS")
    
    # Test 8: Reset functionality
    log("\nTest 8: Reset functionality")
    # First set some values
    cpu.write_reg(1, 0xDEADBEEF)
    cpu.write_reg(2, 0x12345678)
    cpu.write_csr(0x300, 0xAABBCCDD)
    cpu.pc = 0x12345678
    log(f"  Before reset: x1=0x{cpu.read_reg(1):08x}, x2=0x{cpu.read_reg(2):08x}")
    log(f"  Before reset: CSR[0x300]=0x{cpu.read_csr(0x300):08x}, PC=0x{cpu.pc:08x}")
    
    # Reset
    cpu.reset()
    log(f"  After reset:  x1=0x{cpu.read_reg(1):08x}, x2=0x{cpu.read_reg(2):08x}")
    log(f"  After reset:  CSR[0x300]=0x{cpu.read_csr(0x300):08x}, PC=0x{cpu.pc:08x}")
    
    # Check all registers are zero
    for i in range(32):
        if cpu.read_reg(i) != 0:
            test_fail(f"Reset register x{i}", "0x00000000", 
                     f"0x{cpu.read_reg(i):08x}")
    
    # Check PC reset to boot address
    if cpu.pc != 0x80000000:
        test_fail("Reset PC", "0x80000000", f"0x{cpu.pc:08x}")
    
    # Check CSRs are zero
    for addr in cpu.csrs:
        if cpu.read_csr(addr) != 0:
            test_fail(f"Reset CSR 0x{addr:03x}", "0x00000000",
                     f"0x{cpu.read_csr(addr):08x}")
    log("  ✓ PASS")
    
    # Test 9: Register bounds checking
    log("\nTest 9: All 32 registers accessible")
    for i in range(32):
        cpu.write_reg(i, i * 0x11111111)
        result = cpu.read_reg(i)
        expected = 0 if i == 0 else (i * 0x11111111) & 0xFFFFFFFF
        log(f"  x{i:2d} = 0x{result:08x}")
        if result != expected:
            test_fail(f"Register x{i} access", 
                     f"0x{expected:08x}", f"0x{result:08x}")
    log("  ✓ PASS")
    
    log("\n" + "=" * 60)
    log("ALL CPU TESTS PASSED ✓")
    log(f"Log file: {log_path}")
    log("=" * 60 + "\n")
    
    log_file.close()
    
    return log_path


if __name__ == "__main__":
    log_path = run_cpu_tests()
    print(f"CPU tests PASSED ✓ (log: {log_path})")
