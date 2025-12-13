
import csv

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/nodes.csv"

with open(path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader) 
    found = 0
    for row in reader:
        if row[2] == "MTOR":
            print(f"Found MTOR: {row}")
            print(f"ID is: {row[0]}")
            found += 1
        if row[2] == "TP53":
             print(f"Found TP53: {row}")
             print(f"ID is: {row[0]}")
             found += 1
             
        if found >= 2: break
