import numpy as np  

def generate_load_profile(num_prosumers : int, num_steps: int):

    steps_per_day = 24
    num_dyas = num_steps // steps_per_day
    hours = np.linspace(0, 24, steps_per_day, endpoint=False)
    base_shape = 0.5 + 0.5 * np.sin((hours - 18) / 24 * 2 * np.pi)
    base_shape -= base_shape.min()
    base_shape -= base_shape.min()

    loads = np.zeros((num_prosumers, num_steps))

    for i in range(num_prosumers):
       avg_daily_energy = np.random.uniform(10, 30)

       for d in range(num_dyas):
           daily_energy =  avg_daily_energy * np.random.uniform(0.9, 1.1)

           profile = base_shape / base_shape.sum() * daily_energy
           noise = np.random.normal(1, 0.1, size=steps_per_day)
           noise = np.clip(noise, 0.6, 1.4)

           start = d * steps_per_day
           end = start + steps_per_day
           loads[i, start:end] = profile * noise

    return loads

        

           
