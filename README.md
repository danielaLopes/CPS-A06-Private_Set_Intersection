Every different entity must be executed in a different terminal:
* 1 trusted third party
* 2 clients
* 1 application

# Running Trusted Third Party
```
python trusted_third_party.py
```

# Submit a multiset in a client application
Multisets in both clients should be the same size for intersection
```
python client.py submit "<multiset>"
python client.py submit "[0,1,1,2,3]"
python client.py submit "[0,1,1,4,5]"
```

# Use the application to check if a value is in the UNION and INTERSECTION of the clients multisets
```
python application.py union "<value>"
python application.py union "1"

python application.py intersection "<value>"
python application.py intersection "1"
```

# Use the application to test locally
```
python application.py local_union "[0,1,1,2,3]"  "[0,1,1,4,5]" "0"

python application.py local_intersection "[0,1,1,2,3]"  "[0,1,1,4,5]" "0"
```

# UNION Samples
"[0,1,1,2,3]" "[0,1,1,4,5]" "0" => 0, so the value "0" belongs to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "1" => 0, so the value "1" belongs to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "2" => 0, so the value "2" belongs to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "6" => 540000, so the value "6" does not belong to the UNION
"[0,1,1,2,3]" "[0,1,1,4,5]" "-1" => 5760, so the value "-1" does not belong to the UNION

# INTERSECTION Samples
"[0,1,1,2,3]" "[0,1,1,4,5]" "0" => 0, so the value "0" belongs to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "1" => 0, so the value "1" belongs to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "2" => -12, so the value "2" does not belong to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "6" => 5697900, so the value "6" does not belong to the INTERSECTION
"[0,1,1,2,3]" "[0,1,1,4,5]" "-1" => 124416, so the value "-1" does not belong to the INTERSECTION