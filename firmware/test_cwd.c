/*
 * Test working directory syscalls with picolibc
 */

#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

int main(void) {
    char buf[256];
    int fd;
    ssize_t n;
    
    printf("=== Test Working Directory ===\n\n");
    
    // Test 1: Get initial CWD
    if (getcwd(buf, sizeof(buf)) != NULL) {
        printf("[1] Initial CWD: %s\n", buf);
    } else {
        printf("[1] getcwd() failed\n");
        return 1;
    }
    
    // Test 2: Change to /dat
    printf("\n[2] Changing to /dat...\n");
    if (chdir("/dat") == 0) {
        printf("    chdir('/dat') succeeded\n");
    } else {
        printf("    chdir('/dat') failed\n");
        return 1;
    }
    
    // Test 3: Verify new CWD
    if (getcwd(buf, sizeof(buf)) != NULL) {
        printf("    Current CWD: %s\n", buf);
    } else {
        printf("    getcwd() failed\n");
        return 1;
    }
    
    // Test 4: Try to open a file with relative path
    printf("\n[3] Opening 'quest.txt' with relative path...\n");
    fd = open("quest.txt", O_RDONLY);
    if (fd >= 0) {
        printf("    open('quest.txt') succeeded, fd=%d\n", fd);
        
        // Read first 30 bytes
        n = read(fd, buf, 30);
        if (n > 0) {
            buf[n] = '\0';
            printf("    Read %zd bytes: %s...\n", n, buf);
        }
        close(fd);
    } else {
        printf("    open('quest.txt') failed\n");
        return 1;
    }
    
    // Test 5: Change to parent directory
    printf("\n[4] Changing to parent directory '..'...\n");
    if (chdir("..") == 0) {
        printf("    chdir('..') succeeded\n");
    } else {
        printf("    chdir('..') failed\n");
        return 1;
    }
    
    // Test 6: Verify we're back at root
    if (getcwd(buf, sizeof(buf)) != NULL) {
        printf("    Current CWD: %s\n", buf);
    } else {
        printf("    getcwd() failed\n");
        return 1;
    }
    
    // Test 7: Try absolute path
    printf("\n[5] Opening '/dat/quest.txt' with absolute path...\n");
    fd = open("/dat/quest.txt", O_RDONLY);
    if (fd >= 0) {
        printf("    open('/dat/quest.txt') succeeded, fd=%d\n", fd);
        close(fd);
    } else {
        printf("    open('/dat/quest.txt') failed\n");
        return 1;
    }
    
    printf("\n=== All tests passed! ===\n");
    return 0;
}
