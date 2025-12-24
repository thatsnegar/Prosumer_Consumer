from typing import List, Tuple, Dict
# A seller or buyer offer is represented as :
# (prosumers_id, quantity_kwh, price_eur_perkwh)

def match_trades(
        asks : List[Tuple[int, float, float]], #seller offers
        bids : List[Tuple[int, float, float]] #buyer offers
)-> Tuple[
    List[Dict],  #executed trades
    List[Tuple[int, float, float]], #remaining asks
    List[Tuple[int, float, float]] #remaining bids
]:
    """
    Self-organized p2p market matching.

    Sellers are sorted by increasing price.
    Buyers are sorted by decreasing price.

    A trade happens if:
        buyer_price >= seller_price

    Trade quantity:
        min(seller_quantity, buyer_quantity)

    Clearing price:
        (seller_price + buyer_price) / 2

    Returns:
        trades          : list of executed trade dictionaries
        remaining_asks  : sellers not fully matched
        remaining_bids  : buyers not fully matched
    """


    # sort sekllers by increasing price => lowest price first
    asks = sorted(asks, key=lambda x: x[2])

    # sort buyers by decreasing price => highest price first
    bids = sorted(bids, key=lambda x: x[2], reverse=True)

    trades : List[Dict] = []
    i = 0 # index for sellers
    j = 0 # index for buyers

    while i < len(asks) and j < len(bids):
        seller_id, seller_qty, seller_price = asks[i]
        buyer_id, buyer_qty, buyer_price = bids[j]

        # Check if prices overlap
        if buyer_price < seller_price:
            break # No more feasible trades

        # determine traded quantity
        traded_qty = min(seller_qty, buyer_qty)

        # clearing price(simple midpoint rule)
        clearing_price = (seller_price + buyer_price) / 2

        # register trade
        trades.append(
            {
                "seller": seller_id,
                "buyer": buyer_id,
                "quantity": traded_qty,
                "price" : clearing_price,
                "type": "p2p"

            }
        )

        # update remaining quantities
        seller_qty -= traded_qty
        buyer_qty -= traded_qty

        # update seller 
        if seller_qty <= 1e-6:
            i += 1
        else:
            asks[i] = (seller_id, seller_qty, seller_price)

        # update buyer
        if buyer_qty <= 1e-6:
            j += 1
        else:
            bids[j] = (buyer_id, buyer_qty, buyer_price)
        
    # remaining offers go to the local market
    remaining_asks = asks[i:]
    remaining_bids = bids[j:]  

    return trades, remaining_asks, remaining_bids



def match_local_market(
        asks: List[Tuple[int, float, float]], #seller offers 
        bids: List[Tuple[int, float, float]], #buyer offers
        grid_price: float 
) -> Tuple[
    List[Dict],  #executed trades
    List[Tuple[int, float, float]], #remaining asks
    List[Tuple[int, float, float]] #remaining bids
]:
    
    """
    Local market operated by a community aggregator.

    Uses the same matching logic as p2p trading, but:
      - trades are labeled as 'local_market'
      - price is capped by the grid price

    Returns:
        local_trades
        remaining_asks
        remaining_bids
    """

    trades, remaining_asks, remaining_bids = match_trades(asks, bids)

    # relable trade and optionally cap price
    for trade in trades:
        trade["type"] = "local_market"
        # Ensure local market price does not exceed grid price
        trade["price"] = min(trade["price"], grid_price)

    return trades, remaining_asks, remaining_bids

