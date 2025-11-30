# Makefile for RV32IM firmware examples
# Supports both standalone and libc-linked programs with automatic detection

# Toolchain
PREFIX = riscv64-unknown-elf
CC = $(PREFIX)-gcc
OBJCOPY = $(PREFIX)-objcopy
OBJDUMP = $(PREFIX)-objdump
SIZE = $(PREFIX)-size

# Compiler flags
ARCH_FLAGS = -march=rv32im -mabi=ilp32
OPT_FLAGS = -O2 -g
WARN_FLAGS = -Wall -Wextra

# Picolibc configuration
PICOLIBC_INC = /usr/lib/picolibc/riscv64-unknown-elf/include
PICOLIBC_LIB = /usr/lib/picolibc/riscv64-unknown-elf/lib/rv32im/ilp32
PLATFORM_INC = include

# Base flags
BASE_CFLAGS = $(ARCH_FLAGS) $(OPT_FLAGS) $(WARN_FLAGS) -I$(PLATFORM_INC)

# Flags for standalone programs (no libc)
STANDALONE_CFLAGS = $(BASE_CFLAGS) -nostdlib -nostartfiles -ffreestanding -fno-builtin -fno-stack-protector
STANDALONE_LDFLAGS = -T link.ld -nostdlib -nostartfiles -Wl,--gc-sections

# Flags for libc-linked programs
LIBC_CFLAGS = $(BASE_CFLAGS) -isystem $(PICOLIBC_INC)
LIBC_LDFLAGS = -T link.ld -L$(PICOLIBC_LIB) -Wl,--gc-sections -nostartfiles -nodefaultlibs

# Programs that need libc (auto-detected by name patterns)
LIBC_PROGRAMS = printf_test libc_test clock_test tls_test test_file_syscalls test_fopen test_cwd test_argvenvp test_stdio_streams
STANDALONE_PROGRAMS = hello fibonacci echo_test timer_test bad_pointer bad_store bad_uart_offset interpreter_test test_argv

# Special multi-file programs
DHRYSTONE_SOURCES = dhry_1.c dhry_2.c

# Runtime components
RUNTIME_OBJS = crt0.o runtime.o

.PHONY: all runtime clean list help run
.PRECIOUS: %.elf %.bin %.lst

#==============================================================================
# Default target: build all programs
#==============================================================================
ALL_PROGRAMS = $(STANDALONE_PROGRAMS) $(LIBC_PROGRAMS) dhrystone

all: runtime $(addsuffix .bin,$(STANDALONE_PROGRAMS) $(LIBC_PROGRAMS)) dhrystone.bin
	@echo ""
	@echo "=========================================="
	@echo "✓ All programs built successfully!"
	@echo "=========================================="
	@echo ""
	@echo "Standalone programs:"
	@for prog in $(STANDALONE_PROGRAMS); do \
		size=$$(ls -lh $$prog.bin 2>/dev/null | awk '{print $$5}'); \
		echo "  $$prog.bin ($$size)"; \
	done
	@echo ""
	@echo "Programs with libc:"
	@for prog in $(LIBC_PROGRAMS); do \
		size=$$(ls -lh $$prog.bin 2>/dev/null | awk '{print $$5}'); \
		echo "  $$prog.bin ($$size)"; \
	done
	@echo ""
	@echo "Benchmarks:"
	@size=$$(ls -lh dhrystone.bin 2>/dev/null | awk '{print $$5}'); \
	echo "  dhrystone.bin ($$size)"
	@echo ""

#==============================================================================
# Runtime components (for NetHack and other external builds)
#==============================================================================
runtime: crt0.o runtime.o syscalls.o

crt0.o: crt0.S
	@echo "Building crt0.o..."
	$(CC) $(ARCH_FLAGS) -c -o $@ $<

runtime.o: runtime.c
	@echo "Building runtime.o..."
	$(CC) $(STANDALONE_CFLAGS) -c -o $@ $<

