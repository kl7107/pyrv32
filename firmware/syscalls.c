/*
 * Newlib Syscall Stubs for PyRV32 Bare-Metal
 * 
 * Provides minimal syscall implementations for newlib/picolibc.
 * These are NOT OS system calls - just glue functions that newlib expects.
 * 
 * Memory Map:
 *   0x10000000 - Debug UART TX (for diagnostics/stderr)
 *   0x10000004 - Timer (milliseconds since program start)
 *   0x10000008 - Unix time (seconds since epoch, read-only)
 *   0x1000000C - Nanoseconds within current second (0-999999999, read-only)
 *   0x10001000 - Console UART TX (for stdout)
 *   0x10001004 - Console UART RX (for stdin)
 *   0x10001008 - Console UART RX Status
 */

#include <sys/stat.h>
#include <sys/times.h>
#include <sys/time.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <stdarg.h>
#include <errno.h>
#include <stdio.h>
#include <stdio-bufio.h>
#include <fcntl.h>
#include <unistd.h>

/* Linux RV32 syscall numbers */
#define SYS_GETCWD      17
#define SYS_UNLINKAT    35
#define SYS_LINKAT      37
#define SYS_RENAMEAT    38
#define SYS_FACCESSAT   48
#define SYS_CHDIR       49
#define SYS_OPENAT      56
#define SYS_CLOSE       57
#define SYS_LSEEK       62
#define SYS_READ        63
#define SYS_WRITE       64
#define SYS_FSTATAT     79
#define SYS_FSTAT       80
#define SYS_EXIT        93

/* ECALL syscall wrappers - invoke Python syscall handler */
static inline long syscall1(long n, long arg0) {
    register long a7 asm("a7") = n;
    register long a0 asm("a0") = arg0;
    asm volatile ("ecall" : "+r"(a0) : "r"(a7) : "memory");
    return a0;
}

static inline long syscall2(long n, long arg0, long arg1) {
    register long a7 asm("a7") = n;
    register long a0 asm("a0") = arg0;
    register long a1 asm("a1") = arg1;
    asm volatile ("ecall" : "+r"(a0) : "r"(a7), "r"(a1) : "memory");
    return a0;
}

static inline long syscall3(long n, long arg0, long arg1, long arg2) {
    register long a7 asm("a7") = n;
    register long a0 asm("a0") = arg0;
    register long a1 asm("a1") = arg1;
    register long a2 asm("a2") = arg2;
    asm volatile ("ecall" : "+r"(a0) : "r"(a7), "r"(a1), "r"(a2) : "memory");
    return a0;
}

static inline long syscall4(long n, long arg0, long arg1, long arg2, long arg3) {
    register long a7 asm("a7") = n;
    register long a0 asm("a0") = arg0;
    register long a1 asm("a1") = arg1;
    register long a2 asm("a2") = arg2;
    register long a3 asm("a3") = arg3;
    asm volatile ("ecall" : "+r"(a0) : "r"(a7), "r"(a1), "r"(a2), "r"(a3) : "memory");
    return a0;
}

static inline long syscall5(long n, long arg0, long arg1, long arg2, long arg3, long arg4) {
    register long a7 asm("a7") = n;
    register long a0 asm("a0") = arg0;
    register long a1 asm("a1") = arg1;
    register long a2 asm("a2") = arg2;
    register long a3 asm("a3") = arg3;
    register long a4 asm("a4") = arg4;
    asm volatile ("ecall" : "+r"(a0) : "r"(a7), "r"(a1), "r"(a2), "r"(a3), "r"(a4) : "memory");
    return a0;
}

/* Forward declaration for struct passwd */
struct passwd {
    char *pw_name;
    char *pw_passwd;
    uid_t pw_uid;
    gid_t pw_gid;
    char *pw_gecos;
    char *pw_dir;
    char *pw_shell;
};

/* UART addresses */
#define DEBUG_UART_TX    ((volatile unsigned char *)0x10000000)
#define CONSOLE_UART_TX  ((volatile unsigned char *)0x10001000)
#define CONSOLE_UART_RX  ((volatile unsigned char *)0x10001004)
#define CONSOLE_UART_RX_STATUS ((volatile unsigned char *)0x10001008)

