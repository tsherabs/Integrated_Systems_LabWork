
# CTE412 Practical 15 — Campus Notice Board

Student ID: 02230126

## Purpose

Deploy the Campus Notice Board API to a three-node kind
Kubernetes cluster and measure availability during Recreate,
RollingUpdate, failed-release rollback, blue/green switching,
and feature-flag changes.

## Environment

- OS: macOS (record actual version)
- Docker: (record actual version)
- kind: (record actual version)
- kubectl: (record actual version)
- Kubernetes: (record actual cluster version)
- Application: Python 3.12 standard-library HTTP server
- Container base: python:3.12-alpine

## Prerequisites

Install and start Docker Desktop. Install kind, kubectl and Git.

Run all commands from the repository root.

## Build Docker images

docker build --build-arg APP_VERSION=1.0.0 \
  -t notice-board:02230126-1.0.0 ./app

docker build --build-arg APP_VERSION=1.1.0 \
  -t notice-board:02230126-1.1.0 ./app

docker build --build-arg APP_VERSION=1.2.0-broken \
  -t notice-board:02230126-1.2.0-broken ./app

docker pull busybox:1.36

## Create cluster

kind create cluster \
  --name cte412-02230126 \
  --config cluster/kind-cluster.yaml

kubectl config set-context --current \
  --namespace=nb-02230126

## Apply namespace and policies

kubectl apply -f manifests/base/namespace.yaml
kubectl apply -f manifests/base/quota.yaml
kubectl apply -f manifests/base/limitrange.yaml

## Load images into kind

kind load docker-image \
  notice-board:02230126-1.0.0 \
  notice-board:02230126-1.1.0 \
  notice-board:02230126-1.2.0-broken \
  --name cte412-02230126

kind load docker-image busybox:1.36 \
  --name cte412-02230126

Note: On Docker configurations where kind reports a missing
content digest, export a single-platform archive with
docker image save --platform, then use kind load image-archive.
Choose the architecture that matches the kind nodes.

## Recreate the final Task 8 state

kubectl apply -f manifests/bluegreen/flags.yaml
kubectl apply -f manifests/bluegreen/deployments.yaml
kubectl apply -f manifests/bluegreen/production-services.yaml
kubectl apply -f manifests/bluegreen/preview-service.yaml
kubectl apply -f manifests/base/monitor.yaml

kubectl rollout status deployment/notice-board-blue
kubectl rollout status deployment/notice-board-green

## Verify

kubectl get deployments,pods,services
kubectl get pod monitor
kubectl describe resourcequota notice-board-quota
curl -s http://127.0.0.1:30090/version
curl -s http://127.0.0.1:30090/notices

## Clean up

kubectl config set-context --current --namespace=default
kind delete cluster --name cte412-02230126
```

Two corrections to make in the README before treating it as complete:

- On a fresh machine, apply the namespace **before** setting it as the default context namespace. Place `kubectl apply -f manifests/base/namespace.yaml` immediately after creating the cluster.
- Because you previously encountered the missing-digest error, write down the exact `docker image save --platform ...` and `kind load image-archive ...` commands that worked on your Mac. The README must be executable as written, not merely describe a possible workaround.

Use the same working image-loading method in both your actual rebuild and the README.

### Step 4. Preserve the evidence, then remove application objects

First, confirm the complete Task 9 monitor log has already been saved:

```bash
test -s evidence/t9-monitor-full.log \
  && echo "Full monitor log saved"
```

Now create a cleanup manifest containing the retained namespace configuration.

File: `manifests/base/retain.yaml`

```yaml
# Purpose: Retain namespace, ResourceQuota, and LimitRange
# while removing labeled application resources with apply --prune.
# Apply: see Task 9 prune command below.

apiVersion: v1
kind: Namespace
metadata:
  name: nb-02230126
  labels:
    app.kubernetes.io/part-of: campus-notice-board
    cte412/practical: "06"
  annotations:
    cte412/student-name: "Jigme Tsherab Damchoe"
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: notice-board-quota
  namespace: nb-02230126
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    pods: "15"
    count/services: "4"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: notice-board-limits
  namespace: nb-02230126
spec:
  limits:
    - type: Container
      default:
        cpu: 200m
        memory: 128Mi
      defaultRequest:
        cpu: 50m
        memory: 64Mi
      max:
        cpu: 500m
        memory: 512Mi
      min:
        cpu: 10m
        memory: 16Mi
```

Use the same values and metadata as your original Task 1 manifests. Do not silently replace any values you actually configured differently.

Before pruning, preview which application resources match:

```bash
kubectl get deployments,services,pods,configmaps \
  -l cte412/rebuild=managed \
  | tee evidence/t9-before-cleanup.txt
