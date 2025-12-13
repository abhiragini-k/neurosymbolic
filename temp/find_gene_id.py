
import csv

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/nodes.csv"

with open(path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader) # header
    for row in reader:
        # id, kind, name, source
        # or similar structure. Let's check format.
        # usually: id, <metanode>, name, ...
        if "PRKAA1" in row:
            print(f"Found PRKAA1: {row}")
            if row[2] == "PRKAA1":
                print(f"ID is: {row[0]}")
