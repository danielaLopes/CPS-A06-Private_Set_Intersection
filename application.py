#!/usr/bin/python3
import argparse
from argparse import RawTextHelpFormatter
from collections import Counter


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




#def connect_trusted_third_party():

#def union():

#def intersection():

def local_union(multiset1, multiset2, x):
    polinomial_f = get_polinomial(multiset1, x)
    print("polinomial_f: " + str(polinomial1))
    polinomial_g = get_polinomial(multiset2, x)
    print("polinomial_g: " + str(polinomial2))

    return polinomial_f * polinomial_g


def local_intersection(multiset1, multiset2):
    polinomial_f = get_polinomial(multiset1, x)
    print("polinomial_f: " + str(polinomial1))
    polinomial_g = get_polinomial(multiset2, x)
    print("polinomial_g: " + str(polinomial2))

    polinomial_r = calculate_polinomial_for_intersection(multiset1, x)

    polinomial_s = calculate_polinomial_for_intersection(multiset2, x)
    
    return polinomial_f * polinomial_r + polinomial_g * polinomial_s


def main():

    description = 'Welcome to the Private Multiset Operations Interface!\n\
    Experiment this protocol with 2 clients and a Trusted Third Party.\n\
    1. Start by submitting a multiset.\n\
    2. Choose between the following supported operations:\n\
    union                    Perform union operation between multisets\n\
    intersection             Perform intersection operation between multisets\n\
    3. Wait for other client to do the same\n'

    usage = '\n\
    application.py <command> [<args>]\n\
    application.py multiset "<multiset>"\n\
    application.py union\n\
    application.py intersection\n\
    application.py local_union "<multiset1>" "<multiset2>" "<value>""\n\
    application.py local_intersection "<multiset1>" "<multiset2>" "<value>""\n'

    parser = argparse.ArgumentParser(prog='privacy_multiset', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['multiset', 'union', 'intersection', 'local_union', 'local_intersection'])
    parser.add_argument('multiset_arg1', nargs='?')
    parser.add_argument('multiset_arg2', nargs='?')
    parser.add_argument('value', nargs='?')

    args = parser.parse_args()

    if args.command.__eq__('multiset'):
        if args.multiset_arg1:
            multiset = args.multiset_arg1
        else:
            parser.error('wrong arguments for multiset command')
    elif args.command.__eq__('union'):
        if multiset:
            union(multiset)
        else:
            parser.error('no multiset defined')
    elif args.command.__eq__('intersection'):
        if multiset:
            intersection(multiset)
        else:
            parser.error('no multiset defined')
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