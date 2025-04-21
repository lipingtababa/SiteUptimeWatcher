# provision the infrastructure
1. install aws, kubectl and terraform.
2. run ./scripts/setup.sh


# seal the secrets
## Datakit token
1. Have the kuberntes cluster provisioned and connected from your terminal.
2. Install kubeseal
2. Get the token from truewatch.
3. Seal the token by running:

```bash
echo "apiVersion: v1
kind: Secret
metadata:
  name: datakit-token
  namespace: watcher
type: Opaque
stringData:
  token: \"your-token-here\"" | kubeseal --format yaml --scope cluster-wide --controller-namespace kube-system
```

# Known problems
