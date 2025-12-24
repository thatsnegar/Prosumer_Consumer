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
        reward_threshold: float = 0.5,
        reward_amount: float = 0.1
    ):
        self.objective = objective
        self.punish_threshold = punish_threshold
        self.reward_threshold = reward_threshold
        self.reward_amount = reward_amount

    # --------------------------------------------------
    # System-level objective evaluation
    # --------------------------------------------------
    def evaluate_objective(self, stats_t: Dict) -> float:
        """
        Evaluate the regulator objective based on community statistics.
        """

        if self.objective == "maximize_p2p":
            return stats_t.get("p2p_share", 0.0)

        if self.objective == "maximize_profit":
            return stats_t.get("community_profit", 0.0)

        return 0.0

    # --------------------------------------------------
    # Apply regulation rules
    # --------------------------------------------------
    def apply_rules(self, prosumers: List[Prosumer]) -> None:
        """
        Apply reward and punishment rules to each prosumer
        based on behavior in the previous time step.
        """

        for p in prosumers:

            # Ban lasts only one step
            p.banned = False

            # No surplus => nothing to evaluate
            if p.surplus_today <= 0:
                p.reset_step_metrics()
                continue

            # Participation ratio
            participation_ratio = (
                p.p2p_traded_today / (p.surplus_today + 1e-6)
            )

            # Punishment
            if participation_ratio < self.punish_threshold:
                p.banned = True

            # Reward
            elif participation_ratio >= self.reward_threshold:
                p.money += self.reward_amount

            # Reset metrics for next step
            p.reset_step_metrics()
