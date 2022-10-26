#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>

#define die(fmt, args...)\
    fprintf(stderr, fmt "\n", ##args);\
    exit(1);

static char *
describe_poll_revents(int revents)
{
    char buffer[128] = {'\0'};

#define EVENT(mask)\
    if(revents & mask) {\
        strcat(buffer, #mask "|");\
    }

    EVENT(POLLIN);
    EVENT(POLLRDNORM);
    EVENT(POLLRDBAND);
    EVENT(POLLPRI);
    EVENT(POLLOUT);
    EVENT(POLLWRBAND);
    EVENT(POLLERR);
    EVENT(POLLHUP);
    EVENT(POLLNVAL);

#undef EVENT

    if(strlen(buffer)) {
        buffer[strlen(buffer) - 1] = '\0';
    }
    return strdup(buffer);
}

int
main(int argc, char **argv)
{
    int fd;
    int status;
    int input_buffer_size;
    const char *target = argv[1];
    struct pollfd pollfds[1];
    char *poll_description = NULL;

    fd = open(target, O_RDONLY);
    if(fd < 0) {
        die("Unable to open TTY %s: %s", target, strerror(errno));
    }

    pollfds[0].fd = fd;
    pollfds[0].events = POLLIN | POLLRDNORM | POLLRDBAND | POLLPRI | /*POLLOUT | POLLWRBAND |*/ POLLERR | POLLHUP;

    while(1) {
        status = poll(pollfds, 1, -1);
        if(status < 0) {
            die("Unable to poll TTY: %s", strerror(errno));
        }

        poll_description = describe_poll_revents(pollfds[0].revents);
        printf("got activity for TTY: %s\n", poll_description);
        free(poll_description);

        status = ioctl(fd, FIONREAD, &input_buffer_size);
        if(status == -1) {
            die("Unable to ioctl(..., FIONREAD): %s", strerror(errno));
        }
        printf("input buffer size: %d\n", input_buffer_size);
    }
    return 0;
}
