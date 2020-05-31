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
from threshold_paillier import ThresholdPaillier, EncryptedNumber, ThresholdPaillierPublicKey, ThresholdPaillierPrivateKey, combineShares


# Encrypted version
class Encrypted_Set_Intersection_Client:

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

    # --------------------- socket-related methods ---------------------
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
            print("port")
            print(port)
            sock.connect(('127.0.0.1', port))
            print("socket")
            print(sock)

    def acceptConnections(self):
        self.socket.listen(5)
        self.conn, addr = self.socket.accept()

    # --------------------- messaging methods ---------------------
    def broadcast(self, toSend): 
        print("toSend")   
        print(toSend)    
        for sock in self.sockets:
            try:
                sock.send(toSend.encode("utf-8"))
            except:
                self.connectSockets()
                sock.send(toSend.encode("utf-8"))

    def send_to_client_1(self, toSend):
        try:
            self.sockets[0].send(toSend.encode("utf-8"))
        except:
            self.connectSockets()
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

    def receive_key(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        #while n_received < 1:
        data = self.conn.recv(4096)     
        buffer.append(data.decode('utf-8'))
        n_received += 1

        self.refreshSocket()
        return buffer

    def receive_shared_keys(self):
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        #while n_received < 1:
        data = self.conn.recv(4096)     
        buffer.append(data.decode('utf-8'))
        n_received += 1

        self.refreshSocket()
        return buffer

    def receive_encrypted_polinomial(self, n_players):
        # message_delimitor is going to be either ']]}'
        if not hasattr(self, 'conn'):
            self.acceptConnections()
        buffer = []
        n_received = 0
        message_delimitor = ']]}'.encode('utf-8')
        while n_received < n_players:
            print("receiving from player: " + str(n_received+1))
            # necessary because encrypted polynomials can get quite big
            data = self.conn.recv(4096)  
            print("data[-3:]")
            print(data[-3:])
            if data[-3:] == message_delimitor:
                decoded_data = data.decode('utf-8')
                buffer.append(decoded_data)
            else:
                while data[-3:] != message_delimitor:
                    data += self.conn.recv(4096)  
                decoded_data = data.decode('utf-8')
                buffer.append(decoded_data)
            n_received += 1
            self.refreshSocket()
        print("finished receiving polynomial")

        return buffer

    # --------------------- paillier serialization methods ---------------------
    def serialize_public_key(self, toSend):  
        toSend_json = {} 
        toSend_json['public_key'] = {'n': self.public_key.n}
        return json.dumps(toSend_json)

    def deserialize_public_key(self, received):  
        key_dict = json.loads(received)
        public_key = key_dict['public_key']
        return paillier.PaillierPublicKey(n=int(public_key['n']))
    
    def serialize_shared_keys(self, public_key, private_key):  
        toSend_json = {} 
        toSend_json['public_key'] = {'n': self.public_key.n, 
                                    'nSPlusOne': self.public_key.nSPlusOne,
                                    'r': self.public_key.r,
                                    'ns': self.public_key.ns,
                                    'w': self.public_key.w,
                                    'delta': self.public_key.delta,
                                    'combineSharesConstant': self.public_key.combineSharesConstant}
        return json.dumps(toSend_json)

    def deserialize_shared_keys(self, received):  
        key_dict = json.loads(received)
        public_key = key_dict['public_key']
        self.public_key = ThresholdPaillierPublicKey(
                n=int(public_key['n']), nSPlusOne=public_key['nSPlusOne'],
                r=public_key['r'], ns=public_key['ns'], w=public_key['w'],
                delta=public_key['delta'], combineSharesConstant=public_key['combineSharesConstant'])
        #private_key = key_dict['private_key']
        #self.private_key = distributed_paillier.PaillierSharedKey()

    def serialize_encrypted_polinomial(self, toSend):  
        encrypted_polynomial_json = {}
        encrypted_polynomial_json['values'] = [
            (str(x.ciphertext()), x.exponent) for x in toSend
        ]
        return json.dumps(encrypted_polynomial_json)

    def serialize_group_encrypted_polinomial(self, toSend):  
        encrypted_polynomial_json = {}
        encrypted_polynomial_json['values'] = [
            (x.c, x.nSPlusOne, x.n) for x in toSend
        ]
        return json.dumps(encrypted_polynomial_json)

    def deserialize_encrypted_polinomial(self, received):  
        received_dict = json.loads(received)
        encrypted_values = [
            paillier.EncryptedNumber(self.public_key, int(x[0]), int(x[1]))
            for x in received_dict['values']
        ]
        return encrypted_values

    def deserialize_group_encrypted_polinomial(self, received):  
        received_dict = json.loads(received)
        encrypted_values = [
            EncryptedNumber(int(x[0]), x[1], x[2])
            for x in received_dict['values']
        ]
        return encrypted_values

    def deserialize_encrypted_polinomials(self, received):  
        polynomial_list = []
        for polynomial in received:
            polynomial_list.append(Polynomial(self.deserialize_encrypted_polinomial(polynomial)))
        return polynomial_list

    def deserialize_group_encrypted_polinomials(self, received):  
        polynomial_list = []
        for polynomial in received:
            polynomial_list.append(Polynomial(self.deserialize_group_encrypted_polinomial(polynomial)))
        return polynomial_list

    # --------------------- encryption and decryption methods ---------------------
    # pk, sk: paillier key pair
    # all players share sk
    def generate_key_pair(self):
        # TODO: change this
        # only client 1 has private key
        if self.i == 1:
            self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=2048)
            self.broadcast(self.serialize_public_key(self.public_key))
        else:
            self.public_key = self.deserialize_public_key(self.receive_key()[0])

    def generate_shared_key_pair(self):
        if self.i == 1:
            threshold_paillier = ThresholdPaillier(1024, self.n)
            
            #change this
            self.private_keys = threshold_paillier.priv_keys
            self.public_key = threshold_paillier.pub_key
            self.private_key = self.private_keys[0]

            self.broadcast(self.serialize_shared_keys(self.public_key, self.private_key))
            print("type of public_key")
            print(type(self.public_key))
        else:
            self.deserialize_shared_keys(self.receive_shared_keys()[0])
            print("type of public_key")
            print(type(self.public_key))

    def encrypt_polynomial(self, polynomial):
        ciphertext = []
        for value in polynomial.coefficients:
            ciphertext.append(self.public_key.encrypt(value))
        return Polynomial(ciphertext)

    def decrypt_polynomial(self, polynomial):
        plaintext = []
        for value in polynomial.coefficients:
            plaintext.append(self.private_key.decrypt(value))
        return Polynomial(plaintext)

    def decrypt_part_of_polynomial(self, polynomial, key_part):
        plaintext = []
        for value in polynomial.coefficients:
            plaintext.append(key_part.partialDecrypt(value))
        return Polynomial(plaintext)

    # --------------------- encrypted operation methods ---------------------
    # sum two encrypted polynomials:
    def sum_encrypted_polynomials(self, polynomial1, polynomial2):
        return polynomial1.encrypted_sum(polynomial2, self.public_key)

    # multiply an unencrypted polynomial and an encrypted polynomial:
    def multiply_encrypted_unencrypted_polynomials(self, polynomial1, polynomial2):
        #return polynomial1.multiplication(polynomial2)
        return polynomial1.encrypted_multiplication(polynomial2, self.public_key)

    # 1.a)
    def create_polynomial(self):
        # multiset should be in the format [0,1,1,2,3]
        client_input = input("Submit a multiset in the format [a1,...,ak]: ")
        self.multiset = ast.literal_eval(client_input)
        self.polynomial = get_polinomial(self.multiset)
        self.encrypted_polynomial = self.encrypt_polynomial(self.polynomial)

    # 1.b)
    def send_multiset_polynomial(self):
        # TODO: needs adaptations to work with more clients
        if self.i == 1:
            # client 1 is the first to send polynomials   
            #self.broadcast(self.serialize_encrypted_polinomial(self.encrypted_polynomial.coefficients))
            self.broadcast(self.serialize_group_encrypted_polinomial(self.encrypted_polynomial.coefficients))
            print("Waiting to receive encrypted fi from player 1 and player 2")
            #self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(2))
            #self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            self.other_polynomials = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            #self.other_polynomials.append(self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1)))
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            # receives f1 from player 1
            print("Waiting to receive encrypted fi from player 1")
            #self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            self.other_polynomials = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            print("after receiving from player 1")
            #self.broadcast(self.serialize_encrypted_polinomial(self.encrypted_polynomial.coefficients))
            self.broadcast(self.serialize_group_encrypted_polinomial(self.encrypted_polynomial.coefficients))
            # receives f3 from player 3
            #print("Waiting to receive encrypted fi from player 2")
            #self.other_polynomials.append(self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1)))
        elif self.i == 3:
            print("Waiting to receive encrypted fi from player 1 and player 2")
            #self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(2))
            #self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            self.other_polynomials = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            #self.other_polynomials.append(self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1)))
            #print("Waiting to receive encrypted fi from player 2")
            #self.other_polynomials = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))
            print("Broadcasting polynomial to other players")
            #self.broadcast(self.serialize_encrypted_polinomial(self.encrypted_polynomial.coefficients))
            self.broadcast(self.serialize_group_encrypted_polinomial(self.encrypted_polynomial.coefficients))         

    # 1.c)
    def choose_r_polynomials(self):
        self.r_polynomials = []
        for i in (0, self.c): 
            self.r_polynomials.append(generate_r(self.polynomial.degree()))
    
    # 1.d)
    def compute_phi_polynomial(self):
        self.phi_polynomial = self.multiply_encrypted_unencrypted_polynomials(self.encrypted_polynomial, self.r_polynomials[0])
        for i in range(0, len(self.other_polynomials)):
            phi_part = self.multiply_encrypted_unencrypted_polynomials(self.other_polynomials[i], self.r_polynomials[i+1])
            self.phi_polynomial = self.sum_encrypted_polynomials(self.phi_polynomial, phi_part)
    
    # 2. and 3.
    def send_phi_polynomial(self):
        # phi polynomial is already encrypted
        self.lambda_polynomial = self.phi_polynomial
        
        # 2.
        if self.i == 1:         
            # client 1 is the first to send polynomials
            #self.broadcast(str(self.lambda_polynomial.coefficients))
            #serialized_polynomial = self.serialize_encrypted_polinomial(self.lambda_polynomial.coefficients)
            serialized_polynomial = self.serialize_group_encrypted_polinomial(self.lambda_polynomial.coefficients)
            #self.broadcast_encrypted_polinomial(serialized_polynomial)
            self.broadcast(serialized_polynomial)
            # waits until other client sends him the components of the final lambda polynomial, encrypted
            #self.other_lambda_polynomials = self.deserialize_encrypted_polinomial(self.receive_encrypted_polinomial()[0])
            print("waiting for other lambda polynomials...")
            #self.other_lambda_polynomial = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
            self.other_lambda_polynomial = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
            #self.other_lambda_polynomials = self.receive_encrypted_polinomial()
            #print(self.other_lambda_polynomials[0].coefficients)
            # final polynomial should consist on the intersection of the multisets of both players
            # TODO: since i only have 2 clients, the polynomial client 1 sends me is already the right one
            # but i should update the final polynomial in client 1 and send it to all other clients
        # 3.
        elif self.i == 2: 
            # client 2 first receives polynomials from client1 and then sends its own
            #self.other_lambda_polynomial = self.deserialize_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
            self.other_lambda_polynomial = self.deserialize_group_encrypted_polinomials(self.receive_encrypted_polinomial(1))[0]
            self.sum_lambda_phi_polynomials()
            # TODO: change this in case of more clients
            #self.broadcast(str(self.lambda_polynomial.coefficients))
            self.send_lambda_polynomial()


    # 3.b)
    def sum_lambda_phi_polynomials(self):
        # performed by client 2 only
        # TODO: change for more clients
        self.lambda_polynomial = self.sum_encrypted_polynomials(self.other_lambda_polynomial, self.lambda_polynomial)
    
    # 3.c)
    def send_lambda_polynomial(self):
        # performed by client 2 only
        #self.send_to_client_1(self.serialize_encrypted_polinomial(self.lambda_polynomial.coefficients))
        self.send_to_client_1(self.serialize_group_encrypted_polinomial(self.lambda_polynomial.coefficients))

    # returns a multiset of all elements from the client multiset that belong to the intersection multiset
    def get_intersection_multiset(self):
        if self.i == 1:
            self.final_intersection_polynomial = self.decrypt_polynomial(self.other_lambda_polynomial)
            intersection_els = self.final_intersection_polynomial.get_elements(Counter(self.multiset))
            print("final intersection multiset: " + str(intersection_els))

    def get_intersection_group_decryption_multiset(self):
        if self.i == 1:
            share1 = self.decrypt_part_of_polynomial(self.other_lambda_polynomial, self.private_key)

            share2 = self.decrypt_part_of_polynomial(self.other_lambda_polynomial, self.private_keys[1])

            final_coefficients = []
            for i in range(0, len(self.other_lambda_polynomial.coefficients)):
                final_coefficients.append(combineShares([share1.coefficients[i], share2.coefficients[i]], 
                        self.public_key.w, self.public_key.delta, self.public_key.combineSharesConstant, 
                        self.public_key.nSPlusOne, self.public_key.n, self.public_key.ns, [1,2]))

            self.final_intersection_polynomial = Polynomial(final_coefficients)

            #intersection_els = self.final_intersection_polynomial.get_elements_by_roots(Counter(self.multiset))
            intersection_els = self.final_intersection_polynomial.get_elements(Counter(self.multiset))
            print("final intersection multiset: " + str(intersection_els))

    def private_set_intersection(self, isShared):
        # ----------------- Phase 1 ------------------
        # initiate by player 3, then player 2, then player 1
        self.create_polynomial()
        input("Press enter to exchange encrypted polynomial with other players (order by 3, 2 ,1): ")
        self.send_multiset_polynomial()

        input("Press enter to choose r polynomials and compute phi polynomial (order by 3, 2 ,1): ")
        self.choose_r_polynomials()
        self.compute_phi_polynomial()

        # --------------- Phases 2 + 3 ---------------
        input("Press enter to exchange encrypted lambda with other players (order by 3, 2 ,1): ")
        self.send_phi_polynomial()

        # ----------------- Phase 4 ------------------
        if isShared == False:
            self.get_intersection_multiset()
        else:
            self.get_intersection_group_decryption_multiset()


def main():
    
    description = 'Welcome to the Set Intersection Client!\n\
    Experiment this protocol with 2 clients and no Trusted Third Party.\n'

    usage = '\n\
    python set_intersection_client.py <command> [<args>]\n\
    python set_intersection_client.py single_key "<i>" "<n>" "<c>"\n\
    python set_intersection_client.py shared_key "<i>" "<n>" "<c>"'

    parser = argparse.ArgumentParser(prog='client', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['single_key','shared_key'])
    parser.add_argument('i', type=int)
    parser.add_argument('n', type=int)
    parser.add_argument('c', type=int)

    args = parser.parse_args()

    client = Encrypted_Set_Intersection_Client(args.i, args.n, args.c)

    if args.command.__eq__('single_key'):
        client.generate_key_pair()
        client.private_set_intersection(False)
    elif args.command.__eq__('shared_key'):
        client.generate_shared_key_pair()
        client.private_set_intersection(True)
    else:
        parser.error('wrong command')


if __name__ == "__main__":
    main()