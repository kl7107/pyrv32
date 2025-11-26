#!/usr/bin/env python3
"""
RISC-V Debugger Module
Provides breakpoint management and debugging features for pyrv32 simulator
"""

from collections import deque

class TraceEntry:
    """Single entry in the trace buffer"""
    def __init__(self, step, pc, regs, insn):
        self.step = step  # Instruction number
        self.pc = pc
        self.regs = regs.copy()  # Copy of all 32 registers
        self.insn = insn  # The instruction that was executed
        self.index = 0  # Monotonic index, set by TraceBuffer.add()
    
    def __repr__(self):
        return f"TraceEntry(step={self.step}, PC=0x{self.pc:08x}, insn=0x{self.insn:08x}, index={self.index})"


class TraceBuffer:
    """Ring buffer for storing execution trace"""
    def __init__(self, max_size=10000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.enabled = False
        self.total_count = 0  # Monotonic counter, never resets (except on clear)
    
    def add(self, step, pc, regs, insn):
        """Add a trace entry (before executing the instruction)"""
        if not self.enabled:
            return
        entry = TraceEntry(step, pc, regs, insn)
        entry.index = self.total_count  # Assign monotonic index
        self.buffer.append(entry)
        self.total_count += 1
    
    def get_last(self, n):
        """Get last N entries in chronological order (oldest first)"""
        if n <= 0:
            return []
        start_idx = max(0, len(self.buffer) - n)
        return list(self.buffer)[start_idx:]
    
    def get_range(self, start, count):
        """Get COUNT entries starting at index START (chronological order)"""
        if start < 0 or start >= len(self.buffer):
            return []
        end = min(start + count, len(self.buffer))
        return list(self.buffer)[start:end]
    
    def get_all(self):
        """Get all entries in chronological order"""
        return list(self.buffer)
    
    def get_by_index(self, index):
        """Get entry by absolute index (monotonic counter value)"""
        # Find entry with matching index
        for entry in self.buffer:
            if entry.index == index:
                return entry
        return None
    
    def get_reg_index(self, reg_name):
        """Convert register name to index"""
        reg_map = {
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7,
            's0': 8, 'fp': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
            's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23,
            's8': 24, 's9': 25, 's10': 26, 's11': 27,
            't3': 28, 't4': 29, 't5': 30, 't6': 31
        }
        reg_name_lower = reg_name.lower()
        if reg_name_lower in reg_map:
            return reg_map[reg_name_lower]
        if reg_name_lower.startswith('x'):
            return int(reg_name_lower[1:])
        return None
    
    def search_reverse(self, reg_name, value, start_idx=None, not_equal=False):
        """
        Search backwards through trace buffer for register matching (or not matching) value.
        
        Args:
            reg_name: Register name (e.g., 'a0', 's4', 'pc')
            value: Value to search for (integer)
            start_idx: Start searching from this index (None = from end)
            not_equal: If True, search for NOT equal instead of equal
        
        Returns:
            TraceEntry or None
        """
        # Convert register name to index
        reg_map = {
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7,
            's0': 8, 'fp': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
            's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23,
            's8': 24, 's9': 25, 's10': 26, 's11': 27,
            't3': 28, 't4': 29, 't5': 30, 't6': 31
        }
        
        # Special handling for PC
        check_pc = (reg_name.lower() == 'pc')
        
        if not check_pc:
            reg_name_lower = reg_name.lower()
            if reg_name_lower not in reg_map:
                # Try as register number (x0-x31)
                if reg_name_lower.startswith('x'):
                    try:
                        reg_idx = int(reg_name_lower[1:])
                        if 0 <= reg_idx <= 31:
                            pass  # Valid
                        else:
                            return None
                    except ValueError:
                        return None
                else:
                    return None
            else:
                reg_idx = reg_map[reg_name_lower]
        
        # Get entries in reverse order
        entries = list(self.buffer)
        
        # If start_idx specified, find where to start
        if start_idx is not None:
            # Find the position in buffer for this index
            start_pos = None
            for i, entry in enumerate(entries):
                if entry.index == start_idx:
                    start_pos = i
                    break
            
            if start_pos is None:
                return None  # Index not found in buffer
            
            # Search from start_pos backwards to beginning
            entries = entries[:start_pos+1]
        
        # Search backwards
        for entry in reversed(entries):
            if check_pc:
                match = (entry.pc == value)
            else:
                match = (entry.regs[reg_idx] == value)
            
            # Return entry if condition met
            if not_equal:
                if not match:  # Found NOT equal
                    return entry
            else:
                if match:  # Found equal
                    return entry
        
        return None
    
    def clear(self):
        """Clear the trace buffer"""
        self.buffer.clear()
        self.total_count = 0
    
    def enable(self):
        """Enable trace collection"""
        self.enabled = True
    
    def disable(self):
        """Disable trace collection"""
        self.enabled = False
    
    def size(self):
        """Return current number of entries"""
        return len(self.buffer)
    
    def is_full(self):
        """Check if buffer is at max capacity"""
        return len(self.buffer) >= self.max_size


class Breakpoint:
    """Represents a single breakpoint"""
    next_id = 1
    
    def __init__(self, address=None, enabled=True, condition=None, reg_condition=None):
        self.id = Breakpoint.next_id
        Breakpoint.next_id += 1
        self.address = address  # None for register-only breakpoints
        self.enabled = enabled
        self.hit_count = 0
        self.condition = condition  # Future: expression-based conditions
        self.reg_condition = reg_condition  # {'reg': 'a0', 'value': 0x1234}
    
    def check_condition(self, regs):
        """Check if register condition is met"""
        if not self.reg_condition:
            return True
        
        reg_name = self.reg_condition['reg']
        expected_value = self.reg_condition['value']
        
        # Get register index
        reg_map = {
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7,
            's0': 8, 'fp': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
            's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23,
            's8': 24, 's9': 25, 's10': 26, 's11': 27,
            't3': 28, 't4': 29, 't5': 30, 't6': 31
        }
        
        reg_name_lower = reg_name.lower()
        if reg_name_lower in reg_map:
            reg_idx = reg_map[reg_name_lower]
        elif reg_name_lower.startswith('x'):
            reg_idx = int(reg_name_lower[1:])
        else:
            return False
        
        return regs[reg_idx] == expected_value
    
    def __repr__(self):
        status = "enabled" if self.enabled else "disabled"
        if self.reg_condition:
            reg_str = f" when {self.reg_condition['reg']}=0x{self.reg_condition['value']:08x}"
        else:
            reg_str = ""
        
        if self.address is not None:
            return f"Breakpoint {self.id} at 0x{self.address:08x}{reg_str} ({status}, hits: {self.hit_count})"
        else:
            return f"Breakpoint {self.id}{reg_str} ({status}, hits: {self.hit_count})"


class BreakpointManager:
    """Manages all breakpoints for the debugger"""
    
    def __init__(self):
        self.breakpoints = {}  # address -> Breakpoint
        self.breakpoints_by_id = {}  # id -> Breakpoint
        self.register_breakpoints = []  # List of register-only breakpoints
    
    def add(self, address=None, reg_name=None, reg_value=None):
        """Add a breakpoint at address and/or with register condition"""
        if address is not None and reg_name is None:
            # Simple address breakpoint
            if address in self.breakpoints:
                return self.breakpoints[address]
            
            bp = Breakpoint(address=address)
            self.breakpoints[address] = bp
            self.breakpoints_by_id[bp.id] = bp
            return bp
        
        # Register condition breakpoint (with optional address)
        reg_condition = None
        if reg_name is not None and reg_value is not None:
            reg_condition = {'reg': reg_name, 'value': reg_value}
        
        bp = Breakpoint(address=address, reg_condition=reg_condition)
        self.breakpoints_by_id[bp.id] = bp
        
        if address is not None:
            self.breakpoints[address] = bp
        else:
            # Register-only breakpoint
            self.register_breakpoints.append(bp)
        
        return bp
    
    def delete(self, bp_id):
        """Delete a breakpoint by ID"""
        if bp_id not in self.breakpoints_by_id:
            return False
        
        bp = self.breakpoints_by_id[bp_id]
        if bp.address is not None and bp.address in self.breakpoints:
            del self.breakpoints[bp.address]
        if bp in self.register_breakpoints:
            self.register_breakpoints.remove(bp)
        del self.breakpoints_by_id[bp_id]
        return True
    
    def delete_all(self):
        """Delete all breakpoints"""
        count = len(self.breakpoints_by_id)
        self.breakpoints.clear()
        self.breakpoints_by_id.clear()
        self.register_breakpoints.clear()
        Breakpoint.next_id = 1
        return count
    
    def list(self):
        """Return list of all breakpoints sorted by ID"""
        return sorted(self.breakpoints_by_id.values(), key=lambda bp: bp.id)
    
    def check(self, address, regs):
        """Check if there's an enabled breakpoint at this address or register condition"""
        # Check address breakpoints
        if address in self.breakpoints:
            bp = self.breakpoints[address]
            if bp.enabled:
                # Check register condition if present
                if bp.check_condition(regs):
                    bp.hit_count += 1
                    return bp
        
        # Check register-only breakpoints
        for bp in self.register_breakpoints:
            if bp.enabled and bp.check_condition(regs):
                bp.hit_count += 1
                return bp
        
        return None
    
    def get_by_id(self, bp_id):
        """Get breakpoint by ID"""
        return self.breakpoints_by_id.get(bp_id)
    
    def enable(self, bp_id):
        """Enable a breakpoint"""
        bp = self.get_by_id(bp_id)
        if bp:
            bp.enabled = True
            return True
        return False
    
    def disable(self, bp_id):
        """Disable a breakpoint"""
        bp = self.get_by_id(bp_id)
        if bp:
            bp.enabled = False
            return True
        return False


class Debugger:
    """Main debugger interface"""
    
    def __init__(self, trace_buffer_size=10000):
        self.bp_manager = BreakpointManager()
        self.step_mode = False
        self.step_count = 0  # How many instructions to step (0 = continuous)
        self.reg_trace_enabled = False
        self.reg_trace_file = None
        self.reg_trace_interval = 1  # Trace every N instructions
        self.reg_trace_nonzero = False
        self.trace_buffer = TraceBuffer(max_size=trace_buffer_size)
        # Trace buffer is always enabled by default for debugging
        self.trace_buffer.enable()
    
    def should_break(self, pc, instruction_count, regs):
        """Check if execution should break at this PC"""
        # Check breakpoints (both address and register conditions)
        bp = self.bp_manager.check(pc, regs)
        if bp:
            if bp.address is not None:
                if bp.reg_condition:
                    reg_str = f" (condition: {bp.reg_condition['reg']}=0x{bp.reg_condition['value']:08x})"
                else:
                    reg_str = ""
                return True, f"Breakpoint {bp.id} hit at 0x{pc:08x}{reg_str}"
            else:
                return True, f"Breakpoint {bp.id} hit: {bp.reg_condition['reg']}=0x{bp.reg_condition['value']:08x}"
        
        # Check step mode
        if self.step_mode:
            # On first instruction (instruction_count == 0), always break without message
            if instruction_count == 0:
                return True, None  # Break but no message
            
            if self.step_count > 0:
                self.step_count -= 1
                if self.step_count == 0:
                    return True, f"Step complete at 0x{pc:08x}"
        
        return False, None
    
    def set_step_mode(self, enabled, count=1):
        """Enable/disable step mode with optional step count"""
        self.step_mode = enabled
        self.step_count = count if enabled else 0
    
    def enable_reg_trace(self, filename=None, interval=1, nonzero_only=False):
        """Enable register tracing to file or stdout"""
        self.reg_trace_enabled = True
        self.reg_trace_interval = interval
        self.reg_trace_nonzero = nonzero_only
        if filename:
            self.reg_trace_file = open(filename, 'w')
            print(f"Register trace enabled to file: {filename}")
        else:
            print(f"Register trace enabled to stdout")
    
    def disable_reg_trace(self):
        """Disable register tracing"""
        if self.reg_trace_file:
            self.reg_trace_file.close()
            self.reg_trace_file = None
        self.reg_trace_enabled = False
    
    def trace_registers(self, instruction_count, pc, regs):
        """Write register trace if enabled and at interval"""
        if not self.reg_trace_enabled:
            return
        
        if instruction_count % self.reg_trace_interval != 0:
            return
        
        # Format: [step] PC=0xXXXXXXXX  ra=0x... sp=0x... ...
        output = self.format_registers(regs, pc, compact=True, show_nonzero_only=self.reg_trace_nonzero)
        prefix = f"[{instruction_count:7d}] "
        
        # Add prefix to first line
        lines = output.splitlines()
        if lines:
            lines[0] = prefix + lines[0]
            for i in range(1, len(lines)):
                lines[i] = " " * len(prefix) + lines[i]
        
        trace_output = "\n".join(lines)
        
        if self.reg_trace_file:
            self.reg_trace_file.write(trace_output + "\n")
            self.reg_trace_file.flush()
        else:
            print(trace_output)
    
    def format_registers(self, regs, pc, compact=True, show_nonzero_only=False):
        """Format register dump"""
        if compact:
            lines = []
            lines.append(f"PC=0x{pc:08x}  ra=0x{regs[1]:08x} sp=0x{regs[2]:08x} gp=0x{regs[3]:08x} tp=0x{regs[4]:08x}")
            
            # a0-a7
            a_regs = [f"a{i}=0x{regs[10+i]:08x}" for i in range(8)]
            if show_nonzero_only:
                a_regs = [r for i, r in enumerate(a_regs) if regs[10+i] != 0]
            if a_regs:
                lines.append("          " + " ".join(a_regs))
            
            # t0-t6
            t_regs = [f"t{i}=0x{regs[5+i]:08x}" for i in range(3)]
            t_regs += [f"t{i+3}=0x{regs[28+i]:08x}" for i in range(4)]
            if show_nonzero_only:
                t_regs = [r for i, r in enumerate(t_regs) if (regs[5+i] if i < 3 else regs[25+i]) != 0]
            if t_regs:
                lines.append("          " + " ".join(t_regs))
            
            # s0-s11
            s_regs = [f"s{i}=0x{regs[8+i]:08x}" for i in range(2)]
            s_regs += [f"s{i+2}=0x{regs[18+i]:08x}" for i in range(10)]
            if show_nonzero_only:
                s_regs = [r for i, r in enumerate(s_regs) if (regs[8+i] if i < 2 else regs[16+i]) != 0]
            if s_regs:
                lines.append("          " + " ".join(s_regs))
            
            return "\n".join(lines)
        else:
            # Full format (4 columns)
            lines = [f"PC = 0x{pc:08x}"]
            reg_names = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2',
                        's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5',
                        'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7',
                        's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']
            
            for i in range(0, 32, 4):
                row = []
                for j in range(4):
                    if i+j < 32:
                        name = reg_names[i+j]
                        val = regs[i+j]
                        if not show_nonzero_only or val != 0:
                            row.append(f"{name:4s} = 0x{val:08x}")
                if row:
                    lines.append("  ".join(row))
            
            return "\n".join(lines)
    
    def format_trace_entry(self, entry, show_insn_name=True, show_nonzero_only=False):
        """Format a single trace entry for display"""
        lines = []
        
        # Header with step number, PC, and instruction
        if show_insn_name:
            # Will need to decode instruction - for now just show hex
            lines.append(f"[{entry.step:7d}] PC=0x{entry.pc:08x}  insn=0x{entry.insn:08x}")
        else:
            lines.append(f"[{entry.step:7d}] PC=0x{entry.pc:08x}")
        
        # Registers (compact format)
        reg_str = self.format_registers(entry.regs, entry.pc, compact=True, 
                                        show_nonzero_only=show_nonzero_only)
        # Skip the PC line since we already showed it
        reg_lines = reg_str.split('\n')[1:]
        for line in reg_lines:
            lines.append(" " * 10 + line.strip())
        
        return "\n".join(lines)
    
    def dump_trace(self, count=None, start=None, show_insn=True, nonzero_only=False):
        """
        Dump trace buffer entries.
        
        Args:
            count: Number of entries to show (None = all)
            start: Starting index (None = from end if count specified, else 0)
            show_insn: Show instruction hex
            nonzero_only: Only show non-zero registers
        
        Returns:
            Formatted string of trace entries
        """
        if count is None:
            # Show all entries
            entries = self.trace_buffer.get_all()
        elif start is not None:
            # Show COUNT entries starting at START
            entries = self.trace_buffer.get_range(start, count)
        else:
            # Show last COUNT entries
            entries = self.trace_buffer.get_last(count)
        
        if not entries:
            return "Trace buffer is empty"
        
        lines = []
        lines.append(f"Trace buffer: showing {len(entries)} entries (buffer size: {self.trace_buffer.size()}/{self.trace_buffer.max_size})")
        lines.append("=" * 70)
        
        for entry in entries:
            lines.append(self.format_trace_entry(entry, show_insn_name=show_insn, 
                                                 show_nonzero_only=nonzero_only))
            lines.append("")  # Blank line between entries
        
        return "\n".join(lines)
    
    def search_trace_reverse(self, reg_name, value, start_idx=None, not_equal=False):
        """
        Search trace buffer in reverse for a register value (or not equal to value).
        
        Args:
            reg_name: Register name (e.g., 'a0', 's4', 'pc')
            value: Value to search for (integer)
            start_idx: Start searching from this index (None = from end)
            not_equal: If True, search for NOT equal instead of equal
        
        Returns:
            Tuple of (found, message, entry)
        """
        entry = self.trace_buffer.search_reverse(reg_name, value, start_idx, not_equal)
        
        if entry is None:
            op = "!=" if not_equal else "="
            if start_idx is not None:
                msg = f"Register {reg_name}{op}0x{value:08x} not found searching backwards from index {start_idx}"
            else:
                msg = f"Register {reg_name}{op}0x{value:08x} not found in trace buffer"
            return (False, msg, None)
        
        op = "!=" if not_equal else "="
        reg_idx = self.trace_buffer.get_reg_index(reg_name)
        if reg_name.lower() == 'pc':
            actual_val = entry.pc
        elif reg_idx is not None:
            actual_val = entry.regs[reg_idx]
        else:
            actual_val = 0
        msg = f"Found {reg_name}{op}0x{value:08x} at index {entry.index} (step {entry.step}): {reg_name}=0x{actual_val:08x}"
        return (True, msg, entry)


