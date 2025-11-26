/*
 * bad_uart_offset.c - Test UART boundary checking
 *
 * Verify that only 0x10000000 is valid, not 0x10000001+
 */

#include <stdint.h>

void uart_putln(const char *s);

int main() {
    uart_putln("Testing UART boundary...");
    
    // Valid UART access
    volatile uint8_t *uart_tx = (uint8_t*)0x10000000;
    *uart_tx = 'O';
    *uart_tx = 'K';
    *uart_tx = '\n';
    
    // Invalid: UART + 1 (should fault)
    volatile uint8_t *bad_uart = (uint8_t*)0x10000001;
    *bad_uart = 'X';  // Should trigger fault
    
    uart_putln("ERROR: Should not reach here!");
    
    return 0;
}
