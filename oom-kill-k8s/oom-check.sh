#!/bin/bash

# for each minikube, do this five times:
#
# - restore from snapshot
# - start the VM
# - build the image
# - apply the manifests
# - wait for deployment to become ready
# - hit the service with a request to eat 2GB more RAM
# - wait a bit, verify restart of target pod
# - dump all cluster events to $MINIKUBE-$LOOP_COUNT-events.json
# - stop the VM

set -eu

wait_for_eight() {
  local i
  for i in $(seq 1 30) ; do
    ready_count=$(minikube kubectl -- get deployment/oom-kill-k8s -o jsonpath='{.status.readyReplicas}')
    if [[ $ready_count -eq 8 ]] ; then
      return 0
    fi
    sleep 1s
  done

  echo "deployment did not become ready for 30s"

  return 1
}

oneshot() {
  local profile="$1"
  local i="$2"

  VBoxManage snapshot "$profile" restore "$profile-fresh-install"
  export MINIKUBE_PROFILE="$profile"

  minikube start
  eval $(minikube docker-env)
  docker build -t oom-kill-k8s .

  minikube kubectl -- apply -f service.yaml
  minikube kubectl -- apply -f deployment.yaml
  wait_for_eight
  sleep 10m # XXX DEBUG
  victim=$(minikube kubectl -- get pod --no-headers -o custom-columns='NAME:{.metadata.name}' | head -1)
  minikube kubectl -- exec "$victim" -- wget -O - http://127.0.0.1:8060/eat-memory --post-data 'amount=2G' || echo $? > "${profile}-${i}-wget-exit"
  #sleep 5m # XXX DEBUG
  minikube kubectl -- get events -A -o json > "${profile}-${i}-events.json"
  minikube stop
}

minikube profile list -o json | jq -r '.valid | .[] | .Name' | while read profile ; do
  for i in $(seq 1 5) ; do
    oneshot "$profile" "$i"
  done
done
