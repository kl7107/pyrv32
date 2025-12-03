"""Regression tests covering MCP-specific simulator behaviors."""

import importlib.util
import os
import struct
import tempfile

from pyrv32_system import RV32System

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRMWARE_DIR = os.path.join(REPO_ROOT, 'firmware')
HELLO_ELF = os.path.join(FIRMWARE_DIR, 'hello.elf')

SESSION_MANAGER_SPEC = importlib.util.spec_from_file_location(
    'session_manager_for_tests',
    os.path.join(REPO_ROOT, 'pyrv32_mcp', 'session_manager.py')
)
if SESSION_MANAGER_SPEC is None or SESSION_MANAGER_SPEC.loader is None:
    raise ImportError('Unable to load SessionManager spec for tests')
SESSION_MANAGER_MODULE = importlib.util.module_from_spec(SESSION_MANAGER_SPEC)
SESSION_MANAGER_SPEC.loader.exec_module(SESSION_MANAGER_MODULE)
SessionManager = SESSION_MANAGER_MODULE.SessionManager


def _asm(*words):
    """Pack 32-bit instruction words into little-endian bytes."""
    return b"".join(struct.pack('<I', word) for word in words)


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