import sys
import matplotlib.pyplot as plt

def plot_or_save(filename: str):
    if "--save" in sys.argv:
        plt.savefig("figs/" + filename + ".pdf", bbox_inches='tight')
        plt.savefig("figs/" + filename + ".png", bbox_inches='tight')
    else:
        plt.show()
        
