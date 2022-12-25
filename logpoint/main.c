#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

#define die(msg, args...)\
    fprintf(stderr, msg "\n", ##args);\
    exit(1);

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
    pid_t tracee;
    int status;

    breakpoint_line_no = 0;

    tracee = fork();
    if(tracee == -1) {
        die("unable to spawn tracee process: %s", strerror(errno));
    }

    if(tracee) {
        int exit_status;

        // XXX if SIGTRAP is raised, we need to pause the offending thread, *plus* inform
        //     the main thread that the offending thread was stopped
        printf("waiting on tracee child...\n");
        status = waitpid(tracee, &exit_status, 0);
        if(status == -1) {
            fprintf(stderr, "failed to wait for tracee: %s\n", strerror(errno));
        } else {
            printf("exit status for tracee: %d\n", exit_status);
        }
    } else {
        // XXX set me up as a tracee
        foo();
        return 0;
    }

    // XXX pause the thread upon break, then print the target symbol, then resume the thread
    return 0;
}
