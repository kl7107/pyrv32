# Makefile for RV32IM firmware examples

# Toolchain configuration
PREFIX = riscv64-unknown-elf
CC = $(PREFIX)-gcc
OBJCOPY = $(PREFIX)-objcopy
OBJDUMP = $(PREFIX)-objdump
SIZE = $(PREFIX)-size

# Compiler flags
ARCH_FLAGS = -march=rv32im -mabi=ilp32
OPT_FLAGS = -O2 -g
WARN_FLAGS = -Wall -Wextra

# Picolibc paths (smaller, modern embedded libc)
PICOLIBC_INC = /usr/lib/picolibc/riscv64-unknown-elf/include
PICOLIBC_LIB = /usr/lib/picolibc/riscv64-unknown-elf/lib/rv32im/ilp32

# Flags for programs using picolibc
NEWLIB_CFLAGS = $(ARCH_FLAGS) $(OPT_FLAGS) $(WARN_FLAGS) -isystem $(PICOLIBC_INC)
NEWLIB_LDFLAGS = -T link.ld -L$(PICOLIBC_LIB) -Wl,--gc-sections -nostartfiles -nodefaultlibs

# Flags for standalone programs (no libc)
STANDALONE_FLAGS = -nostdlib -nostartfiles -ffreestanding -fno-builtin -fno-stack-protector

CFLAGS = $(ARCH_FLAGS) $(OPT_FLAGS) $(WARN_FLAGS) $(STANDALONE_FLAGS)

# Linker flags
LDFLAGS = -T link.ld -nostdlib -nostartfiles -Wl,--gc-sections

# Default program
PROGRAM = hello
SOURCES = crt0.S runtime.c $(PROGRAM).c

# Dhrystone benchmark
DHRYSTONE_SOURCES = crt0.S runtime.c dhry_1.c dhry_2.c

# Output files
ELF = $(PROGRAM).elf
BIN = $(PROGRAM).bin
LST = $(PROGRAM).lst
MAP = $(PROGRAM).map

.PHONY: all clean run run-verbose disasm size syscalls.o crt0.o

# Object files for external use (tests, etc)
syscalls.o: syscalls.c
	$(CC) $(NEWLIB_CFLAGS) -c -o $@ $<

crt0.o: crt0.S
	$(CC) $(ARCH_FLAGS) -c -o $@ $<

all: $(BIN) $(LST)
	@echo ""
	@echo "✓ Build complete: $(BIN)"
	@$(SIZE) $(ELF)

$(ELF): $(SOURCES) link.ld
	@echo "Building $(PROGRAM)..."
	$(CC) $(CFLAGS) $(LDFLAGS) -Wl,-Map=$(MAP) $(SOURCES) -o $@

$(BIN): $(ELF)
	$(OBJCOPY) -O binary $< $@

$(LST): $(ELF)
	$(OBJDUMP) -d -S $< > $@

size: $(ELF)
	$(SIZE) $(ELF)
	@echo ""
	@ls -lh $(BIN) | awk '{print "Binary size:", $$5}'

disasm: $(LST)
	less $(LST)

run: $(BIN)
	cd .. && ./pyrv32.py --no-test firmware/$(BIN)

run-verbose: $(BIN)
	cd .. && ./pyrv32.py --no-test -v firmware/$(BIN)

clean:
	rm -f *.elf *.bin *.lst *.map *.o

help:
	@echo "RV32IM Firmware Build System"
	@echo ""
	@echo "Targets:"
	@echo "  make              - Build firmware (default)"
	@echo "  make run          - Build and run on emulator"
	@echo "  make run-verbose  - Build and run with instruction trace"
	@echo "  make size         - Show size information"
	@echo "  make disasm       - View disassembly"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make dhrystone    - Build and run Dhrystone benchmark"
	@echo "  make printf_test  - Build and run printf/newlib test"
	@echo ""
	@echo "To build a different program:"
	@echo "  make PROGRAM=myprogram"
	@echo "  make PROGRAM=myprogram run"

# Dhrystone benchmark
dhrystone:
	@$(MAKE) clean
	$(CC) $(CFLAGS) $(LDFLAGS) -Wl,-Map=dhrystone.map $(DHRYSTONE_SOURCES) -o dhrystone.elf
	$(OBJCOPY) -O binary dhrystone.elf dhrystone.bin
	$(OBJDUMP) -d -S dhrystone.elf > dhrystone.lst
	@echo ""
	@echo "✓ Dhrystone build complete"
	@$(SIZE) dhrystone.elf
	@echo ""
	@echo "Running Dhrystone benchmark..."
	@echo ""
	cd .. && ./pyrv32.py --no-test firmware/dhrystone.bin

