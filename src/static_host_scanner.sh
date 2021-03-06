#!/usr/bin/bash

a=$(python -c "v=['$1'.rstrip('0')+str(x) for x in range(1,255)];print ' '.join(v)")

for ip in $a
do
    ping -c 1 $ip | grep "64 bytes from" >> host.txt
    # if [ $res!="" ];then
    #    echo $res
    # else
    #    echo "no response" > /dev/null
    # fi
done
cat host.txt