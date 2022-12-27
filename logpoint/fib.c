#include <stdint.h>
#include <signal.h>

#define maybe_breakpoint()\
    asm("nop")

// globals for now
uint64_t a;
uint64_t b;

uint64_t
fib(int n)
{
    int i;

    a = 1;
    b = 0;

    maybe_breakpoint();

    for(i = 0; i < n; i++) {
        maybe_breakpoint();

        uint64_t new_b = a + b;
        a = b;
        b = new_b;
    }

    maybe_breakpoint();

    return b;
}
