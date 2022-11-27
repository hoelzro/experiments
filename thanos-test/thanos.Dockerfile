FROM quay.io/thanos/thanos:v0.29.0 AS thanos

COPY objstore.yml ./objstore.yml
