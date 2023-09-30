FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

COPY ./main /usr/local/bin/sleep-and-waste-time

ENTRYPOINT ["/usr/local/bin/sleep-and-waste-time"]
