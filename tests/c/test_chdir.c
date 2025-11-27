/*
 * Test 1: Basic chdir/getcwd
 * 
 * Tests:
 * - getcwd() returns current directory
 * - chdir() changes directory
 * - getcwd() reflects the change
 */

#include <unistd.h>
#include <string.h>
#include <stdio.h>

#define TEST_DIR "/tmp/test"

int main(void) {
    char buf[256];
    int ret;
    
    printf("TEST: chdir/getcwd\n");
    
    // Get initial directory
    if (getcwd(buf, sizeof(buf)) == NULL) {
        printf("FAIL: getcwd failed initially\n");
        return 1;
    }
    printf("Initial dir: %s\n", buf);
    
    // Change directory
    printf("Changing to %s...\n", TEST_DIR);
    ret = chdir(TEST_DIR);
    if (ret != 0) {
        printf("FAIL: chdir returned %d\n", ret);
        return 1;
    }
    
    // Get new directory
    if (getcwd(buf, sizeof(buf)) == NULL) {
        printf("FAIL: getcwd failed after chdir\n");
        return 1;
    }
    printf("New dir: %s\n", buf);
    
    // Verify it changed
    if (strcmp(buf, TEST_DIR) != 0) {
        printf("FAIL: Expected %s, got %s\n", TEST_DIR, buf);
        return 1;
    }
    
    printf("PASS\n");
    return 0;
}
