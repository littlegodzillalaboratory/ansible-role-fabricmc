#!/usr/bin/env bash
set -o errexit
set -o nounset

cd ../
. ./.venv/bin/activate
ansible-galaxy role install littlegodzillalaboratory.fabricmc --force --roles-path stage/test-examples/roles/
cd examples/

ansible-playbook -i localhost, -c local playbook-direct.yaml
ansible-playbook -i localhost, -c local playbook-import.yaml