# Module-level test functions
def test_breakpoints():
    """Test breakpoint functionality"""
    print("=== Testing Breakpoint Manager ===")
    
    mgr = BreakpointManager()
    
    # Add breakpoints
    bp1 = mgr.add(0x80000100)
    print(f"Added: {bp1}")
    
    bp2 = mgr.add(0x80000200)
    print(f"Added: {bp2}")
    
    bp3 = mgr.add(0x80000100)  # Duplicate
    print(f"Duplicate: {bp3} (should be same as bp1: {bp1 is bp3})")
    
    # List breakpoints
    print("\nAll breakpoints:")
    for bp in mgr.list():
        print(f"  {bp}")
    
    # Check breakpoints
    print("\nChecking addresses:")
    result = mgr.check(0x80000100)
    print(f"  0x80000100: {result}")
    
    result = mgr.check(0x80000300)
    print(f"  0x80000300: {result}")
    
    result = mgr.check(0x80000200)
    print(f"  0x80000200: {result}")
    
    # Hit count
    print(f"\nBp1 hits: {bp1.hit_count}")
    print(f"Bp2 hits: {bp2.hit_count}")
    
    # Delete breakpoint
    print(f"\nDeleting bp1 (id={bp1.id}): {mgr.delete(bp1.id)}")
    print(f"Remaining breakpoints: {len(mgr.list())}")
    
    # Delete all
    count = mgr.delete_all()
    print(f"\nDeleted all ({count} total)")
    print(f"Remaining: {len(mgr.list())}")
    
    print("\n=== Breakpoint Tests Complete ===\n")


