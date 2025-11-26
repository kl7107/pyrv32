/*
 * Comprehensive libc Test for NetHack Requirements
 * 
 * Tests all libc functions that NetHack 3.4.3 will need.
 * Based on analysis of NetHack source dependencies.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

/* Timer for diagnostics */
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
 * String Functions - NetHack uses these extensively
 */
void test_string_functions(void) {
    char buf1[128];
    char buf2[128];
    char buf3[128];
    
    printf("\n=== String Functions ===\n");
    
    /* strlen */
    TEST_ASSERT(strlen("") == 0, "strlen empty string");
    TEST_ASSERT(strlen("hello") == 5, "strlen normal string");
    TEST_ASSERT(strlen("NetHack") == 7, "strlen 'NetHack'");
    
    /* strcpy */
    strcpy(buf1, "test");
    TEST_ASSERT(strcmp(buf1, "test") == 0, "strcpy basic");
    strcpy(buf1, "");
    TEST_ASSERT(strcmp(buf1, "") == 0, "strcpy empty string");
    
    /* strncpy */
    strncpy(buf1, "abcdefgh", 4);
    buf1[4] = '\0';
    TEST_ASSERT(strcmp(buf1, "abcd") == 0, "strncpy with limit");
    strncpy(buf1, "xy", 10);
    TEST_ASSERT(buf1[0] == 'x' && buf1[1] == 'y' && buf1[2] == '\0', "strncpy shorter than limit");
    
    /* strcmp */
    TEST_ASSERT(strcmp("abc", "abc") == 0, "strcmp equal");
    TEST_ASSERT(strcmp("abc", "xyz") < 0, "strcmp less than");
    TEST_ASSERT(strcmp("xyz", "abc") > 0, "strcmp greater than");
    TEST_ASSERT(strcmp("", "") == 0, "strcmp empty strings");
    
    /* strncmp */
    TEST_ASSERT(strncmp("abcdef", "abcxyz", 3) == 0, "strncmp first 3 match");
    TEST_ASSERT(strncmp("abcdef", "abcxyz", 4) != 0, "strncmp first 4 differ");
    
    /* strcat */
    strcpy(buf1, "Hello");
    strcat(buf1, " World");
    TEST_ASSERT(strcmp(buf1, "Hello World") == 0, "strcat basic");
    
    /* strncat */
    strcpy(buf1, "Hello");
    strncat(buf1, " World", 3);
    TEST_ASSERT(strcmp(buf1, "Hello Wo") == 0, "strncat with limit");
    
    /* strchr */
    char *p = strchr("hello world", 'w');
    TEST_ASSERT(p != NULL && *p == 'w', "strchr found");
    p = strchr("hello", 'x');
    TEST_ASSERT(p == NULL, "strchr not found");
    
    /* strrchr */
    p = strrchr("hello world", 'o');
    TEST_ASSERT(p != NULL && *p == 'o' && *(p+1) == 'r', "strrchr finds last occurrence");
    
    /* strstr */
    p = strstr("the quick brown fox", "brown");
    TEST_ASSERT(p != NULL && strncmp(p, "brown", 5) == 0, "strstr found");
    p = strstr("hello", "xyz");
    TEST_ASSERT(p == NULL, "strstr not found");
    
    /* strcasecmp (if available) - NetHack uses this */
    #ifdef strcasecmp
    TEST_ASSERT(strcasecmp("Hello", "HELLO") == 0, "strcasecmp case insensitive");
    TEST_ASSERT(strcasecmp("abc", "xyz") < 0, "strcasecmp ordering");
    #endif
}

/*
 * Memory Functions - Critical for NetHack
 */
