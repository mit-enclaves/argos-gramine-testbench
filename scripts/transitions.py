import csv
import numpy as np
import matplotlib.pyplot as plt

PATH = "../data-asplos/ubench/transitions.csv"

save_as_pdf = "../figs/transitions.pdf"
save_as_png = "../figs/transitions.png"

raw = []
null = []
raw_rv = []
null_rv = []

with open(PATH, 'r') as file:
  csvreader = csv.reader(file)
  next(csvreader) # Drop first row
  for row in csvreader:
    raw.append(float(row[0]))
    null.append(float(row[1]))
    raw_rv.append(float(row[2]))
    null_rv.append(float(row[3]))

print(f"raw:       {np.average(raw):.5f} +/- {np.std(raw):.5f} us")
print(f"null:      {np.average(null):.5f} +/- {np.std(null):.5f} us")
print(f"raw-rv:    {np.average(raw_rv):.5f} +/- {np.std(raw_rv):.5f} us")
print(f"null-rv:   {np.average(null_rv):.5f} +/- {np.std(null_rv):.5f} us")

null_x86 = np.average(null)
null_rv = np.average(null_rv)
switch_x86 = np.average(raw)
switch_rv = np.average(raw_rv)

sdk = (
    "RISC-V",
    "x86_64",
)

switch_x86 = switch_x86 - null_x86
switch_rv = switch_rv - null_rv

data = {
    "Enter/Exit Anon": np.array([null_rv, null_x86]),
    "Save & restore TD": np.array([switch_rv, switch_x86]),
}
width = 0.5

fig, ax = plt.subplots(figsize=(5, 1.7))
# fig, ax = plt.subplots()
bottom = np.zeros(2)

for label, val in data.items():
    p = ax.barh(sdk, val, width, label=label, left=bottom)
    bottom += val

ax.set_title("TD switch")
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=False, ncol=3)
ax.set_xlabel("Elapsed time (µs)")
# plt.xticks(rotation=25, ha='right')
plt.tight_layout()
# plt.show()
plt.savefig(save_as_pdf)
plt.savefig(save_as_png)
