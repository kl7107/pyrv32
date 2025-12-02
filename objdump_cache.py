"""Caching helpers for objdump -d -S output used by MCP disassembly tools."""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable

CACHE_ROOT = Path(os.environ.get("PYRV32_CACHE_DIR", Path.home() / ".cache")) / "pyrv32" / "disasm"
_SYMBOL_RE = re.compile(r"^([0-9a-fA-F]+) <.+>:")
_ADDR_RE = re.compile(r"^\s*([0-9a-fA-F]+):")


class DisasmCache:
    """Materializes and slices objdump output for ELF files."""

    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or CACHE_ROOT
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, elf_path: str) -> str:
        stat = os.stat(elf_path)
        key = f"{elf_path}:{stat.st_size}:{int(stat.st_mtime)}"
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.txt"

    def ensure_cache(self, elf_path: str) -> Path:
        """Return path to cached objdump output, rebuilding if needed."""
        key = self._cache_key(elf_path)
        cache_path = self._cache_path(key)
        if cache_path.exists():
            return cache_path

        with cache_path.open('w') as fp:
            subprocess.run(
                [
                    'riscv64-unknown-elf-objdump',
                    '-d',
                    '-S',
                    elf_path,
                ],
                check=True,
                text=True,
                stdout=fp,
            )
        return cache_path

    def get_range(self, elf_path: str, start_addr: int, end_addr: int) -> str:
        """Return cached disassembly between start/end addresses."""
        if end_addr <= start_addr:
            raise ValueError("end_addr must be greater than start_addr")

        cache_path = self.ensure_cache(elf_path)
        output_lines: list[str] = []
        pending_symbol: str | None = None
        in_range = False

        with cache_path.open('r') as fp:
            for line in fp:
                sym_match = _SYMBOL_RE.match(line)
                if sym_match:
                    pending_symbol = line
                    continue

                addr_match = _ADDR_RE.match(line)
                if addr_match:
                    addr = int(addr_match.group(1), 16)
                    if addr >= end_addr and in_range:
                        break

                    should_include = start_addr <= addr < end_addr
                    if should_include:
                        if pending_symbol is not None:
                            output_lines.append(pending_symbol)
                            pending_symbol = None
                        output_lines.append(line)
                        in_range = True
                    else:
                        in_range = False
                    continue

                if in_range:
                    output_lines.append(line)

        if not output_lines:
            return f"No disassembly for range 0x{start_addr:08x}-0x{end_addr:08x}"
        return ''.join(output_lines)
