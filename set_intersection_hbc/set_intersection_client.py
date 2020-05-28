#!/usr/bin/python3
import http.client
import json
#import urllib.request
#import urllib.parse
import argparse
from argparse import RawTextHelpFormatter

# import library in a different directory
import sys
sys.path.append('../')

from multiset_operations import get_polinomial, union, intersection


# Non-Encrypted version
class Set_Intersection_Client:

    def __init__(self, i, n, c):
        self.i = i
        self.n = n
        self.c = c
        self.port = 8000 + i

    def create_polynomial(self):
        # multiset should be in the format "[0,1,1,2,3]"
        client_input = input("Submit a multiset in the format \"[a1,...,ak]\": ")
        polynomial = get_polinomial(map(int, client_input.strip('[]').split(',')))



# Encrypted version
class Encrypted_Set_Intersection_Client(Set_Intersection_Client):

    def __init__(self, i, n, c):
        super(Encrypted_Set_Intersection_Client, self).__init__(i, n, c)
        print(self.i)


def submit(multiset):
    PORT = 8000
    #conn = http.client.HTTPSConnection("localhost", PORT)
    conn = http.client.HTTPConnection("localhost", PORT)

    # prepares json for POST
    headers = {'Content-type': 'application/json'}
    json_multiset = {'multiset': multiset}
    json_data = json.dumps(json_multiset)

    conn.request('POST', '/', json_data, headers)

    #conn.request("GET", "/")
    response = conn.getresponse()

    print(response.status, response.reason)
    print(response.read())

    conn.close()


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

    client.create_polynomial()


if __name__ == "__main__":
    main()