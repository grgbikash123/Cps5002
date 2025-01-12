from Entity import Entity
from SparePart import SparePart
from typing import List, Optional


class RechargeStation(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.stored_parts: List[SparePart] = []
        self.current_bots: List[SurvivorBot] = []
        self.max_bots = 5
        self.max_parts = 5

    def can_store_part(self) -> bool:
        """Check if station can store more parts"""
        return len(self.stored_parts) < self.max_parts

    def store_part(self, part: SparePart) -> bool:
        """Store a part if there's space"""
        if self.can_store_part():
            self.stored_parts.append(part)
            return True
        return False

    # def can_accept_bot(self) -> bool:
    #     return len(self.current_bots) < self.max_bots


    def get_smallest_part(self) -> Optional[SparePart]:
        """Get the smallest available part for consumption"""
        if not self.stored_parts:
            return None
        return min(self.stored_parts, key=lambda p: p.size.value["boost"])
