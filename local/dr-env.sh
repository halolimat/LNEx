#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export ANSIBLE_HOST_KEY_CHECKING="False"
export ANSIBLE_INVENTORY="$DIR/.vagrant/provisioners/ansible/inventory/"
export ANSIBLE_REMOTE_USER="root"
export ANSIBLE_PRIVATE_KEY_FILE="$DIR/LNEx.pem"
export ANSIBLE_CONFIG="$DIR/../ansible/ansible.cfg"

if [ ! -L "$ANSIBLE_INVENTORY/group_vars" ]
  then
    echo "Creating symlink to dev-local environment's group_vars in Vagrant's Ansible inventory..."
    mkdir -p $ANSIBLE_INVENTORY
    ln -s $DIR/../ansible/environments/dev-local/group_vars $ANSIBLE_INVENTORY
fi

if [ ! -L "$DIR/../ansible/ansible.cfg" ]
  then
    echo "Creating symlink to dev-local environment's ansible.cfg in 'ansible' dir..."
    $(cd $DIR/../ansible/ && ln -s environments/dev-local/ansible.cfg .)
fi

# increase sysctl values in order to pass Elasticsearch's bootstrap checks
#sudo sysctl -w fs.file-max=65536
#sudo sysctl -w vm.max_map_count=262144

