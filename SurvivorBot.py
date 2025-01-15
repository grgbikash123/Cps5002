from typing import Optional
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
        self.critical_energy_threshold = 5.0

        self.energy_enhancement = 0.0
        self.base_max_energy = 100.0
        self.max_energy = self.base_max_energy

        self.resting = False
        self.rest_energy_threshold = 60.0 # Start resting if energy below 50%
        self.regen_rate = 1.0            # 1% regeneration per step
        self.rest_energy_target = 0.0

    def needs_rest(self) -> bool:
        """Check if bot needs to rest (energy < 50%)"""
        return self.energy < self.rest_energy_threshold

    def has_enough_energy_for_move(self) -> bool:
        """Check if bot has enough energy for movement"""
        return self.energy >= self.movement_energy_cost

    def is_critical_energy(self) -> bool:
        """Check if bot is in critical energy state"""
        return self.energy <= self.critical_energy_threshold

    def start_resting(self) -> None:
        """Start resting and set target energy level"""
        self.resting = True
        self.rest_energy_target = self.rest_energy_threshold

    def rest_at_station(self) -> bool:
        """
        Regenerate energy while resting at station
        Returns True if target energy is reached
        """
        if self.energy < self.rest_energy_target:
            self.energy = min(self.rest_energy_threshold, self.energy + self.regen_rate)
            return False
        self.resting = False
        return True

    def reduce_energy(self, amount: float) -> None:
        """Safely reduce bot's energy ensuring it doesn't go below 0"""
        self.energy = max(0.0, self.energy - amount)


    def recharge(self, amount: float) -> None:
        """Safely recharge bot's energy"""
        self.energy = min(self.max_energy, self.energy + amount)

    def store_part_at_station(self, station: RechargeStation) -> bool:
        """Attempt to store carried part at station"""
        if self.carried_part and station.can_store_part():
            station.store_part(self.carried_part)
            self.carried_part = None
            return True
        return False

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


