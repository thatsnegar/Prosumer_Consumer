from __future__ import annotations
from dataclasses import dataclass, field #simplifies class creation
from typing import Literal, Tuple, Optional #restrict return values => buyer, sellers, none
Role = Literal["buyer", "seller", "none"]

@dataclass
class Prosumer:
    """
    A simple Prosumer agent.

    State:
      - money: cumulative profit (positive) / cost (negative)
      - banned: if True, prosumer is not allowed to participate in P2P trading this step

    Per-step metrics (useful for regulator rules):
      - surplus_today: total surplus energy observed in self-balance (kWh)
      - p2p_traded_today: total energy traded via P2P/local markets (kWh)
      - last_imbalance: latest computed imbalance (kWh)
    """ 
       
    id:int
    has_pv : bool

    #Ecomomic/ regulatory state
    money : float = 0.0
    banned : bool = False

    # per step metrics(reset each step)
    surplus_today : float = 0.0
    p2p_traded_today : float = 0.0
    last_imbalance : float = 0.0


    # behavior knobs
    trade_fraction : float = 0.75  # α: fraction of imbalance to trade in markets
    undercut_factor : float = 0.9  # β: seller price = β * grid_price (slightly cheaper than grid)
    


    def reset_step_metrics(self) -> None:
            """Reset per-step metrics at the beginning of each simulation step.
            regulator evaluates behavior and metrics must be reset each step.
            """
            self.surplus_today = 0.0
            self.p2p_traded_today = 0.0
            self.last_imbalance = 0.0

    def self_balance(self, load_t: float,pv_t: float) -> float:
        """
        Step 1: self-balancing using own PV (and/or other internal resources if extended later).
        Returns imbalance (kWh):
            >0 surplus (can sell), <0 deficit (needs to buy)
        """

        imbalance = pv_t - load_t #we put this formula in the slide 
        self.last_imbalance = imbalance

        if imbalance > 0:
            self.surplus_today += imbalance
        return imbalance




    def decide_P2P_offer(
            self, 
            imbalance: float,
            grid_price_t : float,
            *,
            min_trade_kwh : float = 1e-3,
            cap_kwh :Optional[float] = None  
    ) -> Tuple[Role, float, float]:
            """
            Step 2: decision for self-organized trading (P2P).
            Returns: (role, quantity_kwh, price_eur_per_kwh)

            Strategy (simple baseline):
            - If banned or near-zero imbalance => no offer
            - Trade a fixed fraction of imbalance magnitude
            - Seller offers slightly below grid price
            - Buyer bids up to grid price
            - Optional cap_kwh limits the maximum quantity offered/bid
            """

            if self.banned or abs(imbalance) < min_trade_kwh: #banned prosumers cannot trade , zero imbalance => no trade 
                return "none", 0.0, 0.0
            
            qty = abs(imbalance) * self.trade_fraction

            if cap_kwh is not None:
                    qty = min(qty, max(cap_kwh, 0.0))
            
            if qty < min_trade_kwh:
                return "none", 0.0, 0.0
            
            if imbalance > 0:
                #seller: offer a price slightly below grid price
                price = self.undercut_factor * grid_price_t
                return "seller", qty, price
            else:
                #buyer: willing to pay up to grid price
                price = grid_price_t
                return "buyer", qty, price


    def apply_trade_result(self, role:Role, traded_qty_kwh: float, price:float) -> None:
        """
        Apply a settled trade outcome to this prosumer's state.
        - seller earns: +qty*price
        - buyer pays:   -qty*price
        Also updates p2p_traded_today for regulator metrics.
        """

        if traded_qty_kwh <= 0.0:
            return
        if role == "seller":
            self.money += traded_qty_kwh * price
            self.p2p_traded_today += traded_qty_kwh

        elif role == "buyer":
            self.money -= traded_qty_kwh * price
            self.p2p_traded_today += traded_qty_kwh
        
        


    def settle_with_grid(self,remaining_imbalance: float, grid_price_t: float, fit_price: float) -> Tuple[float, float]:
            """
            Step 3 (fallback): settle any remaining imbalance with the utility grid.
            If remaining_imbalance > 0 (surplus): sell to grid at fit_price
            If remaining_imbalance < 0 (deficit): buy from grid at grid_price_t

            Returns: (grid_import_kwh, grid_export_kwh)
            """

            grid_import = 0.0
            grid_export = 0.0

            if remaining_imbalance > 0:
                # export surplus to grid 
                grid_export = remaining_imbalance
                self.money += remaining_imbalance * fit_price

            elif remaining_imbalance < 0:
                # import deficit from grid
                grid_import = -remaining_imbalance
                self.money -= -remaining_imbalance * grid_price_t
            
            return grid_import, grid_export





