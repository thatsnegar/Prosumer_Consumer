import numpy as np

# Simple bell_shaped PV profile over a day and we assume that no of steps would cover 24h evenly
# different production bc of the different amount of sun during 24h => bell_shaped sunlight intensity 
def default_PV_shape(num_steps: int) -> np.array:
    hours = np.linspace(0, 24, num_steps, endpoint=False)
    # define peak around noon(12h)
    shape = np.exp(-0.5 * ((hours - 12) / 3) ** 2) #Gaussian bell shape
    shape = shape / shape.max()  # normalize to 1
    return shape


# Here we generate PV production for each prosumer and time step 
# what we return is 
# pv[KWH] : np.array of shape (num_prosumers, num_steps)
# capacity[KW] : np.array of shape (num_prosumers,)

def generate_PV_profile(num_prosumers: int, num_steps: int):
    base_shape = default_PV_shape(num_steps)

    # random PV capacity in kW for each prosumer -> some prosumers will have 0 which are our pure consumers
    capacities = np.random.uniform(0, 10, size=num_prosumers)  # capacities between 0 and 10 kW if capacity = 0 -> pure consumer
    pv = np.zeros((num_prosumers, num_steps))
    
    for i in range(num_prosumers):
        noise = np.random.normal(0, 0.05, size=num_steps)  # small random noise per prosumer weather variation and etc 
        # noise example :
        # 1 => perfect shape 
        # 1.3 => 30% more production (very sunny day)
        # 0.7 => 30% less production (cloudy day)
        noise = np.clip(noise, 0.7, 1.3)
        pv[i, :] = capacities[i] * base_shape * noise  #kw approximation

    #convert from kw to kwh per time step
    #if num_steps = 24 -> Δt = 1h, so kw * 1h = kwh
    #for generality:
    delta_t = 24 / num_steps  # hours per time step
    pv = pv * delta_t  # convert from kW to kWh
    return pv, capacities
# PV => matrix of shape (num_prosumers, num_steps) with kWh production values
# capacity => PV size for each prosumer
    