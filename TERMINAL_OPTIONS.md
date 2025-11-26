# NetHack Terminal/Display Options

## Overview

NetHack 3.4.3 supports multiple windowing systems, which are completely separate implementations of the display interface. The **TTY** (text terminal) option is the simplest and most portable.

## Available Window Systems

NetHack 3.4.3 includes these window-ports in `win/`:

| Directory | System | Lines of Code | Complexity | Description |
|-----------|--------|---------------|------------|-------------|
| **tty/** | Text Terminal | ~4,548 | ⭐ Low | Character-based terminal (our target) |
| X11/ | X Window System | ~6,000+ | ⭐⭐⭐ High | Unix GUI with tiles |
| Qt/ | Qt Toolkit | ~7,000+ | ⭐⭐⭐⭐ Very High | Cross-platform GUI |
| gnome/ | GNOME | ~5,000+ | ⭐⭐⭐⭐ Very High | Linux desktop integration |
| win32/ | Windows | ~8,000+ | ⭐⭐⭐⭐ Very High | Native Windows GUI |
| gem/ | GEM | ~3,000+ | ⭐⭐⭐ High | Atari TOS GUI |

**For PyRV32: We want TTY only** (simplest, best fit for embedded/terminal)

---

## TTY Terminal Options

The TTY windowing system has **three different terminal interface modes**:

### 1. **TERMLIB** (Traditional Termcap/Terminfo) ⭐ Recommended

**What it is:**
- Uses the system's terminal capability database (`termcap` or `terminfo`)
- Calls library functions: `tgetent()`, `tgetstr()`, `tgetnum()`, `tputs()`
- Dynamically adapts to different terminal types (VT100, xterm, etc.)

**Files:**
- `win/tty/termcap.c` (1,185 lines) - Terminal capability handling
- Links with: `-ltermcap` (BSD) or `-lcurses`/`-lncurses` (Linux)

**Pros:**
- Portable across Unix systems
- Supports any terminal in termcap/terminfo database
- Handles color, cursor movement, screen clearing automatically
- Well-tested, mature code

**Cons:**
- Requires termcap/terminfo database file
- Links against external library (~30-50KB)
- More complex than raw escape codes

**Configuration:**
```c
#define TTY_GRAPHICS     // in include/config.h
#define TERMLIB          // in include/tcap.h (default for Unix)
#define TERMINFO         // Linux uses terminfo instead of termcap
```

---

### 2. **ANSI_DEFAULT** (Raw ANSI Escape Codes) ⭐⭐ Simplest

**What it is:**
- Hardcoded ANSI/VT100 escape sequences
- No external library needed
- Assumes VT100/ANSI compatible terminal

**Files:**
- `win/tty/termcap.c` still used, but in simplified mode
- Escape sequences defined directly in code

**Pros:**
- **No termcap/terminfo library needed**
- **No database file needed**
- Small code size
- Works with any VT100/ANSI terminal
- Perfect for embedded systems

**Cons:**
- Only works with ANSI-compatible terminals
- No automatic terminal detection
- Less flexible than TERMLIB

**Configuration:**
```c
#define TTY_GRAPHICS
#define ANSI_DEFAULT    // in include/pcconf.h or custom config
#undef TERMLIB          // disable termcap library
```

**Escape sequences used:**
```c
// Cursor movement
#define CM "\033[%d;%dH"     // Move cursor to row;col
#define ND "\033[C"          // Move cursor right
#define UP "\033[A"          // Move cursor up
#define CD "\033[J"          // Clear to end of screen
#define CE "\033[K"          // Clear to end of line
#define CL "\033[2J\033[H"   // Clear screen

// Attributes
#define SO "\033[7m"         // Standout (reverse video)
#define SE "\033[0m"         // End standout
#define US "\033[4m"         // Underline start
#define UE "\033[0m"         // Underline end

// Colors (if TEXTCOLOR defined)
#define MD "\033[1m"         // Bold
#define MR "\033[7m"         // Reverse
#define ME "\033[0m"         // Normal
```

---

### 3. **NO_TERMS** (Minimal/Dumb Terminal) ⭐⭐⭐ Simplest

**What it is:**
- No cursor movement, no colors, no fancy features
- Just scrolling text output
- Like playing on a line printer or teletype

**Files:**
- Most of `termcap.c` is `#ifdef`'d out
- Very minimal display code

**Pros:**
- Absolutely minimal code
- No library dependencies
- Works on ANY terminal (even dumb ones)

**Cons:**
- Poor user experience (no screen positioning)
- Hard to play (status line scrolls away)
- Suitable only for debugging or very limited displays

**Configuration:**
```c
#define TTY_GRAPHICS
#define NO_TERMS        // in include/config.h
```

---

## Terminal Libraries Explained

### Termcap vs Terminfo vs Curses

**Termcap (Terminal Capability):**
- Original Unix terminal database (1970s BSD)
- Database file: `/etc/termcap` (text file)
- Library: `libtermcap.so` or built-in to curses
- API: `tgetent()`, `tgetstr()`, `tgetnum()`, `tgoto()`, `tputs()`

**Terminfo (Terminal Information):**
- Modern replacement for termcap (System V Unix)
- Database: `/usr/share/terminfo/` (compiled binary files)
- Library: Part of `libncurses.so` or `libcurses.so`
- API: `setupterm()`, `tigetstr()`, `tparm()`, `tputs()`
- More efficient, more capabilities than termcap

**Curses/Ncurses:**
- **Full screen library** with window management, input handling
- Includes terminfo (Linux) or termcap (BSD) internally
- Much larger API (hundreds of functions)
- NetHack does **NOT** use curses API directly
- NetHack only uses the **termcap/terminfo functions** from curses library

**Important:** NetHack's TTY mode uses termcap/terminfo functions for terminal control, but does NOT use the curses screen management API. It does its own window management in `wintty.c`.

---

## What NetHack Actually Needs

Looking at `win/tty/termcap.c`, NetHack uses these terminal capabilities:

### Required Capabilities:
- **CM** - Cursor movement (position cursor at row, col)
- **CL** - Clear screen
- **CE** - Clear to end of line
- **LI** - Number of lines (screen height)
- **CO** - Number of columns (screen width)

### Optional Capabilities:
- **ND** - Cursor right (non-destructive)
- **UP** - Cursor up
- **CD** - Clear to end of display
- **SO/SE** - Standout mode start/end (reverse video)
- **US/UE** - Underline start/end
- **HI/HE** - Highlight start/end
- **MD/ME** - Bold start/end
- **Color sequences** - If TEXTCOLOR defined

### Input:
- **KS/KE** - Keypad start/end
- Raw keyboard input (read from stdin)

---

## Recommendation for PyRV32

### Option A: ANSI_DEFAULT (Recommended) ⭐⭐⭐

**Best choice for PyRV32 because:**
1. **No external library** - No need to port termcap/terminfo
2. **No database files** - Everything compiled in
3. **Simple, predictable** - Hardcoded VT100 sequences
4. **Small footprint** - Minimal code size
5. **Our Console UART is VT100-compatible** - Perfect match

**Implementation:**
```c
// In config file (sys/pyrv32/pyrv32config.h)
#define TTY_GRAPHICS
#define ANSI_DEFAULT
#undef TERMLIB
#define TEXTCOLOR    // Optional: if we want colors
```

The `termcap.c` file will compile in ANSI mode with hardcoded escape sequences instead of calling termcap library functions.

---

### Option B: Custom Minimal (If ANSI_DEFAULT too complex)

If even `ANSI_DEFAULT` mode in `termcap.c` is too complex, we can:

1. **Write our own minimal `termcap.c` replacement** (~200 lines)
2. **Implement just the functions NetHack needs:**
   ```c
   void tty_startup(int *width, int *height);
   void cmov(int x, int y);          // Move cursor
   void cl_end(void);                // Clear to end of line
   void clear_screen(void);          // Clear screen
   void standout(void);              // Start reverse video
   void standend(void);              // End reverse video
   ```
3. **Hardcode VT100 sequences directly:**
   ```c
   void cmov(int x, int y) {
       printf("\033[%d;%dH", y+1, x+1);
   }
   void clear_screen(void) {
       printf("\033[2J\033[H");
   }
   ```

**Pros:**
- Absolute minimum code (~200 lines vs 1,185)
- Full control, easy to understand
- No surprise dependencies

**Cons:**
- More work to implement
- Need to verify all NetHack's requirements
- Might miss edge cases

---

## Summary Table

| Mode | Complexity | Library | Database | Code Size | Best For |
|------|------------|---------|----------|-----------|----------|
| **TERMLIB** | High | libtermcap/ncurses | termcap/terminfo files | 1,185 lines | Unix systems |
| **ANSI_DEFAULT** | Medium | None | None | ~800 lines | Embedded/VT100 |
| **NO_TERMS** | Low | None | None | ~200 lines | Dumb terminals |
| **Custom** | Low | None | None | ~200 lines | Full control |

---

## Code Locations in NetHack

```
win/tty/
├── termcap.c       1,185 lines - Terminal control (our focus)
├── wintty.c        2,612 lines - Window management
├── getline.c         284 lines - Input handling
└── topl.c            467 lines - Top line messages

Total TTY code: ~4,548 lines
```

**What each file does:**
- `termcap.c` - Low-level terminal I/O (cursor, colors, clear screen)
- `wintty.c` - High-level window management (create/destroy windows, menus)
- `getline.c` - Command line input with editing
- `topl.c` - Top line message handling

---

## Testing Strategy

For PyRV32, test in this order:

1. **Test VT100 sequences directly** (before NetHack):
   ```c
   printf("\033[2J");        // Clear screen
   printf("\033[10;5H");     // Move to row 10, col 5
   printf("Hello");
   printf("\033[7m");        // Reverse video
   printf("HIGHLIGHTED");
   printf("\033[0m");        // Normal
   ```

2. **Build NetHack with ANSI_DEFAULT**
3. **If that works, we're done**
4. **If not, write minimal custom termcap.c**

---

## Next Steps

1. Test Console UART with VT100 escape sequences
2. Create simple test program that uses cursor movement, colors
3. Decide: ANSI_DEFAULT or custom minimal termcap
4. Configure NetHack build with chosen option
5. Cross-compile and test
