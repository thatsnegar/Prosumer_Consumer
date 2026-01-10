import numpy as np

def retailer_generate_price_profile(num_steps:int):
    # In this function, the retailer generates grid price profile and the Energy Services Manager (GSE) the FiT price.

    hours = np.linspace(0, 24, num_steps, endpoint=False) #[0., 1., 2., ..., 23.] each index corresponds to an hour of the day

    # base pattern cheap at night, expensive in evening
    based = 0.20 + 0.10 * np.sin((hours - 19) / 24 * 2 * np.pi) ** 2 #peak is at 19:00
    noise = np.random.normal(0, 0.01, size=num_steps) 
    grid_price = based + noise 
    grid_price = np.clip(grid_price, 0.12, 0.45) # make sure prices stay within reasonable bounds of 0.12-0.45 €/kWh which is typical in europe
    # clip prevent too low or too high prices due to noise

    # Feed-in-Tariff: the Energy Services Manager (GSE) buys solar surplus to prosumers at FiT price
    # minimum guranteed price is used nowadays in Italy but we use a fixed FiT price to ensure price stability for prosumers
    fit_price = 0.08  # €/kWh grid buys surplus energy from prosumers and it is constant

    return grid_price, fit_price