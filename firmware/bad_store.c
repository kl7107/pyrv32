/*
 * bad_store.c - Test store fault detection
 */

#include <stdint.h>

void uart_putln(const char *s);

int main() {
    uart_putln("Testing store to invalid address...");
    
    // Try to write outside RAM (0x90000000 is way past our 8MB)
    volatile uint32_t *bad_ptr = (uint32_t*)0x90000000;
    *bad_ptr = 0xDEADBEEF;  // Should trigger store fault
    
    uart_putln("ERROR: Should not reach here!");
    
    return 0;
}