/* Timer and clock */
#define TIMER_MS         ((volatile unsigned int *)0x10000004)
#define CLOCK_TIME       ((volatile unsigned int *)0x10000008)
#define CLOCK_NSEC       ((volatile unsigned int *)0x1000000C)

/* File descriptor routing */
#define STDIN_FILENO  0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2

/* Buffered I/O implementations for stdin/stdout/stderr */

/* Read from stdin (Console UART RX) - Non-blocking after first byte */
static ssize_t stdin_read(int fd, void *buf, size_t count) {
    (void)fd;
    unsigned char *ptr = buf;
    size_t i;
    
    if (count == 0) {
        return 0;
    }
    
    /* Block waiting for first byte (ensures we don't return 0 immediately) */
    while ((*CONSOLE_UART_RX_STATUS & 0x01) == 0) {
        /* Wait for first byte */
    }
    ptr[0] = *CONSOLE_UART_RX;
    
    /* Read remaining bytes non-blocking (return partial read if no more data) */
    for (i = 1; i < count; i++) {
        /* Check if more data available */
        if ((*CONSOLE_UART_RX_STATUS & 0x01) == 0) {
            /* No more data - return what we got */
            return i;
        }
        ptr[i] = *CONSOLE_UART_RX;
    }
    
    return count;
}

/* Write to stdout (Console UART TX) */
static ssize_t stdout_write(int fd, const void *buf, size_t count) {
    (void)fd;
    const unsigned char *ptr = buf;
    size_t i;
    
    for (i = 0; i < count; i++) {
        *CONSOLE_UART_TX = ptr[i];
    }
    return count;
}

/* Write to stderr (Debug UART TX) */
static ssize_t stderr_write(int fd, const void *buf, size_t count) {
    (void)fd;
    const unsigned char *ptr = buf;
    size_t i;
    
    for (i = 0; i < count; i++) {
        *DEBUG_UART_TX = ptr[i];
    }
    return count;
}

/* No-op lseek for stdio streams */
static __off_t stdio_lseek(int fd, __off_t offset, int whence) {
    (void)fd; (void)offset; (void)whence;
    errno = ESPIPE;  /* Illegal seek on stream */
    return -1;
}

/* No-op close for stdio streams (never close stdin/stdout/stderr) */
static int stdio_close(int fd) {
    (void)fd;
    return 0;  /* Success, but don't actually close */
}

/* Buffers for stdio streams */
static char stdin_buf[BUFSIZ];
static char stdout_buf[BUFSIZ];
static char stderr_buf[BUFSIZ];

/* Buffered FILE structures for stdin/stdout/stderr */
static struct __file_bufio __stdin_bufio = FDEV_SETUP_BUFIO(
    STDIN_FILENO,
    stdin_buf,
    BUFSIZ,
    stdin_read,
    NULL,  /* no write */
    stdio_lseek,
    stdio_close,
    __SRD,
    0  /* no special buffer flags */
);

static struct __file_bufio __stdout_bufio = FDEV_SETUP_BUFIO(
    STDOUT_FILENO,
    stdout_buf,
    BUFSIZ,
    NULL,  /* no read */
    stdout_write,
    stdio_lseek,
    stdio_close,
    __SWR,
    __BLBF  /* line buffered */
);

static struct __file_bufio __stderr_bufio = FDEV_SETUP_BUFIO(
    STDERR_FILENO,
    stderr_buf,
    BUFSIZ,
    NULL,  /* no read */
    stderr_write,
    stdio_lseek,
    stdio_close,
    __SWR,
    0  /* unbuffered */
);

/* Export FILE pointers for picolibc */
FILE *const stdin = (FILE *)&__stdin_bufio;
FILE *const stdout = (FILE *)&__stdout_bufio;
FILE *const stderr = (FILE *)&__stderr_bufio;

/*
 * Forward declarations
 */
int _write(int fd, char *ptr, int len);
int _read(int fd, char *ptr, int len);

/*
 * write - Write to a file descriptor (picolibc interface)
 * 
 * Picolibc calls write() instead of _write()
 */
ssize_t write(int fd, const void *ptr, size_t len) {
    /* FDs 1,2 use UART directly for performance */
    if (fd == STDOUT_FILENO || fd == STDERR_FILENO) {
        return _write(fd, (char *)ptr, len);
    }
    /* Other FDs use syscall */
    long ret = syscall3(SYS_WRITE, fd, (long)ptr, (long)len);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return (ssize_t)ret;
}

