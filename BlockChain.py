from __future__ import annotations
import hashlib
import json
import time
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Block:
    """
    A single block in the blockchain.
    using json.dump to ensure stable serialization
    """

    index : int #  block number 
    previous_hash : str #hash of previous block
    transactions : List[Dict] #list of energy trades 
    miner_id : int #who mind/validate this block 
    timestamp : float = field(default_factory=time.time)
    nonce:  int = 0 # number used for proof of work
    hash : str = "" # cryptographic finger print 
 
    def compute_hash(self) -> str:
        """
        Computes the SHA-256 hash of the block's contents.
        """
        block_string = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "miner_id": self.miner_id,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
        }

        block_string = json.dumps(block_string, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:

    def __init__(self, difficulty=3, miner_ids=None):
        self.difficulty = difficulty
        self.chain = []

        if miner_ids is None:
            self.miner_ids = list(range(10))
        else:
            if len(miner_ids) < 10:
                raise ValueError("At least 10 miner IDs are required.")
            self.miner_ids = miner_ids

        self.create_genesis_block()

    
    def create_genesis_block(self) -> None:
        """
        create the first block with index 0
        """

        miner_id = random.choice(self.miner_ids)
        genesis = Block(index=0, previous_hash="0", transactions=[], miner_id=miner_id, nonce=0)
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    def last_block(self) -> Block:
        """
        returns the last block in the chain
        """
        return self.chain[-1]


    def mine_block(self, transactions : List[Dict]) -> Block:
        """
        Mine a new block containing the given transactions using Proof of Work.
        """

        previous = self.last_block()
        new_index = previous.index + 1
        previous_hash = previous.hash

        miner_id = random.choice(self.miner_ids)
        block = Block(index=new_index, previous_hash=previous_hash, transactions=transactions, miner_id=miner_id)

        prefix_str = '0' * self.difficulty

        nonce = 0
        while True:
            block.nonce = nonce
            block.hash = block.compute_hash()

            if block.hash.startswith(prefix_str):
                break
            nonce += 1

        self.chain.append(block)
        return block
    

    def is_valid(self) -> bool:
        """Check blockchain integrity and PoW validity."""

        prefix = '0' * self.difficulty

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

            if not current.hash.startswith(prefix):
                return False

        return True

    
    
    def summary(self) -> Dict :
        """
        A short summary
        """

        total_tx = sum(len(block.transactions) for block in self.chain)
        return{
            "num_blocks": len(self.chain),
            "total_transactions": total_tx,
            "difficulty": self.difficulty,
            "num_miners": len(self.miner_ids),
            "last_hash": self.chain[-1].hash if self.chain else None
        }