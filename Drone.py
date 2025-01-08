from typing import List, Optional
from Entity import Entity
from SurvivorBot import SurvivorBot
import random

class Drone(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.energy = 100.0
        self.detection_range = 3
        self.is_hibernating = False
        self.pursuing_bot: Optional[SurvivorBot] = None
        self.recharge_rate = 10.0                            # recharge 10% per simulation step
        self.hibernation_threshold = 20.0                   # minimum energy to enter hibernation state (20% energy)

    def can_detect_bot(self, bot: SurvivorBot, grid_size: int) -> bool:
        """Check if a bot is within detection range (3 cells)"""
        dx = min(abs(self.x - bot.x), grid_size - abs(self.x - bot.x))
        dy = min(abs(self.y - bot.y), grid_size - abs(self.y - bot.y))
        return max(dx, dy) <= self.detection_range

    def attack_bot(self, bot: SurvivorBot) -> None:
        """Attack a survivor bot with different possible outcomes"""        
        # choosing randomly which type of attack to be done
        attack_type = random.random()
        
        if attack_type < 0.6:  # 60% chance of shock attack
            bot.energy -= 5.0
            bot.drop_part()
        else:  # 40% chance of disable attack
            bot.energy -= 20.0
            bot.drop_part()

        # small energy cost for attacking
        self.energy = max(0, self.energy - 2.0)


    def update(self, grid_size: int, bots: List[SurvivorBot]) -> None:
        """Update drone's state and behavior"""
        if self.energy <= self.hibernation_threshold and not self.is_hibernating:
            self.is_hibernating = True
            self.pursuing_bot = None  # stop pursuit when in hibernation step
            return

        if self.energy >= 100.0:
            self.is_hibernating = False

        if self.is_hibernating:
            self.energy = min(100.0, self.energy + self.recharge_rate)
            if self.energy >= 100.0:  # exit hibernation only when fully charged
                self.is_hibernating = False
            return  # Do nothing else while hibernating

        # Normal behavior when not hibernating
        ### roam around the grid and look for nearby bots
        nearby_bots = [bot for bot in bots if self.can_detect_bot(bot, grid_size)]
        
        ## if there is survivor bot in nearby cells
        if nearby_bots:
            # start pursuing the closest bot if not already pursuing
            if not self.pursuing_bot:
                self.pursuing_bot = min(nearby_bots, 
                    key=lambda b: self._calculate_distance(b.x, b.y, grid_size))

            if self.pursuing_bot:
                if self.x == self.pursuing_bot.x and self.y == self.pursuing_bot.y:
                    # attack when caught (when bot and drone are in same cell)
                    self.attack_bot(self.pursuing_bot)
                    self.pursuing_bot = None
                else:
                    # move towards pursued bot
                    self._move_towards_target(self.pursuing_bot.x, self.pursuing_bot.y, grid_size)
                    # reduce the eneryg of drone for a pursuit (20% per step while pursuing)
                    self.energy = max(0, self.energy - 20.0)

                    # don't pursuit if energy gets too low
                    if self.energy <= self.hibernation_threshold:
                        self.pursuing_bot = None
                        self.is_hibernating = True

        else:
            # if there is not any bots nearby, roam randomly
            self.pursuing_bot = None
            self._roam_randomly(grid_size)
            
        # check if energy dropped below threshold after actions
        if self.energy <= self.hibernation_threshold:
            self.is_hibernating = True
            self.pursuing_bot = None


    def _recharge(self) -> None:
        """Recharge drone's energy while in hibernation mode"""
        self.energy = min(100.0, self.energy + self.recharge_rate)
        
        # exit hibernation when fully charged
        if self.energy >= 100.0:
            self.is_hibernating = False
            self.energy = 100.0


    def _roam_randomly(self, grid_size: int) -> None:
        """Move randomly in one of the four directions"""
        direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.x = (self.x + direction[0]) % grid_size
        self.y = (self.y + direction[1]) % grid_size
        
        # small  energy cost for movement
        self.energy = max(0, self.energy - 1.0)



    def _calculate_distance(self, target_x: int, target_y: int, grid_size: int) -> float:
        """Calculate distance considering grid wrapping"""
        dx = min(abs(target_x - self.x), grid_size - abs(target_x - self.x))
        dy = min(abs(target_y - self.y), grid_size - abs(target_y - self.y))
        return (dx ** 2 + dy ** 2) ** 0.5

    def _move_towards_target(self, target_x: int, target_y: int, grid_size: int) -> None:
        """Move towards a target position considering grid wrapping"""
        dx = (target_x - self.x + grid_size // 2) % grid_size - grid_size // 2
        dy = (target_y - self.y + grid_size // 2) % grid_size - grid_size // 2
        
        if abs(dx) > abs(dy):
            self.x = (self.x + (1 if dx > 0 else -1)) % grid_size
        else:
            self.y = (self.y + (1 if dy > 0 else -1)) % grid_size