# Datakit Observability Setup with Helm

This document provides instructions on how to set up and use Datakit for observability in the Site Uptime Watcher application using the official Guance Helm chart.

## Overview

Datakit is an open-source data collection agent from Guance Cloud (观测云) that collects metrics, logs, and traces from various sources. It's integrated with the Site Uptime Watcher application to provide comprehensive observability.

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

### 3. Apply the Configurations

Apply the configurations to your Kubernetes cluster using ArgoCD:

```bash
# Apply the watcher application
kubectl apply -f infra/argocd/watcher.application.yaml

# Apply the datakit application
kubectl apply -f infra/argocd/datakit.application.yaml
```

### 4. Apply the Terraform Configurations

Apply the Terraform configurations to create the IAM role for Datakit:

```bash
cd infra/dependencies
terraform apply
```

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
   kubectl logs -n watcher -l app.kubernetes.io/name=datakit
   ```

2. Verify that the Datakit DaemonSet is running:
   ```bash
   kubectl get daemonset -n watcher
   ```

3. Check the IAM role permissions:
   ```bash
   aws iam get-role --role-name datakit-role
   ```

## Additional Resources

- [Datakit Documentation](https://docs.guance.com/datakit/)
- [Guance Cloud Documentation](https://docs.guance.com/)
- [Datakit Helm Chart](https://helm.guance.com) 