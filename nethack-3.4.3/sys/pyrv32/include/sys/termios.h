/*
 * Minimal termios stub for PyRV32 NetHack port
 * 
 * Since we're using ANSI_DEFAULT mode (hardcoded VT100 sequences),
 * we don't need real terminal control. These are just stubs to satisfy
 * compilation requirements.
 */

#ifndef _SYS_TERMIOS_H_
#define _SYS_TERMIOS_H_

#include <sys/types.h>

/* Terminal control flags */
typedef unsigned int tcflag_t;
typedef unsigned char cc_t;
typedef unsigned int speed_t;

#define NCCS 20

/* Terminal I/O structure */
struct termios {
    tcflag_t c_iflag;   /* Input flags */
    tcflag_t c_oflag;   /* Output flags */
    tcflag_t c_cflag;   /* Control flags */
    tcflag_t c_lflag;   /* Local flags */
    cc_t c_cc[NCCS];    /* Control characters */
    speed_t c_ispeed;   /* Input speed */
    speed_t c_ospeed;   /* Output speed */
};

/* c_iflag bits */
#define IGNBRK  0x00000001
#define BRKINT  0x00000002
#define IGNPAR  0x00000004
#define PARMRK  0x00000008
#define INPCK   0x00000010
#define ISTRIP  0x00000020
#define INLCR   0x00000040
#define IGNCR   0x00000080
#define ICRNL   0x00000100
#define IXON    0x00000200
#define IXOFF   0x00000400

/* c_oflag bits */
#define OPOST   0x00000001
#define ONLCR   0x00000002
#define OCRNL   0x00000004
#define ONOCR   0x00000008
#define ONLRET  0x00000010

/* c_cflag bits */
#define CSIZE   0x00000030
#define CS5     0x00000000
#define CS6     0x00000010
#define CS7     0x00000020
#define CS8     0x00000030
#define CSTOPB  0x00000040
#define CREAD   0x00000080
#define PARENB  0x00000100
#define PARODD  0x00000200
#define HUPCL   0x00000400
#define CLOCAL  0x00000800

/* c_lflag bits */
#define ISIG    0x00000001
#define ICANON  0x00000002
#define ECHO    0x00000008
#define ECHOE   0x00000010
#define ECHOK   0x00000020
#define ECHONL  0x00000040
#define NOFLSH  0x00000080
#define TOSTOP  0x00000100
#define IEXTEN  0x00008000

/* c_cc characters */
#define VINTR    0
#define VQUIT    1
#define VERASE   2
#define VKILL    3
#define VEOF     4
#define VTIME    5
#define VMIN     6
#define VSWTC    7
#define VSTART   8
#define VSTOP    9
#define VSUSP   10
#define VEOL    11
#define VREPRINT 12
#define VDISCARD 13
#define VWERASE 14
#define VLNEXT  15
#define VEOL2   16

/* tcsetattr() optional actions */
#define TCSANOW   0
#define TCSADRAIN 1
#define TCSAFLUSH 2

/* tcflush() queue selector */
#define TCIFLUSH  0
#define TCOFLUSH  1
#define TCIOFLUSH 2

/* tcflow() action */
#define TCOOFF 0
#define TCOON  1
#define TCIOFF 2
#define TCION  3

/* Baud rates */
#define B0      0
#define B50     1
#define B75     2
#define B110    3
#define B134    4
#define B150    5
#define B200    6
#define B300    7
#define B600    8
#define B1200   9
#define B1800  10
#define B2400  11
#define B4800  12
#define B9600  13
#define B19200 14
#define B38400 15

/* Function prototypes - all are stubs for ANSI_DEFAULT mode */

/* Get terminal attributes (stub - returns success, does nothing) */
static inline int tcgetattr(int fd, struct termios *termios_p) {
    (void)fd;
    (void)termios_p;
    return 0;  /* Success */
}

/* Set terminal attributes (stub - returns success, does nothing) */
static inline int tcsetattr(int fd, int optional_actions,
                            const struct termios *termios_p) {
    (void)fd;
    (void)optional_actions;
    (void)termios_p;
    return 0;  /* Success */
}

/* Send break (stub) */
static inline int tcsendbreak(int fd, int duration) {
    (void)fd;
    (void)duration;
    return 0;
}

/* Drain output (stub) */
static inline int tcdrain(int fd) {
    (void)fd;
    return 0;
}

/* Flush I/O (stub) */
static inline int tcflush(int fd, int queue_selector) {
    (void)fd;
    (void)queue_selector;
    return 0;
}

/* Flow control (stub) */
static inline int tcflow(int fd, int action) {
    (void)fd;
    (void)action;
    return 0;
}

/* Get input speed (stub) */
static inline speed_t cfgetispeed(const struct termios *termios_p) {
    (void)termios_p;
    return B9600;  /* Default baud rate */
}

/* Get output speed (stub) */
static inline speed_t cfgetospeed(const struct termios *termios_p) {
    (void)termios_p;
    return B9600;  /* Default baud rate */
}

/* Set input speed (stub) */
static inline int cfsetispeed(struct termios *termios_p, speed_t speed) {
    (void)termios_p;
    (void)speed;
    return 0;
}

/* Set output speed (stub) */
static inline int cfsetospeed(struct termios *termios_p, speed_t speed) {
    (void)termios_p;
    (void)speed;
    return 0;
}

#endif /* _SYS_TERMIOS_H_ */