def test_debugger():
    """Test debugger functionality"""
    print("=== Testing Debugger ===")
    
    dbg = Debugger()
    
    # Add some breakpoints
    dbg.bp_manager.add(0x80001000)
    dbg.bp_manager.add(0x80002000)
    
    # Test should_break
    print("Testing should_break:")
    should_break, msg = dbg.should_break(0x80000500, 100)
    print(f"  PC=0x80000500: break={should_break}, msg={msg}")
    
    should_break, msg = dbg.should_break(0x80001000, 200)
    print(f"  PC=0x80001000: break={should_break}, msg={msg}")
    
    # Test step mode
    print("\nTesting step mode:")
    dbg.set_step_mode(True, count=3)
    for i in range(5):
        should_break, msg = dbg.should_break(0x80000000 + i*4, i)
        print(f"  Instruction {i}: break={should_break}, msg={msg}")
    
    # Test register formatting
    print("\nTesting register formatting:")
    regs = [0] * 32
    regs[1] = 0x80000040  # ra
    regs[2] = 0x80800000  # sp
    regs[10] = 0x00000001  # a0
    regs[11] = 0x801a3c1c  # a1
    
    print("Compact format:")
    print(dbg.format_registers(regs, 0x80001234, compact=True))
    
    print("\nCompact non-zero only:")
    print(dbg.format_registers(regs, 0x80001234, compact=True, show_nonzero_only=True))
    
    print("\n=== Debugger Tests Complete ===\n")


if __name__ == '__main__':
    test_breakpoints()
    test_debugger()