```

Now apply the retained configuration and prune only the selected resource kinds:

```bash
kubectl apply -n nb-02230126 \
  -f manifests/base/retain.yaml \
  --prune \
  -l cte412/rebuild=managed \
  --prune-allowlist=apps/v1/Deployment \
  --prune-allowlist=v1/Service \
  --prune-allowlist=v1/Pod \
  --prune-allowlist=v1/ConfigMap \
  2>&1 | tee evidence/t9-cleanup.txt
```

The prune operation is scoped to resources carrying `cte412/rebuild=managed`. It should remove the two blue/green Deployments, three Services, the monitor, and the feature-flag ConfigMap while preserving the namespace, quota, and LimitRange.

**Check the output carefully.** If your kubectl version rejects or doesn't perform the prune operation, stop rather than deleting resources with another command. Don't claim the cleanup succeeded until the remaining objects have been checked.

### Step 5. Verify the cleanup

```bash
kubectl get all -n nb-02230126
kubectl get configmaps -n nb-02230126
kubectl get resourcequota,limitrange -n nb-02230126
kubectl get namespace nb-02230126
```

Expected:

- No application Deployments, ReplicaSets, Pods, or Services.
- No `notice-board-flags` ConfigMap.
- The namespace, ResourceQuota, and LimitRange remain.

The default `kubernetes` Service exists in the `default` namespace, not yours.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="camera"/>
    **Screenshot 9.2 — Clean namespace**
  </row>
  Capture the output showing the namespace has no application resources while its quota and LimitRange still exist.

  Filename: `t9-r2-clean-namespace.png`

  Save the verification:
  ```bash
  {
    kubectl get all -n nb-02230126
    kubectl get configmaps -n nb-02230126
    kubectl get resourcequota,limitrange -n nb-02230126
  } | tee evidence/t9-cleanup-verification.txt
  ```
</box>

### Important adjustment to the prune command

For `kubectl apply --prune -l cte412/rebuild=managed` to work reliably, the input must include matching desired resources. Add this label to the top-level `metadata.labels` of the three resources in `retain.yaml`:

```yaml
cte412/rebuild: "managed"
```

For example:

```yaml
metadata:
  name: notice-board-quota
  namespace: nb-02230126
  labels:
    cte412/rebuild: "managed"
```

Do the same for the Namespace and LimitRange, leaving all other metadata and specifications unchanged.

The allowlist still limits pruning to Deployments, Services, Pods, and ConfigMaps. The three retained resource kinds are not in that allowlist.

Apply and verify the cleanup using the command from Step 4.

---

## Requirement 2 continued — Rebuild the final state

### Step 6. Recreate using only repository commands

Once the namespace contains only the retained configuration, execute the final-state rebuild commands from your README.

Run and capture the actual output:

```bash
{
  echo "=== Apply ConfigMap ==="
  kubectl apply -f manifests/bluegreen/flags.yaml

  echo "=== Apply blue/green Deployments ==="
  kubectl apply -f manifests/bluegreen/deployments.yaml

  echo "=== Apply production Services ==="
  kubectl apply -f manifests/bluegreen/production-services.yaml

  echo "=== Apply preview Service ==="
  kubectl apply -f manifests/bluegreen/preview-service.yaml

  echo "=== Apply monitor ==="
  kubectl apply -f manifests/base/monitor.yaml

  echo "=== Wait for blue ==="
  kubectl rollout status deployment/notice-board-blue \
    --timeout=180s

  echo "=== Wait for green ==="
  kubectl rollout status deployment/notice-board-green \
    --timeout=180s

} 2>&1 | tee evidence/t9-e1-rebuild-output.txt
```

This rebuild uses the locally loaded images, so Kubernetes must still have all the Notice Board image tags and BusyBox available on its nodes.

Make sure all apply commands and both rollout checks succeed.

### Step 7. Verify the rebuilt application

Run:

```bash
kubectl get deployments
kubectl get pods -l app=notice-board --show-labels
kubectl get services
kubectl get pod monitor
```

Then verify the production version and feature flag:

```bash
curl -s http://127.0.0.1:30090/version
echo

