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
        int exit_status;

        // wait for the tracee to trap itself so that we can set up ptrace options
        status = waitpid(tracee, &exit_status, 0);
        if(status == -1) {
            die("failed to wait for tracee: %s", strerror(errno));
        }

        if(!WIFSTOPPED(exit_status) || WSTOPSIG(exit_status) != SIGTRAP) {
            die("expected the tracee to trap itself, but it didn't =S\n");
        }

        status = ptrace(PTRACE_SETOPTIONS, tracee, 0, PTRACE_O_EXITKILL);
        if(status == -1) {
            die("unable to set up ptrace options: %s", strerror(errno));
        }

        status = ptrace(PTRACE_CONT, tracee, 0, 0);
        if(status == -1) {
            die("unable to resume tracee: %s", strerror(errno));
        }

        while(1) {
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

        // throw in an artificial trap so that we can set options from the parent
        raise(SIGTRAP);

        foo();
        return 0;
    }

    // XXX pause the thread upon break, then print the target symbol, then resume the thread
    return 0;
}
