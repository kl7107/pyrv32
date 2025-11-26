"""
RV32 Exceptions - Custom exceptions for RISC-V execution
"""


class EBreakException(Exception):
    """Raised when EBREAK instruction is executed - used for normal program termination"""
    def __init__(self, pc):
        self.pc = pc
        super().__init__(f"EBREAK at PC=0x{pc:08x}")


class ECallException(Exception):
    """Raised when ECALL instruction is executed - environment/system call"""
    def __init__(self, pc):
        self.pc = pc
        super().__init__(f"ECALL at PC=0x{pc:08x}")


class MemoryAccessFault(Exception):
    """Raised when accessing invalid/unmapped memory address"""
    def __init__(self, address, access_type, pc):
        self.address = address
        self.access_type = access_type  # 'load', 'store', or 'fetch'
        self.pc = pc
        super().__init__(
            f"Memory Access Fault: {access_type} at address 0x{address:08x} "
            f"(PC=0x{pc:08x})"
        )
