#!/usr/bin/python3
import socket
import json
import argparse
from argparse import RawTextHelpFormatter
import os
import ast 
from collections import Counter
import phe
from phe import paillier

# import library in a different directory
import sys
sys.path.append('../')

from multiset_operations import get_polinomial, union, intersection, generate_r, Polynomial


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
            try:
                sock.send(toSend.encode("utf-8"))
            except:
                self.connectSockets()
                sock.send(toSend.encode("utf-8"))

    def send_to_client_1(self, toSend):
        self.sockets[0].send(toSend.encode("utf-8"))

    def receive(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
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

    # TODO: remove self.connectSockets() and self.acceptConnections
    """
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
            self.broadcast(str(self.polynomial.coefficients))"""

    # 1.c)
    def choose_r_polynomials(self):
        # TODO: i dont know how to do this
        self.r_polynomials = []
        #for i in (0, self.c):
        # r for 
        self.r_polynomials.append(generate_r(self.polynomial.degree()))
    
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

    def encrypt_polynomial(polynomial):
        ciphertext = []
        for value in polynomial:
            ciphertext.append(self.private_key.encrypt(value))
        return ciphertext

    def decrypt_polynomial(polynomial):
        plaintext = []
        for value in polynomial:
            plaintext.append(self.public_key.encrypt(value))
        return plaintext

    def sum_encrypted_polynomials(polynomial1, polynomial2):
        sum_polynomial = []
        max_index = max(len(polynomial1), len(polynomial2))
        min_index = min(len(polynomial1), len(polynomial2))
        for i in range(0, min_index):
            sum_polynomial.append(polynomial1[i] + polynomial2[i])
        if len(polynomial1) < max_index:
            for i in range(min_index, max_index):
                sum_polynomial.append(polynomial2)
        else:
            for i in range(min_index, max_index):
                sum_polynomial.append(polynomial1)

    def generate_key_pair(self):
        # only client 1 has private key
        if self.i == 1:
            self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=2048)
            self.broadcast(str(self.public_key))
        else:
            self.public_key = self.receive_key()[0]

    def test_homomorphic_sum(self):
        if self.i == 1:
            ciphered_num1 = self.public_key.encrypt(3, precision=1)
            ciphered_num2 = self.public_key.encrypt(4, precision=1)
            print("ciphered_num2: " + str(ciphered_num2))
            ciphered_sum = ciphered_num1 + ciphered_num2
            deciphered_sum = self.private_key.decrypt(ciphered_sum)
            print("deciphered_sum: " + str(deciphered_sum))

    def receive_key(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        while n_received < self.n-1:
            data = self.conn.recv(4096)     
            buffer.append(data.decode('utf-8'))
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

    # 2. and 3.
    def send_phi_polynomial(self):
        # 2.
        if self.i == 1:
            # encrypt phi polynomial to send to other players

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

    client.generate_key_pair()
    client.test_homomorphic_sum()

    # ----------------- Phase 1 ------------------
    """
    client.create_polynomial()
    input("Press enter to continue: ")
    #client.send_multiset_polynomial()

    input("Press enter to continue: ")
    client.choose_r_polynomials()
    client.compute_phi_polynomial()

    # --------------- Phases 2 + 3 ---------------
    input("Press enter to continue: ")
    client.send_phi_polynomial()

    # ----------------- Phase 4 ------------------
    client.get_client_intersection_elements()"""

if __name__ == "__main__":
    main()