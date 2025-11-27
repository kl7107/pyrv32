/*
 * Test 4: lseek
 * 
 * Tests:
 * - lseek() positions file pointer
 * - SEEK_SET, SEEK_CUR, SEEK_END
 * - Read/write at different positions
 */

#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>

#define TEST_FILE "/tmp/seektest.txt"

int main(void) {
    int fd;
    off_t pos;
    char buf[16];
    
    printf("TEST: lseek\n");
    
    // Create file with known content
    fd = open(TEST_FILE, O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("FAIL: open failed\n");
        return 1;
    }
    
    write(fd, "0123456789", 10);
    
    // SEEK_SET: absolute position
    printf("Testing SEEK_SET...\n");
    pos = lseek(fd, 5, SEEK_SET);
    if (pos != 5) {
        printf("FAIL: lseek SEEK_SET returned %ld\n", (long)pos);
        return 1;
    }
    
    read(fd, buf, 1);
    buf[1] = '\0';
    if (buf[0] != '5') {
        printf("FAIL: Expected '5', got '%c'\n", buf[0]);
        return 1;
    }
    printf("Read at pos 5: '%c' ✓\n", buf[0]);
    
    // SEEK_CUR: relative to current
    printf("Testing SEEK_CUR...\n");
    pos = lseek(fd, 2, SEEK_CUR);
    if (pos != 8) {
        printf("FAIL: lseek SEEK_CUR returned %ld, expected 8\n", (long)pos);
        return 1;
    }
    
    read(fd, buf, 1);
    buf[1] = '\0';
    if (buf[0] != '8') {
        printf("FAIL: Expected '8', got '%c'\n", buf[0]);
        return 1;
    }
    printf("Read at pos 8: '%c' ✓\n", buf[0]);
    
    // SEEK_END: relative to end
    printf("Testing SEEK_END...\n");
    pos = lseek(fd, -3, SEEK_END);
    if (pos != 7) {
        printf("FAIL: lseek SEEK_END returned %ld, expected 7\n", (long)pos);
        return 1;
    }
    
    read(fd, buf, 1);
    buf[1] = '\0';
    if (buf[0] != '7') {
        printf("FAIL: Expected '7', got '%c'\n", buf[0]);
        return 1;
    }
    printf("Read at pos 7: '%c' ✓\n", buf[0]);
    
    close(fd);
    
    printf("PASS\n");
    return 0;
}
