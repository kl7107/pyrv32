# Shared PyRV32 toolchain settings for NetHack builds.
# Include this from other makefiles via:
#   PYRV32_THIS_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
#   include $(PYRV32_THIS_DIR)/toolchain.mk

PREFIX_CROSS ?= riscv64-unknown-elf
CC ?= $(PREFIX_CROSS)-gcc
AR ?= $(PREFIX_CROSS)-ar
SIZE ?= $(PREFIX_CROSS)-size
LINK ?= $(CC)

ARCH_FLAGS ?= -march=rv32im -mabi=ilp32

FIRMWARE_PATH ?= ../../firmware
PLATFORM_INC ?= $(FIRMWARE_PATH)/include
LINKER_SCRIPT ?= $(FIRMWARE_PATH)/link.ld

PICOLIBC_ROOT ?= /usr/lib/picolibc/$(PREFIX_CROSS)
PICOLIBC_INC ?= $(PICOLIBC_ROOT)/include
PICOLIBC_LIB ?= $(PICOLIBC_ROOT)/lib/rv32im/ilp32

CRT0 ?= $(FIRMWARE_PATH)/crt0.o
SYSCALLS ?= $(FIRMWARE_PATH)/syscalls.o
RUNTIME_OBJS ?= $(CRT0) $(SYSCALLS)

PYRV32_COMMON_CFLAGS ?= $(ARCH_FLAGS) -O2 -g -Wall \
	-ffunction-sections -fdata-sections \
	-isystem $(PICOLIBC_INC) \
	-DPYRV32

PYRV32_COMMON_LDFLAGS ?= $(ARCH_FLAGS) \
	-T$(LINKER_SCRIPT) \
	-L$(PICOLIBC_LIB) \
	-Wl,--gc-sections \
	-nostartfiles -nodefaultlibs
