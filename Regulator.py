from typing import List, Dict
from Agents import Prosumer


class Regulator:
    """
    Regulator that observes prosumer behavior and applies
    reward/punishment rules to achieve a system-level objective.
    """

    def __init__(
        self,
        objective: str = "maximize_p2p",
        punish_threshold: float = 0.1,
        reward_threshold_silver: float = 0.5,
        reward_threshold_gold: float = 0.8,
        reward_amount1: float = 0.025,
        reward_amount2: float = 0.05,
        reward_amount3: float = 0.1
    ):
        self.objective = objective
        self.punish_threshold = punish_threshold
        self.reward_threshold_silver = reward_threshold_silver
        self.reward_threshold_gold = reward_threshold_gold
        self.reward_amount1 = reward_amount1
        self.reward_amount2 = reward_amount2
        self.reward_amount3 = reward_amount3

    # --------------------------------------------------
    # System-level objective evaluation
    # --------------------------------------------------
    def evaluate_objective(self, stats_t: Dict) -> float:
        """
        Evaluate the regulator objective based on community statistics.
        """

        if self.objective == "maximize_p2p":
            #return stats_t.get("p2p_share", 0.0)
            return stats_t.get("P2P_penetration_ratio", 0.0)

        # if we want to maximize profit, not implemented in the project but potential improvement
        if self.objective == "maximize_profit":
            return stats_t.get("community_profit", 0.0)

        return 0.0

    # --------------------------------------------------
    # Apply regulation rules
    # --------------------------------------------------
    def apply_rules(self, prosumers: List[Prosumer], total_community_surplus: float, total_community_deficit: float) -> None:
        """
        Apply reward and punishment rules to each prosumer
        based on behavior in the previous time step.
        """

        for p in prosumers:

            # We do not ban prosumers in this regulation
            p.banned = False

            """"
             For this regulation, we consider the imbalance of the prosumer as the potential P2P trade. 
             Thus we consider both surplus and deficit situations which can both lead to P2P trading.
             This allows to evaluate the participation ratio in P2P trading (P2P buy for deficit, P2P sell for surplus).
             last_imbalance represents the net surplus (positive) or deficit (negative) of the prosumer after local consumption and production.
            """

            
            # We define the theoric maximum P2P trade for this agent
            # => This allows not to punish prosumers for not trading with P2P while there is a lack of supply / demand on the market

            if p.last_imbalance > 0: #Seller
                # He can't sell more than his surplus
                # AND he can't sell more than the total community demand
                achievable_p2p = min(abs(p.last_imbalance), total_community_deficit)
            else: #Buyer
                # He can't buy more than his deficit
                # AND he can't buy more than the total community offer
                achievable_p2p = min(abs(p.last_imbalance), total_community_surplus)  

            #Security: if P2P market is empty (no offer/demand)
            if achievable_p2p <= 1e-6:
                p.reset_step_metrics()
                continue


            # Participation ratio
            participation_ratio = p.p2p_traded_today / (achievable_p2p + 1e-6)

            # PUNISHMENT
            if participation_ratio < self.punish_threshold:

                # Case 1: If it's a buyer but there is no P2P offers available
                if p.last_imbalance < 0 and total_community_surplus == 0:
                    pass # We don't punish the seller if he has nothing to buy

                # Case 2: If it's a seller but there is no P2P demand available
                elif p.last_imbalance > 0 and total_community_deficit == 0:
                    pass # We don't punish the buyer if there is no offer
                
                # Case 3: The prosumer did not participate despite available P2P offers/demands
                else:
                    #p.banned = True: we could have ban the prosumer but it had a negative effect on p2p share so we didn't
                    # Deduct a fine from the prosumer's money instead:
                    p.money -= 0.2
                    # Agent "learns" that he must be more cooperative in future to avoid being fined
                    p.trade_fraction = min(1.0, p.trade_fraction + 0.1)


                """
                REWARD
                with the reward, prosumer becomes more cooperative in future and trades more
                However, the behavior boost decreases after a certain level despite the increase of reward
                (The reward system becomes insensitive after a certain level)
                """
            elif self.punish_threshold <= participation_ratio < self.reward_threshold_silver:
                p.money += self.reward_amount1
                p.trade_fraction = min(1.0, p.trade_fraction + 0.03) #First behavior boost

            elif self.reward_threshold_silver <= participation_ratio < self.reward_threshold_gold:
                p.money += self.reward_amount2
                p.trade_fraction = min(1.0, p.trade_fraction + 0.015) #Second behavior boost

            elif participation_ratio >= self.reward_threshold_gold:
                p.money += self.reward_amount3
                p.trade_fraction = min(1.0, p.trade_fraction + 0.01) #Third behavior boost


            # Reset metrics for next step
            p.reset_step_metrics()
