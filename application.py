#!/usr/bin/python3
import argparse
from argparse import RawTextHelpFormatter
from collections import Counter
import http.client

from multiset_operations import union
from multiset_operations import intersection


def get_polinomial(multiset, x):
    counter_multiset = Counter(multiset)
    print("counter_multiset: " + str(counter_multiset))
    polinomial = 1
    for value in counter_multiset:
        multiplicity = counter_multiset[value]
        print("key: " + str(value))
        print("value: " + str(multiplicity))
        polinomial *= pow((x - value), multiplicity)
    return polinomial


def coeficients(multiset):
    coeficients = []
    polinomial = ""
    counter_multiset = Counter(multiset)
    for value in counter_multiset:
        multiplicity = counter_multiset[value]
        polinomial += ""


def deg(multiset):
    return len(multiset)


def calculate_polinomial_for_intersection(multiset, polinomial, x):
    degree = deg(multiset)
    sum_value = 0
    # does a summation include the last element???
    for i in range(0, degree):
        # what is r, r[i] and R ???????
        sum_value += r[i] * pow(x, i)
        
    return r


def connect_ttp(operation, value):
    PORT = 8000
    #conn = http.client.HTTPSConnection("localhost", PORT)
    conn = http.client.HTTPConnection("localhost", PORT)

    conn.request("GET", "/" + operation + "?value=" + value)
    #conn.request("GET", "/", "operation=" + operation)
    response = conn.getresponse()

    response_bytes = response.read()

    print(response.status, response.reason)

    conn.close()

    return response_bytes


def ttp_union(value):
    return connect_ttp("union", value)


def ttp_intersection(value):
    return connect_ttp("intersection", value)


# input : [0,1,1,2,3] [3,4,4,4,5]
# r: [1,1,1,1,1]
# s: [3,3,3,3,3]
# value 2 : belongs ????
# value 3: belongs

# r: [1,1,1,1,1]
# s: [3,3,3,3,3]
# value 3: belongs

# input : [0,1,5,2,3] [3,2,4,4,5]
# r: [1,1,1,1,1]
# s: [3,3,3,3,3]
# value 2 : belongs
# value 3: belongs
# value 5: belongs
"""
def local_intersection(multiset1, multiset2, x):
    polinomial_f = get_polinomial(multiset1, x)
    print("polinomial_f: " + str(polinomial_f))
    polinomial_g = get_polinomial(multiset2, x)
    print("polinomial_g: " + str(polinomial_g))

    #polinomial_r = calculate_polinomial_for_intersection(multiset1, x)
    polinomial_r = get_polinomial([1,1,1,1,1], x)

    #polinomial_s = calculate_polinomial_for_intersection(multiset2, x)
    polinomial_s = get_polinomial([3,3,3,3,3], x)
    
    return polinomial_f * polinomial_r + polinomial_g * polinomial_s
"""
def local_union(multiset1, multiset2, x):
    return union(multiset1, multiset2, x)


def local_intersection(multiset1, multiset2, x):
    return intersection(multiset1, multiset2, x)


def main():

    description = 'Welcome to the Private Multiset Operations Interface!\n\
    Experiment this protocol with 2 clients and a Trusted Third Party.\n\
    1. Both clients should submit a multiset.\n\
    2. Choose between the following supported operations:\n\
    union                    Perform union operation between multisets\n\
    intersection             Perform intersection operation between multisets\n\n\
                            OR\n\n\
    1. Perform local operations for testing:\n\
    local_union              Test union operation between multisets\n\
    local_intersection       Test intersection operation between multisets\n'

    usage = '\n\
    python application.py <command> [<args>]\n\
    python application.py union "<value>"\n\
    python application.py intersection "<value>"\n\
    python application.py local_union "<multiset1>" "<multiset2>" "<value>""\n\
    python application.py local_intersection "<multiset1>" "<multiset2>" "<value>""\n'

    parser = argparse.ArgumentParser(prog='privacy_multiset', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['union', 'intersection', 'local_union', 'local_intersection'])
    parser.add_argument('multiset_arg1', nargs='?')
    parser.add_argument('multiset_arg2', nargs='?')
    parser.add_argument('value', nargs='?')

    args = parser.parse_args()

    if args.command.__eq__('union'):
        value = args.multiset_arg1
        result_bytes = ttp_union(value)
        result = result_bytes.decode('utf-8')
        if result == "0":
            print("Value " + value + " belongs to the UNION; result is " + str(result))
        else:
            print("Value " + value + " does not belong to the UNION; result is " + str(result))

    elif args.command.__eq__('intersection'):
        value = args.multiset_arg1
        result_bytes = ttp_intersection(value)
        result = result_bytes.decode('utf-8')
        if result == "0":
            print("Value " + value + " belongs to the UNION; result is " + str(result))
        else:
            print("Value " + value + " does not belong to the UNION; result is " + str(result))

    elif args.command.__eq__('local_union'):
        if args.multiset_arg1 and args.multiset_arg2 and args.value:
            multiset1 = map(int, args.multiset_arg1.strip('[]').split(','))
            multiset2 = map(int, args.multiset_arg2.strip('[]').split(','))
            result = local_union(multiset1, multiset2, int(args.value))
            if result == 0:
                print("Value " + args.value + " belongs to the UNION; result is " + str(result))
            else:
                print("Value " + args.value + " does not belong to the UNION; result is " + str(result))
        else:
            parser.error('no multisets defined')

    elif args.command.__eq__('local_intersection'):
        if args.multiset_arg1 and args.multiset_arg2 and args.value:
            multiset1 = map(int, args.multiset_arg1.strip('[]').split(','))
            multiset2 = map(int, args.multiset_arg2.strip('[]').split(','))
            result = local_intersection(multiset1, multiset2, int(args.value))
            if result == 0:
                print("Value " + args.value + " belongs to the INTERSECTION; result is " + str(result))
            else:
                print("Value " + args.value + " does not belong to the INTERSECTION; result is " + str(result))
        else:
            parser.error('no multisets defined')


if __name__ == "__main__":
    main()