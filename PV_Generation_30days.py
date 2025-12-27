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
    steps_per_day = 24
    num_dayes = num_steps // steps_per_day
    base_day = default_PV_shape(steps_per_day)

    # random PV capacity in kW for each prosumer -> some prosumers will have 0 which are our pure consumers
    capacities = np.random.uniform(0, 10, size=num_prosumers)  #
    
    pv = np.zeros((num_prosumers, num_steps))
    
    for d in range(num_dayes):
        day_factors = np.random.uniform(0.8, 1.2) #sunny/cloudy days
        daily_shape = base_day * day_factors

        for i in range(num_prosumers):
            noise = np.random.normal(1, 0.05, size=steps_per_day)  # small random noise
            noise = np.clip(noise, 0.7, 1.3)  # limit noise to reasonable bounds

            start =  d * steps_per_day
            end = start + steps_per_day

            pv[i, start:end] = capacities[i] * daily_shape * noise
    pv *= 1.0 ## kWh since Δt = 1h
    return pv, capacities
