"""Regression tests covering MCP-specific simulator behaviors."""

import asyncio
import importlib.util
import os
import struct
import sys
import tempfile

from pyrv32_system import RV32System

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRMWARE_DIR = os.path.join(REPO_ROOT, 'firmware')
HELLO_ELF = os.path.join(FIRMWARE_DIR, 'hello.elf')

Pyrv32_MCP_DIR = os.path.join(REPO_ROOT, 'pyrv32_mcp')
if Pyrv32_MCP_DIR not in sys.path:
    sys.path.insert(0, Pyrv32_MCP_DIR)

SESSION_MANAGER_SPEC = importlib.util.spec_from_file_location(
    'session_manager_for_tests',
    os.path.join(REPO_ROOT, 'pyrv32_mcp', 'session_manager.py')
)
if SESSION_MANAGER_SPEC is None or SESSION_MANAGER_SPEC.loader is None:
    raise ImportError('Unable to load SessionManager spec for tests')
SESSION_MANAGER_MODULE = importlib.util.module_from_spec(SESSION_MANAGER_SPEC)
SESSION_MANAGER_SPEC.loader.exec_module(SESSION_MANAGER_MODULE)
SessionManager = SESSION_MANAGER_MODULE.SessionManager

SIM_SERVER_SPEC = importlib.util.spec_from_file_location(
    'mcp_server_for_tests',
    os.path.join(REPO_ROOT, 'pyrv32_mcp', 'sim_server_mcp_v2.py')
)
if SIM_SERVER_SPEC is None or SIM_SERVER_SPEC.loader is None:
    raise ImportError('Unable to load MCPSimulatorServer spec for tests')
SIM_SERVER_MODULE = importlib.util.module_from_spec(SIM_SERVER_SPEC)
SIM_SERVER_SPEC.loader.exec_module(SIM_SERVER_MODULE)
MCPSimulatorServer = SIM_SERVER_MODULE.MCPSimulatorServer


PROGRAM_START = 0x80000000
READ_WATCH_ADDR = 0x80004000
WRITE_WATCH_ADDR = 0x80005000


def _asm(*words):
    """Pack 32-bit instruction words into little-endian bytes."""
    return b"".join(struct.pack('<I', word) for word in words)


def _addi_t1(value):
    """Encode `addi t1, x0, value` for small immediates."""
    imm = value & 0xFFF
    rd = 6   # t1
    rs1 = 0  # x0
    opcode = 0x13
    funct3 = 0
    return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def _lui(rd, imm20):
    """Encode an RV32I LUI instruction."""
    return (imm20 << 12) | (rd << 7) | 0x37


def _lbu(rd, rs1, imm):
    """Encode `lbu rd, imm(rs1)`."""
    imm &= 0xFFF
    return (imm << 20) | (rs1 << 15) | (4 << 12) | (rd << 7) | 0x03


def _sb(rs1, rs2, imm):
    """Encode `sb rs2, imm(rs1)`."""
    imm &= 0xFFF
    imm_hi = (imm >> 5) & 0x7F
    imm_lo = imm & 0x1F
    return (imm_hi << 25) | (rs2 << 20) | (rs1 << 15) | (0 << 12) | (imm_lo << 7) | 0x23


def _call_tool_text(server, name, **arguments):
    """Call an MCP tool synchronously and return concatenated text blocks."""
    response = asyncio.run(server.call_tool(name, arguments))
    return "\n".join(block.get('text', '') for block in response if block.get('type') == 'text')


def _write_program_via_tools(server, session_id, program_bytes, start_addr=PROGRAM_START):
    """Load raw program bytes and set PC through MCP tools."""
    hex_blob = program_bytes.hex()
    _call_tool_text(
        server,
        'sim_write_memory',
        session_id=session_id,
        address=f"0x{start_addr:08x}",
        data=hex_blob
    )
    _call_tool_text(
        server,
        'sim_set_register',
        session_id=session_id,
        register='pc',
        value=f"0x{start_addr:08x}"
    )


