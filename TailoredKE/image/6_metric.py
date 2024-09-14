import matplotlib.pyplot as plt
import numpy as np

# Define data
x = np.arange(1, 11)
y = np.random.randint(1, 10, size=(10, 3))

# Define titles for each line graph
titles = ["Original GPT", "PMT", "MEMIT", "MEND", "ROME", "Generalization"]

# Define the grid layout
fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))

# Loop through each line graph and plot it
for i, ax in enumerate(axs.flat):
    if i < len(titles):
        ax.plot(x, y[:, i], color=["orange", "purple", "yellow"][i % 3])
        ax.set_title(titles[i])
        ax.set_xlabel("Number of Edits")
        ax.set_ylabel("Score")

# Add overall labels
fig.suptitle("Editing Performance of PMET and Baselines", fontsize=16)
fig.text(0.5, 0.04, "Number of Edits", ha="center", fontsize=14)
fig.text(0.04, 0.5, "Score", va="center", rotation="vertical", fontsize=14)

plt.show()
