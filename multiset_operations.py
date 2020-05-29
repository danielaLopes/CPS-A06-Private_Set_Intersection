"""from collections import Counter
counterA = Counter(['a','b','b','c'])
counterA
Counter({'b': 2, 'a': 1, 'c': 1})
lst = [Counter(['a','b']), Counter(['a'])]
"""
from collections import Counter
import numpy as np


class Polynomial:
    
    # transforms a multiset into a polynomial represented as a a list of coefficients
    def __init__(self, coefficients_lst):
        self.coefficients = coefficients_lst
          
    def __repr__(self):
        polynomial_str = ""
        degree = 0
        for coefficient in self.coefficients:
            if degree != 0:
                polynomial_str += " + "
            polynomial_str += str(coefficient) + "X^" + str(degree)
            degree += 1
        return polynomial_str

    def degree(self):
        # first element has degree 0, hence -1
        return len(self.coefficients) - 1

    def sum(self, other):
        len_self = len(self.coefficients)
        len_other = len(other.coefficients)

        max_len = max(len_self, len_other)

        res = []
        for i in range(0, max_len):
            res.append(0)

        # to handle polynomials of the same size
        if len_self == len_other:
            for i in range(0, max_len):   
                res[i] += self.coefficients[i] + other.coefficients[i]
        elif len_self == max_len:
            for i in range(0, len_other):   
                res[i] += self.coefficients[i] + other.coefficients[i]
            for i in range(len_other, len_self):   
                res[i] += self.coefficients[i]
        else:
            for i in range(0, len_self):   
                res[i] += self.coefficients[i] + other.coefficients[i]
            for i in range(len_self, len_other):   
                res[i] += other.coefficients[i]  

        return Polynomial(res)

    def multiplication(self, other):       
        len_self = len(self.coefficients)
        len_other = len(other.coefficients)
        degree = len_self + len_other - 1

        res = []
        for i in range(0, degree):
            res.append(0)

        for i in range(0, len_self):
            for j in range(0, len_other):      
                res_index = i + j
                res[res_index] += self.coefficients[i] * other.coefficients[j]

        return Polynomial(res)

    # performs the division of two polynomials and returns the remainder
    def division(self, other):       
        res = np.polydiv(np.array(self.coefficients), np.array(other.coefficients))

        return res[1][0]

    # gets list of elements from a given multiset and respective multiplicity that are in the dividend polynomial (self)
    def get_elements(self, multiset):
        res = []
        np.seterr(divide='ignore', invalid='ignore')
 
        for value in multiset:      
            print("Testing if " + str(value) + " is in intersection multiset")    
            multiplicity = multiset[value] 
            if value <= 0:
                divisor_polynomial = Polynomial([value, 1])
            else:
                divisor_polynomial = Polynomial([-value, 1])
            
            # any polinomial in the format [0, x, y, z, ...] is divisible by 0
            if value == 0:
                if self.coefficients[0] == 0:
                    remainder = 0.0
                else:
                    remainder = -1
            else:
                remainder = self.division(divisor_polynomial)
            print(" dividend: " +  str(self.coefficients))
            print(" divisor: " + str(divisor_polynomial.coefficients))
            if remainder == 0.0:
                res.append(value)

                divisor_polynomial_multiplicity = divisor_polynomial
                # if it were 0 it would mean the element appeared 0 times in the set
                for b in range(1, multiplicity + 1):

                    divisor_polynomial_multiplicity = divisor_polynomial_multiplicity.multiplication(divisor_polynomial)
                    print(" dividend: " +  str(self.coefficients))
                    print(" divisor: " + str(divisor_polynomial_multiplicity.coefficients))
                    if divisor_polynomial_multiplicity.degree() > self.degree(): 
                        #print(" divisor_polynomial.degree(): " +  str(divisor_polynomial.degree()))
                        #print(" self.degree(): " + str(self.degree()))
                        break
                    # TODO: do i need to keep dividing?? or can i assume the multiples are always going to be divisors???
                    remainder = self.division(divisor_polynomial_multiplicity)
                    print(" remainder: " + str(remainder))
                    if remainder == 0.0:
                        res.append(value)

        return Counter(res)