def test_load_elf_metadata_reports_segments(runner):
    """ELF loader should populate metadata needed by MCP tools."""
    if not os.path.exists(HELLO_ELF):
        runner.test_fail('load_elf metadata', 'hello.elf exists', 'missing hello.elf')

    system = RV32System()
    info = system.load_elf(HELLO_ELF)

    if system.cpu.pc != info['entry_point']:
        runner.test_fail('load_elf metadata', 'PC matches entry point', f"pc=0x{system.cpu.pc:08x} entry=0x{info['entry_point']:08x}")

    if info['bytes_loaded'] <= 0:
        runner.test_fail('load_elf metadata', 'bytes_loaded > 0', info['bytes_loaded'])

    if not info['segments']:
        runner.test_fail('load_elf metadata', 'segments present', 'no segments recorded')

    if info['symbols_loaded'] == 0:
        runner.test_fail('load_elf metadata', 'symbol table populated', 0)

    if info.get('disasm_cache') != 'ready':
        runner.test_fail('load_elf metadata', 'disasm cache ready', info.get('disasm_cache'))


def test_console_uart_write_normalizes_line_endings(runner):
    """console_uart_write must normalize LF to CR to mimic MCP injection."""
    system = RV32System()
    system.console_uart_write('line1\nline2')
    rx_bytes = bytes(system.memory.console_uart.rx_buffer)
    if b'\n' in rx_bytes:
        runner.test_fail('console_uart_write newline', 'no LF bytes remain', rx_bytes)
    if rx_bytes != b'line1\rline2':
        runner.test_fail('console_uart_write newline', b'line1\rline2', rx_bytes)

    system = RV32System()
    system.console_uart_write(b'abc\ndef')
    rx_bytes = bytes(system.memory.console_uart.rx_buffer)
    if rx_bytes != b'abc\rdef':
        runner.test_fail('console_uart_write bytes normalization', b'abc\rdef', rx_bytes)


def test_run_until_console_status_read_triggers_watchpoint(runner):
    """run_until_console_status_read must halt when RX status is polled."""
    # Program: load Console UART base into t0, read RX status (offset 8), halt
    program = _asm(
        0x100012B7,  # lui t0, 0x10001 -> 0x10001000
        0x0082C303,  # lbu t1, 8(t0) -> touches 0x10001008 without MMIO fault
        0x00100073   # ebreak
    )
    system = RV32System()
    system.load_binary_data(program)
    result = system.run_until_console_status_read(max_steps=10)

    if result.status != 'halted':
        runner.test_fail('run_until_console_status_read', 'halted status', result.status)

    if result.error is None or 'watchpoint' not in result.error.lower():
        runner.test_fail('run_until_console_status_read', 'watchpoint error message', result.error)

    if 0x10001008 in system.memory.read_watchpoints:
        runner.test_fail('run_until_console_status_read', 'temporary watchpoint removed', system.memory.read_watchpoints)


def test_console_uart_tx_program_output(runner):
    """A simple program that stores to console UART TX should produce output."""
    program = _asm(
        0x100012B7,  # lui t0, 0x10001 -> console UART base
        0x04100313,  # addi t1, x0, 65 ('A')
        0x00628023,  # sb t1, 0(t0) -> write 'A' to 0x10001000
        0x00100073   # ebreak
    )
    system = RV32System()
    system.load_binary_data(program)
    result = system.run(max_steps=10)

    if result.status != 'halted':
        runner.test_fail('console UART TX program', 'halted status', result.status)

    output = system.console_uart_read_all()
    if output != 'A':
        runner.test_fail('console UART TX program', "output 'A'", repr(output))


def test_disassemble_cached_returns_cached_objdump(runner):
    """disassemble_cached should return objdump output without error markers."""
    if not os.path.exists(HELLO_ELF):
        runner.test_fail('disassemble_cached', 'hello.elf exists', 'missing hello.elf')

    system = RV32System()
    info = system.load_elf(HELLO_ELF)
    start = info['entry_point']
    disasm = system.disassemble_cached(hex(start), hex(start + 0x10))
    if 'Error' in disasm:
        runner.test_fail('disassemble_cached', 'objdump text', disasm.split('\n', 1)[0])


