import numpy as np

def generate_price_profile(num_steps:int):

    steps_day_day = 24  
    num_days = num_steps // steps_day_day

    prices = np.zeros(num_steps)

    for d in range(num_days):


        hours = np.linspace(0, 24, num_steps, endpoint=False) #[0., 1., 2., ..., 23.] each index corresponds to an hour of the day

        # base pattern cheap at night, expensive in evening
        based = 0.20 + 0.10 * np.sin((hours - 19) / 24 * 2 * np.pi) ** 2 #peak is at 19:00
        noise = np.random.normal(0, 0.01, size=num_steps) 
        
        grid_price = based + noise
        grid_price = np.clip(grid_price, 0.12, 0.45) # make sure prices stay within reasonable bounds of 0.12-0.45 €/kWh which is typical in europe
        # clip prevent too low or too high prices due to noise
        fit_price = 0.08  # €/kWh grid buys surplus energy from prosumers and it is constant

        return grid_price, fit_price