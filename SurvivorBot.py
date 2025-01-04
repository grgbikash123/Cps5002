from Entity import Entity
from SparePart import SparePart
from RechargeStation import RechargeStation


class SurvivorBot(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.energy = 100.0
        self.carried_part: Optional[SparePart] = None
        self.target_part = None
        self.target_station = None

        
    def move(self, new_x: int, new_y: int, grid_size: int):
        # Implement wrapping around edges
        self.x = new_x % grid_size
        self.y = new_y % grid_size
        self.energy -= 5.0  # 5% energy loss per movement

    def pickup_part(self, part: SparePart) -> bool:
        if self.carried_part is None:
            self.carried_part = part
            return True
        return False

    def deposit_part(self, station: RechargeStation):
        if self.carried_part:
            station.store_part(self.carried_part)
            self.carried_part = None

    def drop_part(self) -> None:
        """Drop the currently carried part"""
        if self.carried_part:
            # Update part position to bot's current position
            self.carried_part.x = self.x
            self.carried_part.y = self.y
            dropped_part = self.carried_part
            self.carried_part = None
            self.target_part = dropped_part  # Remember the dropped part location
            return dropped_part
        return None


