/*
 * Test: getpwnam
 * 
 * Tests:
 * - getpwnam() returns non-NULL pointer
 * - Returns same struct as getpwuid()
 * - Works with "player" username
 */

#include <sys/types.h>
#include <pwd.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    struct passwd *pw_uid, *pw_name;
    
    printf("TEST: getpwnam\n");
    
    // Test 1: Returns non-NULL for "player"
    printf("Testing non-NULL return...\n");
    pw_name = getpwnam("player");
    if (pw_name == NULL) {
        printf("FAIL: getpwnam(\"player\") returned NULL\n");
        return 1;
    }
    printf("  getpwnam(\"player\") = %p ✓\n", pw_name);
    
    // Test 2: Returns same struct as getpwuid(0)
    printf("Testing consistency with getpwuid...\n");
    pw_uid = getpwuid(0);
    if (pw_uid == NULL) {
        printf("FAIL: getpwuid(0) returned NULL\n");
        return 1;
    }
    
    if (pw_name != pw_uid) {
        printf("FAIL: getpwnam and getpwuid returned different structs\n");
        printf("  getpwnam=%p, getpwuid=%p\n", pw_name, pw_uid);
        return 1;
    }
    printf("  Both return same struct ✓\n");
    
    // Test 3: Different names still return same struct (single-user)
    printf("Testing different names...\n");
    struct passwd *pw_root = getpwnam("root");
    struct passwd *pw_nobody = getpwnam("nobody");
    
    if (pw_root == NULL || pw_nobody == NULL) {
        printf("FAIL: getpwnam returned NULL for different name\n");
        return 1;
    }
    
    if (pw_root != pw_name || pw_nobody != pw_name) {
        printf("FAIL: Different names returned different structs\n");
        printf("  player=%p, root=%p, nobody=%p\n", pw_name, pw_root, pw_nobody);
        return 1;
    }
    printf("  All names return same struct ✓\n");
    
    printf("PASS\n");
    return 0;
}
