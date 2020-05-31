#!/usr/bin/python3
import argparse
from argparse import RawTextHelpFormatter
from collections import Counter
import http.client
import ast

from multiset_operations import polynomial_union, polynomial_intersection


def connect_ttp(operation):
    PORT = 8000
    conn = http.client.HTTPConnection("localhost", PORT)

    conn.request("GET", "/" + operation)

    response = conn.getresponse()
    response_bytes = response.read()

    print(response.status, response.reason)

    conn.close()

    return response_bytes


def ttp_union():
    return connect_ttp("union")


def ttp_intersection():
    return connect_ttp("intersection")


def local_union(multiset1, multiset2):
    result = polynomial_union(multiset1, multiset2)
    union_multiset = result.get_elements(Counter(multiset1 + multiset2))
    return union_multiset


def local_intersection(multiset1, multiset2):
    result = polynomial_intersection(multiset1, multiset2)
    intersection_multiset = result.get_elements(Counter(multiset1))
    return intersection_multiset


def main():

    description = 'Welcome to the Private Multiset Operations Interface!\n\
    Experiment this protocol with 2 clients and a Trusted Third Party.\n\
    1. Both clients should submit a multiset.\n\
    2. Choose between the following supported operations:\n\
    union                    Perform union operation between multisets and obtain the resulting multiset\n\
    intersection             Perform intersection operation between multisets and obtain the resulting multiset\n\n\
                            OR\n\n\
    1. Perform local operations for testing:\n\
    local_union              Test union operation between multisets\n\
    local_intersection       Test intersection operation between multisets\n'

    usage = '\n\
    python application.py <command> [<args>]\n\
    python application.py union\n\
    python application.py intersection\n\
    python application.py local_union "<multiset1>" "<multiset2>"\n\
    python application.py local_intersection "<multiset1>" "<multiset2>"\n'

    parser = argparse.ArgumentParser(prog='privacy_multiset', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['union', 'intersection', 'local_union', 'local_intersection'])
    parser.add_argument('multiset_arg1', nargs='?')
    parser.add_argument('multiset_arg2', nargs='?')

    args = parser.parse_args()

    if args.command.__eq__('union'):
        result_bytes = ttp_union()
        result = result_bytes.decode('utf-8')
        print("union multiset: " + result)

    elif args.command.__eq__('intersection'):
        result_bytes = ttp_intersection()
        result = result_bytes.decode('utf-8')
        print("intersection multiset: " + result)

    elif args.command.__eq__('local_union'):
        if args.multiset_arg1 and args.multiset_arg2:
            multiset1 = ast.literal_eval(args.multiset_arg1) 
            multiset2 = ast.literal_eval(args.multiset_arg2) 
            result = local_union(multiset1, multiset2)
            print("local union multiset: " + str(result))
        else:
            parser.error('no multisets defined')

    elif args.command.__eq__('local_intersection'):
        if args.multiset_arg1 and args.multiset_arg2:
            multiset1 = ast.literal_eval(args.multiset_arg1) 
            multiset2 = ast.literal_eval(args.multiset_arg2) 
            result = local_intersection(multiset1, multiset2)
            print("local intersection multiset: " + str(result))
        else:
            parser.error('no multisets defined')


if __name__ == "__main__":
    main()