from typing import List, Optional
from Entity import Entity
from SparePart import SparePart
from SurvivorBot import SurvivorBot
from Drone import Drone
import random

class ScavengerSwarm(Entity):
    def __init__(self, x: int, y: int, size: int = 1):
        super().__init__(x, y)
        self.size = size                    # size of swarm (increases when merging)
        self.consumed_material = 0          # track consumed materials for replication
        self.replication_threshold = 100    # when this threshold reaches by adding `consumed_matrials` of both swarm then they can replicate
        self.decay_range = 1                # range of decay field effect

    def update(self, grid_size: int, parts: List[SparePart], bots: List[SurvivorBot], 
              drones: List[Drone], swarms: List['ScavengerSwarm']) -> None:
        """Update swarm behavior"""

        # roam around the grid randomly
        self._roam_randomly(grid_size)
                
        # consumes inactive bots and parts
        self._consume_resources(parts, bots)
        
        # merge with nearby swarms
        self._merge_with_nearby_swarms(swarms, grid_size)
        
        # check if can replicate
        new_swarm = self._try_replicate(grid_size)
        if new_swarm:
            swarms.append(new_swarm)

    def _roam_randomly(self, grid_size: int) -> None:
        """Move randomly in one of the four directions"""
        direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.x = (self.x + direction[0]) % grid_size
        self.y = (self.y + direction[1]) % grid_size

    def _consume_resources(self, parts: List[SparePart], bots: List[SurvivorBot]) -> None:
        """
        Consume spare parts and inactive bots
        here spare parts and inactive bots are given a value which gets added when swarm consumes them
        - Small spare parts  : 1
        - Medium spare parts : 2
        - Large spare parts  : 3
        - inactive bots      : 5

        NOTE: all of these values are assumed(not provided in the details of assessment)
        """
        # consume spare parts
        for part in parts[:]:  # Create copy of list to modify during iteration
            if self.x == part.x and self.y == part.y:
                if part.size.name == 'SMALL':
                    self.consumed_material += 1
                elif part.size.name == 'MEDIUM':
                    self.consumed_material += 2
                else:  # LARGE
                    self.consumed_material += 3
                parts.remove(part)
        
        # Consume inactive bots
        for bot in bots[:]:
            if bot.energy <= 0 and self.x == bot.x and self.y == bot.y:
                self.consumed_material += 5
                bots.remove(bot)

    def _merge_with_nearby_swarms(self, swarms: List['ScavengerSwarm'], grid_size: int) -> None:
        """merge with nearby swarms"""
        for swarm in swarms[:]:
            if swarm != self and self._is_adjacent(swarm.x, swarm.y, grid_size):
                self.size += swarm.size
                self.consumed_material += swarm.consumed_material
                swarms.remove(swarm)

    def _try_replicate(self, grid_size: int) -> Optional['ScavengerSwarm']:
        """try to replicate if enough material gathered"""
        if self.consumed_material >= self.replication_threshold:
            # Create new swarm in adjacent cell
            new_x = (self.x + random.choice([-1, 0, 1])) % grid_size
            new_y = (self.y + random.choice([-1, 0, 1])) % grid_size
            self.consumed_material -= self.replication_threshold
            return ScavengerSwarm(new_x, new_y)
        return None

    def _is_in_decay_range(self, target_x: int, target_y: int, grid_size: int) -> bool:
        """checks if target is within decay field range"""
        dx = min(abs(self.x - target_x), grid_size - abs(self.x - target_x))
        dy = min(abs(self.y - target_y), grid_size - abs(self.y - target_y))
        return max(dx, dy) <= self.decay_range

    def _is_adjacent(self, target_x: int, target_y: int, grid_size: int) -> bool:
        """checks if target is in adjacent cell"""
        dx = min(abs(self.x - target_x), grid_size - abs(self.x - target_x))
        dy = min(abs(self.y - target_y), grid_size - abs(self.y - target_y))
        return max(dx, dy) == 1