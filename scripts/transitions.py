import csv
import numpy as np

PATH = "../data/ubench/transitions.csv"

tyche = []
kvm = []
raw = []
null = []

with open(PATH, 'r') as file:
  csvreader = csv.reader(file)
  next(csvreader) # Drop first row
  for row in csvreader:
    tyche.append(float(row[0]))
    raw.append(float(row[1]))
    kvm.append(float(row[2]))
    null.append(float(row[3]))
    

print(f"sdk-tyche: {np.average(tyche):.5f} +/- {np.std(tyche):.5f} us")
print(f"kvm:       {np.average(kvm):.5f} +/- {np.std(kvm):.5f} us")
print(f"raw:       {np.average(raw):.5f} +/- {np.std(raw):.5f} us")
print(f"null:      {np.average(null):.5f} +/- {np.std(null):.5f} us")

