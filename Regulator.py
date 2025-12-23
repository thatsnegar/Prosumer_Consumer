from typing import List, Dict 
from Agents import Prosumer


class Regulator:
    """
    Regulator that observes prosumer behavior and applies 
    reward/punishemnt rule to acheive a system level objective
    """

    def __init__(self, objective: str = "Maximize_p2p",
                 punish_threshold : float = 0.1,
                 reward_threshold : float = 0.5,
                 reward_amount : float = 0.1,):
        
        """
        Parameters:
        - objective (str): System level objective to achieve (maximize_p2p, maximize_profit, etc)
        - punish_threshold (float): minimum p2p participation rate to avoid punishment
        - reward_threshold (float): minimum p2p participation rate to receive reward
        - reward_amount (float): amount of reward/punishment to apply
        """

        self.objective = objective
        self.punish_threshold = punish_threshold
        self.reward_threshold = reward_threshold
        self.reward_amount = reward_amount


     # system level objective evaluation 
    
    def evaluate_objectives(self, stats_t: Dict)-> float:
        """
        evaluate the regulator objective based on community statics
        """

        if self.objective == "Maximize_p2p":
            return stats_t.get("P2P_share", 0.0)
        
        if self.objective == "Maximize_profit":
            return stats_t.get("Community_profit", 0.0)
        
        return 0.0
    
    # apply regulation rules

    def apply_rules(self, prosumers: List[Prosumer]) -> None:
        """
        apply reward and punishment rules to each prosumer 
        based on behavior in the previous time step
        """

        for p in prosumers:
            
            # reset ban by default => ban lasts one time step
            p.banned = False

            # if no surplus, nothing to evaluate 
            if p.surplus_today <= 0:
                p.reset_step_metrics()
                continue

            # Participation ratio 
            participation_ratio = p.p2p_traded_today / p.surplus_today + 1e-6


            # punishment 
            if participation_ratio < self.punish_threshold:
                p.banned = True
            
            # reward
            elif participation_ratio >= self.reward_threshold:
                # small monetary bonus
                p.money += self.reward_amount

            # reset metrics for next step
            p.reset_step_metrics()



            
    