# Printf test with picolibc
printf_test:
	@$(MAKE) clean
	$(CC) $(NEWLIB_CFLAGS) $(NEWLIB_LDFLAGS) -Wl,-Map=printf_test.map \
		crt0.S runtime.c syscalls.c printf_test.c -lc -lgcc -o printf_test.elf
	$(OBJCOPY) -O binary printf_test.elf printf_test.bin
	$(OBJDUMP) -d -S printf_test.elf > printf_test.lst
	@echo ""
	@echo "✓ Printf test build complete"
	@$(SIZE) printf_test.elf
	@echo ""
	@echo "Running printf test..."
	@echo ""
	cd .. && python3 pyrv32.py firmware/printf_test.bin

# Comprehensive libc test for NetHack requirements
libc_test:
	@$(MAKE) clean
	$(CC) $(NEWLIB_CFLAGS) $(NEWLIB_LDFLAGS) -Wl,-Map=libc_test.map \
		crt0.S runtime.c syscalls.c libc_test.c -lc -lgcc -o libc_test.elf
	$(OBJCOPY) -O binary libc_test.elf libc_test.bin
	$(OBJDUMP) -d -S libc_test.elf > libc_test.lst
	@echo ""
	@echo "✓ libc test build complete"
	@$(SIZE) libc_test.elf
	@echo ""
	@echo "Running libc test..."
	@echo ""
	cd .. && python3 pyrv32.py firmware/libc_test.bin

# Quick qsort debug test
qsort_test:
	@$(MAKE) clean
	$(CC) $(NEWLIB_CFLAGS) $(NEWLIB_LDFLAGS) -Wl,-Map=qsort_test.map \
		crt0.S runtime.c syscalls.c qsort_test.c -lc -lgcc -o qsort_test.elf
	$(OBJCOPY) -O binary qsort_test.elf qsort_test.bin
	$(OBJDUMP) -d -S qsort_test.elf > qsort_test.lst
	@echo ""
	@echo "✓ qsort test build complete"
	@$(SIZE) qsort_test.elf
	@echo ""
	@echo "Running qsort test..."
	@echo ""
	cd .. && python3 pyrv32.py firmware/qsort_test.bin

# rand/srand TLS investigation
rand_test:
	@$(MAKE) clean
	$(CC) $(NEWLIB_CFLAGS) $(NEWLIB_LDFLAGS) -Wl,-Map=rand_test.map \
		crt0.S runtime.c syscalls.c rand_test.c -lc -lgcc -o rand_test.elf
	$(OBJCOPY) -O binary rand_test.elf rand_test.bin
	$(OBJDUMP) -d -S rand_test.elf > rand_test.lst
	@echo ""
	@echo "✓ rand test build complete"
	@$(SIZE) rand_test.elf
	@echo ""
	@echo "Running rand test..."
	@echo ""
	cd .. && python3 pyrv32.py firmware/rand_test.bin

# Comprehensive TLS test
tls_test:
	@$(MAKE) clean
	$(CC) $(NEWLIB_CFLAGS) $(NEWLIB_LDFLAGS) -Wl,-Map=tls_test.map \
		crt0.S runtime.c syscalls.c tls_test.c -lc -lgcc -o tls_test.elf
	$(OBJCOPY) -O binary tls_test.elf tls_test.bin
	$(OBJDUMP) -d -S tls_test.elf > tls_test.lst
	@echo ""
	@echo "✓ TLS test build complete"
	@$(SIZE) tls_test.elf
	@echo ""
	@echo "Running TLS test..."
	@echo ""
	cd .. && python3 pyrv32.py firmware/tls_test.bin

# Real-time clock test
clock_test:
	@$(MAKE) clean
	$(CC) $(NEWLIB_CFLAGS) $(NEWLIB_LDFLAGS) -Wl,-Map=clock_test.map \
		crt0.S runtime.c syscalls.c clock_test.c -lc -lgcc -o clock_test.elf
	$(OBJCOPY) -O binary clock_test.elf clock_test.bin
	$(OBJDUMP) -d -S clock_test.elf > clock_test.lst
	@echo ""
	@echo "✓ Clock test build complete"
	@$(SIZE) clock_test.elf
	@echo ""
	@echo "Running clock test..."
	@echo ""
	cd .. && python3 pyrv32.py firmware/clock_test.bin
