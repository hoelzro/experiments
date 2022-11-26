FROM prom/prometheus:v2.40.3 AS prometheus

COPY prometheus.yml /etc/prometheus/prometheus.yml

VOLUME /prometheus
