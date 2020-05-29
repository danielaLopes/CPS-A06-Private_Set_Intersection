#!/usr/bin/python3
import socket
from threading import Thread
import json
#import urllib.request
#import urllib.parse
import argparse
from argparse import RawTextHelpFormatter
import os
import ast 

# import library in a different directory
import sys
sys.path.append('../')

from multiset_operations import get_polinomial, union, intersection, Polynomial


class Server_Thread(Thread):
    def __init__(self):

    def run(self):
        while True:

# Non-Encrypted version
class Set_Intersection_Client:

    def __init__(self, i, n, c):
        self.i = i
        self.n = n
        self.c = c
        self.port = 8000 + i

        self.other_ports= []
        self.sockets = []
        for client_id in range(1, self.n + 1):
            if client_id != self.i:
                self.other_ports.append(8000 + client_id)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #sock.connect(('127.0.0.1', 8000 + client_id))
                self.sockets.append(sock)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('127.0.0.1', self.port))
                self.socket = sock

    def refreshSockets(self):
        for sock in self.sockets:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def refreshSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', self.port))
        self.socket = sock

    def connectSockets(self):
        for (sock,port) in zip(self.sockets,self.other_ports):
            sock.connect(('127.0.0.1', port))

    def broadcast(self, toSend):
        for sock in self.sockets:
            sock.send(toSend.encode("utf-8"))
        #self.refreshSockets()
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #if self.i == 1:
            #sock.connect(('127.0.0.1', 8002))
        #elif self.i == 2:
            #sock.connect(('127.0.0.1', 8001))
        #sock.send(toSend.encode("utf-8"))
        print("tosend: " + toSend)

    def send_to_client_1(self, toSend):
        self.sockets[0].connect(('127.0.0.1', self.other_ports[0]))
        self.sockets[0].send(toSend.encode("utf-8"))

    def receive(self):
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #sock.bind(('127.0.0.1', 8000 + self.i))

        self.socket.listen(5)
        #sock.listen(5)
        print("waiting to receive data...")
        #try:
        conn, addr = self.socket.accept()
        #conn, addr = sock.accept()
        #except KeyboardInterrupt:
            #print("exiting")
            #os._exit()  
        n_received = 0
        buffer = []
        print("received data")
        while n_received < self.n-1:
            print("inside while")
            data = conn.recv(4096)     
            print("data: " + str(data.decode('utf-8')))
            buffer.append(Polynomial(ast.literal_eval(data.decode('utf-8'))))
            n_received += 1

        self.refreshSocket()
        return buffer

    # returns a multiset of all elements from the client multiset that belong to the intersection multiset
    def get_client_intersection_elements(self):
        if self.i == 1:
            intersection_els = self.other_lambda_polynomials[0].get_elements(Counter(self.multiset))
        else:
            intersection_els = self.lambda_polynomial.get_elements(Counter(self.multiset))
        print("final intersection multiset: " + str(intersection_els))

    # 1.a)
    def create_polynomial(self):
        # multiset should be in the format "[0,1,1,2,3]"
        client_input = input("Submit a multiset in the format [a1,...,ak]: ")
        self.multiset = map(int, client_input.strip('[]').split(','))
        self.polynomial = get_polinomial(self.multiset)

    # 1.b)
    def send_multiset_polynomial(self):
        # TODO: needs adaptations to work with more clients
        if self.i == 1:
            self.connectSockets()
            # client 1 is the first to send polynomials
            self.broadcast(str(self.polynomial.coefficients))
            self.other_polynomials = self.receive()   
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_polynomials = self.receive()
            self.connectSockets()
            self.broadcast(str(self.polynomial.coefficients))

        print("self.other_polynomials: " + str(self.other_polynomials))

    # 1.c)
    def choose_r_polynomials(self):
        # TODO: i dont know how to do this
        self.r_polynomials = []
        #for i in (0, self.c):
        # r for 
        self.r_polynomials.append(get_polinomial([1,1]))
        #self.append(get_polinomial([1,1]))
    
    # 1.d)
    def compute_phi_polynomial(self):
        # TODO: this is wrong
        # calculate this client phi part: phi_i = f_i * r_i,0
        self.phi_polynomial = self.polynomial.multiplication(self.r_polynomials[0])
        # calculate other clients phi part (c): phi_i = f_i-c * r_i,i-c + ... + f_i-1 * r_i,i-1 + f_i * r_i,0
        # TODO: see if it needs to reverse order of polynomials to correspond to r
        if len(self.r_polynomials) > 1:
            for (r, f) in (self.r_polynomials[1: ], self.other_polynomials):
                self.phi_polynomial = f.multiplication(r)

    # 2. and 3.
    def send_phi_polynomial(self):
        # 2.
        if self.i == 1:
            print("Client 1!")
            # client 1 is the first to send polynomials
            self.broadcast(str(self.phi_polynomial.coefficients))
            print("sent data: " + str(self.phi_polynomial.coefficients))
            # waits until other client sends him the final lambda polynomial
            #self.other_lambda_polynomials = self.receive()
            # final polynomial should consist on the intersection of the multisets of both players
            print("Received final polinomial: " + self.other_lambda_polynomials[0].__repr__())
        # 3.
        elif self.i == 2: 
            print("Client 2!")
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_lambda_polynomials = self.receive()
            print("received self.other_lambda_polynomials: " + str(self.other_lambda_polynomials))
            self.sum_lambda_phi_polynomials()
            # TODO: change this in case of more clients
            #self.broadcast(str(self.lambda_polynomial.coefficients))
            self.send_lambda_polynomial()

        print("self.other_lambda_polynomials: " + str(self.other_lambda_polynomials))

    # 3.b)
    def sum_lambda_phi_polynomials(self):
        # performed by client 2 only
        self.lambda_polynomial = self.other_lambda_polynomials[0].sum(self.phi_polynomial)
    
    # 3.c)
    def send_lambda_polynomial(self):
        # performed by client 2 only
        self.send_to_client_1(self.lambda_polynomial.coefficients)



