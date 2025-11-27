/*
 * Test 5: access
 * 
 * Tests:
 * - access() checks file existence/permissions
 * - F_OK, R_OK, W_OK
 */

#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

#define TEST_FILE "/tmp/accesstest.txt"
#define NOEXIST_FILE "/tmp/nosuchfile.txt"

int main(void) {
    int fd, ret;
    
    printf("TEST: access\n");
    
    // Create file
    fd = open(TEST_FILE, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("FAIL: open failed\n");
        return 1;
    }
    close(fd);
    
    // Test F_OK (exists)
    printf("Testing F_OK on existing file...\n");
    ret = access(TEST_FILE, F_OK);
    if (ret != 0) {
        printf("FAIL: access F_OK returned %d\n", ret);
        return 1;
    }
    printf("File exists ✓\n");
    
    // Test R_OK (readable)
    printf("Testing R_OK...\n");
    ret = access(TEST_FILE, R_OK);
    if (ret != 0) {
        printf("FAIL: access R_OK returned %d\n", ret);
        return 1;
    }
    printf("File readable ✓\n");
    
    // Test W_OK (writable)
    printf("Testing W_OK...\n");
    ret = access(TEST_FILE, W_OK);
    if (ret != 0) {
        printf("FAIL: access W_OK returned %d\n", ret);
        return 1;
    }
    printf("File writable ✓\n");
    
    // Test nonexistent file
    printf("Testing nonexistent file...\n");
    ret = access(NOEXIST_FILE, F_OK);
    if (ret == 0) {
        printf("FAIL: access on nonexistent file should fail\n");
        return 1;
    }
    printf("Nonexistent file correctly fails ✓\n");
    
    printf("PASS\n");
    return 0;
}
