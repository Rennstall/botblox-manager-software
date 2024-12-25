from scapy.all import *

interface = conf.iface

eth = Ether()
vlan = Dot1Q(vlan=94)
ip = IP(dst="127.0.0.1")
udp = UDP(sport=54321, dport=12345)
payload = Raw(load=b"DEADBEEF")

packet = eth/vlan/ip/udp/payload

packet = packet.__class__(bytes(packet))

sendp(packet, iface=interface)