# Encrypted version
class Encrypted_Set_Intersection_Client(Set_Intersection_Client):

    def __init__(self, i, n, c):
        super(Encrypted_Set_Intersection_Client, self).__init__(i, n, c)
        print(self.i)


def main():
    
    description = 'Welcome to the Set Intersection Client!\n\
    Experiment this protocol with 2 clients and no Trusted Third Party.\n\
    1. Choose between encrypted and non-encrypted client version and give parameters to create client.\n\
    2. Submit a multiset.\n'

    usage = '\n\
    python set_intersection_client.py <command> [<args>]\n\
    python set_intersection_client.py non_encrypted "<i>" "<n>" "<c>"\n\
    python set_intersection_client.py encrypted "<i>" "<n>" "<c>"'

    parser = argparse.ArgumentParser(prog='client', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['non_encrypted', 'encrypted'])
    parser.add_argument('i', type=int)
    parser.add_argument('n', type=int)
    parser.add_argument('c', type=int)

    args = parser.parse_args()

    if args.command.__eq__('non_encrypted'):
        client = Set_Intersection_Client(args.i, args.n, args.c)
    elif args.command.__eq__('encrypted'):
        client = Encrypted_Set_Intersection_Client(args.i, args.n, args.c)
    else:
        parser.error('wrong command')

    # ----------------- Phase 1 ------------------
    client.create_polynomial()
    input("Press enter to continue: ")
    client.send_multiset_polynomial()

    input("Press enter to continue: ")
    client.choose_r_polynomials()
    client.compute_phi_polynomial()

    # --------------- Phases 2 + 3 ---------------
    input("Press enter to continue: ")
    client.send_phi_polynomial()

    # ----------------- Phase 4 ------------------
    client.get_client_intersection_elements()

if __name__ == "__main__":
    main()