#!/bin/bash

round_counter=1
max_round_number=4
main_sleep_time=50

user_name='root'

receiver_ip=10.10.2.2

server1=10.10.1.2
server2=10.10.1.3
server3=10.10.1.4
server4=10.10.1.5
server5=10.10.1.6
server6=10.10.1.7
server7=10.10.1.8
server8=10.10.1.9

ethernet_interface_name='p1p2'
network_bw=1024mbit
limited_bw=false

clear_OSS_cache(){
    echo "Clearing cache on receiver oss server1";
    ssh root@$server1 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver oss server2";
    ssh root@$server2 'sync; echo 3 > /proc/sys/vm/drop_caches';

    echo "Clearing cache on receiver oss server3";
    ssh root@$server3 'sync; echo 3 > /proc/sys/vm/drop_caches';

#    echo "Clearing cache on receiver oss server4";
#    ssh root@$server4 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server5";
#    ssh root@$server5 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server6";
#    ssh root@$server6 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server7";
#    ssh root@$server7 'sync; echo 3 > /proc/sys/vm/drop_caches';
#
#    echo "Clearing cache on receiver oss server8";
#    ssh root@$server8 'sync; echo 3 > /proc/sys/vm/drop_caches';
}


clear_all_caches() {
    clear_OSS_cache
    echo "Clearing cache on receiver lustre client";
    ssh root@$receiver_ip 'sync; echo 3 > /proc/sys/vm/drop_caches';
    echo "Clearing cache on sender lustre client";
    sync; echo 3 > /proc/sys/vm/drop_caches;
}
kill_all_java_python3_processes(){
    ssh root@$receiver_ip 'killall -9  -u root python3'
    ssh root@$receiver_ip 'killall -9  -u root java'

    killall -9  -u $user_name python3;
    killall -9  -u $user_name java;
}

# sys_config_tcp_receive_buffer=_buffer_  0.5max 0.25max 0.125max 4*default 2*default default
levels=(["43"]=204800 ["44"]=153600 ["45"]=102400 ["46"]=65536 ["47"]=32768 ["48"]=16384)
#levels=(["43"]=122880 ["44"]=102400 ["45"]=81920 ["46"]=61440 ["47"]=40960 ["48"]=20480)
#levels=(["43"]=33554432 ["44"]=16777216 ["45"]=8388608 ["46"]=4194304 ["47"]=2097152 ["48"]=1048576)
#levels=(["43"]=2097152 ["44"]=1887436 ["45"]=1468006 ["46"]=1258291 ["47"]=1048576 ["48"]=838860)


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
      ssh root@$receiver_ip "python3 /users/Ehsan/AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 2 -jsp 50505 -jtl ${label}"&
      ssh root@$receiver_ip 'cat /proc/sys/net/ipv4/tcp_rmem > ./receiver/tcp_rmem_original_val && sed -r "/^net.ipv4.tcp_rmem=.*$/d" -i /etc/sysctl.conf';
      ssh root@$receiver_ip 'cat /proc/sys/net/core/rmem_max > ./receiver/core_rmem_original_val && sed -r "/^net.core.rmem_max=.*$/d" -i /etc/sysctl.conf';
      ssh root@$receiver_ip "echo 'net.ipv4.tcp_rmem= 4096	87380 '${levels[$i]} >> /etc/sysctl.conf";
      ssh root@$receiver_ip "echo 'net.core.rmem_max= '${levels[$i]} >> /etc/sysctl.conf && sysctl -p";
      if $limited_bw
      then
        sudo tc qdisc add dev $ethernet_interface_name root netem rate ${network_bw};
      fi
      sleep 8;
      echo "Run the Java client on sender side and Start metric collector agent";
      python3 ../../AgentMetricCollector/multi_transfer_parallel_metric_collector.py -l ${label} -rj 1 -jlp 50521 -jtl ${label}&
      sleep $main_sleep_time;
      kill_all_java_python3_processes
      if $limited_bw
      then
        tc qdisc del dev $ethernet_interface_name root;
      fi
      ssh root@$receiver_ip 'sed -r "/^net.ipv4.tcp_rmem=.*$/d" -i /etc/sysctl.conf && sed -r "/^net.core.rmem_max=.*$/d" -i /etc/sysctl.conf && echo "net.ipv4.tcp_rmem= " $(cat ./receiver/tcp_rmem_original_val) >> /etc/sysctl.conf && echo "net.core.rmem_max= " $(cat ./receiver/core_rmem_original_val) >> /etc/sysctl.conf && rm ./receiver/tcp_rmem_original_val  && rm ./receiver/core_rmem_original_val  && sysctl -p';
      sleep 1;
    done
    round_counter=$(($round_counter+1));
done