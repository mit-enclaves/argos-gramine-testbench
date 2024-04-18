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
    "tcp-vanilla-vm",
    "tcp-tyche-vm",
    "tcp-encr",
    "tcp-ssl",
]

labels = [
    "Linux native",
    "Anon native",
    "Anon enclave",
    "Linux VM",
    "Anon VM",
    "Nested enclaves",
    "SSL",
]

color_vanilla = "lightgreen"
color_tyche = "royalblue"

colors = [
    color_vanilla,
    color_tyche,
    color_tyche,
    color_vanilla,
    color_tyche,
    color_tyche,
    # color_tyche,
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
                "ops": json_data["ALL STATS"]["Totals"]["Ops/sec"],
                "latency": json_data["ALL STATS"]["Totals"]["Percentile Latencies"]["p99.00"] * 1000 # convert to μs
            }
        except json.JSONDecodeError as e:
            print(f"Error opening {filename}: {e}")

print(f"{'experiment': <16}, {'ops': <9}")
for (key, item) in data.items():
    print(f"{key: <16}, {item['ops']: <9}")


print(data)

exps = list(data.keys())
ops = [data[p]['ops'] for p in exps]
lat = [data[p]['latency'] for p in exps]

# Create two subplots for set and get operations
# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)  # Share x-axis for alignment
fig, ax1 = plt.subplots(1, 1, sharex=True, figsize=(6, 2.5))  # Share x-axis for alignment

# Plot set operations on first subplot
ax1.bar(labels, ops, color=colors)
ax1.set_ylabel('Requests/s')
ax1.set_title('Requests per seconds for different Redis configurations')
ax1.legend()

# Plot get operations on second subplot
# ax2.bar(labels, lat, color=colors)
# ax2.set_ylabel('p99 Latency (μs)')
# ax2.set_xlabel('Expriments')
# ax2.set_title('Get Operations per Second for Different Protocols')
# ax2.legend()

# Adjust layout for better spacing
handles = [
    plt.Rectangle((0,0),1,1, color=color_vanilla),
    plt.Rectangle((0,0),1,1, color=color_tyche),
]
legends = ["Stock Linux", "With Anon"]
plt.legend(handles, legends)
plt.xticks(rotation=25, ha='right')
plt.tight_layout()
# plt.show()
plt.savefig(save_as_pdf)
plt.savefig(save_as_png)
