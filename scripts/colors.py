import numpy as np
import matplotlib.pyplot as plt

# base_cmaps = ['Greys','Purples','Reds','Blues','Oranges','Greens']

def get_shades(color: str):
    N = 5 # number of colors to extract from each of the base_cmaps below
    return plt.get_cmap(color)(np.linspace(0.2,0.8,N))[::-1]

def get_tyche():
    return get_shades("Blues")

def get_native():
    return get_shades("Greens")
