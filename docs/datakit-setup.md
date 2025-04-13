# Datakit Observability Setup with Helm

This document provides instructions on how to set up and use Datakit for observability in the Site Uptime Watcher application using the official Guance Helm chart.

## Overview

Datakit is an open-source data collection agent from Guance Cloud (观测云) that collects metrics, logs, and traces from various sources. It's integrated with the Site Uptime Watcher application to provide comprehensive observability.

## Architecture

The Site Uptime Watcher application uses Datakit as a sidecar container in the same pod. This approach provides several benefits:

1. **Simplified Networking**: The application and Datakit are in the same pod, making communication between them straightforward.
2. **Shared Resources**: Both containers share the same environment variables and resources.
3. **Coordinated Lifecycle**: The lifecycle of Datakit is tied to the lifecycle of the application.

## Prerequisites

1. A Guance Cloud account (观测云账号)
2. A Datakit token from Guance Cloud
3. ArgoCD installed in your Kubernetes cluster

## Setup Instructions

### 1. Get a Datakit Token

1. Log in to your Guance Cloud account at https://www.guance.com/
2. Navigate to the "DataKit" section
3. Create a new token or use an existing one
4. Copy the token for use in the Kubernetes configuration

### 2. Update the Datakit Token

Edit the `infra/application/datakit-secret.yaml` file and replace `YOUR_DATAKIT_TOKEN_HERE` with your actual Datakit token:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: datakit-secret
  namespace: watcher
type: Opaque
stringData:
  token: "YOUR_ACTUAL_TOKEN_HERE"
```

Also, update the token in the ArgoCD application configuration:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: datakit
  namespace: argocd
spec:
  # ...
  source:
    # ...
    helm:
      parameters:
        - name: global.dataway.token
          value: "YOUR_ACTUAL_TOKEN_HERE"
```

### 3. Configure Secure String Parameters

The application uses AWS SSM Parameter Store to store sensitive information like database passwords. These parameters are stored as secure strings and require special permissions to access.

The IAM role for Datakit has been configured to allow access to secure string parameters with decryption. The Datakit configuration has also been updated to handle secure string parameters.

If you need to add more secure string parameters, update the `aws_ssm` section in the `infra/application/datakit/values.yaml` file:

```yaml
inputs:
  aws_ssm:
    enabled: true
    region: us-east-1
    with_decryption: true
    parameters:
      - name: /watcher/postgre/password
        interval: 60s
      # Add more parameters as needed
```

### 4. Apply the Configurations

Apply the configurations to your Kubernetes cluster using ArgoCD:

```bash
# Apply the watcher application
kubectl apply -f infra/argocd/watcher.application.yaml

# Apply the datakit application
kubectl apply -f infra/argocd/datakit.application.yaml
```

### 5. Apply the Terraform Configurations

Apply the Terraform configurations to create the IAM role for Datakit:

```bash
cd infra/dependencies
terraform apply
```

## Application Integration

The Site Uptime Watcher application integrates with Datakit using the HTTP API. The application sends metrics to Datakit using the following endpoint:

- `/v1/write/metrics` - For sending metrics

The metrics are sent by the Keeper component, which batches metrics and sends them to Datakit after storing them in the database. This approach is more efficient than sending metrics individually for each request.

The application is configured to send the following data to Datakit:

1. **Metrics**:
   - `site_uptime_watcher.response_time` - The time taken for each endpoint to respond
   - `site_uptime_watcher.status_code` - The HTTP status code returned by each endpoint
   - `site_uptime_watcher.regex_match` - Whether the response content matched the expected regex pattern

## Metrics Collected

The following metrics are collected and sent to Datakit:

1. **Response Time**: The time taken for each endpoint to respond
2. **Status Code**: The HTTP status code returned by each endpoint
3. **Regex Match**: Whether the response content matched the expected regex pattern

## Viewing Metrics in Guance Cloud

1. Log in to your Guance Cloud account
2. Navigate to the "Observability" section
3. Select "Metrics" to view the collected metrics
4. Select "Logs" to view the collected logs

## Troubleshooting

If you encounter issues with Datakit:

1. Check the Datakit logs:
   ```bash
   kubectl logs -n watcher -l app=watcher -c datakit
   ```

2. Verify that the Datakit sidecar is running:
   ```bash
   kubectl get pods -n watcher -l app=watcher -o wide
   ```

3. Check the IAM role permissions:
   ```bash
   aws iam get-role --role-name datakit-role
   ```

4. If you're having issues with secure string parameters, check the AWS SSM input logs:
   ```bash
   kubectl logs -n watcher -l app=watcher -c datakit | grep "aws_ssm"
   ```

5. Check the application logs for any errors when sending metrics to Datakit:
   ```bash
   kubectl logs -n watcher -l app=watcher -c watcher
   ```

## Additional Resources

- [Datakit Documentation](https://docs.guance.com/datakit/)
- [Guance Cloud Documentation](https://docs.guance.com/)
- [Datakit Helm Chart](https://helm.guance.com)
- [AWS SSM Parameter Store Documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [Datakit HTTP API Documentation](https://docs.guance.com/datakit/api/) 