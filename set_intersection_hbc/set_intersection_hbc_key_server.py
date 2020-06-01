#!/usr/bin/python3
import socket
import json

# import library in a different directory
import sys
sys.path.append('../')

from threshold_paillier import ThresholdPaillier


class Set_Intersection_HBC_Key_Server:
    
    def __init__(self):
        self.port1 = 9001
        self.port2 = 9002

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', self.port1))
        self.socket1 = sock

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', self.port2))
        self.socket2 = sock

        self.generated_shared_keys = {}

    def acceptConnections(self, sock):
        sock.listen(5)
        conn, addr = sock.accept()

        data = conn.recv(4096)   
        print(data)

        request_json = json.loads(data.decode('utf-8'))
        uuid = request_json['uuid']
        i = request_json['i'] - 1
        if uuid not in self.generated_shared_keys:
            n = request_json['n']
            self.generate_shared_key_pair(uuid, n)
        key_part = self.select_key_part(uuid, i)

        conn.sendall(key_part.encode('utf-8'))
        conn.close()

    def refreshSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', self.port))
        self.socket = sock
    
    def generate_shared_key_pair(self, uuid, n):
        threshold_paillier = ThresholdPaillier(1024, n)
        self.generated_shared_keys[uuid] = Shared_Key_Info(threshold_paillier.priv_keys, threshold_paillier.pub_key)

    def select_key_part(self, uuid, id):
        response = {}
        shared_key = self.generated_shared_keys[uuid]
        
        response['public_key'] = {'n': shared_key.public_key.n, 
                                'nSPlusOne': shared_key.public_key.nSPlusOne,
                                'r': shared_key.public_key.r,
                                'ns': shared_key.public_key.ns,
                                'w': shared_key.public_key.w,
                                'delta': shared_key.public_key.delta,
                                'combineSharesConstant': shared_key.public_key.combineSharesConstant}
        
        response['private_key'] = {'n': shared_key.private_keys[id].n, 
                                'l': shared_key.private_keys[id].l, 
                                'combineSharesConstant': shared_key.private_keys[id].combineSharesConstant,
                                'w': shared_key.private_keys[id].w, 
                                'v': shared_key.private_keys[id].v, 
                                'viarray': shared_key.private_keys[id].viarray, 
                                'si': shared_key.private_keys[id].si,
                                'server_id': shared_key.private_keys[id].server_id,
                                'r': shared_key.private_keys[id].r,
                                'delta': shared_key.private_keys[id].delta,
                                'nSPlusOne': shared_key.private_keys[id].nSPlusOne}

        return json.dumps(response)


class Shared_Key_Info:
    
    def __init__(self, private_keys, public_key):
        self.private_keys = private_keys
        self.public_key = public_key


def main():
    
    server = Set_Intersection_HBC_Key_Server()
    print("Key Server waiting for requests")

    server.acceptConnections(server.socket1)
    server.acceptConnections(server.socket2)


if __name__ == "__main__":
    main()