#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>

#define die(fmt, args...)\
    fprintf(stderr, fmt "\n", ##args);\
    exit(1);

int
main(int argc, char **argv)
{
    int fd;
    int status;
    int input_buffer_size;
    const char *target = argv[1];

    fd = open(target, O_RDONLY);
    if(fd < 0) {
        die("Unable to open TTY %s: %s", target, strerror(errno));
    }

    status = ioctl(fd, FIONREAD, &input_buffer_size);
    if(status == -1) {
        die("Unable to ioctl(..., FIONREAD): %s", strerror(errno));
    }
    printf("input buffer size: %d\n", input_buffer_size);
    return 0;
}
