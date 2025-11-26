/*
 * Minimal malloc/free for embedded systems
 */

#ifndef _STDLIB_H
#define _STDLIB_H

/* Simple bump allocator for Dhrystone */
static char heap[8192];  /* 8KB heap */
static char *heap_ptr = heap;

void *malloc(unsigned int size) {
    void *ptr = heap_ptr;
    /* Align to 4 bytes */
    size = (size + 3) & ~3;
    heap_ptr += size;
    
    /* Simple check to prevent overflow */
    if (heap_ptr > heap + sizeof(heap)) {
        return 0;  /* Out of memory */
    }
    
    return ptr;
}

void free(void *ptr) {
    /* Simple allocator doesn't support free */
}

#endif /* _STDLIB_H */
