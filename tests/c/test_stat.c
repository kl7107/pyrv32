/*
 * Test 3: stat/fstat
 * 
 * Tests:
 * - stat() gets file info by path
 * - fstat() gets file info by fd
 * - Results match
 */

#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <stdio.h>

#define TEST_FILE "/tmp/stattest.txt"

int main(void) {
    int fd;
    struct stat st1, st2;
    
    printf("TEST: stat/fstat\n");
    
    // Create file
    fd = open(TEST_FILE, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("FAIL: open failed\n");
        return 1;
    }
    write(fd, "test", 4);
    close(fd);
    
    // stat by path
    printf("Testing stat()...\n");
    if (stat(TEST_FILE, &st1) != 0) {
        printf("FAIL: stat failed\n");
        return 1;
    }
    printf("stat: size=%ld mode=0%o\n", (long)st1.st_size, st1.st_mode);
    
    // fstat by fd
    printf("Testing fstat()...\n");
    fd = open(TEST_FILE, O_RDONLY);
    if (fd < 0) {
        printf("FAIL: open failed\n");
        return 1;
    }
    
    if (fstat(fd, &st2) != 0) {
        printf("FAIL: fstat failed\n");
        return 1;
    }
    printf("fstat: size=%ld mode=0%o\n", (long)st2.st_size, st2.st_mode);
    
    // Compare
    if (st1.st_size != st2.st_size) {
        printf("FAIL: size mismatch (%ld vs %ld)\n", (long)st1.st_size, (long)st2.st_size);
        return 1;
    }
    
    if (st1.st_size != 4) {
        printf("FAIL: wrong size (expected 4, got %ld)\n", (long)st1.st_size);
        return 1;
    }
    
    close(fd);
    
    printf("PASS\n");
    return 0;
}
