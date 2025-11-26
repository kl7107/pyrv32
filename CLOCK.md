# Real-Time Clock Registers

PyRV32 provides three time-related memory-mapped registers for precise timing and real-world clock access.

## Memory Map

| Address    | Name        | Type      | Description |
|------------|-------------|-----------|-------------|
| 0x10000004 | TIMER_MS    | Read-only | Milliseconds since program start (32-bit, wraps at ~49 days) |
| 0x10000008 | CLOCK_TIME  | Read-only | Unix time - seconds since epoch (32-bit, valid until 2038) |
| 0x1000000C | CLOCK_NSEC  | Read-only | Nanoseconds within current second (32-bit, 0-999,999,999) |

## Usage Examples

### C Code (Direct Register Access)

```c
#define TIMER_MS   ((volatile unsigned int *)0x10000004)
#define CLOCK_TIME ((volatile unsigned int *)0x10000008)
#define CLOCK_NSEC ((volatile unsigned int *)0x1000000C)

/* Get elapsed time since program start */
unsigned int elapsed_ms = *TIMER_MS;
printf("Program running for %u ms\n", elapsed_ms);

/* Get current Unix time */
unsigned int unix_time = *CLOCK_TIME;
printf("Unix time: %u\n", unix_time);

/* Get high-precision time */
unsigned int seconds = *CLOCK_TIME;
unsigned int nanos = *CLOCK_NSEC;
printf("Current time: %u.%09u seconds\n", seconds, nanos);
```

### C Code (Standard Library)

The syscalls layer implements `time()` and `gettimeofday()` using these registers:

```c
#include <time.h>
#include <sys/time.h>

/* Get Unix time (seconds) */
time_t t = time(NULL);
printf("Unix time: %ld\n", (long)t);

/* Get high-precision time */
struct timeval tv;
gettimeofday(&tv, NULL);
printf("Time: %ld.%06ld seconds\n", 
       (long)tv.tv_sec, (long)tv.tv_usec);
```

### Assembly Code

```asm
# Read timer (milliseconds)
lui  t0, 0x10000
lw   a0, 4(t0)         # a0 = milliseconds since start

# Read Unix time (seconds)
lui  t0, 0x10000
lw   a0, 8(t0)         # a0 = Unix time

# Read nanoseconds
lui  t0, 0x10000
lw   a0, 12(t0)        # a0 = nanoseconds within second
```

## Implementation Details

### TIMER_MS (0x10000004)
- 32-bit counter initialized to 0 when program starts
- Increments in milliseconds based on host system time
- Wraps around at 2^32 ms (~49.7 days)
- Useful for measuring elapsed time and timeouts

### CLOCK_TIME (0x10000008)
- 32-bit Unix timestamp (seconds since Jan 1, 1970 00:00:00 UTC)
- Reads host system's real-time clock
- Valid until year 2038 (Y2038 problem with 32-bit timestamps)
- Used by `time()` and `gettimeofday()`

### CLOCK_NSEC (0x1000000C)
- 32-bit nanosecond counter (0 to 999,999,999)
- Represents fractional seconds within current second
- Provides sub-second precision for timing measurements
- Combined with CLOCK_TIME for full precision in `gettimeofday()`

## Performance Notes

- All registers are **read-only** (writes are ignored)
- Reads are instantaneous (no actual hardware delay)
- Clock registers reflect host system time, so they advance even when the emulator is paused
- For performance benchmarking, use TIMER_MS (doesn't include emulator overhead)

## Use Cases

### Elapsed Time Measurement
```c
unsigned int start = *TIMER_MS;
do_work();
unsigned int end = *TIMER_MS;
printf("Work took %u ms\n", end - start);
```

### Real-World Timestamps
```c
time_t now = time(NULL);
struct tm *tm = localtime(&now);
printf("Current time: %04d-%02d-%02d %02d:%02d:%02d\n",
       tm->tm_year + 1900, tm->tm_mon + 1, tm->tm_mday,
       tm->tm_hour, tm->tm_min, tm->tm_sec);
```

### High-Precision Timing
```c
struct timeval start, end;
gettimeofday(&start, NULL);
do_work();
gettimeofday(&end, NULL);

long elapsed_us = (end.tv_sec - start.tv_sec) * 1000000 +
                  (end.tv_usec - start.tv_usec);
printf("Work took %ld microseconds\n", elapsed_us);
```

### Random Number Seeding
```c
#include <stdlib.h>
#include <time.h>

/* Seed RNG with current time */
srand(time(NULL));
int random_value = rand();
```

## Testing

Run the clock test to verify all registers work correctly:

```bash
cd pyrv32/firmware
make clock_test
```

Expected output:
- 15/15 tests passing
- Verification of Unix time, nanoseconds, timer independence
- Demonstration of `time()` and `gettimeofday()` functions