/*
 * read - Read from a file descriptor (picolibc interface)
 * 
 * Picolibc calls read() instead of _read()
 */
ssize_t read(int fd, void *ptr, size_t len) {
    /* FD 0 (stdin) uses UART directly */
    if (fd == STDIN_FILENO) {
        return _read(fd, (char *)ptr, len);
    }
    /* Other FDs use syscall */
    long ret = syscall3(SYS_READ, fd, (long)ptr, (long)len);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return (ssize_t)ret;
}

/*
 * gettimeofday - Get current time (picolibc interface)
 * 
 * Picolibc's time() calls this function
 */
int gettimeofday(struct timeval *tv, void *tz) {
    return _gettimeofday(tv, tz);
}

/*
 * _write - Write to a file descriptor
 * 
 * File descriptors:
 *   0 (stdin)  - invalid for writing
 *   1 (stdout) - Console UART
 *   2 (stderr) - Debug UART
 *   other      - not supported
 */
int _write(int fd, char *ptr, int len) {
    int i;
    
    if (fd == STDOUT_FILENO) {
        /* Write to Console UART */
        for (i = 0; i < len; i++) {
            *CONSOLE_UART_TX = ptr[i];
        }
        return len;
    } else if (fd == STDERR_FILENO) {
        /* Write to Debug UART */
        for (i = 0; i < len; i++) {
            *DEBUG_UART_TX = ptr[i];
        }
        return len;
    }
    
    errno = EBADF;
    return -1;
}

/*
 * _read - Read from a file descriptor
 * 
 * File descriptors:
 *   0 (stdin)  - Console UART RX
 *   1 (stdout) - invalid for reading
 *   2 (stderr) - invalid for reading
 *   other      - not supported
 */
int _read(int fd, char *ptr, int len) {
    int i;
    unsigned char status, byte;
    
    if (fd == STDIN_FILENO) {
        /* Read from Console UART */
        for (i = 0; i < len; i++) {
            /* Check if data available */
            status = *CONSOLE_UART_RX_STATUS;
            if (status == 0) {
                /* No data available */
                if (i == 0) {
                    /* No data read at all - return 0 (would block) */
                    return 0;
                } else {
                    /* Return what we got so far */
                    return i;
                }
            }
            
            /* Read byte */
            byte = *CONSOLE_UART_RX;
            if (byte == 0xFF) {
                /* 0xFF means no data (shouldn't happen if status==1) */
                return i;
            }
            
            ptr[i] = byte;
        }
        return len;
    }
    
    errno = EBADF;
    return -1;
}

/*
 * _close - Close a file descriptor
 * 
 * Not supported in bare-metal.
 */
int _close(int fd) {
    errno = EBADF;
    return -1;
}

/*
 * _fstat - Get file status
 * 
 * All file descriptors are character devices.
 */
int _fstat(int fd, struct stat *st) {
    if (fd >= 0 && fd <= 2) {
        st->st_mode = S_IFCHR;  /* Character device */
        st->st_blksize = 0;
        return 0;
    }
    
    errno = EBADF;
    return -1;
}

/*
 * _isatty - Check if file descriptor is a terminal
 * 
 * stdin/stdout/stderr are all terminals (UARTs).
 */
int _isatty(int fd) {
    if (fd >= 0 && fd <= 2) {
        return 1;
    }
    return 0;
}

/*
 * _lseek - Seek in a file
 * 
 * Not supported for character devices.
 */
int _lseek(int fd, int offset, int whence) {
    errno = ESPIPE;  /* Illegal seek */
    return -1;
}

/*
 * _exit - Exit program
 * 
 * Use EBREAK to halt the emulator cleanly.
 * Exit status is passed in register a0.
 */
