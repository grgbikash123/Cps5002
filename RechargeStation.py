from Entity import Entity
from SparePart import SparePart


class RechargeStation(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.stored_parts: List[SparePart] = []
        self.current_bots: List['SurvivorBot'] = []
        self.max_bots = 5

    def store_part(self, part: SparePart):
        self.stored_parts.append(part)

    def can_accept_bot(self) -> bool:
        return len(self.current_bots) < self.max_bots
