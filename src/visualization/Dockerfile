FROM grafana/grafana

COPY postgres-datasource.yml /etc/grafana/provisioning/datasources/
COPY url-latencies.json /etc/grafana/provisioning/dashboards/
COPY url-latencies.json /var/lib/grafana/dashboards/

COPY dashboards.yml /etc/grafana/provisioning/dashboards/
