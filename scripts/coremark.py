import csv
import numpy as np
import matplotlib.pyplot as plt

exp = [
    ("Linux Native", "../data/ubench/coremark_linux.txt"),
    ("Anon Native", "../data/ubench/coremark_tyche.txt"),
    ("Linux VM", "../data/ubench/coremark_linux_vm_1.txt"),
    ("Anon VM", "../data/ubench/coremark_tyche_vm_1.txt"),
]

raw_data = {}

for (exp_name, file_path) in exp:
    with open(file_path, 'r') as file:
      for line in file.readlines():
        if not "CoreMark-PRO" in line:
            continue
        values = line.split()
        if not exp_name in raw_data:
            raw_data[exp_name] = []
        raw_data[exp_name].append(float(values[2]))


for (name, values) in raw_data.items():
    print(f"{name: <16}{np.mean(values):.2f} +/- {np.std(values):.2f}")

