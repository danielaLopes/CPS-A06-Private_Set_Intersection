"""from collections import Counter
counterA = Counter(['a','b','b','c'])
counterA
Counter({'b': 2, 'a': 1, 'c': 1})
lst = [Counter(['a','b']), Counter(['a'])]
"""
from collections import Counter


class Polynomial:
    
    def __init__(self, multiset):
        # transforms a multiset that represents a polynomy in the form:
        # (x-a)^mult(a)...
        # into: 
        """ input: coefficients are in the form a_n, ...a_1, a_0 
        """
        self.polinomial_str = ""

        counter_multiset = Counter(multiset)
        for value in counter_multiset:
            multiplicity = counter_multiset[value]
            
            #self.polinomial += "(X-" + str(value) + ")^" + 
        self.coefficients = list(coefficients) # tuple is turned into a list
     
    def __repr__(self):
        """
        method to return the canonical string representation 
        of a polynomial.
   
        """
        return "Polynomial" + str(self.coefficients)
            
    def __call__(self, x):    
        res = 0
        for index, coeff in enumerate(self.coefficients[::-1]):
            res += coeff * x** index
        return res 



#def __init__(self):

# determines if a value x is in the UNION of two multisets
def union(multiset1, multiset2, x):
    polinomial_f = get_polinomial(multiset1, x)
    polinomial_g = get_polinomial(multiset2, x)

    return polinomial_f * polinomial_g


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
