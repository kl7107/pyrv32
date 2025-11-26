/*
 * Test program for syscall stubs
 * Tests basic functionality of all NetHack-required syscalls
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>

void test_file_ops(void) {
    printf("\n=== Testing File Operations ===\n");
    
    // Test open (should fail - no filesystem)
    int fd = open("test.txt", O_RDONLY);
    printf("open('test.txt', O_RDONLY) = %d (errno=%d: %s)\n", 
           fd, errno, strerror(errno));
    
    // Test creat (should fail)
    fd = creat("newfile.txt", 0666);
    printf("creat('newfile.txt', 0666) = %d (errno=%d: %s)\n",
           fd, errno, strerror(errno));
    
    // Test close on invalid fd (should fail)
    int result = close(99);
    printf("close(99) = %d (errno=%d: %s)\n",
           result, errno, strerror(errno));
    
    // Test fstat on invalid fd (should fail)
    struct stat st;
    result = fstat(99, &st);
    printf("fstat(99, &st) = %d (errno=%d: %s)\n",
           result, errno, strerror(errno));
    
    // Test unlink (should fail - no filesystem)
    result = unlink("somefile.txt");
    printf("unlink('somefile.txt') = %d (errno=%d: %s)\n",
           result, errno, strerror(errno));
    
    // Test isatty on stdin/stdout/stderr (should succeed)
    printf("isatty(0) = %d (stdin)\n", isatty(0));
    printf("isatty(1) = %d (stdout)\n", isatty(1));
    printf("isatty(2) = %d (stderr)\n", isatty(2));
    printf("isatty(99) = %d (invalid fd)\n", isatty(99));
}

void test_user_ops(void) {
    printf("\n=== Testing User/Group Operations ===\n");
    
    uid_t uid = getuid();
    printf("getuid() = %u\n", uid);
    
    uid_t euid = geteuid();
    printf("geteuid() = %u\n", euid);
    
    gid_t gid = getgid();
    printf("getgid() = %u\n", gid);
    
    gid_t egid = getegid();
    printf("getegid() = %u\n", egid);
    
    int result = setuid(1000);
    printf("setuid(1000) = %d (errno=%d: %s)\n",
           result, errno, strerror(errno));
    
    result = setgid(1000);
    printf("setgid(1000) = %d (errno=%d: %s)\n",
           result, errno, strerror(errno));
}

void test_dir_ops(void) {
    printf("\n=== Testing Directory Operations ===\n");
    
    char cwd[256];
    char *result = getcwd(cwd, sizeof(cwd));
    printf("getcwd() = '%s'\n", result ? result : "NULL");
    
    int ret = chdir("/tmp");
    printf("chdir('/tmp') = %d (errno=%d: %s)\n",
           ret, errno, strerror(errno));
}

void test_process_ops(void) {
    printf("\n=== Testing Process Operations ===\n");
    
    // Test fork (should fail - not supported)
    pid_t pid = fork();
    printf("fork() = %d (errno=%d: %s)\n",
           pid, errno, strerror(errno));
    
    // If fork succeeded (it shouldn't!), we're in trouble
    if (pid == 0) {
        printf("ERROR: fork() succeeded - we're in child process!\n");
        exit(1);
    }
    
    // Test wait (should fail - no children)
    int status;
    pid = wait(&status);
    printf("wait(&status) = %d (errno=%d: %s)\n",
           pid, errno, strerror(errno));
    
    // Test execl (should fail - not supported)
    // Note: if this succeeds, we won't return!
    // So test it last
}

extern short ospeed;

void test_termcap(void) {
    printf("\n=== Testing Termcap Variables ===\n");
    
    printf("ospeed = %d\n", ospeed);
    
    // Test tputs - should output string directly
    printf("Testing tputs with '\\033[1;31mRED\\033[0m': ");
    fflush(stdout);
    
    // tputs signature: int tputs(const char *str, int affcnt, int (*putc)(int))
    // In our stub, it just outputs the string
    extern int tputs(const char *str, int affcnt, int (*putc)(int));
    tputs("\033[1;31mRED\033[0m", 1, putchar);
    printf("\n");
}

int main(void) {
    printf("=======================================================\n");
    printf("    PyRV32 Syscall Test Suite\n");
    printf("=======================================================\n");
    
    test_file_ops();
    test_user_ops();
    test_dir_ops();
    test_termcap();
    test_process_ops();  // Keep this last in case execl does something weird
    
    printf("\n=======================================================\n");
    printf("    All Tests Complete\n");
    printf("=======================================================\n");
    
    return 0;
}
