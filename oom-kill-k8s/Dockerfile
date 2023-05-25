FROM golang:1.20 AS builder

COPY . /go/src/oom-kill-k8s/
WORKDIR /go/src/oom-kill-k8s/
RUN go install .

FROM busybox:latest

COPY --from=builder /go/bin/oom-kill-k8s /usr/bin/

ENTRYPOINT ["/usr/bin/oom-kill-k8s"]
