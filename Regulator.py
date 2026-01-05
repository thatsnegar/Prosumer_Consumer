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
        reward_amount1: float = 0.1,
        reward_amount2: float = 0.3,
        reward_amount3: float = 0.5
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
            return stats_t.get("p2p_share", 0.0)

        # if we want to maximize profit what we are going to do 
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

            # Ban lasts only one step
            p.banned = False

            # For this regulation, we consider the imbalance of the prosumer as the potential P2P trade. 
            # Thus we consider both surplus and deficit situations which can both lead to P2P trading.
            # This allows to evaluate the participation ratio in P2P trading (P2P buy for deficit, P2P sell for surplus).
            # last_imbalance represents the net surplus (positive) or deficit (negative) of the prosumer after local consumption and production.

            potential_p2p = abs(p.last_imbalance)

            # No imbalance => nothing to evaluate
            if potential_p2p <= 1e-6:
                p.reset_step_metrics()
                continue

            # Participation ratio
            participation_ratio = p.p2p_traded_today / (potential_p2p)


            # PUNISHMENT
            if participation_ratio < self.punish_threshold:

                # Case 1: If it's a buyer but there is no P2P offers available
                if p.last_imbalance < 0 and total_community_surplus == 0:
                    pass # We don't ban the seller if he has nothing to buy

                # Case 2: If it's a seller but there is no P2P demand available
                elif p.last_imbalance > 0 and total_community_deficit == 0:
                    pass # We don't ban the buyer if there is no offer
                
                # Case 3: The prosumer did not participate despite available P2P offers/demands
                else:
                    p.banned = True
                    # Agent "learns" that he must be more cooperative in future to avoid being banned
                    p.trade_fraction = min(1.0, p.trade_fraction + 0.1)

            # REWARD
            # with the reward, prosumer becomes more cooperative in future and trades more
            # However, the behavior boost decreases after a certain level despite the increase of reward
            # (The reward system becomes insensitive after a certain level)
            elif self.punish_threshold <= participation_ratio < self.reward_threshold_silver:
                p.money += self.reward_amount1
                p.trade_fraction = min(1.0, p.trade_fraction + 0.05) #First behavior boost

            elif self.reward_threshold_silver <= participation_ratio < self.reward_threshold_gold:
                p.money += self.reward_amount2
                p.trade_fraction = min(1.0, p.trade_fraction + 0.03) #Second behavior boost

            elif participation_ratio >= self.reward_threshold_gold:
                p.money += self.reward_amount3
                p.trade_fraction = min(1.0, p.trade_fraction + 0.01) #Third behavior boost


            # Reset metrics for next step
            p.reset_step_metrics()
