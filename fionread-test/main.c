#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/ioctl.h>

#define die(fmt, args...)\
    fprintf(stderr, fmt "\n", ##args);\
    exit(1);

static char *
describe_epoll_events(uint32_t events)
{
    char buffer[128] = {'\0'};

#define EVENT(mask)\
    if(events & mask) strcat(buffer, #mask "|")
    EVENT(EPOLLIN);
    EVENT(EPOLLOUT);
    EVENT(EPOLLRDHUP);
    EVENT(EPOLLPRI);
    EVENT(EPOLLERR);
    EVENT(EPOLLHUP);
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
    int epoll_fd;
    struct epoll_event event;
    char *poll_description = NULL;

    fd = open(target, O_RDONLY);
    if(fd < 0) {
        die("Unable to open TTY %s: %s", target, strerror(errno));
    }

    epoll_fd = epoll_create(1);
    if(epoll_fd < 0) {
        die("Unable to create epoll FD: %s", strerror(errno));
    }

    event.events = EPOLLIN | EPOLLRDHUP | EPOLLPRI | EPOLLERR | EPOLLHUP | EPOLLET;
    event.data.fd = 0;

    status = epoll_ctl(epoll_fd, EPOLL_CTL_ADD, fd, &event);
    if(status < 0) {
        die("Unable to set up FD for polling: %s", strerror(errno));
    }

    while(1) {
        status = epoll_wait(epoll_fd, &event, 1, -1);
        if(status < 0) {
            die("Unable to poll TTY: %s", strerror(errno));
        }

        poll_description = describe_epoll_events(event.events);
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