def test_session_manager_lifecycle_and_lock_cleanup(runner):
    """SessionManager should clean locks, track sessions, and propagate cwd."""
    with tempfile.TemporaryDirectory() as tmp_fs_root:
        lock_dir = os.path.join(tmp_fs_root, 'usr/games/lib/nethackdir')
        os.makedirs(lock_dir, exist_ok=True)
        lock_path = os.path.join(lock_dir, 'perm_lock')
        with open(lock_path, 'w', encoding='utf-8') as handle:
            handle.write('stale-lock')

        manager = SessionManager()
        session_id = manager.create_session(fs_root=tmp_fs_root)

        if os.path.exists(lock_path):
            runner.test_fail('SessionManager lock cleanup', 'stale locks removed', lock_path)

        if manager.get_session_count() != 1:
            runner.test_fail('SessionManager session count', 1, manager.get_session_count())

        if session_id not in manager.list_sessions():
            runner.test_fail('SessionManager list_sessions', session_id, manager.list_sessions())

        session = manager.get_session(session_id)
        if session is None:
            runner.test_fail('SessionManager get_session', 'RV32System instance', session)

        workdir = os.path.join(tmp_fs_root, 'workdir')
        os.makedirs(workdir, exist_ok=True)
        if not manager.set_working_directory(session_id, workdir):
            runner.test_fail('SessionManager set_working_directory', True, False)

        if getattr(session.syscall_handler, 'cwd', None) != workdir:
            runner.test_fail('SessionManager cwd propagation', workdir, session.syscall_handler.cwd)

        if not manager.destroy_session(session_id):
            runner.test_fail('SessionManager destroy_session', True, False)

        if manager.get_session_count() != 0:
            runner.test_fail('SessionManager destroy_session', 0, manager.get_session_count())

        if manager.list_sessions():
            runner.test_fail('SessionManager destroy_session', 'no remaining sessions', manager.list_sessions())


def test_register_accessor_handles_abi_and_pc(runner):
    """Register helpers should honor ABI names, pc, and x0 immutability."""
    system = RV32System()

    system.set_register('a0', 0x12345678)
    if system.get_register('a0') != 0x12345678:
        runner.test_fail('register access ABI name', 0x12345678, system.get_register('a0'))

    system.set_register('pc', 0x90000010)
    if system.get_register('pc') != 0x90000010:
        runner.test_fail('register access pc', 0x90000010, system.get_register('pc'))

    system.set_register('x5', 0x1FFFFFFFF)
    if system.get_register('t0') != 0xFFFFFFFF:
        runner.test_fail('register access masking', 0xFFFFFFFF, system.get_register('t0'))

    system.set_register('zero', 0xDEADBEEF)
    if system.get_register('x0') != 0:
        runner.test_fail('register access zero immutability', 0, system.get_register('x0'))

    regs = system.get_registers()
    if regs['pc'] != 0x90000010:
        runner.test_fail('register dump pc', 0x90000010, regs['pc'])
    if regs['x0'] != 0:
        runner.test_fail('register dump x0', 0, regs['x0'])


def test_memory_read_write_roundtrip_exposes_ram_to_cpu(runner):
    """RV32System read/write memory helpers must round-trip bytes visible to CPU."""
    system = RV32System()
    base_addr = 0x80005000
    payload_a = b'Memory!'
    payload_b = b'Buffer!'

    system.write_memory(base_addr, payload_a)
    read_back = system.read_memory(base_addr, len(payload_a))
    if read_back != payload_a:
        runner.test_fail('memory read/write roundtrip', payload_a, read_back)

    program = _asm(
        _lui(5, base_addr >> 12),   # t0 = data base (aligned so no addi needed)
        _lui(6, 0x10001),          # t1 = console UART base
        _lbu(7, 5, 0),             # t2 = byte at data base
        _sb(6, 7, 0),              # write byte to console TX
        0x00100073                 # ebreak
    )

    system.load_binary_data(program)
    result = system.run(max_steps=32)
    if result.status != 'halted':
        runner.test_fail('memory read/write run', 'halted status', result.status)

    expected_char = chr(payload_a[0])
    output = system.console_uart_read()
    if output != expected_char:
        runner.test_fail('memory read/write UART output', expected_char, output)

    system.write_memory(base_addr, payload_b)
    read_back_b = system.read_memory(base_addr, len(payload_b))
    if read_back_b != payload_b:
        runner.test_fail('memory rewrite roundtrip', payload_b, read_back_b)

    system.load_binary_data(program)
    result = system.run(max_steps=32)
    if result.status != 'halted':
        runner.test_fail('memory rewrite run', 'halted status', result.status)

    expected_char_b = chr(payload_b[0])
    output_b = system.console_uart_read()
    if output_b != expected_char_b:
        runner.test_fail('memory rewrite UART output', expected_char_b, output_b)


