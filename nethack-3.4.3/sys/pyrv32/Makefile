#	NetHack Makefile for PyRV32 (RISC-V RV32IM)
#	Based on sys/unix/Makefile.top

# Cross-compilation setup
PREFIX_CROSS = riscv64-unknown-elf
CC_CROSS = $(PREFIX_CROSS)-gcc
AR_CROSS = $(PREFIX_CROSS)-ar
OBJCOPY_CROSS = $(PREFIX_CROSS)-objcopy
SIZE_CROSS = $(PREFIX_CROSS)-size

# Architecture flags for RV32IM
ARCH_FLAGS = -march=rv32im -mabi=ilp32

# Picolibc paths
PICOLIBC_INC = /usr/lib/picolibc/riscv64-unknown-elf/include
PICOLIBC_LIB = /usr/lib/picolibc/riscv64-unknown-elf/lib/rv32im/ilp32

# Compiler flags
CFLAGS = $(ARCH_FLAGS) -O2 -g -Wall \
	-isystem $(PICOLIBC_INC) \
	-I../include -I../sys/pyrv32

# Linker flags
LDFLAGS = -T../sys/pyrv32/link.ld \
	-L$(PICOLIBC_LIB) \
	-Wl,--gc-sections \
	-nostartfiles -nodefaultlibs

# Libraries
LIBS = -lc -lgcc

# Host tools (run on build machine, not cross-compiled)
CC_HOST = gcc
CFLAGS_HOST = -O2 -I../include

# Game name and locations
GAME = nethack
GAMEDIR = .
VARDIR = .

# Utilities built for host
MAKEDEFS = util/makedefs
LEV_COMP = util/lev_comp
DGN_COMP = util/dgn_comp

# Data files
VARDATD = data oracles options quest.dat rumors
DATHELP = help hh cmdhelp history opthelp wizhelp

# Special levels
SPEC_LEVS = asmodeus.lev baalz.lev castle.lev fakewiz1.lev \
	juiblex.lev knox.lev medusa-1.lev minend-1.lev minefill.lev \
	minetn-1.lev oracle.lev orcus.lev sanctum.lev soko1-1.lev \
	tower1.lev valley.lev wizard1.lev \
	astral.lev air.lev earth.lev fire.lev water.lev

# Quest levels (will be generated)
QUEST_LEVS = Arc-goal.lev Arc-strt.lev

# All data
DAT = $(VARDATD) $(DATHELP) dungeon $(SPEC_LEVS) $(QUEST_LEVS)

# Source files
GAMESRC = ../src
UTILSRC = ../util

# Runtime files for PyRV32
RUNTIME_OBJS = crt0.o syscalls.o

.PHONY: all clean host-tools game-data game install

all: host-tools game-data game
	@echo "Build complete!"
	@$(SIZE_CROSS) src/$(GAME).elf

# Build host utilities first
host-tools: $(MAKEDEFS) $(LEV_COMP) $(DGN_COMP)
	@echo "Host tools built"

# Build data files
game-data: dat/data
	@echo "Game data built"

# Build the game binary
game: src/$(GAME).bin
	@echo "Game binary built"

# Host utility: makedefs
$(MAKEDEFS): $(UTILSRC)/makedefs.c
	@echo "Building makedefs (host)..."
	@mkdir -p util
	$(CC_HOST) $(CFLAGS_HOST) -o $@ $<

# Host utility: lev_comp  
$(LEV_COMP): $(UTILSRC)/lev_comp.c $(UTILSRC)/lev_lex.c $(UTILSRC)/lev_yacc.c
	@echo "Building lev_comp (host)..."
	@mkdir -p util
	$(CC_HOST) $(CFLAGS_HOST) -o $@ $(UTILSRC)/lev_comp.c $(UTILSRC)/lev_lex.c $(UTILSRC)/lev_yacc.c $(UTILSRC)/alloc.c $(UTILSRC)/panic.c

# Host utility: dgn_comp
$(DGN_COMP): $(UTILSRC)/dgn_comp.c $(UTILSRC)/dgn_lex.c $(UTILSRC)/dgn_yacc.c
	@echo "Building dgn_comp (host)..."
	@mkdir -p util
	$(CC_HOST) $(CFLAGS_HOST) -o $@ $(UTILSRC)/dgn_comp.c $(UTILSRC)/dgn_lex.c $(UTILSRC)/dgn_yacc.c $(UTILSRC)/alloc.c $(UTILSRC)/panic.c

# Generate data files
dat/data: $(MAKEDEFS)
	@echo "Generating data files..."
	@mkdir -p dat
	$(MAKEDEFS) -d

# Game binary (delegates to src Makefile)
src/$(GAME).bin: $(RUNTIME_OBJS)
	@echo "Building game..."
	( cd src && $(MAKE) -f Makefile.pyrv32 )

# Runtime objects
crt0.o: ../sys/pyrv32/crt0.S
	$(CC_CROSS) $(ARCH_FLAGS) -c -o $@ $<

syscalls.o: ../sys/pyrv32/syscalls.c
	$(CC_CROSS) $(CFLAGS) -c -o $@ $<

# Install (copy to emulator directory)
install: all
	@echo "Copying to emulator directory..."
	cp src/$(GAME).bin ../../firmware/
	@echo "Install complete. Run: cd ../../ && python3 pyrv32.py firmware/$(GAME).bin"

clean:
	rm -f $(MAKEDEFS) $(LEV_COMP) $(DGN_COMP)
	rm -rf util dat
	rm -f $(RUNTIME_OBJS)
	( cd src && $(MAKE) -f Makefile.pyrv32 clean )
	@echo "Clean complete"

help:
	@echo "NetHack 3.4.3 for PyRV32 - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  make              - Build everything (tools, data, game)"
	@echo "  make host-tools   - Build host utilities only"
	@echo "  make game-data    - Generate game data files"
	@echo "  make game         - Build game binary only"
	@echo "  make install      - Copy binary to emulator"
	@echo "  make clean        - Remove all build artifacts"
	@echo ""
	@echo "Output:"
	@echo "  src/nethack.elf   - ELF binary with debug symbols"
	@echo "  src/nethack.bin   - Raw binary for emulator"
