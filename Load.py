import numpy as np

def generate_load_profile(num_prosumers: int, num_steps: int):

    print(">>> NEW DOUBLE-PEAK LOAD PROFILE USED <<<")


    hours = np.linspace(0, 24, num_steps, endpoint=False)

    # --- Base load (always-on devices) ---
    base_load = 0.4 * np.ones_like(hours)

    # --- Morning peak (around 7–9) ---
    morning_peak = np.exp(-0.5 * ((hours - 7.5) / 1.5) ** 2)

    # --- Evening peak (around 18–22) ---
    evening_peak = np.exp(-0.5 * ((hours - 19.5) / 2.0) ** 2)

    # Combined normalized shape
    shape = (
        base_load +
        1.2 * morning_peak +
        1.6 * evening_peak
    )

    shape = shape / shape.sum()  # normalize to daily energy

    loads = np.zeros((num_prosumers, num_steps))

    for i in range(num_prosumers):
        # Daily household energy (kWh/day)
        daily_energy = np.random.uniform(8, 25)

        # Individual randomness
        noise = np.random.normal(1.0, 0.15, size=num_steps)
        noise = np.clip(noise, 0.6, 1.5)

        loads[i, :] = daily_energy * shape * noise

    return loads
