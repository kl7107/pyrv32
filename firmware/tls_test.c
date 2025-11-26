/*
 * TLS (Thread Local Storage) Test
 * 
 * Tests all picolibc functions that use TLS to ensure
 * our thread pointer initialization is correct.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>

#define TIMER_MS ((volatile unsigned int *)0x10000004)

/* Test result tracking */
static int tests_passed = 0;
static int tests_failed = 0;

#define TEST_ASSERT(condition, message) \
    do { \
        if (condition) { \
            tests_passed++; \
            printf("  ✓ %s\n", message); \
        } else { \
            tests_failed++; \
            printf("  ✗ FAIL: %s\n", message); \
        } \
    } while(0)

/*
 * Test errno - Uses TLS
 */
void test_errno(void) {
    printf("\n=== errno (TLS) ===\n");
    
    /* errno should start at 0 */
    errno = 0;
    TEST_ASSERT(errno == 0, "errno initialized to 0");
    
    /* Set errno */
    errno = EINVAL;
    TEST_ASSERT(errno == EINVAL, "errno set to EINVAL");
    
    /* Clear errno */
    errno = 0;
    TEST_ASSERT(errno == 0, "errno cleared");
    
    /* Test different error codes */
    errno = ENOMEM;
    TEST_ASSERT(errno == ENOMEM, "errno set to ENOMEM");
    
    errno = ENOENT;
    TEST_ASSERT(errno == ENOENT, "errno set to ENOENT");
}

/*
 * Test rand/srand - Uses TLS (_rand_next)
 */
void test_rand(void) {
    printf("\n=== rand/srand (TLS) ===\n");
    
    /* Basic rand test */
    srand(12345);
    int r1 = rand();
    TEST_ASSERT(r1 >= 0 && r1 <= RAND_MAX, "rand() returns valid value");
    
    /* Deterministic sequence */
    srand(12345);
    int r2 = rand();
    TEST_ASSERT(r1 == r2, "srand() gives deterministic sequence");
    
    /* Different values */
    int r3 = rand();
    TEST_ASSERT(r3 != r2, "consecutive rand() calls differ");
}

/*
 * Test strtok - Uses TLS (_strtok_last)
 */
void test_strtok(void) {
    printf("\n=== strtok (TLS) ===\n");
    
    char str1[] = "This is a test";
    char str2[] = "one,two,three";
    
    /* First string */
    char *token = strtok(str1, " ");
    TEST_ASSERT(token != NULL && strcmp(token, "This") == 0, "strtok first token");
    
    token = strtok(NULL, " ");
    TEST_ASSERT(token != NULL && strcmp(token, "is") == 0, "strtok second token");
    
    token = strtok(NULL, " ");
    TEST_ASSERT(token != NULL && strcmp(token, "a") == 0, "strtok third token");
    
    token = strtok(NULL, " ");
    TEST_ASSERT(token != NULL && strcmp(token, "test") == 0, "strtok fourth token");
    
    token = strtok(NULL, " ");
    TEST_ASSERT(token == NULL, "strtok returns NULL at end");
    
    /* Second string with different delimiter */
    token = strtok(str2, ",");
    TEST_ASSERT(token != NULL && strcmp(token, "one") == 0, "strtok new string");
    
    token = strtok(NULL, ",");
    TEST_ASSERT(token != NULL && strcmp(token, "two") == 0, "strtok continues");
}

/*
 * Test time functions - Use TLS buffers
 */
void test_time_tls(void) {
    printf("\n=== Time functions (TLS buffers) ===\n");
    
    /* time() - note: our gettimeofday implementation returns timer_ms */
    time_t t = time(NULL);
    TEST_ASSERT(t >= 0, "time() returns non-negative value");
    
    /* Note: localtime() and asctime() may use TLS buffers but 
     * they require more complex timezone/system support that we 
     * haven't implemented yet. Skip for now.
     */
    printf("  (localtime/asctime skipped - requires timezone support)\n");
}

/*
 * Test multiple TLS variables don't interfere
 */
void test_tls_isolation(void) {
    printf("\n=== TLS variable isolation ===\n");
    
    /* Set errno */
    errno = EINVAL;
    
    /* Use rand */
    srand(999);
    int r1 = rand();
    
    /* Use strtok */
    char str[] = "a b c";
    char *tok = strtok(str, " ");
    
    /* Check errno wasn't corrupted */
    TEST_ASSERT(errno == EINVAL, "errno preserved after rand/strtok");
    
    /* Check rand state wasn't corrupted */
    srand(999);
    int r2 = rand();
    TEST_ASSERT(r1 == r2, "rand state preserved after errno/strtok");
    
    /* Check strtok state */
    tok = strtok(NULL, " ");
    TEST_ASSERT(tok != NULL && strcmp(tok, "b") == 0, "strtok state preserved");
}

/*
 * Test TLS with function calls
 */
void test_tls_across_calls(void) {
    printf("\n=== TLS across function calls ===\n");
    
    /* Set errno in this function */
    errno = ENOMEM;
    
    /* Call a function that uses different TLS */
    srand(12345);
    int r = rand();
    
    /* Check errno survived */
    TEST_ASSERT(errno == ENOMEM, "errno survives other TLS usage");
    
    /* Modify errno in place */
    errno = ENOENT;
    TEST_ASSERT(errno == ENOENT, "errno can be modified");
}

/*
 * Stress test - rapid TLS access
 */
void test_tls_stress(void) {
    printf("\n=== TLS stress test ===\n");
    
    int i;
    int all_good = 1;
    
    /* Rapidly access different TLS variables */
    for (i = 0; i < 100; i++) {
        errno = i;
        if (errno != i) all_good = 0;
        
        srand(i);
        int r = rand();
        if (r < 0 || r > RAND_MAX) all_good = 0;
        
        if (errno != i) all_good = 0;
    }
    
    TEST_ASSERT(all_good, "100 iterations of errno/rand access");
    
    /* Verify final state */
    TEST_ASSERT(errno == 99, "errno has final value");
}

int main(void) {
    printf("\n");
    printf("================================================================================\n");
    printf("PyRV32 TLS (Thread Local Storage) Test\n");
    printf("================================================================================\n");
    
    unsigned int start_time = *TIMER_MS;
    
    test_errno();
    test_rand();
    test_strtok();
    test_time_tls();
    test_tls_isolation();
    test_tls_across_calls();
    test_tls_stress();
    
    unsigned int end_time = *TIMER_MS;
    
    printf("\n");
    printf("================================================================================\n");
    printf("Test Results\n");
    printf("================================================================================\n");
    printf("Passed: %d\n", tests_passed);
    printf("Failed: %d\n", tests_failed);
    printf("Total:  %d\n", tests_passed + tests_failed);
    printf("Time:   %u ms\n", end_time - start_time);
    printf("================================================================================\n");
    
    if (tests_failed == 0) {
        printf("\n✓ All TLS tests PASSED - Thread Local Storage working correctly!\n");
        printf("\n");
        return 0;
    } else {
        printf("\n✗ Some TLS tests FAILED - review failures above\n");
        printf("\n");
        return 1;
    }
}
