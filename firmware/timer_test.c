/*
 * Test program for millisecond timer
 */

#define UART_TX  ((volatile char *)0x10000000)
#define TIMER_MS ((volatile unsigned int *)0x10000004)

void uart_print(const char *s) {
    while (*s) {
        *UART_TX = *s++;
    }
}

void uart_print_int(unsigned int val) {
    char buf[12];
    int i = 0;
    
    if (val == 0) {
        buf[i++] = '0';
    } else {
        while (val > 0) {
            buf[i++] = '0' + (val % 10);
            val /= 10;
        }
    }
    
    /* Reverse */
    for (int j = 0; j < i / 2; j++) {
        char tmp = buf[j];
        buf[j] = buf[i - 1 - j];
        buf[i - 1 - j] = tmp;
    }
    buf[i] = '\0';
    
    uart_print(buf);
}

/* Simple delay loop (not accurate, just burns time) */
void delay(int count) {
    volatile int i;
    for (i = 0; i < count; i++) {
        asm volatile("nop");
    }
}

int main(void) {
    unsigned int start, end, elapsed;
    
    uart_print("=== Millisecond Timer Test ===\n\n");
    
    /* Test 1: Read timer at start */
    start = *TIMER_MS;
    uart_print("Timer at start: ");
    uart_print_int(start);
    uart_print(" ms\n\n");
    
    /* Test 2: Multiple reads */
    uart_print("Reading timer 5 times with delays:\n");
    for (int i = 0; i < 5; i++) {
        unsigned int t = *TIMER_MS;
        uart_print("  Read ");
        uart_print_int(i + 1);
        uart_print(": ");
        uart_print_int(t);
        uart_print(" ms\n");
        delay(100000);  /* Burn some time */
    }
    uart_print("\n");
    
    /* Test 3: Measure elapsed time */
    uart_print("Measuring elapsed time for delay loop...\n");
    start = *TIMER_MS;
    delay(500000);
    end = *TIMER_MS;
    elapsed = end - start;
    
    uart_print("Start time:   ");
    uart_print_int(start);
    uart_print(" ms\n");
    uart_print("End time:     ");
    uart_print_int(end);
    uart_print(" ms\n");
    uart_print("Elapsed time: ");
    uart_print_int(elapsed);
    uart_print(" ms\n\n");
    
    uart_print("Timer test completed!\n");
    
    /* ebreak to exit */
    asm volatile("ebreak");
    
    return 0;
}
