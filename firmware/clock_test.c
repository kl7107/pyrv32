/*
 * Real-Time Clock Test
 * 
 * Tests the Unix time and nanosecond clock registers.
 */

#include <stdio.h>
#include <time.h>
#include <sys/time.h>

#define TIMER_MS   ((volatile unsigned int *)0x10000004)
#define CLOCK_TIME ((volatile unsigned int *)0x10000008)
#define CLOCK_NSEC ((volatile unsigned int *)0x1000000C)

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

void test_direct_register_access(void) {
    printf("\n=== Direct Register Access ===\n");
    
    /* Read millisecond timer */
    unsigned int ms1 = *TIMER_MS;
    printf("  Timer (ms): %u\n", ms1);
    TEST_ASSERT(ms1 >= 0, "Timer readable");
    
    /* Read Unix time */
    unsigned int unix_time = *CLOCK_TIME;
    printf("  Unix time: %u (0x%08x)\n", unix_time, unix_time);
    TEST_ASSERT(unix_time > 1700000000, "Unix time reasonable (after 2023)");
    TEST_ASSERT(unix_time < 2000000000, "Unix time reasonable (before 2033)");
    
    /* Read nanoseconds */
    unsigned int nsec = *CLOCK_NSEC;
    printf("  Nanoseconds: %u\n", nsec);
    TEST_ASSERT(nsec < 1000000000, "Nanoseconds within valid range");
}

void test_clock_increments(void) {
    printf("\n=== Clock Increments ===\n");
    
    unsigned int time1 = *CLOCK_TIME;
    unsigned int nsec1 = *CLOCK_NSEC;
    
    /* Busy wait a bit */
    volatile int i;
    for (i = 0; i < 100000; i++);
    
    unsigned int time2 = *CLOCK_TIME;
    unsigned int nsec2 = *CLOCK_NSEC;
    
    printf("  Time1: %u.%09u\n", time1, nsec1);
    printf("  Time2: %u.%09u\n", time2, nsec2);
    
    /* Time should have incremented (or stayed same in very fast execution) */
    TEST_ASSERT(time2 >= time1, "Time doesn't go backwards");
    
    /* If same second, nanoseconds should have increased (or wrapped to next second) */
    if (time2 == time1) {
        TEST_ASSERT(nsec2 >= nsec1, "Nanoseconds increment within same second");
    } else {
        printf("  (Clock advanced %u seconds during test - emulator is slow)\n", 
               time2 - time1);
    }
}

void test_time_function(void) {
    printf("\n=== time() Function ===\n");
    
    /* Use libc time() */
    time_t t = time(NULL);
    unsigned int clock_reg = *CLOCK_TIME;
    
    printf("  time(): %ld\n", (long)t);
    printf("  CLOCK_TIME: %u\n", clock_reg);
    
    /* Should be very close (within a second) */
    long diff = (long)t - (long)clock_reg;
    if (diff < 0) diff = -diff;
    
    TEST_ASSERT(diff <= 1, "time() matches CLOCK_TIME register");
}

void test_gettimeofday(void) {
    printf("\n=== gettimeofday() Function ===\n");
    
    struct timeval tv;
    int result = gettimeofday(&tv, NULL);
    
    printf("  Result: %d\n", result);
    printf("  tv_sec: %ld\n", (long)tv.tv_sec);
    printf("  tv_usec: %ld\n", (long)tv.tv_usec);
    
    TEST_ASSERT(result == 0, "gettimeofday succeeds");
    TEST_ASSERT(tv.tv_sec > 1700000000, "tv_sec reasonable");
    TEST_ASSERT(tv.tv_usec >= 0 && tv.tv_usec < 1000000, "tv_usec in valid range");
    
    /* Compare with direct register access */
    unsigned int clock_time = *CLOCK_TIME;
    unsigned int clock_nsec = *CLOCK_NSEC;
    unsigned int expected_usec = clock_nsec / 1000;
    
    printf("  Direct CLOCK_TIME: %u\n", clock_time);
    printf("  Direct CLOCK_NSEC: %u (= %u usec)\n", clock_nsec, expected_usec);
    
    /* Should match (allowing for tiny timing differences) */
    TEST_ASSERT((unsigned int)tv.tv_sec == clock_time || 
                (unsigned int)tv.tv_sec == clock_time + 1,
                "gettimeofday tv_sec matches register");
}

void test_clock_precision(void) {
    printf("\n=== Clock Precision ===\n");
    
    /* Read clock multiple times rapidly */
    unsigned int times[5];
    unsigned int nsecs[5];
    
    int i;
    for (i = 0; i < 5; i++) {
        times[i] = *CLOCK_TIME;
        nsecs[i] = *CLOCK_NSEC;
    }
    
    printf("  Rapid readings:\n");
    for (i = 0; i < 5; i++) {
        printf("    %d: %u.%09u\n", i, times[i], nsecs[i]);
    }
    
    /* All times should be within 1 second of first */
    int all_close = 1;
    for (i = 1; i < 5; i++) {
        if (times[i] < times[0] || times[i] > times[0] + 1) {
            all_close = 0;
        }
    }
    TEST_ASSERT(all_close, "Rapid reads stay close together");
    
    /* At least some nanosecond variation (unless very unlucky) */
    int has_variation = 0;
    for (i = 1; i < 5; i++) {
        if (nsecs[i] != nsecs[0]) {
            has_variation = 1;
            break;
        }
    }
    TEST_ASSERT(has_variation, "Nanoseconds show variation");
}

void test_timer_independence(void) {
    printf("\n=== Timer vs Clock Independence ===\n");
    
    unsigned int timer_ms = *TIMER_MS;
    unsigned int clock_time = *CLOCK_TIME;
    
    printf("  Timer (ms from start): %u\n", timer_ms);
    printf("  Clock (Unix time): %u\n", clock_time);
    
    /* Timer should be small (we just started) */
    TEST_ASSERT(timer_ms < 60000, "Timer shows elapsed ms (< 1 min)");
    
    /* Clock should be real Unix time */
    TEST_ASSERT(clock_time > 1700000000, "Clock shows real Unix time");
    
    /* They should be very different values */
    TEST_ASSERT(timer_ms != clock_time, "Timer and clock are independent");
}

int main(void) {
    printf("\n");
    printf("================================================================================\n");
    printf("PyRV32 Real-Time Clock Test\n");
    printf("================================================================================\n");
    
    unsigned int start_time = *TIMER_MS;
    
    test_direct_register_access();
    test_clock_increments();
    test_time_function();
    test_gettimeofday();
    test_clock_precision();
    test_timer_independence();
    
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
        printf("\n✓ All clock tests PASSED - Real-time clock working correctly!\n");
        printf("\n");
        return 0;
    } else {
        printf("\n✗ Some clock tests FAILED - review failures above\n");
        printf("\n");
        return 1;
    }
}
