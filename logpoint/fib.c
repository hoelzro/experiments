#include <signal.h>

extern int breakpoint_line_no;

#define maybe_breakpoint()\
    if(__LINE__ == breakpoint_line_no)\
        raise(SIGTRAP);

// globals for now
long long a;
long long b;

long long
fib(int n)
{
    int i;

    a = 1;
    b = 0;

    maybe_breakpoint();

    for(i = 0; i < n; i++) {
        maybe_breakpoint();

        long long new_b = a + b;
        a = b;
        b = new_b;
    }

    maybe_breakpoint();

    return b;
}
