#include <errno.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <unistd.h>

#define die(msg, args...)\
    fprintf(stderr, msg "\n", ##args);\
    exit(1);

extern uint64_t fib(int n);

static void
baz()
{
    printf("%lu\n", fib(100));
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

static uintptr_t
apply_text_segment_offset(uintptr_t offset)
{
    char *line = NULL;
    size_t length;
    FILE *fp;
    ssize_t bytes_read;
    char exe_path[PATH_MAX + 1];
    uintptr_t result = 0;

    bytes_read = readlink("/proc/self/exe", exe_path, PATH_MAX);

    if(bytes_read == -1) {
        return -1;
    }
    exe_path[bytes_read] = '\0';

    fp = fopen("/proc/self/maps", "r");

    if(!fp) {
        return -1;
    }

    while(getline(&line, &length, fp) != -1) {
        char *cursor = NULL;
        char *token;

        uintptr_t region_start;
        uintptr_t file_offset;

        // parse the start address for the region
        token = strtok_r(line, " ", &cursor);
        *strchr(token, '-') = '\0';
        region_start = strtoul(token, NULL, 16);

        // grab the permissions - if the region we're looking at doesn't have
        // execute permissions, it's not a text segment so skip it
        token = strtok_r(NULL, " ", &cursor);
        if(!strchr(token, 'x')) {
            continue;
        }

        // parse the offset field
        token = strtok_r(NULL, " ", &cursor);
        file_offset = strtoul(token, NULL, 16);

        // skip the dev and inode fields
        strtok_r(NULL, " ", &cursor);
        strtok_r(NULL, " ", &cursor);

        // get the pathname field
        token = strtok_r(NULL, " ", &cursor);

        // strip trailing newlines
        while(strlen(token) && token[strlen(token) - 1] == '\n') {
            token[strlen(token) - 1] = '\0';
        }

        // if we're looking at a region that doesn't correspond to our executable, move along
        if(strcmp(token, exe_path)) {
            continue;
        }

        // XXX make sure the offset is before the region end?
        // XXX make sure it's set exactly once?
        result = region_start + offset - file_offset;
    }

    free(line);

    if(!feof(fp)) {
        fclose(fp);
        return -1;
    }

    fclose(fp);

    return result;
}

int
main(int argc, char **argv)
{
    pid_t tracee;
    int status;
    const char *target_expr;
    uintptr_t breakpoint_addr;

    if(argc < 3) {
        die("usage: %s [breakpoint] [expr]", argv[0]);
    }

    breakpoint_addr = strtoul(argv[1], NULL, 16);
    breakpoint_addr = apply_text_segment_offset(breakpoint_addr);

    target_expr = argv[2];

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
                    extern uint64_t a, b;
                    uint64_t *target;
                    long target_value;

                    if(!strcmp(target_expr, "a")) {
                        target = &a;
                    } else if(!strcmp(target_expr, "b")) {
                        target = &b;
                    } else {
                        fprintf(stderr, "invalid target expression '%s'\n", target_expr);
                    }

                    target_value = ptrace(PTRACE_PEEKDATA, tracee, target, 0);
                    // XXX distinguish between failure and actual value of -1?
                    if(target_value == -1) {
                        fprintf(stderr, "unable to peek at target expression: %s\n", strerror(errno));
                        break;
                    }

                    printf("%ld\n", target_value);

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

    return 0;
}
