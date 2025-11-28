/*
 * Test: getpwuid
 * 
 * Tests:
 * - getpwuid() returns non-NULL pointer
 * - pw_name is valid string
 * - pw_uid matches requested uid
 * - pw_dir is valid path
 * - Multiple calls return same struct
 */

#include <sys/types.h>
#include <pwd.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    struct passwd *pw;
    
    printf("TEST: getpwuid\n");
    
    // Test 1: Returns non-NULL
    printf("Testing non-NULL return...\n");
    pw = getpwuid(0);
    if (pw == NULL) {
        printf("FAIL: getpwuid(0) returned NULL\n");
        return 1;
    }
    printf("  getpwuid(0) = %p ✓\n", pw);
    
    // Test 2: pw_name is valid
    printf("Testing pw_name...\n");
    if (pw->pw_name == NULL) {
        printf("FAIL: pw_name is NULL\n");
        return 1;
    }
    if (strcmp(pw->pw_name, "player") != 0) {
        printf("FAIL: pw_name is '%s', expected 'player'\n", pw->pw_name);
        return 1;
    }
    printf("  pw_name = '%s' ✓\n", pw->pw_name);
    
    // Test 3: pw_uid matches
    printf("Testing pw_uid...\n");
    if (pw->pw_uid != 0) {
        printf("FAIL: pw_uid is %u, expected 0\n", pw->pw_uid);
        return 1;
    }
    printf("  pw_uid = %u ✓\n", pw->pw_uid);
    
    // Test 4: pw_dir is valid path
    printf("Testing pw_dir...\n");
    if (pw->pw_dir == NULL) {
        printf("FAIL: pw_dir is NULL\n");
        return 1;
    }
    if (pw->pw_dir[0] != '/') {
        printf("FAIL: pw_dir is '%s', expected to start with /\n", pw->pw_dir);
        return 1;
    }
    printf("  pw_dir = '%s' ✓\n", pw->pw_dir);
    
    // Test 5: Multiple UIDs return same struct (single-user system)
    printf("Testing consistency across UIDs...\n");
    struct passwd *pw1 = getpwuid(1);
    struct passwd *pw1000 = getpwuid(1000);
    
    if (pw1 == NULL || pw1000 == NULL) {
        printf("FAIL: getpwuid returned NULL for different UID\n");
        return 1;
    }
    
    if (pw != pw1 || pw1 != pw1000) {
        printf("FAIL: Different UIDs returned different structs\n");
        printf("  pw(0)=%p, pw(1)=%p, pw(1000)=%p\n", pw, pw1, pw1000);
        return 1;
    }
    printf("  All UIDs return same struct ✓\n");
    
    printf("PASS\n");
    return 0;
}
