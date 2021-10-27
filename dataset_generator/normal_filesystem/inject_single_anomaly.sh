
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
    if [ $((number%2)) -eq 0 ]
    then
        # T ODO check if with or with out "" is true
        stress-ng --vm-bytes "$(awk '/MemAvailable/{printf "%d\n", $2 * 0.98;}' < /proc/meminfo)"k --vm-keep -m 10  &
        sleep 5;
        python3 metric_collector.py 35 &
        sleep $main_sleep_time;
        killall -9 stress-ng;
        killall -9 python3;
        killall -9 java;
        wait_period=$(($wait_period+60));
        sleep 5;
    fi
done
