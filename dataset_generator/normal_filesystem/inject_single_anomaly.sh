
#!/bin/bash

wait_period=0
ethernet_interface_name='enp0s31f6'
main_sleep_time=30
while true
do
    echo "wait period ${wait_period}"
    if [ $wait_period -gt 36000 ];then
       break
    fi
    
    python3 metric_collector.py 0 &
    sleep $main_sleep_time;
    killall -9 python3;
    killall -9 java;
    wait_period=$(($wait_period+60));
    sleep 5;
    
    
    if [ $((number%2)) -eq 0 ]
    then
        sudo tc qdisc add dev $ethernet_interface_name root netem delay 0.1ms 0.5ms distribution normal;
        sleep 5;
        python3 metric_collector.py 41 &
        sleep $main_sleep_time;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        tc qdisc del dev $ethernet_interface_name root;
        sleep 5;
    fi
done
