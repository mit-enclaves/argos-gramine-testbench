import json
import matplotlib.pyplot as plt
import utils

DATA_PATH = "data-asplos/"
REDIS_FILE = "redis.json"
NATIVE = "native/"
NATIVE_VM = "native-vm/"
GRAMINE_TYCHE = "gramine-tyche/"
GRAMINE_SGX = "gramine-sgx/"
TYCHE = "tyche/"
THEMIS = "themis-vm/"
THEMIS_CONF = "themis-conf/"
THEMIS_GRAMINE = "themis-conf-gramine/"


def get_data(path):
    # Load the JSON data
    with open(path, "r") as f:
        data = json.load(f)

    # Extract the latency values and corresponding percentiles
    latencies = [item["<=msec"] for item in data["ALL STATS"]["GET"]][1:]
    percentiles = [item["percent"] for item in data["ALL STATS"]["GET"]][1:]

    return latencies, percentiles

# sgx_latencies, sgx_percentiles = get_data(DATA_PATH + GRAMINE_SGX)

# # Plot the latency data as a line chart
# plt.plot(sgx_latencies, sgx_percentiles, marker="", linestyle="-", label = "Gramine SGX")
# plt.plot(tyche_latencies, tyche_percentiles, marker="", linestyle="-", label = "Gramine Tyche")

def plot_one(path: str, label: str):
    latencies, percentiles = get_data(DATA_PATH + path + REDIS_FILE)
    plt.plot(latencies, percentiles, marker="", linestyle="-", label = label)

plt.figure(figsize=(6.4, 2.6))
plt.subplots_adjust(bottom=0.18)

plot_one(NATIVE,        "Native")
plot_one(NATIVE_VM,     "Native VM")
plot_one(GRAMINE_SGX,   "SGX enclave")
plot_one(TYCHE,         "TD0")
plot_one(THEMIS,        "TD1 VM")
plot_one(THEMIS_CONF,   "TD1 CVM")
plot_one(GRAMINE_TYCHE, "TD1 enclave")
plot_one(THEMIS_GRAMINE, "TD2 enclave")

# Set the chart title and labels
plt.title("Redis GET Latency Distribution")
plt.xlabel("Latency (ms)")
plt.ylabel("Percentile")
plt.legend()

# Customize the grid and axis limits
plt.grid(True)

# tyche_latencies, _ = get_data(DATA_PATH + GRAMINE_TYCHE)
# plt.xlim(0, max(tyche_latencies) * 1.1)  # Adjust x-axis limit if needed
plt.xlim(0, 25)  # Adjust x-axis limit
plt.ylim(0, 100)
# plt.yscale('log')


# Show the plot
utils.plot_or_save("redis_latency")
