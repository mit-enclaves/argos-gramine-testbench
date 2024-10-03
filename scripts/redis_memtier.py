import json
import matplotlib.pyplot as plt

DATA_PATH = "data-asplos/"
GRAMINE_TYCHE = "redis-gramine-tyche.json"
GRAMINE_SGX = "redis-gramine-sgx.json"


def get_data(path):
    # Load the JSON data
    with open(path, "r") as f:
        data = json.load(f)

    # Extract the latency values and corresponding percentiles
    latencies = [item["<=msec"] for item in data["ALL STATS"]["GET"]][1:]
    percentiles = [item["percent"] for item in data["ALL STATS"]["GET"]][1:]

    return latencies, percentiles

tyche_latencies, tyche_percentiles = get_data(DATA_PATH + GRAMINE_TYCHE)
sgx_latencies, sgx_percentiles = get_data(DATA_PATH + GRAMINE_SGX)

# Plot the latency data as a line chart
plt.plot(sgx_latencies, sgx_percentiles, marker="", linestyle="-", label = "Gramine SGX")
plt.plot(tyche_latencies, tyche_percentiles, marker="", linestyle="-", label = "Gramine Tyche")

# Set the chart title and labels
plt.title("Redis GET Latency Distribution")
plt.xlabel("Latency (ms)")
plt.ylabel("Percentile")
plt.legend()

# Customize the grid and axis limits
plt.grid(True)
plt.xlim(0, max(tyche_latencies) * 1.1)  # Adjust x-axis limit if needed
plt.ylim(0, 100)
# plt.yscale('log')


# Show the plot
plt.show()
