#Kevin Lee 10/11/2025
#v03 Kevin Lee 11/03/2025 Modified for LightSwarm Project
import socket
print("####################################")
print("!!!!!!!!!!!!!!!!!!Hi!!!!!>0<!!!!!!!!")
print("####################################")
#UDP_IP = input("Enter Listening IP or Enter to default 0.0.0.0: ") or "0.0.0.0"
#UDP_PORT = 8386
#Laptop_UDP_IP = input("Enter Laptop IP or Enter to default 172.20.10.4: ") or "172.20.10.4"
#Laptop_UDP_PORT = 823
#ESP32_UDP_IP = input("Enter ESP32 IP or Enter to default 172.20.10.2: ") or "172.20.10.2"
#ESP32_UDP_PORT = 1996
UDP_IP   = "255.255.255.255"
UDP_PORT = 1996

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   # ? allow broadcast
sock.bind((UDP_IP, UDP_PORT))

message_r = "", ""
new_msg_cnt = 0
LScmd = ""

def UDP_Send(message):
    #BroadCast UDP
    sock.sendto(message, (UDP_IP, UDP_PORT))#.encode()

    print(f"BroadCasting UDP Message:'{message}' to {UDP_IP}:{UDP_PORT}")

def UDP_Receive():
    global message_r
    global new_msg_cnt

    while True:
        data, addr = sock.recvfrom(1024)
        message_r = (data, addr)  #store tuple (bytes, address)
        new_msg_cnt += 1
        #print(f"Received {len(data)} bytes from {addr}: {list(data)}")

def get_message_r():
    #for getting the received UDP message
    return message_r

def get_new_msg_cnt():
    #for getting the UDP message incoming status
    return new_msg_cnt
    
def getLSCommand():
    global LScmd
    return LScmd

def setLSCommand(cmd):
    global LScmd
    LScmd = cmd