curl -s http://127.0.0.1:30090/notices
echo
```

Your final state should have:

| Component | Expected state |
|---|---|
| `notice-board-blue` | 3/3 Ready, version 1.0.0 |
| `notice-board-green` | 3/3 Ready, version 1.1.0 |
| Production Services | Select `slot=green` |
| Preview Service | Select `slot=green` |
| `notice-board-flags` | `FEATURE_PINNED=true` |
| `monitor` | 1/1 Running |
| `/notices` | `"pinnedFirst":true` |

### Official E9.1 — Rebuild evidence

Save the final verification output:

```bash
{
  echo "=== Deployments ==="
  kubectl get deployments

  echo "=== Pods ==="
  kubectl get pods -l app=notice-board --show-labels

  echo "=== Services ==="
  kubectl get services

  echo "=== Monitor ==="
  kubectl get pod monitor

  echo "=== Production version ==="
  curl -s http://127.0.0.1:30090/version
  echo

  echo "=== Production notices ==="
  curl -s http://127.0.0.1:30090/notices
  echo
} | tee evidence/t9-e1-rebuild-verification.txt
```

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="camera"/>
    **Screenshot E9.1 — Successfully rebuilt**
  </row>
  Capture the rebuilt resources and production API output, showing both Deployments at `3/3`, the monitor Running, version `1.1.0` in production, and pinned-first ordering enabled.

  Filename: `t9-e1-rebuild-success.png`

  Required evidence:
  - `evidence/t9-e1-rebuild-output.txt`
  - `evidence/t9-e1-rebuild-verification.txt`
</box>

**Don't delete the cluster unless E9.1 confirms the rebuild is successful.**

---

## Requirement 3 — Reset namespace, delete cluster, and commit

> Reset the context namespace to default, delete the cluster, and commit.

### Step 1. Save the final cluster information

Before deletion:

```bash
{
  kubectl get nodes -o wide
  kubectl get deployments -n nb-02230126
  kubectl get pods -n nb-02230126
} | tee evidence/t9-final-cluster-state.txt
```

### Step 2. Reset the current namespace

```bash
kubectl config set-context --current --namespace=default
```

Verify:

```bash
kubectl config view --minify \
  -o jsonpath='{..namespace}{"\n"}'
```

Expected output:

```text
default
```

### Step 3. Delete the kind cluster

This command is specifically required by Task 9:

```bash
kind delete cluster --name cte412-02230126 \
  2>&1 | tee evidence/t9-cluster-deletion.txt
```

Once deleted, the local cluster's Pods, Services, Deployments, and other Kubernetes resources are gone.

### Step 4. Capture official evidence E9.2

The PDF asks for output proving the cluster has been deleted.

Run:

```bash
{
  echo "Remaining kind clusters:"
  kind get clusters

  echo "Check deleted cluster containers:"
  docker ps -a --filter 'name=cte412-02230126'
} | tee evidence/t9-e2-deletion-verification.txt
```

The deleted cluster name should be absent from both outputs.

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={2}>
    <icon name="camera"/>
    **Screenshot E9.2 — Cluster deleted**
  </row>
  Capture the Terminal showing the successful `kind delete cluster` output, followed by `kind get clusters` without `cte412-02230126`.

  Filename: `t9-e2-cluster-deleted.png`

  Required evidence:
  - `evidence/t9-cluster-deletion.txt`
  - `evidence/t9-e2-deletion-verification.txt`
</box>

### Step 5. Commit your Task 9 work

```bash
git add README.md manifests/base/ evidence/t9-*

git commit -m "Task 9: Verify reproducible rebuild and clean up kind cluster"
```

Check the repository status:

```bash
git status
git log --oneline -9
```

You should have a clean Git working tree, assuming all files from previous tasks were already committed.

---

# Official evidence summary

| Evidence | What to capture | Filename |
|---|---|---|
| Requirement 1 | Complete available monitor history | `t9-monitor-full.log` |
| **E9.1** | Output proving all final Task 8 resources were recreated from manifests | `t9-e1-rebuild-output.txt` |
| **E9.2** | Output proving the kind cluster was deleted | `t9-e2-deletion-verification.txt` |

## Task 9 checklist

{@body const items = ["R1 — Full available monitor log saved","R2 — README contains a complete rebuild procedure","R2 — Cleanup retains namespace, quota and LimitRange","R2 — Final Task 8 state recreated successfully","E9.1 — Rebuild output and verification saved","R3 — Context reset to default namespace","R3 — Kind cluster deleted","E9.2 — Cluster deletion verified","All Task 9 files committed to Git"]}
{@body const [done,setDone] = DIL.useState([])}
<box border radius="lg" padding={3} gap={3}>
  <row align="center" justify="between">
    **Task 9 progress**
    <text color="secondary" tabularNums>{done.length}/{items.length}</text>
  </row>
  <box background="surface-tertiary" height="6px" radius="full" clip>
    <box background="surface-inverted" height="100%" width={`${100*done.length/items.length}%`} radius="full"/>
  </box>
  {#each items as item,i}
    <checkbox key={i} checked={done.includes(i)} onChange={v=>setDone(p=>v?[...p,i]:p.filter(x=>x!==i))}>{item}</checkbox>
  {/each}
</box>

## What remains after Task 9?

The practical also requires a report at `report/p06-report.md`, with these sections:

1. Objective
2. Environment
3. Results — measured comparison table for every release
4. Analysis — answers to A1–A5
5. Reflection
6. References

The report must use the **actual numbers recorded by your monitor**, particularly failed requests, mixed-version windows, and peak Pods.

Your final submission is the repository URL on the VLE, not just the screenshots. Once Task 9 is completed, the next step is to prepare the report and check the repository against the 15-mark rubric.