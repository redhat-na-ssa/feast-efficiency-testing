#!/bin/bash

oc apply -f manifests/namespace.yaml
sleep 2
oc apply -f manifests
sleep 30

oc rsync model_execution_test/  kaggle-speed-0:/opt/app-root/src/
oc rsync feature_pull_test/  kaggle-speed-0:/opt/app-root/src/