#!/bin/bash

round_counter=1
max_round_number=2
main_sleep_time=60

user_name='root'

receiver_remote_client_ip=10.10.2.2
remote_client_ip=10.10.2.3

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

ethernet_interface_name='p1p1'

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
levels=([1]=3145728 [2]=1572864 [3]=786432 [4]=8192 [5]=4096 [6]=2048)

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
      ssh root@$receiver_remote_client_ip 'cat /proc/sys/net/ipv4/tcp_rmem > ./receiver/tcp_rmem_original_val && sed -r "/^net.ipv4.tcp_rmem=.*$/d" -i /etc/sysctl.conf';
      ssh root@$receiver_remote_client_ip "echo 'net.ipv4.tcp_rmem= 2048 87380 '${levels[$i]} >> /etc/sysctl.conf && sysctl -p";
      sysctl -p
      sleep 5;
      echo "Start collecting metrics on sender side";
      python3 ../parallel_metric_collector.py -l ${label}  -jsp 50505&
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      ssh root@$receiver_remote_client_ip 'sed -r "/^net.ipv4.tcp_rmem=.*$/d" -i /etc/sysctl.conf && echo "net.ipv4.tcp_rmem= " $(cat ./receiver/tcp_rmem_original_val) >> /etc/sysctl.conf && rm ./receiver/tcp_rmem_original_val && sysctl -p';
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done