/*
 * sys/termios.h - Terminal I/O definitions for PyRV32 Platform
 * 
 * Minimal implementation to satisfy NetHack's terminal handling needs.
 * Based on POSIX termios structure but simplified for our UART-based terminal.
 */

#ifndef _SYS_TERMIOS_H
#define _SYS_TERMIOS_H

#include <sys/types.h>

/* Control character array indices */
#define VINTR    0   /* Interrupt character (^C) */
#define VQUIT    1   /* Quit character (^\) */
#define VERASE   2   /* Erase character (backspace) */
#define VKILL    3   /* Kill line character (^U) */
#define VEOF     4   /* End-of-file character (^D) */
#define VTIME    5   /* Time for non-canonical read */
#define VMIN     6   /* Min chars for non-canonical read */
#define VSWTC    7   /* Switch character */
#define VSTART   8   /* Start flow control (^Q) */
#define VSTOP    9   /* Stop flow control (^S) */
#define VSUSP   10   /* Suspend character (^Z) */
#define VEOL    11   /* Additional end-of-line */
#define VREPRINT 12  /* Reprint unread characters */
#define VDISCARD 13  /* Discard pending output */
#define VWERASE 14   /* Word erase */
#define VLNEXT  15   /* Literal next */
#define VEOL2   16   /* Second end-of-line */

#define NCCS    17   /* Number of control characters */

/* Terminal control structure */
typedef unsigned int tcflag_t;
typedef unsigned char cc_t;
typedef unsigned int speed_t;

struct termios {
    tcflag_t c_iflag;   /* Input modes */
    tcflag_t c_oflag;   /* Output modes */
    tcflag_t c_cflag;   /* Control modes */
    tcflag_t c_lflag;   /* Local modes */
    cc_t c_line;        /* Line discipline */
    cc_t c_cc[NCCS];    /* Control characters */
    speed_t c_ispeed;   /* Input speed */
    speed_t c_ospeed;   /* Output speed */
};

/* Input mode flags - c_iflag */
#define IGNBRK  0000001
#define BRKINT  0000002
#define IGNPAR  0000004
#define PARMRK  0000010
#define INPCK   0000020
#define ISTRIP  0000040
#define INLCR   0000100
#define IGNCR   0000200
#define ICRNL   0000400
#define IUCLC   0001000
#define IXON    0002000
#define IXANY   0004000
#define IXOFF   0010000

/* Output mode flags - c_oflag */
#define OPOST   0000001
#define OLCUC   0000002
#define ONLCR   0000004
#define OCRNL   0000010
#define ONOCR   0000020
#define ONLRET  0000040
#define OFILL   0000100
#define OFDEL   0000200

/* Control mode flags - c_cflag */
#define CBAUD   0010017
#define B0      0000000
#define B50     0000001
#define B75     0000002
#define B110    0000003
#define B134    0000004
#define B150    0000005
#define B200    0000006
#define B300    0000007
#define B600    0000010
#define B1200   0000011
#define B1800   0000012
#define B2400   0000013
#define B4800   0000014
#define B9600   0000015
#define B19200  0000016
#define B38400  0000017

#define CSIZE   0000060
#define CS5     0000000
#define CS6     0000020
#define CS7     0000040
#define CS8     0000060
#define CSTOPB  0000100
#define CREAD   0000200
#define PARENB  0000400
#define PARODD  0001000
#define HUPCL   0002000
#define CLOCAL  0004000

/* Local mode flags - c_lflag */
#define ISIG    0000001
#define ICANON  0000002
#define ECHO    0000010
#define ECHOE   0000020
#define ECHOK   0000040
#define ECHONL  0000100
#define NOFLSH  0000200
#define TOSTOP  0000400
#define IEXTEN  0100000

/* tcsetattr() optional actions */
#define TCSANOW   0
#define TCSADRAIN 1
#define TCSAFLUSH 2

/* tcflush() queue selectors */
#define TCIFLUSH  0
#define TCOFLUSH  1
#define TCIOFLUSH 2

/* tcflow() actions */
#define TCOOFF 0
#define TCOON  1
#define TCIOFF 2
#define TCION  3

/* Function declarations - these are stubs, implemented in syscalls.c */
int tcgetattr(int fd, struct termios *termios_p);
int tcsetattr(int fd, int optional_actions, const struct termios *termios_p);
int tcsendbreak(int fd, int duration);
int tcdrain(int fd);
int tcflush(int fd, int queue_selector);
int tcflow(int fd, int action);
speed_t cfgetispeed(const struct termios *termios_p);
speed_t cfgetospeed(const struct termios *termios_p);
int cfsetispeed(struct termios *termios_p, speed_t speed);
int cfsetospeed(struct termios *termios_p, speed_t speed);

#endif /* _SYS_TERMIOS_H */

