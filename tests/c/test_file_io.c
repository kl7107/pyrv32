/*
 * Test 2: File open/close/read/write
 * 
 * Tests:
 * - open() creates/opens file
 * - write() writes data
 * - close() closes file
 * - open() reopens file
 * - read() reads data back
 * - Data matches what was written
 */

#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>

#define TEST_FILE "/tmp/testfile.txt"
#define TEST_DATA "Hello, World!"

int main(void) {
    int fd;
    ssize_t n;
    char buf[256];
    
    printf("TEST: open/write/read/close\n");
    
    // Create and write
    printf("Creating %s...\n", TEST_FILE);
    fd = open(TEST_FILE, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("FAIL: open for write returned %d\n", fd);
        return 1;
    }
    printf("Opened fd=%d\n", fd);
    
    printf("Writing '%s'...\n", TEST_DATA);
    n = write(fd, TEST_DATA, strlen(TEST_DATA));
    if (n != strlen(TEST_DATA)) {
        printf("FAIL: write returned %ld, expected %lu\n", (long)n, (unsigned long)strlen(TEST_DATA));
        return 1;
    }
    
    if (close(fd) != 0) {
        printf("FAIL: close failed\n");
        return 1;
    }
    printf("Closed file\n");
    
    // Reopen and read
    printf("Reopening for read...\n");
    fd = open(TEST_FILE, O_RDONLY);
    if (fd < 0) {
        printf("FAIL: open for read returned %d\n", fd);
        return 1;
    }
    
    memset(buf, 0, sizeof(buf));
    n = read(fd, buf, sizeof(buf));
    if (n != strlen(TEST_DATA)) {
        printf("FAIL: read returned %ld, expected %lu\n", (long)n, (unsigned long)strlen(TEST_DATA));
        return 1;
    }
    
    printf("Read: '%s'\n", buf);
    
    if (strcmp(buf, TEST_DATA) != 0) {
        printf("FAIL: Data mismatch\n");
        return 1;
    }
    
    close(fd);
    
    printf("PASS\n");
    return 0;
}
