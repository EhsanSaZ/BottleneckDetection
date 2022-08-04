#!/bin/bash

user_name='root'
receiver_remote_client_ip=10.10.2.2
#remote_client_ip=10.10.2.3
#other_oss_server_ip=10.10.1.4

sender_oss_server_ip=10.10.1.2
receiver_oss_server_ip=10.10.1.3

ethernet_interface_name='p1p1'

main_sleep_time=60

clear_all_caches() {
    echo "Clearing cache on sender oss server";
    ssh root@$sender_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on receiver oss server";
    ssh root@$receiver_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
#    echo "Clearing cache on other oss server";
#    ssh root@$other_oss_server_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver lustre client";
    ssh root@$receiver_remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
#    echo "Clearing cache on remote lustre client";
#    ssh root@$remote_client_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on sender lustre client";
    sync; echo 3 > /proc/sys/vm/drop_caches;
}
kill_all_java_processes(){
#    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;

#    ssh root@$receiver_remote_client_ip 'killall -9  -u root python3'
    ssh root@$receiver_remote_client_ip 'killall -9  -u root java'
}

clear_all_caches
label='sys_config_tcp_receive_buffer_1'
ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
sleep 5;
java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ 0 &
sleep $main_sleep_time;
kill_all_java_processes
killall -9  -u $user_name python3;
sleep 1;

label_general="sys_config_tcp_receive_buffer_"
# 0.5max 0.25max 0.125max
# 0.5default 0.25default 0.125default
levels=([1]=3145728 [2]=1572864 [3]=786432 [4]=8192 [5]=4096 [6]=2048)

for i in "${!levels[@]}"; do
#  printf "%s\t%s\n" "$i" "${levels[$i]}"
  clear_all_caches
  label=${label_general}${levels[$i]}
  echo $label
  ssh root@$receiver_remote_client_ip "java /users/Ehsan/AgentMetricCollector/collectors/SimpleReceiver_per_second_thr_monitor.java /lustre/dstDataDir/dstData/ 50505 ${label}"&
  ssh root@$receiver_remote_client_ip 'cat /proc/sys/net/ipv4/tcp_rmem > ./receiver/tcp_rmem_original_val && sed -r "/^net.ipv4.tcp_rmem=.*$/d" -i /etc/sysctl.conf';
  ssh root@$receiver_remote_client_ip "echo 'net.ipv4.tcp_rmem= 2048 87380 '${levels[$i]} >> /etc/sysctl.conf && sysctl -p";
  sleep 5;
  java /users/Ehsan/BottleneckDetection/dataset_generator/utilities/SimpleSender1.java $receiver_remote_client_ip 50505 /lustre/dataDir/srcData/ $i &
  sleep $main_sleep_time;
  kill_all_java_processes
  ssh root@$receiver_remote_client_ip 'sed -r "/^net.ipv4.tcp_rmem=.*$/d" -i /etc/sysctl.conf && echo "net.ipv4.tcp_rmem= " $(cat ./receiver/tcp_rmem_original_val) >> /etc/sysctl.conf && rm ./receiver/tcp_rmem_original_val && sysctl -p';
  sleep 1;
done