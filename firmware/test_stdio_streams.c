/*
 * Test stdio stream initialization (stdin/stdout/stderr)
 * 
 * This test validates that stdin/stdout/stderr FILE* structures
 * are properly initialized in our bare-metal picolibc environment.
 * 
 * Tests:
 * 1. Basic existence: stdin/stdout/stderr are non-NULL
 * 2. File descriptor mapping: fileno() returns correct values (0/1/2)
 * 3. Stream flags: FILE structures have valid flags set
 * 4. freopen() on stdin: Can redirect stdin to a file
 * 5. freopen() on stdout: Can redirect stdout to a file
 * 6. fprintf() to streams: Can write to stdout/stderr
 * 7. fscanf() from stdin: Can read from stdin (after freopen)
 */

#include <stdio.h>
#include <string.h>

/* Test result tracking */
static int tests_run = 0;
static int tests_passed = 0;

#define TEST(name, condition) do { \
    tests_run++; \
    if (condition) { \
        printf("PASS: %s\n", name); \
        tests_passed++; \
    } else { \
        printf("FAIL: %s\n", name); \
    } \
} while(0)

int main(void) {
    printf("=== stdio Stream Initialization Tests ===\n\n");
    
    /* Test 1: stdin/stdout/stderr exist and are non-NULL */
    TEST("stdin is non-NULL", stdin != NULL);
    TEST("stdout is non-NULL", stdout != NULL);
    TEST("stderr is non-NULL", stderr != NULL);
    
    /* Test 2: File descriptor mapping */
    if (stdin != NULL) {
        int fd = fileno(stdin);
        TEST("stdin fileno() returns 0", fd == 0);
    }
    if (stdout != NULL) {
        int fd = fileno(stdout);
        TEST("stdout fileno() returns 1", fd == 1);
    }
    if (stderr != NULL) {
        int fd = fileno(stderr);
        TEST("stderr fileno() returns 2", fd == 2);
    }
    
    /* Test 3: Stream flags - check if FILE structures have valid flags
     * We can't directly access FILE internals, but we can test operations
     */
    if (stdout != NULL) {
        /* Try fflush - should work if stdout is valid */
        int result = fflush(stdout);
        TEST("fflush(stdout) succeeds", result == 0);
    }
    
    if (stderr != NULL) {
        /* Try fprintf to stderr */
        int result = fprintf(stderr, "[stderr test]\n");
        TEST("fprintf(stderr) succeeds", result > 0);
    }
    
    /* Test 4: freopen() on stdin
     * This is the critical test - dgn_comp uses freopen(file, "r", stdin)
     * 
     * For this test to work, we need a file to open. In the simulator,
     * we'll need to have a file at /dat/test_input.txt
     */
    printf("\nTesting freopen() on stdin...\n");
    FILE *new_stdin = freopen("test_input.txt", "r", stdin);
    if (new_stdin != NULL) {
        printf("PASS: freopen(\"test_input.txt\", \"r\", stdin) succeeded\n");
        tests_passed++;
        
        /* Try to read from the reopened stdin */
        char buffer[64];
        if (fgets(buffer, sizeof(buffer), new_stdin) != NULL) {
            printf("PASS: fgets() from reopened stdin succeeded\n");
            printf("  Read: %s", buffer);
            tests_passed++;
        } else {
            printf("FAIL: fgets() from reopened stdin failed\n");
        }
        tests_run += 2;
        
        fclose(new_stdin);
    } else {
        printf("FAIL: freopen(\"test_input.txt\", \"r\", stdin) returned NULL\n");
        perror("  freopen");
        tests_run++;
    }
    
    /* Test 5: freopen() on stdout */
    printf("\nTesting freopen() on stdout...\n");
    FILE *new_stdout = freopen("test_output.txt", "w", stdout);
    if (new_stdout != NULL) {
        /* Note: This message won't appear on console since stdout is redirected */
        fprintf(new_stdout, "PASS: freopen() on stdout succeeded\n");
        fprintf(new_stdout, "This text should be in test_output.txt\n");
        fclose(new_stdout);
        
        /* Reopen stdout to console (we can't do this in bare-metal, so just note success) */
        printf("PASS: freopen(\"test_output.txt\", \"w\", stdout) succeeded\n");
        tests_passed++;
    } else {
        printf("FAIL: freopen(\"test_output.txt\", \"w\", stdout) returned NULL\n");
        perror("  freopen");
    }
    tests_run++;
    
    /* Summary */
    printf("\n=== Test Summary ===\n");
    printf("Tests run: %d\n", tests_run);
    printf("Tests passed: %d\n", tests_passed);
    printf("Tests failed: %d\n", tests_run - tests_passed);
    
    if (tests_passed == tests_run) {
        printf("\nALL TESTS PASSED\n");
        return 0;
    } else {
        printf("\nSOME TESTS FAILED\n");
        return 1;
    }
}