def test_vt100_screen_helpers_capture_tx_output(runner):
    """VT100 helpers should mirror console TX output and allow screen dumps."""
    system = RV32System()

    console_uart = system.memory.console_uart

    if not getattr(console_uart, 'vt100_enabled', False):
        runner.test_fail('vt100 screen helpers', 'VT100 emulation enabled', 'disabled')

    message = 'Hello, VT100!'
    words = [0x100012B7]  # lui t0, 0x10001 -> console UART base
    for char in message + '\n':
        words.append(_addi_t1(ord(char)))
        words.append(0x00628023)  # sb t1, 0(t0)
    words.append(0x00100073)  # ebreak

    system.load_binary_data(_asm(*words))
    result = system.run(max_steps=256)

    if result.status != 'halted':
        runner.test_fail('vt100 screen helpers', 'program halted', result.status)

    screen_lines = console_uart.get_screen_display()
    if not screen_lines:
        runner.test_fail('vt100 screen display', '24 lines of text', screen_lines)

    flattened = ''.join(screen_lines)
    if 'Hello, VT100!' not in flattened:
        runner.test_fail('vt100 screen content', 'Hello, VT100!', screen_lines[0])

    screen_text = console_uart.get_screen_text()
    if 'Hello, VT100!' not in screen_text:
        runner.test_fail('vt100 screen text', 'Hello, VT100!', screen_text)

    dump_text = console_uart.dump_screen(show_cursor=False)
    if 'Hello, VT100!' not in dump_text:
        runner.test_fail('vt100 screen dump', 'Hello, VT100!', dump_text)


def test_mcp_watchpoint_tools_cover_read_and_write(runner):
    """MCP JSON tooling should manage watchpoints and halt when they fire."""
    read_program = _asm(
        _lui(5, READ_WATCH_ADDR >> 12),
        _lbu(6, 5, 0),
        0x00100073
    )
    write_program = _asm(
        _lui(5, WRITE_WATCH_ADDR >> 12),
        _addi_t1(ord('Z')),
        _sb(5, 6, 0),
        0x00100073
    )

    expected_read = f"0x{READ_WATCH_ADDR:08x}"
    expected_write = f"0x{WRITE_WATCH_ADDR:08x}"

    session_id = None
    with tempfile.TemporaryDirectory() as tmp_fs_root:
        server = MCPSimulatorServer()
        try:
            create_text = _call_tool_text(server, 'sim_create', fs_root=tmp_fs_root)
            sessions = server.session_manager.list_sessions()
            if not sessions:
                runner.test_fail('mcp watchpoint sim_create', 'session created', sessions)
            session_id = sessions[0]
            if 'Created session' not in create_text:
                runner.test_fail('mcp watchpoint sim_create text', 'Created session message', create_text)

            _call_tool_text(server, 'sim_add_read_watchpoint', session_id=session_id, address=expected_read)
            _call_tool_text(server, 'sim_add_write_watchpoint', session_id=session_id, address=expected_write)

            list_text = _call_tool_text(server, 'sim_list_watchpoints', session_id=session_id)
            if 'Read watchpoints' not in list_text or 'Write watchpoints' not in list_text:
                runner.test_fail('mcp watchpoint list headings', 'read/write headings present', list_text)
            if expected_read not in list_text:
                runner.test_fail('mcp watchpoint list read entry', expected_read, list_text)
            if expected_write not in list_text:
                runner.test_fail('mcp watchpoint list write entry', expected_write, list_text)

            _write_program_via_tools(server, session_id, read_program)
            run_text = _call_tool_text(server, 'sim_run', session_id=session_id, max_steps=8)
            if 'Read watchpoint' not in run_text or expected_read not in run_text:
                runner.test_fail('mcp read watchpoint halt', f'Read watchpoint at {expected_read}', run_text)

            _call_tool_text(server, 'sim_remove_read_watchpoint', session_id=session_id, address=expected_read)
            list_text = _call_tool_text(server, 'sim_list_watchpoints', session_id=session_id)
            if expected_read in list_text:
                runner.test_fail('mcp watchpoint removal read', f'removed {expected_read}', list_text)
            if expected_write not in list_text:
                runner.test_fail('mcp watchpoint removal write persistence', expected_write, list_text)

            _write_program_via_tools(server, session_id, write_program)
            run_text = _call_tool_text(server, 'sim_run', session_id=session_id, max_steps=8)
            if 'Write watchpoint' not in run_text or expected_write not in run_text:
                runner.test_fail('mcp write watchpoint halt', f'Write watchpoint at {expected_write}', run_text)

            _call_tool_text(server, 'sim_remove_write_watchpoint', session_id=session_id, address=expected_write)
            list_text = _call_tool_text(server, 'sim_list_watchpoints', session_id=session_id)
            if 'No watchpoints set' not in list_text:
                runner.test_fail('mcp watchpoint removal final', 'No watchpoints set', list_text)

        finally:
            if session_id:
                _call_tool_text(server, 'sim_destroy', session_id=session_id)
            server.log_fp.close()