void _exit(int status) {
    /* Write exit message to Debug UART */
    const char *msg = "\n[Program exited with status ";
    int i;
    
    for (i = 0; msg[i] != '\0'; i++) {
        *DEBUG_UART_TX = msg[i];
    }
    
    /* Print status as decimal */
    if (status < 0) {
        *DEBUG_UART_TX = '-';
        status = -status;
    }
    
    if (status == 0) {
        *DEBUG_UART_TX = '0';
    } else {
        char digits[10];
        int ndigits = 0;
        while (status > 0) {
            digits[ndigits++] = '0' + (status % 10);
            status /= 10;
        }
        for (i = ndigits - 1; i >= 0; i--) {
            *DEBUG_UART_TX = digits[i];
        }
    }
    
    *DEBUG_UART_TX = ']';
    *DEBUG_UART_TX = '\n';
    
    /* Set exit status in a0 and halt with EBREAK */
    register int a0 __asm__("a0") = status;
    __asm__ volatile ("ebreak" : : "r"(a0));
    
    /* Should never reach here, but just in case */
    while (1) {
        /* Spin forever */
    }
}

/*
 * _kill - Send signal to process
 * 
 * Not supported in bare-metal.
 */
int _kill(int pid, int sig) {
    errno = EINVAL;
    return -1;
}

/*
 * _getpid - Get process ID
 * 
 * Always return 1 (we're the only process).
 */
int _getpid(void) {
    return 1;
}

/*
 * _open - Open a file
 * 
 * Not supported in bare-metal (no filesystem).
 */
int _open(const char *name, int flags, int mode) {
    errno = ENOENT;
    return -1;
}

/*
 * _unlink - Delete a file
 * 
 * Not supported in bare-metal (no filesystem).
 */
int _unlink(const char *name) {
    errno = ENOENT;
    return -1;
}

/*
 * _link - Create hard link
 * 
 * Not supported in bare-metal (no filesystem).
 */
int _link(const char *oldpath, const char *newpath) {
    errno = EMLINK;
    return -1;
}

/*
 * _stat - Get file status
 * 
 * Not supported in bare-metal (no filesystem).
 */
int _stat(const char *file, struct stat *st) {
    errno = ENOENT;
    return -1;
}

/*
 * _times - Get process times
 * 
 * Return elapsed time from timer.
 */
clock_t _times(struct tms *buf) {
    unsigned int ms = *TIMER_MS;
    
    if (buf != NULL) {
        /* All times are user time (no system/children) */
        buf->tms_utime = ms;
        buf->tms_stime = 0;
        buf->tms_cutime = 0;
        buf->tms_cstime = 0;
    }
    
    return ms;
}

/*
 * _gettimeofday - Get current time
 * 
 * Use real-time clock (Unix time + nanoseconds).
 */
int _gettimeofday(struct timeval *tv, void *tz) {
    if (tv != NULL) {
        /* Read Unix time (seconds since epoch) */
        tv->tv_sec = *CLOCK_TIME;
        
        /* Read nanoseconds and convert to microseconds */
        tv->tv_usec = (*CLOCK_NSEC) / 1000;
    }
    
    return 0;
}

/*
 * _fork - Create child process
 * 
 * Not supported in bare-metal.
 */
int _fork(void) {
    errno = EAGAIN;
    return -1;
}

/*
 * _execve - Execute program
 * 
 * Not supported in bare-metal.
 */
int _execve(const char *name, char *const argv[], char *const env[]) {
    errno = ENOMEM;
    return -1;
}

/*
 * _wait - Wait for child process
 * 
 * Not supported in bare-metal.
 */
int _wait(int *status) {
    errno = ECHILD;
    return -1;
}

/* Additional syscalls for NetHack */

/* Non-underscore versions (some programs call these directly) */
int open(const char *name, int flags, ...) {
    /* Use openat with AT_FDCWD to open relative to current directory */
    long ret = syscall4(SYS_OPENAT, AT_FDCWD, (long)name, (long)flags, 0644);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return (int)ret;
}

