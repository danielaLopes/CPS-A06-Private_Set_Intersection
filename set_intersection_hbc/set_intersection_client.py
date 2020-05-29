#!/usr/bin/python3
import socket
import json
#import urllib.request
#import urllib.parse
import argparse
from argparse import RawTextHelpFormatter
import os
import ast 
from collections import Counter

# import library in a different directory
import sys
sys.path.append('../')

from multiset_operations import get_polinomial, union, intersection, Polynomial


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

    def acceptConnections(self):
        self.socket.listen(5)
        #try:
        self.conn, addr = self.socket.accept()
        #conn, addr = sock.accept()
        #except KeyboardInterrupt:
            #print("exiting")
            #os._exit()  

    def broadcast(self, toSend):
        for sock in self.sockets:
            sock.send(toSend.encode("utf-8"))

    def send_to_client_1(self, toSend):
        self.sockets[0].send(toSend.encode("utf-8"))

    def receive(self):
        buffer = []
        n_received = 0
        while n_received < self.n-1:
            data = self.conn.recv(4096)     
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
        self.multiset = ast.literal_eval(client_input)
        self.polynomial = get_polinomial(self.multiset)

    # 1.b)
    def send_multiset_polynomial(self):
        # TODO: needs adaptations to work with more clients
        if self.i == 1:
            self.connectSockets()
            # client 1 is the first to send polynomials
            self.broadcast(str(self.polynomial.coefficients))
            self.acceptConnections()
            self.other_polynomials = self.receive()   
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.acceptConnections()
            self.other_polynomials = self.receive()
            self.connectSockets()
            self.broadcast(str(self.polynomial.coefficients))

    # 1.c)
    def choose_r_polynomials(self):
        # TODO: i dont know how to do this
        self.r_polynomials = []
        #for i in (0, self.c):
        # r for 
        self.r_polynomials.append(Polynomial([1,1,1,1]))
        #self.append(Polynomial([1,1]))
    
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
        print("STEP 1.d) my phi polynomial: " + str(self.phi_polynomial.coefficients))

    # 2. and 3.
    def send_phi_polynomial(self):
        # 2.
        if self.i == 1:
            # client 1 is the first to send polynomials
            self.broadcast(str(self.phi_polynomial.coefficients))
            # waits until other client sends him the final lambda polynomial
            self.other_lambda_polynomials = self.receive()
            # final polynomial should consist on the intersection of the multisets of both players
            # TODO: since i only have 2 clients, the polynomial client 1 sends me is already the right one
            # but i should update the final polynomial in client 1 and send it to all other clients
            print("STEP 3.c) Received lambda polinomial: " + str(self.other_lambda_polynomials[0].coefficients))
        # 3.
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            self.other_lambda_polynomials = self.receive()
            print("STEP 3.a) received lambda_polynomial: " + str(self.other_lambda_polynomials[0].coefficients))
            self.sum_lambda_phi_polynomials()
            # TODO: change this in case of more clients
            #self.broadcast(str(self.lambda_polynomial.coefficients))
            self.send_lambda_polynomial()

    # 3.b)
    def sum_lambda_phi_polynomials(self):
        # performed by client 2 only
        self.lambda_polynomial = self.other_lambda_polynomials[0].sum(self.phi_polynomial)
        print("STEP 3.b) my lambda polynomial: " + str(self.lambda_polynomial.coefficients))
    
    # 3.c)
    def send_lambda_polynomial(self):
        # performed by client 2 only
        self.send_to_client_1(str(self.lambda_polynomial.coefficients))


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