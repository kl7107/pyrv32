"""
CPU Module - RV32IMC CPU Register State

Contains the RV32CPU class which manages:
- General purpose registers (x0-x31)
- Program counter (PC)
- Control and Status Registers (CSRs)
"""


class RV32CPU:
    """
    RISC-V RV32IMC CPU Simulator
    
    Registers:
    - x0-x31: 32 general purpose registers (x0 is always 0)
    - pc: Program counter
    - CSRs: Control and Status Registers (minimal set for user-space)
    """
    
    def __init__(self):
        # General purpose registers x0-x31
        # Using a list for simplicity - direct indexing with register number
        self.regs = [0] * 32
        
        # Program counter
        self.pc = 0
        
        # Control and Status Registers (CSRs)
        # Using a dictionary for CSRs since they're accessed by address
        self.csrs = {
            0x300: 0,  # mstatus - Machine status register
            0x305: 0,  # mtvec - Machine trap-vector base-address
            0x341: 0,  # mepc - Machine exception program counter
            0x342: 0,  # mcause - Machine trap cause
            0x304: 0,  # mie - Machine interrupt-enable
            0x344: 0,  # mip - Machine interrupt-pending
        }
    
    def read_reg(self, index):
        """
        Read a general purpose register.
        
        Args:
            index: Register number (0-31)
            
        Returns:
            Register value (32-bit unsigned)
            
        Note: x0 always returns 0
        """
        if index == 0:
            return 0
        return self.regs[index] & 0xFFFFFFFF
    
    def write_reg(self, index, value):
        """
        Write to a general purpose register.
        
        Args:
            index: Register number (0-31)
            value: Value to write
            
        Note: Writes to x0 are ignored
        """
        if index != 0:
            # Mask to 32 bits to simulate hardware behavior
            self.regs[index] = value & 0xFFFFFFFF
    
    def read_csr(self, address):
        """
        Read a Control and Status Register.
        
        Args:
            address: CSR address
            
        Returns:
            CSR value (32-bit)
        """
        if address in self.csrs:
            return self.csrs[address] & 0xFFFFFFFF
        # Unimplemented CSRs return 0
        return 0
    
    def write_csr(self, address, value):
        """
        Write to a Control and Status Register.
        
        Args:
            address: CSR address
            value: Value to write
        """
        if address in self.csrs:
            self.csrs[address] = value & 0xFFFFFFFF
    
    def reset(self):
        """
        Reset the CPU to initial state.
        """
        # Clear all general purpose registers
        for i in range(32):
            self.regs[i] = 0
        
        # Reset program counter (typically starts at 0x80000000 for RISC-V)
        self.pc = 0x80000000
        
        # Clear CSRs
        for addr in self.csrs:
            self.csrs[addr] = 0
    
    def dump_registers(self):
        """
        Print all register values for debugging.
        """
        # ABI register names
        abi_names = [
            "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
            "s0/fp", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
            "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
            "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6"
        ]
        
        print("=" * 60)
        print("Register Dump")
        print("=" * 60)
        
        # Print registers in groups of 4
        for i in range(0, 32, 4):
            line = ""
            for j in range(4):
                if i + j < 32:
                    reg_num = i + j
                    reg_val = self.read_reg(reg_num)
                    line += f"x{reg_num:2d}({abi_names[reg_num]:5s})={reg_val:08x}  "
            print(line)
        
        print(f"\nPC = {self.pc:08x}")
        print("=" * 60)