int close(int fd) {
    long ret = syscall1(SYS_CLOSE, fd);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

off_t lseek(int fd, off_t offset, int whence) {
    long ret = syscall3(SYS_LSEEK, fd, (long)offset, (long)whence);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return (off_t)ret;
}

/* Unix user/group functions (stubs) */
uid_t getuid(void) {
    return 0;  /* Always root */
}

uid_t geteuid(void) {
    return 0;  /* Always root */
}

gid_t getgid(void) {
    return 0;  /* Always root group */
}

gid_t getegid(void) {
    return 0;  /* Always root group */
}

int setuid(uid_t uid) {
    (void)uid;
    return 0;  /* Always succeeds */
}

int setgid(gid_t gid) {
    (void)gid;
    return 0;  /* Always succeeds */
}

int chdir(const char *path) {
    long ret = syscall1(SYS_CHDIR, (long)path);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

char *getcwd(char *buf, unsigned int size) {
    long ret = syscall2(SYS_GETCWD, (long)buf, (long)size);
    if (ret < 0) {
        errno = -ret;
        return NULL;
    }
    return buf;
}

/* Process functions (stubs) */
int execl(const char *path, const char *arg, ...) {
    (void)path;
    (void)arg;
    errno = ENOENT;
    return -1;
}

/* Additional file/process operations */
int creat(const char *pathname, mode_t mode) {
    return open(pathname, O_CREAT | O_WRONLY | O_TRUNC, mode);
}

int unlink(const char *pathname) {
    /* Use unlinkat with AT_FDCWD and flags=0 */
    long ret = syscall3(SYS_UNLINKAT, AT_FDCWD, (long)pathname, 0);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

int fstat(int fd, struct stat *buf) {
    long ret = syscall2(SYS_FSTAT, fd, (long)buf);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

int isatty(int fd) {
    /* FDs 0, 1, 2 are UART */
    return (fd >= 0 && fd <= 2) ? 1 : 0;
}

pid_t fork(void) {
    errno = ENOSYS;
    return -1;
}

pid_t wait(int *status) {
    (void)status;
    errno = ECHILD;
    return -1;
}

/* Additional Unix functions for NetHack compatibility */
pid_t getpid(void) {
    return 1;  /* Always return PID 1 */
}

mode_t umask(mode_t mask) {
    (void)mask;
    return 0022;  /* Return default umask */
}

int chmod(const char *pathname, mode_t mode) {
    (void)pathname;
    (void)mode;
    errno = ENOENT;
    return -1;
}

int stat(const char *pathname, struct stat *buf) {
    /* Use fstatat with AT_FDCWD and flags=0 */
    long ret = syscall4(SYS_FSTATAT, AT_FDCWD, (long)pathname, (long)buf, 0);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

unsigned int sleep(unsigned int seconds) {
    /* Simple busy-wait delay using timer */
    volatile uint32_t *timer = (volatile uint32_t *)0x10000004;
    uint32_t start = *timer;
    uint32_t target = start + (seconds * 1000);
    while (*timer < target) {
        /* Busy wait */
    }
    return 0;
}

char *getlogin(void) {
    return "player";  /* Default username */
}

/* Password database stubs - return dummy entries */
static struct passwd dummy_passwd = {
    .pw_name = "player",
    .pw_passwd = "x",
    .pw_uid = 0,
    .pw_gid = 0,
    .pw_gecos = "NetHack Player",
    .pw_dir = "/",
    .pw_shell = "/bin/sh"
};

struct passwd *getpwuid(uid_t uid) {
    (void)uid;
    return &dummy_passwd;
}

struct passwd *getpwnam(const char *name) {
    (void)name;
    return &dummy_passwd;
}

/* Terminal I/O control - ioctl implementation */
int ioctl(int fd, unsigned long request, ...) {
    va_list args;
    va_start(args, request);
    
    /* Handle TIOCGWINSZ - get terminal window size */
    if (request == TIOCGWINSZ) {
        struct winsize *ws = va_arg(args, struct winsize *);
        if (ws) {
            /* Return standard 80x24 terminal size */
            ws->ws_row = 24;
            ws->ws_col = 80;
            ws->ws_xpixel = 0;
            ws->ws_ypixel = 0;
            va_end(args);
            return 0;
        }
    }
    
    va_end(args);
    
    /* Unsupported ioctl */
    (void)fd;
    errno = ENOTTY;
    return -1;
}

/* Terminal I/O control functions (termios) */
/* We implement these as no-ops since we use ANSI_DEFAULT mode */

int tcgetattr(int fd, struct termios *termios_p) {
    if (!termios_p) {
        errno = EINVAL;
        return -1;
    }
    
    /* Return a default termios structure */
    /* Set up reasonable defaults for a dumb terminal */
    termios_p->c_iflag = ICRNL;  /* Map CR to NL on input */
    termios_p->c_oflag = OPOST | ONLCR;  /* Post-process output, map NL to CR-NL */
    termios_p->c_cflag = CS8 | CREAD | CLOCAL | B9600;  /* 8-bit, enable receiver, ignore modem */
    termios_p->c_lflag = ISIG | ICANON | ECHO | ECHOE | ECHOK;  /* Canonical mode with echo */
    
    /* Set control characters */
    termios_p->c_cc[VINTR]    = 0x03;  /* ^C */
    termios_p->c_cc[VQUIT]    = 0x1C;  /* ^\ */
    termios_p->c_cc[VERASE]   = 0x7F;  /* DEL */
    termios_p->c_cc[VKILL]    = 0x15;  /* ^U */
    termios_p->c_cc[VEOF]     = 0x04;  /* ^D */
    termios_p->c_cc[VTIME]    = 0;
    termios_p->c_cc[VMIN]     = 1;
    termios_p->c_cc[VSTART]   = 0x11;  /* ^Q */
    termios_p->c_cc[VSTOP]    = 0x13;  /* ^S */
    termios_p->c_cc[VSUSP]    = 0x1A;  /* ^Z */
    
    termios_p->c_ispeed = B9600;
    termios_p->c_ospeed = B9600;
    
    (void)fd;
    return 0;
}

int tcsetattr(int fd, int optional_actions, const struct termios *termios_p) {
    /* No-op - we don't actually change terminal settings */
    /* ANSI_DEFAULT mode handles everything */
    (void)fd;
    (void)optional_actions;
    (void)termios_p;
    return 0;
}

int tcsendbreak(int fd, int duration) {
    (void)fd;
    (void)duration;
    return 0;
}

int tcdrain(int fd) {
    (void)fd;
    return 0;
}

int tcflush(int fd, int queue_selector) {
    (void)fd;
    (void)queue_selector;
    return 0;
}

int tcflow(int fd, int action) {
    (void)fd;
    (void)action;
    return 0;
}

speed_t cfgetispeed(const struct termios *termios_p) {
    return termios_p ? termios_p->c_ispeed : B9600;
}

speed_t cfgetospeed(const struct termios *termios_p) {
    return termios_p ? termios_p->c_ospeed : B9600;
}

int cfsetispeed(struct termios *termios_p, speed_t speed) {
    if (termios_p) {
        termios_p->c_ispeed = speed;
        return 0;
    }
    errno = EINVAL;
    return -1;
}

int cfsetospeed(struct termios *termios_p, speed_t speed) {
    if (termios_p) {
        termios_p->c_ospeed = speed;
        return 0;
    }
    errno = EINVAL;
    return -1;
}

long fpathconf(int fd, int name) {
    (void)fd;
    (void)name;
    return -1;  /* Not supported */
}

/* Additional file operations */
int rename(const char *oldpath, const char *newpath) {
    /* Use renameat with AT_FDCWD for both paths */
    long ret = syscall4(SYS_RENAMEAT, AT_FDCWD, (long)oldpath, AT_FDCWD, (long)newpath);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

int link(const char *oldpath, const char *newpath) {
    /* Use linkat with AT_FDCWD for both paths, flags=0 */
    long ret = syscall5(SYS_LINKAT, AT_FDCWD, (long)oldpath, AT_FDCWD, (long)newpath, 0);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

int access(const char *pathname, int mode) {
    /* Use faccessat with AT_FDCWD and flags=0 */
    long ret = syscall3(SYS_FACCESSAT, AT_FDCWD, (long)pathname, (long)mode);
    if (ret < 0) {
        errno = -ret;
        return -1;
    }
    return 0;
}

int access_stub_removed(const char *pathname, int mode) {
    (void)pathname;
    (void)mode;
    errno = ENOENT;
    return -1;
}

/* Process execution */
int execv(const char *pathname, char *const argv[]) {
    (void)pathname;
    (void)argv;
    errno = ENOENT;
    return -1;
}

/* Signal handling stubs */
int kill(pid_t pid, int sig) {
    (void)pid;
    (void)sig;
    errno = ESRCH;  /* No such process */
    return -1;
}

/* Termcap function stubs */
int tputs(const char *str, int affcnt, int (*putc_func)(int)) {
    /* In ANSI_DEFAULT mode, just output the string directly */
    (void)affcnt;
    if (str) {
        while (*str) {
            putc_func(*str++);
        }
    }
    return 0;
}
