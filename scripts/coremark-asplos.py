import os
import numpy as np
import matplotlib.pyplot as plt

exp = [
    ("Linux Native", "../data/ubench/coremark_linux.txt"),
    ("Anon Native", "../data/ubench/coremark_tyche.txt"),
    ("Linux VM", "../data/ubench/coremark_linux_vm_1.txt"),
    ("Anon VM", "../data/ubench/coremark_tyche_vm_1.txt"),
]

NATIVE_PATH = "data-asplos/coremark-native/"
NATIVE = "native"
THEMIS_PATH = "data-asplos/coremark-themis/"
THEMIS = "sdktyche"

raw_data = {}

def parse_data(exp: str, path: str):
    for filename in os.listdir(path):
        prefix = filename.split(".")[0]
        nb_cores = int(prefix.split("_")[1])
        with open(path + filename, "r") as file:
            for line in file.readlines():
                if "CoreMark-PRO" not in line:
                    continue
                score = float(line.split()[1])
                if exp not in raw_data:
                    raw_data[exp] = []
                raw_data[exp].append((nb_cores, score))
                break
    raw_data[exp].sort(key = lambda x: x[0])

parse_data(NATIVE, NATIVE_PATH)
parse_data(THEMIS, THEMIS_PATH)

print(raw_data)

fig, ax = plt.subplots()

x = [elt[0] for elt in raw_data[NATIVE]]
y = [elt[1] for elt in raw_data[NATIVE]]
ax.plot(x, y, label="native")

x = [elt[0] for elt in raw_data[THEMIS]]
y = [elt[1] for elt in raw_data[THEMIS]]
ax.plot(x, y, label="themis")

ax.legend()
ax.set(xlabel='nb cpu', ylabel='CoreMark-Pro score',
       title='Multicore VM scaling')
ax.grid()

plt.show()
