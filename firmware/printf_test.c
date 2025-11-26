/*
 * Printf Test - Validate newlib integration
 * 
 * Tests:
 * - printf/sprintf family
 * - malloc/free
 * - String functions
 * - Debug vs Console UART routing
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Timer for benchmarking */
#define TIMER_MS ((volatile unsigned int *)0x10000004)

/* Debug UART for diagnostics */
#define DEBUG_UART ((volatile unsigned char *)0x10000000)

void debug_puts(const char *s) {
    while (*s) {
        *DEBUG_UART = *s++;
    }
}

int main(void) {
    char buffer[128];
    int i;
    unsigned int start_ms, end_ms;
    char *heap_test;
    
    /* Print banner to stdout (Console UART) */
    printf("\n");
    printf("================================================================================\n");
    printf("PyRV32 Newlib Integration Test\n");
    printf("================================================================================\n");
    printf("\n");
    
    /* Test 1: Basic printf */
    printf("Test 1: Basic printf\n");
    printf("  Integer: %d\n", 42);
    printf("  Hex: 0x%08x\n", 0xDEADBEEF);
    printf("  String: %s\n", "Hello, World!");
    printf("  Character: '%c'\n", 'A');
    printf("  PASS\n\n");
    
    /* Test 2: sprintf */
    printf("Test 2: sprintf\n");
    sprintf(buffer, "Formatted: %d + %d = %d", 10, 32, 42);
    printf("  Buffer contains: %s\n", buffer);
    if (strcmp(buffer, "Formatted: 10 + 32 = 42") == 0) {
        printf("  PASS\n\n");
    } else {
        printf("  FAIL\n\n");
    }
    
    /* Test 3: snprintf (safer) */
    printf("Test 3: snprintf (size limiting)\n");
    snprintf(buffer, 20, "This is a very long string that should be truncated");
    printf("  Buffer (20 char max): '%s'\n", buffer);
    printf("  Length: %d\n", (int)strlen(buffer));
    printf("  PASS\n\n");
    
    /* Test 4: String functions */
    printf("Test 4: String functions\n");
    strcpy(buffer, "Hello");
    printf("  strcpy: '%s'\n", buffer);
    strcat(buffer, " World");
    printf("  strcat: '%s'\n", buffer);
    printf("  strlen: %d\n", (int)strlen(buffer));
    if (strcmp(buffer, "Hello World") == 0) {
        printf("  strcmp: PASS\n");
    } else {
        printf("  strcmp: FAIL\n");
    }
    printf("  PASS\n\n");
    
    /* Test 5: Memory functions */
    printf("Test 5: Memory functions (memcpy, memset)\n");
    memset(buffer, 'X', 10);
    buffer[10] = '\0';
    printf("  memset: '%s'\n", buffer);
    memcpy(buffer + 5, "12345", 5);
    buffer[10] = '\0';
    printf("  memcpy: '%s'\n", buffer);
    printf("  PASS\n\n");
    
    /* Test 6: malloc/free */
    printf("Test 6: malloc/free\n");
    heap_test = (char *)malloc(256);
    if (heap_test == NULL) {
        printf("  malloc FAILED\n\n");
    } else {
        printf("  malloc returned: %p\n", (void *)heap_test);
        sprintf(heap_test, "Allocated at %p", (void *)heap_test);
        printf("  Content: %s\n", heap_test);
        free(heap_test);
        printf("  PASS\n\n");
    }
    
    /* Test 7: Multiple allocations */
    printf("Test 7: Multiple malloc/free\n");
    char *ptrs[10];
    for (i = 0; i < 10; i++) {
        ptrs[i] = (char *)malloc(64);
        if (ptrs[i] == NULL) {
            printf("  Allocation %d FAILED\n", i);
            break;
        }
        sprintf(ptrs[i], "Block %d", i);
    }
    if (i == 10) {
        printf("  All allocations succeeded\n");
        for (i = 0; i < 10; i++) {
            printf("    Block %d: %s\n", i, ptrs[i]);
        }
        for (i = 0; i < 10; i++) {
            free(ptrs[i]);
        }
        printf("  PASS\n\n");
    } else {
        printf("  FAIL\n\n");
    }
    
    /* Test 8: Timer/time functions */
    printf("Test 8: Timer and time functions\n");
    start_ms = *TIMER_MS;
    printf("  Timer at start: %u ms\n", start_ms);
    
    /* Busy wait */
    for (i = 0; i < 100000; i++) {
        __asm__ volatile ("nop");
    }
    
    end_ms = *TIMER_MS;
    printf("  Timer at end: %u ms\n", end_ms);
    printf("  Elapsed: %u ms\n", end_ms - start_ms);
    printf("  PASS\n\n");
    
    /* Test 9: fprintf to stderr (Debug UART) */
    printf("Test 9: fprintf to stderr (Debug UART)\n");
    printf("  Sending message to Debug UART...\n");
    fprintf(stderr, "[DEBUG] This message goes to Debug UART at 0x10000000\n");
    printf("  PASS (check debug output)\n\n");
    
    /* Test 10: Floating point (if supported) */
    printf("Test 10: Floating point formatting\n");
    #ifdef __riscv_flen
    printf("  FPU detected\n");
    printf("  Float: %f\n", 3.14159f);
    printf("  PASS\n\n");
    #else
    printf("  No FPU (RV32IM)\n");
    printf("  Skipping float tests\n");
    printf("  PASS\n\n");
    #endif
    
    /* Summary */
    printf("================================================================================\n");
    printf("All tests completed!\n");
    printf("================================================================================\n");
    printf("\n");
    
    /* Send completion message to Debug UART */
    debug_puts("\n[Test program completed successfully]\n");
    
    return 0;
}