# determines if a value x is in the UNION of two multisets
def union(multiset1, multiset2, x):
    polinomial_f = get_polinomial(multiset1, x)
    polinomial_g = get_polinomial(multiset2, x)

    return polinomial_f * polinomial_g

# determines the polynomial resultant from the UNION of two mulisets
def polynomial_union(multiset1, multiset2):
    polinomial_f = get_polinomial(multise1)
    polinomial_g = get_polinomial(multiset2)

    return polinomial_f.multiplication(polinomial_g)

# determines the multiset resultant from the UNION of two multisets
def multiset_union(multiset1, multiset2):
    counter_multiset1 = Counter(multiset1)
    counter_multiset2 = Counter(multiset2)

    return counter_multiset1 + counter_multiset2


# determines if a value x is in the INTERSECTION of two multisets
def intersection(multiset1, multiset2, x):
    polinomial_f = get_polinomial(multiset1, x)
    polinomial_g = get_polinomial(multiset2, x)

    #polinomial_r = calculate_polinomial_for_intersection(multiset1, x)
    polinomial_r = get_polinomial([1,1,1,1,1], x)

    #polinomial_s = calculate_polinomial_for_intersection(multiset2, x)
    polinomial_s = get_polinomial([3,3,3,3,3], x)
    
    return polinomial_f * polinomial_r + polinomial_g * polinomial_s

# determines the multiset resultant from the INTERSECTION of two multisets
def polynomial_intersection(multiset1, multiset2):
    polinomial_f = get_polinomial(multiset1)
    polinomial_g = get_polinomial(multiset2)

    return polinomial_f.sum(polinomial_g)

# determines the multiset resultant from the INTERSECTION of two multisets
def multiset_intersection(multiset1, multiset2):
    counter_multiset1 = Counter(multiset1)
    counter_multiset2 = Counter(multiset2)
    
    return counter_multiset1 & counter_multiset2


def get_polinomial(multiset, x):
    counter_multiset = Counter(multiset)
    polinomial = 1
    for value in counter_multiset:
        multiplicity = counter_multiset[value]
        polinomial *= pow((x - value), multiplicity)
    return polinomial


def get_polinomial(multiset):
    counter_multiset = Counter(multiset)
    print(counter_multiset)
    k = sum(counter_multiset.values())

    # transform multiset in a list of lists of polynomials
    multiset_polinomials = []
    for value in counter_multiset:
        multiplicity = counter_multiset[value] 
        # [x^0, x^1] 
        if value <= 0:
            polynomial = Polynomial([value, 1])
        else:
            polynomial = Polynomial([-value, 1])

        for i in range(0, multiplicity):
            multiset_polinomials.append(polynomial)
    
    res_polinomial = multiset_polinomials[0]
    for i in range(1, len(multiset_polinomials)) :
        res_polinomial = res_polinomial.multiplication(multiset_polinomials[i])

    """print("res back to multiset with division for 1: " + str(res_polinomial.division(Polynomial([-1,1]))))
    print("res back to multiset with division for 6: " + str(res_polinomial.division(Polynomial([-6,1]))))
    print("res back to multiset with division for 5: " + str(res_polinomial.division(Polynomial([-5,1]))))
    print("res back to multiset with division for 4: " + str(res_polinomial.division(Polynomial([-4,1]))))
    print("res back to multiset with division for 100: " + str(res_polinomial.division(Polynomial([-100,1]))))
    print("res back to multiset with division for 3: " + str(res_polinomial.division(Polynomial([-3,1]))))
    #print("res back to multiset with division for 0: " + str(res_polinomial.division(Polynomial([0,1]))))
    print("res back to multiset with division for -1: " + str(res_polinomial.division(Polynomial([1,1]))))
    print("res back to multiset with division for 2: " + str(res_polinomial.division(Polynomial([-2,1]))))"""
    # TODO: how to test with 0???????? we cannot divide by 0
    #print(res_polinomial.get_elements(Counter([1,2,3,4,0])))
    return res_polinomial

def generate_r(degree):
    # a polynomial with coefficients chosen independently from R (set of all possible coefficients, needs to be sufficiently large)
        
    return r
