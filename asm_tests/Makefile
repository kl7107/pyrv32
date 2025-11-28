# Makefile for pyrv32 assembly tests
#
# Assembles .s files to .bin files using the RISC-V toolchain

# Toolchain
AS = riscv64-unknown-elf-as
OBJCOPY = riscv64-unknown-elf-objcopy
OBJDUMP = riscv64-unknown-elf-objdump

# Flags
ASFLAGS = -march=rv32i -mabi=ilp32
OBJCOPY_FLAGS = -O binary

# Find all .s files recursively
SOURCES = $(shell find . -name '*.s' 2>/dev/null)
BINARIES = $(SOURCES:.s=.bin)
LISTINGS = $(SOURCES:.s=.lst)
ELFS = $(SOURCES:.s=.elf)

.PHONY: all clean list help

# Default target
all: $(BINARIES)

# Pattern rule: .s -> .elf -> .bin
%.elf: %.s
	@echo "AS  $<"
	@$(AS) $(ASFLAGS) $< -o $@

%.bin: %.elf
	@echo "BIN $@"
	@$(OBJCOPY) $(OBJCOPY_FLAGS) $< $@
	@$(OBJDUMP) -d $< > $(@:.bin=.lst)
	@ls -lh $@ | awk '{print "    Size:", $$5}'

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@find . -name '*.bin' -delete
	@find . -name '*.elf' -delete
	@find . -name '*.lst' -delete
	@echo "Clean complete"

# List all tests
list:
	@echo "Available tests:"
	@find . -name '*.s' | sort | sed 's|^\./||'

# Help
help:
	@echo "pyrv32 Assembly Test Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all     - Build all tests (default)"
	@echo "  clean   - Remove all build artifacts"
	@echo "  list    - List all test source files"
	@echo "  help    - Show this help"
	@echo ""
	@echo "Variables:"
	@echo "  AS      = $(AS)"
	@echo "  OBJCOPY = $(OBJCOPY)"
	@echo "  ASFLAGS = $(ASFLAGS)"
	@echo ""
	@echo "Usage:"
	@echo "  make              # Build all tests"
	@echo "  make clean        # Clean build artifacts"
	@echo "  make basic/test_lui.bin  # Build specific test"