void test_memory_functions(void) {
    char buf1[128];
    char buf2[128];
    char buf3[128];
    
    printf("\n=== Memory Functions ===\n");
    
    /* memset */
    memset(buf1, 'A', 10);
    buf1[10] = '\0';
    TEST_ASSERT(strcmp(buf1, "AAAAAAAAAA") == 0, "memset basic");
    memset(buf1, 0, 128);
    TEST_ASSERT(buf1[0] == 0 && buf1[127] == 0, "memset zeros");
    
    /* memcpy */
    strcpy(buf1, "source data");
    memcpy(buf2, buf1, 12);
    TEST_ASSERT(strcmp(buf2, "source data") == 0, "memcpy basic");
    
    /* memmove (handles overlapping regions) */
    strcpy(buf1, "0123456789");
    memmove(buf1 + 2, buf1, 5);  /* Overlap */
    TEST_ASSERT(buf1[2] == '0' && buf1[3] == '1', "memmove overlapping");
    
    /* memcmp */
    TEST_ASSERT(memcmp("abc", "abc", 3) == 0, "memcmp equal");
    TEST_ASSERT(memcmp("abc", "abd", 3) < 0, "memcmp less than");
    TEST_ASSERT(memcmp("xyz", "abc", 3) > 0, "memcmp greater than");
    
    /* memchr */
    char *p = (char *)memchr("hello world", 'w', 11);
    TEST_ASSERT(p != NULL && *p == 'w', "memchr found");
    p = (char *)memchr("hello", 'x', 5);
    TEST_ASSERT(p == NULL, "memchr not found");
}

/*
 * Character Classification - NetHack uses for parsing
 */
void test_ctype_functions(void) {
    printf("\n=== Character Classification ===\n");
    
    /* isalpha */
    TEST_ASSERT(isalpha('a') && isalpha('Z'), "isalpha letters");
    TEST_ASSERT(!isalpha('5') && !isalpha('@'), "isalpha non-letters");
    
    /* isdigit */
    TEST_ASSERT(isdigit('0') && isdigit('9'), "isdigit numbers");
    TEST_ASSERT(!isdigit('a') && !isdigit(' '), "isdigit non-numbers");
    
    /* isalnum */
    TEST_ASSERT(isalnum('a') && isalnum('5'), "isalnum alphanumeric");
    TEST_ASSERT(!isalnum('@') && !isalnum(' '), "isalnum non-alphanumeric");
    
    /* isspace */
    TEST_ASSERT(isspace(' ') && isspace('\t') && isspace('\n'), "isspace whitespace");
    TEST_ASSERT(!isspace('a') && !isspace('5'), "isspace non-whitespace");
    
    /* isupper / islower */
    TEST_ASSERT(isupper('A') && isupper('Z'), "isupper uppercase");
    TEST_ASSERT(!isupper('a') && !isupper('5'), "isupper non-uppercase");
    TEST_ASSERT(islower('a') && islower('z'), "islower lowercase");
    TEST_ASSERT(!islower('A') && !islower('5'), "islower non-lowercase");
    
    /* toupper / tolower */
    TEST_ASSERT(toupper('a') == 'A', "toupper lowercase");
    TEST_ASSERT(toupper('5') == '5', "toupper non-letter");
    TEST_ASSERT(tolower('Z') == 'z', "tolower uppercase");
    TEST_ASSERT(tolower('5') == '5', "tolower non-letter");
    
    /* isprint / isgraph */
    TEST_ASSERT(isprint('a') && isprint(' '), "isprint printable");
    TEST_ASSERT(!isprint('\n') && !isprint(0x7F), "isprint non-printable");
    TEST_ASSERT(isgraph('a') && isgraph('@'), "isgraph graphic");
    TEST_ASSERT(!isgraph(' ') && !isgraph('\t'), "isgraph non-graphic");
}

/*
 * Conversion Functions - NetHack uses for parsing
 */
void test_conversion_functions(void) {
    printf("\n=== Conversion Functions ===\n");
    
    /* atoi */
    TEST_ASSERT(atoi("42") == 42, "atoi positive");
    TEST_ASSERT(atoi("-123") == -123, "atoi negative");
    TEST_ASSERT(atoi("0") == 0, "atoi zero");
    TEST_ASSERT(atoi("  456") == 456, "atoi with leading spaces");
    
    /* atol */
    TEST_ASSERT(atol("123456") == 123456L, "atol large number");
    TEST_ASSERT(atol("-999") == -999L, "atol negative");
    
    /* strtol */
    char *endptr;
    long val = strtol("123abc", &endptr, 10);
    TEST_ASSERT(val == 123 && *endptr == 'a', "strtol with remainder");
    val = strtol("0xFF", &endptr, 16);
    TEST_ASSERT(val == 255, "strtol hexadecimal");
    val = strtol("101", &endptr, 2);
    TEST_ASSERT(val == 5, "strtol binary");
    
    /* strtoul */
    unsigned long uval = strtoul("4294967295", &endptr, 10);
    TEST_ASSERT(uval == 4294967295UL, "strtoul max unsigned");
}