syscalls.o: syscalls.c
	@echo "Building syscalls.o..."
	$(CC) $(LIBC_CFLAGS) -c -o $@ $<

#==============================================================================
# Pattern rules for standalone programs
#==============================================================================
$(STANDALONE_PROGRAMS): %: %.bin
	@echo ""
	@echo "✓ Build complete: $@.bin"
	@$(SIZE) $@.elf

%.elf: %.c crt0.o runtime.o link.ld
	@echo "Linking $@ (standalone)..."
	$(CC) $(STANDALONE_CFLAGS) $(STANDALONE_LDFLAGS) -Wl,-Map=$*.map \
		crt0.o runtime.o $< -o $@

#==============================================================================
# Pattern rules for libc programs
#==============================================================================
$(LIBC_PROGRAMS): %: %.bin
	@echo ""
	@echo "✓ Build complete: $@.bin"
	@$(SIZE) $@.elf

$(foreach prog,$(LIBC_PROGRAMS),$(prog).elf): %.elf: %.c crt0.o runtime.o syscalls.o link.ld
	@echo "Linking $@ (with libc)..."
	$(CC) $(LIBC_CFLAGS) $(LIBC_LDFLAGS) -Wl,-Map=$*.map \
		crt0.o runtime.o syscalls.o $< -o $@ -lc -lgcc

#==============================================================================
# Special programs
#==============================================================================
dhrystone: dhrystone.bin
	@echo ""
	@echo "✓ Dhrystone benchmark complete"
	@$(SIZE) dhrystone.elf

dhrystone.elf: $(DHRYSTONE_SOURCES) crt0.o runtime.o link.ld
	@echo "Linking dhrystone.elf (standalone)..."
	$(CC) $(STANDALONE_CFLAGS) $(STANDALONE_LDFLAGS) -Wl,-Map=dhrystone.map \
		crt0.o runtime.o $(DHRYSTONE_SOURCES) -o $@

#==============================================================================
# Generic binary generation and disassembly
#==============================================================================
%.bin: %.elf
	@echo "Creating binary: $@"
	$(OBJCOPY) -O binary $< $@

%.lst: %.elf
	@echo "Generating disassembly: $@"
	$(OBJDUMP) -d -S $< > $@

#==============================================================================
# Utility targets
#==============================================================================
list:
	@echo "Available programs:"
	@echo ""
	@echo "Standalone (no libc):"
	@for prog in $(STANDALONE_PROGRAMS); do echo "  make $$prog"; done
	@echo ""
	@echo "With libc:"
	@for prog in $(LIBC_PROGRAMS); do echo "  make $$prog"; done
	@echo ""
	@echo "Special:"
	@echo "  make dhrystone"
	@echo ""
	@echo "Run any program:"
	@echo "  make run PROG=<name>"

run:
ifndef PROG
	@echo "Usage: make run PROG=<program>"
	@echo "Example: make run PROG=hello"
else
	@$(MAKE) --no-print-directory $(PROG)
	@echo ""
	@echo "Running $(PROG)..."
	@echo "========================================"
	cd .. && ./pyrv32.py firmware/$(PROG).bin
endif

clean:
	@echo "Cleaning build artifacts..."
	rm -f *.elf *.bin *.lst *.map *.o

help:
	@echo "RV32IM Firmware Build System"
	@echo "============================="
	@echo ""
	@echo "Quick start:"
	@echo "  make              - Build all programs"
	@echo "  make runtime      - Build only runtime components (crt0.o, runtime.o, syscalls.o)"
	@echo "  make list         - Show all available programs"
	@echo "  make hello        - Build specific program"
	@echo "  make run PROG=hello - Build and run a program"
	@echo "  make clean        - Remove all build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make printf_test  - Build printf test (auto-links with libc)"
	@echo "  make fibonacci    - Build fibonacci (standalone)"
	@echo "  make dhrystone    - Build Dhrystone benchmark"
	@echo ""
	@echo "The Makefile automatically detects which programs need libc."
