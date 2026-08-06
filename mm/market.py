import numpy as np #for random
import matplotlib.pyplot as plt #for plotting

#create a random number generator with seed 42
rng = np.random.default_rng(42)
price = 100.0 #initial price
path = [price] #list storing price path at each time step

#simulate price path for 1000 time steps
for _ in range(1000): #_ is a throwaway variable since we don't need the loop index
    price += rng.normal(0.0, 0.05) #normal distribution with mean 0 and std dev 0.05
    path.append(price) #add new price to path

#plot the price path
plt.plot(path)
plt.xlabel('Time Step')
plt.ylabel('Price')
plt.savefig("results/figures/day_2_price_path.png", dpi=150) #save the plot as a PNG file





