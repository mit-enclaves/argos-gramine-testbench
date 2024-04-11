import os
import json
import matplotlib.pyplot as plt

path = "../data/"
save_as_pdf = "../figs/redis.pdf"
save_as_png = "../figs/redis.png"

# Get all Redis benchmark files
experiments = [
    "tcp-vanilla",
    "tcp-tyche",
    "tcp-enclave",
    "tcp-encr",
    "tcp-ssl",
]

data = {}

for exp in experiments:
    filename = f"{path}redis-{exp}.json"
    # Open the file in read mode
    with open(filename, "r") as json_file:
        # Load the JSON content
        try:
            json_data = json.load(json_file)

            data[exp] = {
                "set": json_data["ALL STATS"]["Sets"]["Ops/sec"],
                "get": json_data["ALL STATS"]["Gets"]["Ops/sec"],
            }
        except json.JSONDecodeError as e:
            print(f"Error opening {filename}: {e}")

print(f"{'experiment': <16}, {'get': <9}, {'set': <9}")
for (key, item) in data.items():
    print(f"{key: <16}, {item['get']: <9}, {item['set']: <9}")


print(data)

exps = list(data.keys())
set_ops = [data[p]['set'] for p in exps]
get_ops = [data[p]['get'] for p in exps]

# Extract set and get operations data for each protocol
exps = list(data.keys())
set_ops = [data[p]['set'] for p in exps]
get_ops = [data[p]['get'] for p in exps]

# Create two subplots for set and get operations
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)  # Share x-axis for alignment

# Plot set operations on first subplot
ax1.bar(exps, set_ops)
ax1.set_ylabel('Set ops/s')
ax1.set_title('Requests per seconds for different Redis configurations')
# ax1.legend()

# Plot get operations on second subplot
ax2.bar(exps, get_ops)
ax2.set_xlabel('Protocols')
ax2.set_ylabel('Get ops/s')
# ax2.set_title('Get Operations per Second for Different Protocols')
# ax2.legend()

# Adjust layout for better spacing
plt.tight_layout()
# plt.show()
plt.savefig(save_as_pdf)
plt.savefig(save_as_png)
