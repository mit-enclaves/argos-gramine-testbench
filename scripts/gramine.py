import os
import numpy as np
import matplotlib.pyplot as plt

GRAMINE_PATH = "data-asplos/gramine-sgx/"
TYCHE_PATH = "data-asplos/gramine-tyche/"
HYPER = "hyper.txt"

def parse_wrk(path: str):
    data = []
    with open(path, 'r') as file:
        for line in file:
            if not line.startswith("Requests/sec:"):
                continue

            req_per_sec = float(line.split()[1])
            data.append(req_per_sec)

            # We keep at most 10 samples
            if len(data) >= 10:
                break
    if len(data) < 10:
        print(f"WARNING: less than 10 samples in {path}")
    return data

sgx_hyper = parse_wrk(GRAMINE_PATH + HYPER)
tyche_hyper = parse_wrk(TYCHE_PATH + HYPER)

print(f"SGX:   {np.mean(sgx_hyper):.2f} +/- {np.std(sgx_hyper):.2f} Req/Sec")
print(f"Tyche: {np.mean(tyche_hyper):.2f} +/- {np.std(tyche_hyper):.2f} Req/Sec")
print(f"  Tyche is {np.mean(tyche_hyper) / np.mean(sgx_hyper):.2f}x faster than SGX")
