#!/bin/bash

round_counter=1
max_round_number=2
main_sleep_time=60

user_name='root'

receiver_remote_client_ip=10.10.2.2
remote_client_ip=10.10.2.3

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

ethernet_interface_name='p1p2'
network_bw=1024mbit
limited_bw=false
clear_all_caches() {
    echo "Clearing cache on sender oss server";
    ssh root@$sender_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on receiver oss server";
    ssh root@$receiver_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver lustre client";
    ssh root@$receiver_remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on remote lustre client";
    ssh root@$remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on sender lustre client";
    sync; echo 3 > /proc/sys/vm/drop_caches;
}

kill_all_java_python3_processes(){
    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;

    ssh root@$receiver_remote_client_ip 'killall -9  -u root python3'
    ssh root@$receiver_remote_client_ip 'killall -9  -u root java'
}
# sys_config_tcp_send=_buffer_  0.5max 0.25max 0.125max 0.5default 0.25default 0.125default
#levels=(["145"]=33554432 ["146"]=16777216 ["147"]=8388608 ["148"]=43690 ["149"]=21845 ["150"]=10922)
levels=(["145"]=33554432 ["146"]=16777216 ["147"]=8388608 ["148"]=4194304 ["149"]=2097152 ["150"]=1048576)

while true
do
    printf "\n"
    echo "round number ${round_counter}"
    if [ $round_counter -gt $max_round_number ];then
       break
    fi
    for i in "${!levels[@]}"; do
      clear_all_caches
      label=$i
      echo "Run the java server on receiver side and start metric collector agent";
      ssh root@$receiver_remote_client_ip "python3 /users/Ehsan/AgentMetricCollector/remote_parallel_metric_collector.py -l ${label} -jsp 50505 -jtl ${label}"&
      if $limited_bw
      then
        sudo tc qdisc add dev $ethernet_interface_name root netem rate ${network_bw};
      fi
      cat /proc/sys/net/ipv4/tcp_wmem > tcp_wmem_original_val
      cat /proc/sys/net/core/wmem_max > core_wmem_original_val
      sed -r "/^net.core.wmem_max=.*$/d" -i /etc/sysctl.conf
      sed -r "/^net.ipv4.tcp_wmem=.*$/d" -i /etc/sysctl.conf
      echo 'net.core.wmem_max= '${levels[$i]} >> /etc/sysctl.conf
      echo 'net.ipv4.tcp_wmem= 10240 87380 '${levels[$i]} >> /etc/sysctl.conf
      sysctl -p
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ../parallel_metric_collector.py -l ${label}  -jsp 50505&
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      if $limited_bw
      then
        tc qdisc del dev $ethernet_interface_name root;
      fi
      sed -r "/^net.core.wmem_max=.*$/d" -i /etc/sysctl.conf
      sed -r "/^net.ipv4.tcp_wmem=.*$/d" -i /etc/sysctl.conf
      echo "net.core.wmem_max= " $(cat core_wmem_original_val) >> /etc/sysctl.conf
      echo "net.ipv4.tcp_wmem= " $(cat tcp_wmem_original_val) >> /etc/sysctl.conf
      rm tcp_wmem_original_val
      rm core_wmem_original_val
      sysctl -p
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done