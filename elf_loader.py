"""Shared helpers for loading RISC-V ELF images into simulator memory."""
from __future__ import annotations

import io
from dataclasses import dataclass
from typing import BinaryIO, Dict, List, Tuple, Union

from elftools.elf.elffile import ELFFile


@dataclass
class ElfSegment:
    """Metadata for a single PT_LOAD segment."""
    vaddr: int
    filesz: int
    memsz: int
    flags: int


@dataclass
class ElfLoadResult:
    """Details returned after loading an ELF image."""
    entry_point: int
    bytes_loaded: int
    segments: List[ElfSegment]
    symbols: Dict[str, int]
    reverse_symbols: Dict[int, str]


ElfSource = Union[str, bytes, bytearray, BinaryIO]


def load_elf_image(memory, source: ElfSource, *, require_riscv32: bool = True) -> ElfLoadResult:
    """Load an ELF image from *source* into *memory* and return metadata."""
    elf, stream, should_close = _open_elf(source)
    try:
        _validate_header(elf, require_riscv32)
        entry_point = elf.header['e_entry']
        bytes_loaded = 0
        segments: List[ElfSegment] = []

        for segment in elf.iter_segments():
            if segment['p_type'] != 'PT_LOAD':
                continue
            vaddr = segment['p_vaddr']
            filesz = segment['p_filesz']
            memsz = segment['p_memsz']
            if filesz:
                memory.load_program(vaddr, segment.data())
            if memsz > filesz:
                memory.load_program(vaddr + filesz, bytes(memsz - filesz))
            bytes_loaded += memsz
            segments.append(ElfSegment(vaddr=vaddr, filesz=filesz, memsz=memsz, flags=segment['p_flags']))

        if not segments:
            raise ValueError("ELF file contains no loadable PT_LOAD segments")

        symbols, reverse_symbols = _extract_symbols(elf)
        return ElfLoadResult(
            entry_point=entry_point,
            bytes_loaded=bytes_loaded,
            segments=segments,
            symbols=symbols,
            reverse_symbols=reverse_symbols,
        )
    finally:
        if should_close:
            stream.close()


def _open_elf(source: ElfSource) -> Tuple[ELFFile, BinaryIO, bool]:
    """Return (ELFFile, underlying stream, should_close) for *source*."""
    if isinstance(source, (bytes, bytearray)):
        stream: BinaryIO = io.BytesIO(source)
        return ELFFile(stream), stream, True
    if isinstance(source, str):
        stream = open(source, 'rb')  # noqa: SIM115 - handled by caller
        return ELFFile(stream), stream, True
    if hasattr(source, 'read'):
        return ELFFile(source), source, False
    raise TypeError(f"Unsupported ELF source type: {type(source)!r}")


def _validate_header(elf: ELFFile, require_riscv32: bool) -> None:
    """Validate machine/class constraints for the ELF image."""
    if require_riscv32:
        if elf.header['e_machine'] != 'EM_RISCV':
            raise ValueError(f"Unsupported ELF machine: {elf.header['e_machine']}")
        if elf.elfclass != 32:
            raise ValueError(f"Unsupported ELF class: {elf.elfclass} (expected 32-bit)")


def _extract_symbols(elf: ELFFile) -> Tuple[Dict[str, int], Dict[int, str]]:
    """Return symbol dictionaries with function names preferred for reverse lookups."""
    symtab = elf.get_section_by_name('.symtab')
    if not symtab:
        return {}, {}

    symbols: Dict[str, int] = {}
    reverse: Dict[int, str] = {}

    for symbol in symtab.iter_symbols():
        name = symbol.name
        addr = symbol['st_value']
        if not (name and addr):
            continue
        symbols[name] = addr
        is_function = symbol['st_info']['type'] == 'STT_FUNC'
        if addr not in reverse or is_function:
            reverse[addr] = name

    return symbols, reverse
