FROM phusion/baseimage 
#used to use :0.9.22

# Enable SSH
RUN rm -f /etc/service/sshd/down

ADD LNEx.pub /root/.ssh/authorized_keys
RUN chmod 0600 /root/.ssh/authorized_keys

# Install oracle java 8
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:webupd8team/java
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections

RUN apt-get -q update && apt-get -q -y upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -q -y install aptitude python python-apt runit oracle-java8-installer oracle-java8-set-default sudo

CMD ["/sbin/my_init"]
