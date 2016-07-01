FROM ubuntu
MAINTAINER Kevin Whitaker <kevin@lisnr.com>

LABEL Description="Keybot, your friendly neighborhood user and key manager." Vendor="Lisnr" Version="1.0"
RUN apt-get update && apt-get install -y python2.7 python-requests python-libuser python-enum34 sudo openssh-server
RUN mkdir /var/run/sshd
RUN echo "PasswordAuthentication no" >> /etc/ssh/sshd_config

EXPOSE 22

ADD src /keybot
CMD python /keybot/main.py && /usr/sbin/sshd -D -f /etc/ssh/sshd_config