#!/bin/bash

sudo yum -y install chrony
\cp chrony.conf /etc/chrony.conf
systemctl enable chronyd.service
systemctl start chronyd.service
chronyc sources