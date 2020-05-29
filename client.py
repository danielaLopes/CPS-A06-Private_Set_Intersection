#!/usr/bin/python3
import http.client
import json
#import urllib.request
#import urllib.parse
import argparse
from argparse import RawTextHelpFormatter

def submit(multiset):
    PORT = 8000
    #conn = http.client.HTTPSConnection("localhost", PORT)
    conn = http.client.HTTPConnection("localhost", PORT)

    # prepares json for POST
    headers = {'Content-type': 'application/json'}
    json_multiset = {'multiset': multiset}
    json_data = json.dumps(json_multiset)

    conn.request('POST', '/', json_data, headers)

    response = conn.getresponse()

    print(response.status, response.reason)
    print(response.read())

    conn.close()


def main():
    
    description = 'Welcome to the Private Multiset Operations Client!\n\
    Experiment this protocol with 2 clients and a Trusted Third Party.\n\
    1. Submit a multiset.\n'

    usage = '\n\
    python client.py <command> [<args>]\n\
    python client.py submit "<multiset>"\n'

    parser = argparse.ArgumentParser(prog='client', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['submit'])
    parser.add_argument('multiset_arg1', nargs='?')

    args = parser.parse_args()

    if args.command.__eq__('submit'):
        if args.multiset_arg1:
            print("Submitted multiset: " + args.multiset_arg1)
            submit(args.multiset_arg1)
        else:
            parser.error('wrong arguments for submit command')


if __name__ == "__main__":
    main()