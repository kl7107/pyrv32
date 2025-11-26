/*
 * Minimal string library for Dhrystone
 */

#ifndef _STRING_H
#define _STRING_H

static inline int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(unsigned char *)s1 - *(unsigned char *)s2;
}

static inline char *strcpy(char *dest, const char *src) {
    char *ret = dest;
    while ((*dest++ = *src++));
    return ret;
}

static inline int strlen(const char *s) {
    int len = 0;
    while (*s++) len++;
    return len;
}

#endif /* _STRING_H */
