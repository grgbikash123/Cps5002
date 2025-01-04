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

    def can_detect_bot(self, bot: SurvivorBot, grid_size: int) -> bool:
        """Check if a bot is within detection range (3 cells)"""
        dx = min(abs(self.x - bot.x), grid_size - abs(self.x - bot.x))
        dy = min(abs(self.y - bot.y), grid_size - abs(self.y - bot.y))
        return max(dx, dy) <= self.detection_range

    def attack_bot(self, bot: SurvivorBot) -> None:
        """Attack a survivor bot with different possible outcomes"""
        import random
        
        # choosing randomly which type of attack to be done
        attack_type = random.random()
        
        if attack_type < 0.6:  # 60% chance of shock attack
            bot.energy -= 5.0
            bot.drop_part()
        else:  # 40% chance of disable attack
            bot.energy -= 20.0
            bot.drop_part()

    def update(self, grid_size: int, bots: List[SurvivorBot]) -> None:
        """Update drone's state and behavior"""
        if self.energy <= 20.0:
            self.is_hibernating = True
            self.energy = min(100.0, self.energy + 10.0)  # Recharge in hibernation
            return

        if self.energy >= 100.0:
            self.is_hibernating = False

        if self.is_hibernating:
            return

        # Look for nearby bots
        nearby_bots = [bot for bot in bots if self.can_detect_bot(bot, grid_size)]
        
        if nearby_bots and not self.pursuing_bot:
            # Start pursuing the closest bot if not already pursuing
            if not self.pursuing_bot:
                self.pursuing_bot = min(nearby_bots, 
                    key=lambda b: self._calculate_distance(b.x, b.y, grid_size))
                self.energy -= 20.0  # Energy cost for pursuit

            if self.pursuing_bot:
                if self._calculate_distance(self.pursuing_bot.x, self.pursuing_bot.y, grid_size) <= 1:
                    # Attack if adjacent
                    self.attack_bot(self.pursuing_bot)
                    self.pursuing_bot = None
                else:
                    # Move towards pursued bot
                    self._move_towards_target(self.pursuing_bot.x, self.pursuing_bot.y, grid_size)
        else:
            # No bots nearby, roam randomly
            self.pursuing_bot = None
            self._roam_randomly(grid_size)

    def _roam_randomly(self, grid_size: int) -> None:
        """Move randomly in one of the four directions"""
        direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.x = (self.x + direction[0]) % grid_size
        self.y = (self.y + direction[1]) % grid_size
        # Small energy cost for movement
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