/*
 * sprintf/snprintf - NetHack uses heavily for message formatting
 */
void test_sprintf_functions(void) {
    char buf[256];
    int n;
    
    printf("\n=== sprintf/snprintf Functions ===\n");
    
    /* sprintf - basic formatting */
    sprintf(buf, "Value: %d", 42);
    TEST_ASSERT(strcmp(buf, "Value: 42") == 0, "sprintf integer");
    
    sprintf(buf, "String: %s", "test");
    TEST_ASSERT(strcmp(buf, "String: test") == 0, "sprintf string");
    
    sprintf(buf, "Hex: 0x%x", 255);
    TEST_ASSERT(strcmp(buf, "Hex: 0xff") == 0, "sprintf hex lowercase");
    
    sprintf(buf, "Hex: 0x%X", 255);
    TEST_ASSERT(strcmp(buf, "Hex: 0xFF") == 0, "sprintf hex uppercase");
    
    sprintf(buf, "Char: %c", 'A');
    TEST_ASSERT(strcmp(buf, "Char: A") == 0, "sprintf character");
    
    sprintf(buf, "Multiple: %d %s %c", 1, "two", '3');
    TEST_ASSERT(strcmp(buf, "Multiple: 1 two 3") == 0, "sprintf multiple args");
    
    /* Width and precision */
    sprintf(buf, "%5d", 42);
    TEST_ASSERT(strcmp(buf, "   42") == 0, "sprintf width padding");
    
    sprintf(buf, "%-5d", 42);
    TEST_ASSERT(strcmp(buf, "42   ") == 0, "sprintf left align");
    
    sprintf(buf, "%05d", 42);
    TEST_ASSERT(strcmp(buf, "00042") == 0, "sprintf zero padding");
    
    sprintf(buf, "%.3s", "hello");
    TEST_ASSERT(strcmp(buf, "hel") == 0, "sprintf string precision");
    
    /* snprintf - size limiting */
    n = snprintf(buf, 10, "This is a very long string");
    TEST_ASSERT(n > 10 && strlen(buf) == 9, "snprintf truncation");
    
    n = snprintf(buf, 50, "Short");
    TEST_ASSERT(n == 5 && strcmp(buf, "Short") == 0, "snprintf no truncation");
}

/*
 * malloc/free - NetHack allocates memory dynamically
 */
void test_malloc_free(void) {
    printf("\n=== malloc/free ===\n");
    
    /* Basic allocation */
    void *ptr1 = malloc(100);
    TEST_ASSERT(ptr1 != NULL, "malloc 100 bytes");
    free(ptr1);
    
    /* Multiple allocations */
    void *ptrs[10];
    int i;
    for (i = 0; i < 10; i++) {
        ptrs[i] = malloc(1024);
        TEST_ASSERT(ptrs[i] != NULL, "malloc in loop");
    }
    for (i = 0; i < 10; i++) {
        free(ptrs[i]);
    }
    
    /* Large allocation */
    void *big = malloc(100000);
    TEST_ASSERT(big != NULL, "malloc 100KB");
    memset(big, 0x55, 100000);
    TEST_ASSERT(((char*)big)[0] == 0x55 && ((char*)big)[99999] == 0x55, "large block writable");
    free(big);
    
    /* calloc */
    char *zeros = (char *)calloc(100, 1);
    TEST_ASSERT(zeros != NULL, "calloc allocation");
    int all_zero = 1;
    for (i = 0; i < 100; i++) {
        if (zeros[i] != 0) all_zero = 0;
    }
    TEST_ASSERT(all_zero, "calloc zeros memory");
    free(zeros);
    
    /* realloc */
    char *ptr = (char *)malloc(10);
    strcpy(ptr, "test");
    ptr = (char *)realloc(ptr, 100);
    TEST_ASSERT(ptr != NULL && strcmp(ptr, "test") == 0, "realloc preserves data");
    free(ptr);
}

