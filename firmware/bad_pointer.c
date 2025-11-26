/*
 * bad_pointer.c - Test memory access fault detection
 *
 * This program intentionally accesses invalid memory to verify
 * that the emulator properly detects and reports memory faults.
 */

#include <stdint.h>

void uart_putc(char c);
void uart_puts(const char *s);
void uart_putln(const char *s);

int main() {
    uart_putln("Testing memory access fault detection...");
    
    // Try to read from invalid address (outside RAM and UART)
    uart_puts("Reading from 0x00000000... ");
    
    volatile uint32_t *bad_ptr = (uint32_t*)0x00000000;
    uint32_t value = *bad_ptr;  // Should trigger memory access fault
    
    uart_puts("ERROR: Should not reach here!\n");
    (void)value;  // Suppress unused warning
    
    return 0;
}
