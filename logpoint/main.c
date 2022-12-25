#include <stdio.h>

extern long long fib(int n);

int breakpoint_line_no;

static void
baz()
{
    printf("%d\n", fib(100));
}

static void
bar()
{
    baz();
}

static void
foo()
{
    bar();
}

int
main(void)
{
    breakpoint_line_no = 0;
    foo();
    return 0;
}
