/*	pyrv32conf.h - Configuration for PyRV32 (RISC-V RV32IM emulator) */
/* Copyright (c) 2024. NetHack may be freely redistributed. See license for details. */

#ifndef PYRV32CONF_H
#define PYRV32CONF_H

/*
 * PyRV32 System Configuration
 * 
 * Target: RV32IM RISC-V emulator with 8MB RAM
 * libc: Picolibc 1.8.6-2
 * Terminal: ANSI_DEFAULT (hardcoded VT100 escape sequences)
 * Features: Minimal - TTY only, no save/load for now
 */

/* Define as Unix-like system */
#define UNIX

/* Prevent NetHack from redeclaring standard functions that picolibc provides */
#define _POSIX_SOURCE
#define POSIX_TYPES

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

/* Include base Unix configuration */
#include "unixconf.h"

/*
 * Override Unix defaults for minimal bare-metal build
 * These #undefs MUST come AFTER unixconf.h is included
 */

/* Disable MAIL completely - requires getpwuid, stat, etc. */
#ifdef MAIL
#undef MAIL
#endif
#ifdef DEF_MAILREADER
#undef DEF_MAILREADER
#endif
#ifdef MAILCKFREQ
#undef MAILCKFREQ
#endif

/* Disable SHELL - requires fork, exec */
#ifdef SHELL
#undef SHELL
#endif

/* Disable pager - requires fork, exec */
#ifdef DEF_PAGER
#undef DEF_PAGER
#endif

/* Disable user authentication - no password database */
#ifdef USER_SOUNDS
#undef USER_SOUNDS
#endif

/* Disable file-based features */
#ifdef SELECTSAVED
#undef SELECTSAVED  /* No saved game selection - requires stat, directory functions */
#endif

#ifdef SYSCF
#undef SYSCF  /* No system configuration file */
#endif

#ifdef PANICLOG
#undef PANICLOG  /* No panic log file */
#endif

/* Disable score file - requires file locking */
#ifdef RECORD
#undef RECORD
#endif

#ifdef SCORE_ON_BOTL
#undef SCORE_ON_BOTL
#endif

/* Simplify terminal handling - use minimal termios stubs */
#ifdef TIMED_DELAY
#undef TIMED_DELAY  /* No precise timing */
#endif

#endif /* PYRV32CONF_H */
