/*
 * sys/ioctl.h - Terminal I/O Control for PyRV32 Platform
 * 
 * This header provides OS-level ioctl definitions for the PyRV32 platform.
 * On a real Unix system, this would be provided by the kernel/OS, not the application.
 * 
 * Our implementation provides basic terminal window size support via UART.
 */

#ifndef _SYS_IOCTL_H
#define _SYS_IOCTL_H

/* Terminal window size structure */
struct winsize {
    unsigned short ws_row;    /* rows, in characters */
    unsigned short ws_col;    /* columns, in characters */
    unsigned short ws_xpixel; /* horizontal size, pixels (unused) */
    unsigned short ws_ypixel; /* vertical size, pixels (unused) */
};

/* ioctl request codes - using Linux values for compatibility */
#define TIOCGWINSZ 0x5413  /* Get window size */

/* ioctl function - implemented in syscalls.c */
int ioctl(int fd, unsigned long request, ...);

#endif /* _SYS_IOCTL_H */
