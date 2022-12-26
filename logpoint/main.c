#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
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
main(int argc, char **argv)
{
    pid_t tracee;
    int status;

    if(argc < 2) {
        die("usage: %s [breakpoint]", argv[0]);
    }

    breakpoint_line_no = atoi(argv[1]);

    tracee = fork();
    if(tracee == -1) {
        die("unable to spawn tracee process: %s", strerror(errno));
    }

    if(tracee) {
        while(1) {
            int exit_status;

            status = waitpid(tracee, &exit_status, 0);
            if(status == -1) {
                fprintf(stderr, "failed to wait for tracee: %s\n", strerror(errno));
                break;
            } else {
                if(!WIFSTOPPED(exit_status)) {
                    if(WIFEXITED(exit_status)) {
                        printf("exit status for tracee: %d\n", WEXITSTATUS(exit_status));
                    } else if(WIFSIGNALED(exit_status)) {
                        printf("exit signal for tracee: %d\n", WTERMSIG(exit_status));
                    } else {
                        printf("some other trace event =S (0x%x)\n", exit_status);
                    }

                    break;
                }

                if(WSTOPSIG(exit_status) == SIGTRAP) {
                    printf("tracee hit a breakpoint\n");
                    status = ptrace(PTRACE_CONT, tracee, 0, 0);
                } else {
                    status = ptrace(PTRACE_CONT, tracee, 0, WSTOPSIG(exit_status));
                }

                if(status == -1) {
                    fprintf(stderr, "Unable to resume tracee: %s\n", strerror(errno));
                    break;
                }
            }
        }
    } else {
        status = ptrace(PTRACE_TRACEME, 0, 0, 0);
        if(status == -1) {
            die("unable to set tracee up for tracing: %s", strerror(errno));
        }

        // XXX set options so we die if our parent does?

        foo();
        return 0;
    }

    // XXX pause the thread upon break, then print the target symbol, then resume the thread
    return 0;
}
