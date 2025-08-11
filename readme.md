### Please read and follow the manual first
[\[\[Memmert AtmoWeb\]\]](https://www.memmert.com/index.php?eID=dumpFile&t=f&f=22945&token=b1d41113272ae66efa92fc7b42e50f1f6fd2d07c)

## Pi setup

### IP setup
open Terminal 
``` bash
ip link show
```

Typical output when a USB-Ethernet dongle is attached:
``` makefile
1: lo:  <LOOPBACK,UP,LOWER_UP> ...
2: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> ...
3: enx001122334455: <BROADCAST,MULTICAST> ...
```

on our pi show
``` sql
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000 link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00 

2: enxb827ebf92bf3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000 link/ether b8:27:eb:f9:2b:f3 brd ff:ff:ff:ff:ff:ff 

3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DORMANT group default qlen 1000 link/ether b8:27:eb:ac:7e:a6 brd ff:ff:ff:ff:ff:ff
```
our wired NIC(Network Interface Card) is ` enxb827ebf92bf3 `  (IFACE)

``` bash
sudo ip link set <IFACE> up
sudo ip addr flush dev  <IFACE> 

sudo ip addr add 192.168.100.100/24 dev <IFACE>
```

and ping 
``` bash
ping -c4 192.168.100.100
``` 
it should see the following
``` sql
PING 192.168.100.100 (192.168.100.100) 56(84) bytes of data.
64 bytes from 192.168.100.100: icmp_seq=1 ttl=64 time=0.606 ms
64 bytes from 192.168.100.100: icmp_seq=2 ttl=64 time=0.373 ms
64 bytes from 192.168.100.100: icmp_seq=3 ttl=64 time=0.372 ms
64 bytes from 192.168.100.100: icmp_seq=4 ttl=64 time=0.381 ms

--- 192.168.100.100 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 155ms
rtt min/avg/max/mdev = 0.372/0.433/0.606/0.099 ms
```

### Debug port and IP
if not shown the same result please check the ethernet cable and setting on [[#Memmert setup]].
the following is verify the owner of each address, in case IP address conflict.
``` bash
# What addresses does the Pi have?
ip addr show enxb827ebf92bf3

# Who owns 192.168.100.100 according to the ARP table?
ip neigh show 192.168.100.100
```

it should like
``` sql
pi@Pi:~/Desktop/ovenControl $ ip addr show enxb827ebf92bf3
2: enxb827ebf92bf3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether b8:27:eb:f9:2b:f3 brd ff:ff:ff:ff:ff:ff
    inet 169.254.221.146/16 brd 169.254.255.255 scope global noprefixroute enxb827ebf92bf3
       valid_lft forever preferred_lft forever
    inet6 fe80::c4b9:d1d6:2a6:b303/64 scope link 
       valid_lft forever preferred_lft forever
```

if you see something like 
``` sql
pi@Pi:~/Desktop/ovenControl $ ip addr show enxb827ebf92bf3
2: enxb827ebf92bf3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether b8:27:eb:f9:2b:f3 brd ff:ff:ff:ff:ff:ff
    inet 169.254.221.146/16 brd 169.254.255.255 scope global noprefixroute enxb827ebf92bf3
       valid_lft forever preferred_lft forever
    inet 192.168.100.10/24 scope global enxb827ebf92bf3
       valid_lft forever preferred_lft forever
    inet 192.168.100.110/24 scope global secondary enxb827ebf92bf3
       valid_lft forever preferred_lft forever
    inet6 fe80::c4b9:d1d6:2a6:b303/64 scope link 
       valid_lft forever preferred_lft forever
```

execute `sudo ip addr del 192.168.100.110/24 dev enxb827ebf92bf3` and `sudo ip addr del 192.168.100.10/24 dev enxb827ebf92bf3` to delete the duplication.

### Initial test
``` bash
curl -v http://192.168.100.100/atmoweb?Temp1Read=
```
it should like this
``` sql
* Expire in 0 ms for 6 (transfer 0xb71950)
*   Trying 192.168.100.100...
* TCP_NODELAY set
* Expire in 200 ms for 4 (transfer 0xb71950)
* Connected to 192.168.100.100 (192.168.100.100) port 80 (#0)
> GET /atmoweb?Temp1Read= HTTP/1.1
> Host: 192.168.100.100
> User-Agent: curl/7.64.0
> Accept: */*
> 
< HTTP/1.1 200 OK
< Content-Type: Unknown
< Server: Memmert
* no chunk, no close, no size. Assume close to signal end
< 
* Closing connection 0
"Temp1Read": 28.7,
```
it shown `"Temp1Read": 28.7,` ! Great we connect Memmert device successfully! 

