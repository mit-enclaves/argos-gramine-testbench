import csv
import numpy as np
import matplotlib.pyplot as plt

PATH = "../data/ubench/transitions.csv"

save_as_pdf = "../figs/transitions.pdf"
save_as_png = "../figs/transitions.png"

tyche = []
kvm = []
raw = []
null = []
raw_rv = []
tyche_rv = []
null_rv = []

with open(PATH, 'r') as file:
  csvreader = csv.reader(file)
  next(csvreader) # Drop first row
  for row in csvreader:
    tyche.append(float(row[0]))
    raw.append(float(row[1]))
    kvm.append(float(row[2]))
    null.append(float(row[3]))
    tyche_rv.append(float(row[4]))
    raw_rv.append(float(row[5]))
    null_rv.append(float(row[6]))

print(f"sdk-tyche: {np.average(tyche):.5f} +/- {np.std(tyche):.5f} us")
print(f"kvm:       {np.average(kvm):.5f} +/- {np.std(kvm):.5f} us")
print(f"raw:       {np.average(raw):.5f} +/- {np.std(raw):.5f} us")
print(f"null:      {np.average(null):.5f} +/- {np.std(null):.5f} us")
print(f"tyche-rv:  {np.average(tyche_rv):.5f} +/- {np.std(tyche_rv):.5f} us")
print(f"raw-rv:    {np.average(raw_rv):.5f} +/- {np.std(raw_rv):.5f} us")
print(f"null-rv:   {np.average(null_rv):.5f} +/- {np.std(null_rv):.5f} us")

null_x86 = np.average(null)
null_rv = np.average(null_rv)
switch_x86 = np.average(raw)
switch_rv = np.average(raw_rv)
tyche_x86 = np.average(tyche)
tyche_rv = np.average(tyche_rv)
kvm_x86 = np.average(kvm)

sdk = (
    "Anon-capa\nx86_64",
    "KVM-Anon\nx86_64",
    "Anon-capa\nRISC-V",
)

switch_x86 = switch_x86 - null_x86
switch_rv = switch_rv - null_rv
tyche_x86 = tyche_x86 - switch_x86
tyche_rv = tyche_rv - switch_rv
kvm_x86 = kvm_x86 - switch_x86

data = {
    "Call to Anon": np.array([null_x86, null_x86, null_rv]),
    "Save & restore": np.array([switch_x86, switch_x86, switch_rv]),
    "SDK + Driver": np.array([tyche_x86, kvm_x86, tyche_rv]),
}
width = 0.5

fig, ax = plt.subplots(figsize=(5, 2))
# fig, ax = plt.subplots()
bottom = np.zeros(3)

for label, val in data.items():
    p = ax.bar(sdk, val, width, label=label, bottom=bottom)
    bottom += val

ax.set_title("TD context switch")
ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=False, ncol=3)
ax.set_ylabel("Elapsed time (µs)")
# plt.xticks(rotation=25, ha='right')
plt.tight_layout()
# plt.show()
plt.savefig(save_as_pdf)
plt.savefig(save_as_png)
