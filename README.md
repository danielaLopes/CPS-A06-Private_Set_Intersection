# Motivation and Use Cases
## Set-Intersection Problem
* **Social Networking:** Finding common interests or common friends with people that are not our friends.
* **Airlines:** Determine which patients are on a 'do-not-fly' list, by computing the intersection of their passenger list set and the government's list without disclosing each other's set.
* **Medical Records:** If an organization needs to determine the list of people on welfare who have cancer, the union of all cancer patient's list of all hospitals, and then the intersection of the union and the people on the welfare must be performed, without disclosing the list of all cancer patients.


# Implementation
## Attacker model
* honest-but-curious players (HBC): no players collude and disclose their information to reveal other players information. A Trusted Third Party receives the inputs of all parties and outputs the result of the defined function.
* PPT-bounded adversary model: probabilistic polynomial-time machines

## Techniques and Tools
* Polynomial Representation
* Multiset Operations with Trusted-Third-Party

### Multiset Operations
* Union
* Intersection

## Modes and Algorithms
* **Set-Intersection-HBC:** 
    Considering the number of players n = 2 and c = 1 of which are dishonestly colluding.
    1. a) Two players, each has a private input set of size k. Both players share secret key sk, to which pk is the public key to the homomorphic cryptosystem.
    1. b) Each player calculates polinomial of its private input multiset and sends its encryption to the other player and receives the player's encrypted polynomial. 
    1. c) Chooses c + 1 polynomials r from a set of all polynomials with degree between 0 and k with coefficients from R.
    1. d) Calculates the homomorphic multiplication operation of the encrypted polynomials it has received: f * r
    2. Player 1 sends the encrypted f * r polynomial to Player 2
    3. 

* **Shuffle Protocol:** all n players learn the joint n multisets ??? See this better


# Possible Extensions
* Attacker model for malicious players by integrating zero-knowledge proofs.



# Execution with Trusted Third Party
Every different entity must be executed in a different terminal:
* 1 trusted third party
* 2 clients
* 1 application

## Running Trusted Third Party
Is responsible for receiving players input multiset and computes a fixed function on the group of all multisets.
```
python trusted_third_party.py
```

## Submit a multiset in a client application
Multisets in both clients should be the same size for intersection
```
python client.py submit "<multiset>"
python client.py submit "[0,1,1,2,3]"
python client.py submit "[0,1,1,4,5]"
```

## Use the application to check if a value is in the UNION and INTERSECTION of the clients multisets
```
python application.py union "<value>"
python application.py union "1"

python application.py intersection "<value>"
python application.py intersection "1"
```

## Use the application to test locally
```
python application.py local_union "[0,1,1,2,3]"  "[0,1,1,4,5]" "0"

python application.py local_intersection "[0,1,1,2,3]"  "[0,1,1,4,5]" "0"
```


# Execution of Set Intersection HBC algorithm
Every different entity must be executed in a different terminal:
* 2 clients

## Execute a client
```
cd set_intersection_hbc/
python set_intersection_client.py non_encrypted <i> <n> <c>
python set_intersection_client.py non_encrypted 1 2 0
python set_intersection_client.py non_encrypted 2 2 0
```
or
```
cd set_intersection_hbc/
python set_intersection_client.py encrypted <i> <n> <c>
python set_intersection_client.py encrypted 1 2 0
python set_intersection_client.py encrypted 2 2 0
```


# Samples
## UNION
```
"[0,1,1,2,3]" "[0,1,1,4,5]" "0" => 0, so the value "0" belongs to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "1" => 0, so the value "1" belongs to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "2" => 0, so the value "2" belongs to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "6" => 540000, so the value "6" does not belong to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "-1" => 5760, so the value "-1" does not belong to the UNION
```

## INTERSECTION
```
"[0,1,1,2,3]" "[0,1,1,4,5]" "0" => 0, so the value "0" belongs to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "1" => 0, so the value "1" belongs to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "2" => -12, so the value "2" does not belong to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "6" => 5697900, so the value "6" does not belong to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "-1" => 124416, so the value "-1" does not belong to the INTERSECTION
```