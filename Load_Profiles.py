import numpy as np  

def generate_load_profile(num_prosumers : int, num_steps: int):

    hours = np.linspace(0, 24, num_steps, endpoint=False)

    # base load shape : more in evening, less at night  
    base_shape = 0.5 + 0.5 * np.sin((hours - 18) / 24 * 2 * np.pi)
    base_shape = base_shape - base_shape.min()  # shift to be non-negative
    base_shape = base_shape / base_shape.max()  # normalize to [0, 1]

    loads = np.zeros((num_prosumers, num_steps))

    for i in range(num_prosumers):
        # each prosumer has a personal average daily energy (kwh/day)
        daily_energy = np.random.uniform(10, 30)  # between 10 and 30 kWh/day
        # distribute this daily energy according to the shape
        profile = base_shape / base_shape.sum() * daily_energy 
        noise = np.random.normal(1, 0.1, size=num_steps) 
        noise = np.clip(noise, 0.6, 1.4)
        loads[i, :] = profile * noise

    return loads