
import csv

path = "c:/Users/kabhi/neurosymbolic/finalKG/data/nodes.csv"
targets = ["MTOR", "PRKAA1", "TP53", "EGFR", "BRCA1", "BRCA2", "ERBB2", "AKT1", "PIK3CA"]
mapping = {}

with open(path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader) 
    for row in reader:
        if row[2] in targets:
            mapping[row[2]] = row[0]
            
print("VIP_TARGETS_NEW = {")
for t in targets:
    if t in mapping:
        key = t if t != "PRKAA1" else "AMPK"
        if t == "ERBB2": key = "HER2"
        print(f'    "{key}": "{mapping[t]}",')
print("}")
