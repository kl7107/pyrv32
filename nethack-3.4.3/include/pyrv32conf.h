/*	pyrv32conf.h - Configuration for PyRV32 (RISC-V RV32IM emulator) */
/* Copyright (c) 2024. NetHack may be freely redistributed. See license for details. */

#ifndef PYRV32CONF_H
#define PYRV32CONF_H

/*
 * PyRV32 System Configuration
 * 
 * Target: RV32IM RISC-V emulator with 8MB RAM
 * libc: Picolibc 1.8.6-2
 * Terminal: ANSI terminal via UART
 * System: Minimal UNIX-like environment
 */

/* Define as Unix-like system */
#define UNIX

/* Use POSIX types (picolibc provides these) */
#define POSIX_TYPES

/* Include ioctl support early to define TIOCGWINSZ */
#include <sys/ioctl.h>

/* Window system - TTY only with ANSI terminal */
#define TTY_GRAPHICS
#define DEFAULT_WINDOW_SYS "tty"

/* Terminal handling - use ANSI_DEFAULT (no termcap library) */
#define ANSI_DEFAULT
/* Note: tcap.h will define TERMLIB, but we undefine it in hack.h patch */

/* Enable text colors (VT100 supports this) */
#define TEXTCOLOR

/* Disable features that need file I/O (Phase 1) */
#undef INSURANCE        /* No checkpoint/restore */
#undef NEWS            /* No news file */
#undef MAIL            /* No mail daemon */
#undef LOGFILE         /* No game logging */
#undef XLOGFILE        /* No extended logging */

/* Disable complex features */
#undef WIZARD          /* No wizard mode */
#undef EXPLORE_MODE    /* No explore mode */

/* Disable features requiring external programs */
#undef COMPRESS        /* No save file compression */
#undef COMPRESS_EXTENSION
#undef DEF_PAGER       /* No external pager */
#undef SHELL           /* No shell escape */

/* Enable core gameplay features */
#define AUTOPICKUP_EXCEPTIONS
#define GOLDOBJ        /* Gold as object */

/* Memory configuration for 8MB system */
#define CLIPPING       /* Viewport clipping (saves memory) */

/* System characteristics */
#define NETWORK        /* For network byte order functions (we have them in libc) */

/* File paths - minimal, mostly unused in Phase 1 */
#ifndef HACKDIR
#define HACKDIR "/nethack"
#endif

/* Compiler/platform specifics */
#define POSIX_TYPES    /* Use POSIX standard types */

/* Character set */
#define ASCIIGRAPH     /* Use ASCII for graphics (with ANSI_DEFAULT) */

/* Disable sound (no hardware support) */
#undef USER_SOUNDS

/* Disable tiles (TTY text only) */
#undef USE_TILES

/* Miscellaneous */
#define FCMASK 0660    /* file creation mask */

/* Floating point - RV32IM has no FPU, but NetHack uses integer math anyway */
/* No special defines needed */

/* Do NOT include unixconf.h here - it will be included by global.h */

#endif /* PYRV32CONF_H */
