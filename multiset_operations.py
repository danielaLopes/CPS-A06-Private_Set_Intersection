from collections import Counter
import numpy as np
import secrets
import phe
from phe import paillier
from threshold_paillier import EncryptedNumber

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

    def encrypted_sum(self, other, public_key):
        len_self = len(self.coefficients)
        len_other = len(other.coefficients)

        max_len = max(len_self, len_other)

        res = []
        zero = public_key.encrypt(0)
        for i in range(0, max_len):
            res.append(zero)

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

    def encrypted_multiplication(self, other, public_key):       
        len_self = len(self.coefficients)
        len_other = len(other.coefficients)
        degree = len_self + len_other - 1

        res = []
        zero = public_key.encrypt(0)
        for i in range(0, degree):
            res.append(zero)

        for i in range(0, len_self):
            for j in range(0, len_other):      
                res_index = i + j

                if isinstance(self.coefficients[i], EncryptedNumber):
                    res[res_index] += self.coefficients[i] * other.coefficients[j]
                elif isinstance(self.coefficients[j], EncryptedNumber):
                    res[res_index] += self.coefficients[j] * other.coefficients[i]

        return Polynomial(res)


    # performs the division of two polynomials and returns the remainder
    def division(self, other): 
        # remainder : res[1][0]
        # result: res[0][0]      
        res = np.polydiv(np.array(self.coefficients), np.array(other.coefficients))

        return res

    def division_by_x(self):    
        new_coefficients = [] 
        for i in range(1, len(self.coefficients)):
            new_coefficients.append(self.coefficients[i])

        self.coefficients = new_coefficients
        return self

    # gets list of elements from a given multiset and respective multiplicity that are in the dividend polynomial (self)
    def get_elements(self, multiset):
        res = []
        np.seterr(divide='ignore', invalid='ignore')
 
        for value in multiset:      
            print("Testing if " + str(value) + " is in intersection multiset")    
            multiplicity = multiset[value] 

            divisor_polynomial = Polynomial([-value, 1])
            
            # any polinomial in the format [0, x, y, z, ...] is divisible by 0
            if value == 0:
                if self.coefficients[0] == 0:
                    remainder = 0.0
                    resultant_dividend = self.division_by_x()
                else:
                    remainder = -1
            else:
                result = self.division(divisor_polynomial)
                remainder = result[1][0]
                resultant_dividend = Polynomial(result[0])
        
            if remainder == 0.0:
                res.append(value)
 
                # if it were 0 it would mean the element appeared 0 times in the set
                for b in range(1, multiplicity + 1):

                    if divisor_polynomial.degree() > resultant_dividend.degree(): 
                        break
                    
                    if value == 0:
                        if self.coefficients[0] == 0:
                            remainder = 0.0
                            resultant_dividend = resultant_dividend.division_by_x()
                        else:
                            remainder = -1
                    else:
                        result = resultant_dividend.division(divisor_polynomial)
                        resultant_dividend = Polynomial(result[0])
                        remainder = result[1][0]

                    if remainder == 0.0:
                        res.append(value)
        
        return res

    # gets list of elements from a given multiset that belong to a polynomial representation of a set, checking if it's a root
    # does not include multiplicity
    def get_elements_by_roots(self, multiset):
        res = []
        np.seterr(divide='ignore', invalid='ignore')

        for value in multiset:      
            print("Testing if " + str(value) + " is in intersection multiset")    
            if self.check_if_root(value) == 0:
                res.append(value)
            
        return res

    def check_if_root(self, value):
        res = 0
        for i in range(0, len(self.coefficients)):
            res += self.coefficients[i] * pow(value, i)
        return res

# determines if a value x is in the UNION of two multisets
def union(multiset1, multiset2, x):
    polinomial_f = get_polinomial(multiset1, x)
    polinomial_g = get_polinomial(multiset2, x)

    return polinomial_f * polinomial_g

# determines the polynomial resultant from the UNION of two mulisets
def polynomial_union(multiset1, multiset2):
    polinomial_f = get_polinomial(multiset1)
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

    polinomial_r = generate_r(polinomial_f.degree()).check_if_root(x)
    polinomial_s = generate_r(polinomial_g.degree()).check_if_root(x)
    
    return polinomial_f * polinomial_r + polinomial_g * polinomial_s

# determines the multiset resultant from the INTERSECTION of two multisets
def polynomial_intersection(multiset1, multiset2):
    polinomial_f = get_polinomial(multiset1)
    polinomial_g = get_polinomial(multiset2)

    polinomial_r = generate_r(polinomial_f.degree())
    polinomial_s = generate_r(polinomial_g.degree())

    mult_polynomial1 = polinomial_f.multiplication(polinomial_r)
    mult_polynomial2 = polinomial_g.multiplication(polinomial_s)

    return mult_polynomial1.sum(mult_polynomial2)

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
    k = sum(counter_multiset.values())

    # transform multiset in a list of lists of polynomials
    multiset_polinomials = []
    for value in counter_multiset:
        multiplicity = counter_multiset[value] 
        # [x^0, x^1] 
        polynomial = Polynomial([-value, 1])

        for i in range(0, multiplicity):
            multiset_polinomials.append(polynomial)
    
    res_polinomial = multiset_polinomials[0]
    for i in range(1, len(multiset_polinomials)) :
        res_polinomial = res_polinomial.multiplication(multiset_polinomials[i])

    return res_polinomial


def generate_r(degree):
    # a polynomial with coefficients chosen independently from R (set of all possible coefficients, needs to be sufficiently large)
    r_coeficients = []
    for i in range(0, degree + 1):
        r_coeficients.append(secrets.randbelow(1000) )
    return Polynomial(r_coeficients)
