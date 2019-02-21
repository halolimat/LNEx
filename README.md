# DisasterRecord - Deployment

DisasterRecord is a platform for disaster relief, coordination and response. DisasterRecord utilzes LNEx (which requires [Photon OSM](https://github.com/komoot/photon)). Please ensure you have installed or have access to a deployment of Photon OSM.

### Technology

Please be fimilar with the following technologies.

* [Vagrant](https://www.vagrantup.com/) - Development environments management (Vagrant 2.2.2)
* [Docker](https://www.docker.com/) - Application containors (Docker version 18.09.0, build 4d60db4)
* [Ansible](https://www.ansible.com/) - DevOps automation (ansible 2.7.4)
* [Redis](https://redis.io/) - In memory data store

### Provision Installation

Before cloning this repo please do the following to provision your host machine for the environment.

##### Vagrant:

Download:

```sh
$ wget https://releases.hashicorp.com/vagrant/2.2.2/vagrant_2.2.2_x86_64.deb
$ sudo dpkg -i vagrant_2.2.2_x86_64.deb
```

Make Docker the default:

```sh
$ echo 'export VAGRANT_DEFAULT_PROVIDER="docker"' >> ~/.profile
$ . ~/.profile
```
[Vagrant Download](https://www.vagrantup.com/downloads.html)
##### Docker:

Install dependencies:

```sh
$ sudo apt-get update
$ sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
$ sudo apt-get install software-properties-common
```

Install:

```sh
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ sudo apt-key fingerprint 0EBFCD88
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
$ sudo apt-get update
$ sudo apt-get install docker-ce
```

Add yourself to docker group:

```sh
$ sudo usermod -aG docker <user>
```
[Docker Install Guides For Ubuntu](https://docs.docker.com/install/linux/docker-ce/debian/)
##### Ansible:

Install:

```sh
$ sudo apt-add-repository --yes --update ppa:ansible/ansible
$ sudo apt-get update
$ sudo apt-get install ansible
```

__RECOMMENDED: [RESTART FOR DESKTOP ] OR [LOG OUT / LOG IN FOR OPENSTACK]__  

__NOTE: YOUR USER WON'T JOIN THE DOCKER GROUP UNTIL DOING ONE OF THESE__  

[Ansible Install Guides For Ubuntu](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#latest-releases-via-apt-ubuntu)
### Launch

Now it's time to clone this repo and begin setting up the environment

##### Configuration

There are a couple of variables specific to your deployment of DisasterRecord that will need to be set. These variables are found in the [group_vars/all](ansible/environments/dev-local/group_vars/all) file. The variables are explained as follows:

* hostip - This is the IP of the host where the docker containers will be hosted. This is used in the configuration file for the [LNExAPI Server Django application](ansible/roles/codebase_api/templates/settings.py.j2).
* photonip - This is the IP address where your [Photon OSM](https://github.com/komoot/photon) deployment is located.
* photonport - This is the port that your [Photon OSM](https://github.com/komoot/photon) deployment uses.

##### Init Setup:

Once you have cloned the repo and set the variables please navigate to "local" directory

```sh
$ cd DisasterRecord-deployment/local
```

Create a docker network for the deployment:

```sh
$ docker network create --subnet 192.168.67.0/24 dr
```

Create the Base Image:

```sh
$ docker build -t disasterrecord/disasterrecord_base .
```

Bring up the environment (this may take around 5 minutes or more):

```sh
$ . dr-env.sh   # source the environment variables 
$ vagrant up    # bring up the environment
```

To shutdown the environment use:

```sh
$ vagrant halt
```

To destroy environment use:

```sh
$ vagrant destroy
```

Note: If you need to start over you can simply use `vagrant destroy --force` to delete the containers and then use `vagrant up` to recreate them.

### What's Next?

* [LNExAPI Server Guide](LNExAPIServer.md)
* [LNExAPI Client Guide](LNExAPIClient.md)
* [DisasterRecord Server](#)
* [DisasterRecord Web Application](#)
* [DisasterRecord API](#)