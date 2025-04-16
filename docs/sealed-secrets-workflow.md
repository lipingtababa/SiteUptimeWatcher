# Using Sealed Secrets for Datakit Token

This document explains how to use Sealed Secrets to securely store and deploy the Datakit token.

## Prerequisites

- ArgoCD installed and configured
- Sealed Secrets controller installed via ArgoCD
- `kubeseal` CLI tool installed locally

## Workflow

### 1. Create and Seal the Secret in One Step

Run the following command to create and seal the secret in one step:

```bash
kubectl create secret generic datakit-token \
  --namespace=watcher \
  --from-literal=token="your-actual-token-here" \
  --dry-run=client -o yaml | \
  kubeseal > infra/application/datakit-token-sealed.yaml
```

This approach:
- Creates the secret in memory only
- Immediately pipes it to kubeseal
- Saves only the encrypted version to disk
- Never writes the unencrypted token to any file

### 2. Commit the Sealed Secret to Git

The sealed secret can be safely committed to Git as it is encrypted and can only be decrypted by the Sealed Secrets controller in your cluster.

```bash
git add infra/application/datakit-token-sealed.yaml
git commit -m "Add sealed Datakit token"
git push
```

### 3. Update the Kustomization File

Uncomment the line in `kustomization.yaml` to include the sealed secret:

```yaml
resources:
  - watcher.deployment.yaml
  - db-init-job.yaml
  - datakit-daemonset.yaml
  - datakit-token-sealed.yaml  # Uncomment this line
```

### 4. ArgoCD will Automatically Apply the Changes

ArgoCD will detect the changes and apply them to your cluster. The Sealed Secrets controller will automatically decrypt the secret and create a Kubernetes Secret with your Datakit token.

## Updating the Token

To update the token:

1. Run the sealing command again with the new token
2. Commit and push the changes

## Benefits

- The Datakit token is never stored in plain text in Git
- The token can only be decrypted by the Sealed Secrets controller in your cluster
- Different environments can use different tokens without changing the application code
- The token can be rotated without changing the application code 