/*
 * Time Functions - NetHack uses for seeding RNG and tracking time
 */
void test_time_functions(void) {
    printf("\n=== Time Functions ===\n");
    
    /* time() - current time */
    time_t t1 = time(NULL);
    TEST_ASSERT(t1 > 0, "time() returns value");
    
    /* Timer-based operations */
    unsigned int start_ms = *TIMER_MS;
    volatile int i;
    for (i = 0; i < 10000; i++);  /* Busy wait */
    unsigned int end_ms = *TIMER_MS;
    TEST_ASSERT(end_ms >= start_ms, "timer increments");
    
    /* struct tm operations would go here if needed */
}

/*
 * Random Number Functions - NetHack needs good RNG
 */
void test_random_functions(void) {
    printf("\n=== Random Number Functions ===\n");
    
    /* rand/srand */
    srand(12345);
    int r1 = rand();
    int r2 = rand();
    TEST_ASSERT(r1 != r2, "rand produces different values");
    
    /* Seeding produces same sequence */
    srand(12345);
    int r3 = rand();
    TEST_ASSERT(r1 == r3, "srand produces deterministic sequence");
    
    /* Range check */
    srand(*TIMER_MS);  /* Seed with timer */
    int in_range = 1;
    int i;
    for (i = 0; i < 100; i++) {
        int r = rand();
        if (r < 0 || r > RAND_MAX) in_range = 0;
    }
    TEST_ASSERT(in_range, "rand values within RAND_MAX");
    
    /* RAND_MAX is defined */
    TEST_ASSERT(RAND_MAX > 0, "RAND_MAX defined and positive");
}

/*
 * Miscellaneous Functions NetHack might use
 */

/* Comparison function for qsort/bsearch */
int compare_ints(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}

void test_misc_functions(void) {
    printf("\n=== Miscellaneous Functions ===\n");
    
    /* abs */
    TEST_ASSERT(abs(-42) == 42, "abs negative");
    TEST_ASSERT(abs(42) == 42, "abs positive");
    TEST_ASSERT(abs(0) == 0, "abs zero");
    
    /* labs */
    TEST_ASSERT(labs(-123456L) == 123456L, "labs negative");
    
    /* div (integer division) */
    div_t result = div(17, 5);
    TEST_ASSERT(result.quot == 3 && result.rem == 2, "div quotient and remainder");
    
    /* qsort - NetHack uses for sorting */
    int arr[] = {5, 2, 8, 1, 9, 3};
    qsort(arr, 6, sizeof(int), compare_ints);
    TEST_ASSERT(arr[0] == 1 && arr[5] == 9, "qsort ascending order");
    TEST_ASSERT(arr[1] == 2 && arr[2] == 3 && arr[3] == 5 && arr[4] == 8, "qsort complete");
    
    /* bsearch - binary search */
    int key = 5;
    int *found = (int *)bsearch(&key, arr, 6, sizeof(int), compare_ints);
    TEST_ASSERT(found != NULL && *found == 5, "bsearch finds element");
    
    key = 99;
    found = (int *)bsearch(&key, arr, 6, sizeof(int), compare_ints);
    TEST_ASSERT(found == NULL, "bsearch returns NULL for missing element");
}

/*
 * Main test runner
 */
int main(void) {
    printf("\n");
    printf("================================================================================\n");
    printf("PyRV32 libc Test Suite for NetHack Requirements\n");
    printf("================================================================================\n");
    
    unsigned int start_time = *TIMER_MS;
    
    test_string_functions();
    test_memory_functions();
    test_ctype_functions();
    test_conversion_functions();
    test_sprintf_functions();
    test_malloc_free();
    test_time_functions();
    test_random_functions();
    test_misc_functions();
    
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
        printf("\n✓ All tests PASSED - libc ready for NetHack!\n");
        printf("\n");
        return 0;
    } else {
        printf("\n✗ Some tests FAILED - review failures above\n");
        printf("\n");
        return 1;
    }
}
