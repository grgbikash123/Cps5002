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
        self.movement_energy_cost = 5.0


    def reduce_energy(self, amount: float) -> None:
        """Safely reduce bot's energy ensuring it doesn't go below 0"""
        self.energy = max(0, self.energy - amount)

    def has_enough_energy_for_move(self) -> bool:
        """Check if bot has enough energy for movement"""
        return self.energy >= self.movement_energy_cost

    def move(self, new_x: int, new_y: int, grid_size: int):
        """ implements wrapping around edges """
        if self.has_enough_energy_for_move():
            self.x = new_x % grid_size
            self.y = new_y % grid_size
            # self.energy -= 5.0  # 5% energy loss per movement
            self.reduce_energy(self.movement_energy_cost)

    def pickup_part(self, part: SparePart) -> bool:
        """ picks up part from grid when bot is not carrying any part """
        if self.carried_part is None:
            self.carried_part = part
            return True
        return False

    def deposit_part(self, station: RechargeStation):
        """ deposits the gathered part from grid to recharge station """
        if self.carried_part:
            station.store_part(self.carried_part)
            self.carried_part = None

    def drop_part(self) -> None:
        """ drops the currently carried part """
        if self.carried_part:
            # update part position to bot's current position
            self.carried_part.x = self.x
            self.carried_part.y = self.y
            dropped_part = self.carried_part
            self.carried_part = None
            self.target_part = dropped_part
            return dropped_part
        return None


