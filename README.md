https://coderzcolumn.com/tutorials/python/threshold-paillier

# Motivation and Use Cases
## Set-Intersection Problem
* **Social Networking:** Finding common interests or common friends with people that are not our friends.
* **Airlines:** Determine which patients are on a 'do-not-fly' list, by computing the intersection of their passenger list set and the government's list without disclosing each other's set.
* **Medical Records:** If an organization needs to determine the list of people on welfare who have cancer, the union of all cancer patient's list of all hospitals, and then the intersection of the union and the people on the welfare must be performed, without disclosing the list of all cancer patients.


# Implementation
## Attacker model
* honest-but-curious players (HBC): even if c < n players collude and disclose their information, gains information about other players input other than what can be deduced by the result of the protocol. A Trusted Third Party receives the inputs of all parties and outputs the result of the defined function.

## Techniques and Tools
* Polynomial Representation
* Multiset Operations with Polynomial Representation

### Multiset Operations
* Union
* Intersection

## Modes and Algorithms
* [Set-Intersection with 2 clients and a Trusted Third Party](#execution-with-trusted-third-party)
* Set-Intersection HBC with 2 clients no Trusted Third Party:
    * [without colluding players](#without-colluding-players)
    * [with colluding players but no shared key (player 1 performs decryption)](#with-colluding-players-but-no-shared-key)
    * [with colluding players and shared key for group decryption](#with-colluding-players-and-shared-key)


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
Client 2 should be the first to be executed and submitted input multiset, then it waits for client 1 to start protocol

### Without colluding players
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

### With colluding players but no shared key
```
python set_intersection_hbc_client.py single_key 1 2 0
python set_intersection_hbc_client.py single_key 2 2 0
```

### With colluding players and shared key
```
python set_intersection_hbc_client.py shared_key 1 2 0
python set_intersection_hbc_client.py shared_key 2 2 0

python set_intersection_hbc_client.py encrypted 1 3 2
python set_intersection_hbc_client.py encrypted 2 3 2
python set_intersection_hbc_client.py encrypted 3 3 2
```