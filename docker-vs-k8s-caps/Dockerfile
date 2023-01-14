FROM ubuntu:22.04

RUN mkdir -p /chroot/usr/bin /chroot/lib/x86_64-linux-gnu /chroot/lib64 \
    && cp -a /usr/bin/sleep /chroot/usr/bin/sleep \
    && cp -a /lib/x86_64-linux-gnu/libc.so.6 /chroot/lib/x86_64-linux-gnu/libc.so.6 \
    && cp -a /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /chroot/lib64/ld-linux-x86-64.so.2
