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
