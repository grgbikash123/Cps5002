from typing import List, Tuple, Optional
from SurvivorBot import SurvivorBot
from SparePart import SparePart, PartSize
from RechargeStation import RechargeStation
import random
from Colors import COLORS



class TechburgGrid:
    def __init__(self, size: int):
        self.size = size
        self.stations: List[RechargeStation] = []
        self.bots: List[SurvivorBot] = []
        self.parts: List[SparePart] = []

    def initialize_simulation(self, num_stations: int, num_bots: int, num_parts: int):
        # Place recharge stations
        for _ in range(num_stations):
            x, y = self._get_random_empty_position()
            self.stations.append(RechargeStation(x, y))

        # Place survivor bots
        for _ in range(num_bots):
            x, y = self._get_random_empty_position()
            self.bots.append(SurvivorBot(x, y))

        # Place spare parts
        for _ in range(num_parts):
            x, y = self._get_random_empty_position()
            size = random.choice(list(PartSize))
            self.parts.append(SparePart(x, y, size))

    def _get_random_empty_position(self) -> Tuple[int, int]:
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self._is_position_empty(x, y):
                return x, y

    def _is_position_empty(self, x: int, y: int) -> bool:
        for entity in self.stations + self.bots + self.parts:
            if entity.x == x and entity.y == y:
                return False
        return True

    def clear_entities(self):
        """Clear all entities from the grid"""
        self.stations = []
        self.bots = []
        self.parts = []


    def simulate_step(self):
        for bot in self.bots:
            if bot.energy <= 0:
                continue

            # Find nearest part if not carrying one
            if not bot.carried_part:
                nearest_part = self._find_nearest_part(bot)
                if nearest_part:
                    self._move_towards(bot, nearest_part.x, nearest_part.y)
                    if bot.x == nearest_part.x and bot.y == nearest_part.y:
                        bot.pickup_part(nearest_part)
                        self.parts.remove(nearest_part)

            # If carrying a part, find nearest station
            else:
                nearest_station = self._find_nearest_station(bot)
                if nearest_station:
                    self._move_towards(bot, nearest_station.x, nearest_station.y)
                    if bot.x == nearest_station.x and bot.y == nearest_station.y:
                        bot.deposit_part(nearest_station)

            # Corrode parts
            for part in self.parts:
                part.corrode()

    def _find_nearest_part(self, bot: SurvivorBot) -> Optional[SparePart]:
        return min(self.parts, key=lambda p: self._calculate_distance(bot.x, bot.y, p.x, p.y), default=None)

    def _find_nearest_station(self, bot: SurvivorBot) -> Optional[RechargeStation]:
        return min(self.stations, key=lambda s: self._calculate_distance(bot.x, bot.y, s.x, s.y), default=None)

    def _calculate_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        dx = min(abs(x2 - x1), self.size - abs(x2 - x1))
        dy = min(abs(y2 - y1), self.size - abs(y2 - y1))
        return (dx ** 2 + dy ** 2) ** 0.5

    def _move_towards(self, bot: SurvivorBot, target_x: int, target_y: int):
        dx = (target_x - bot.x + self.size // 2) % self.size - self.size // 2
        dy = (target_y - bot.y + self.size // 2) % self.size - self.size // 2
        
        if abs(dx) > abs(dy):
            new_x = bot.x + (1 if dx > 0 else -1)
            bot.move(new_x, bot.y, self.size)
        else:
            new_y = bot.y + (1 if dy > 0 else -1)
            bot.move(bot.x, new_y, self.size)

    def display_tkinter(self, canvas):
        """Display the current state of the grid using Tkinter"""
        canvas.delete("all")  # Clear previous frame
        cell_size = min(900 // self.size, 900 // self.size)  # Dynamically calculate cell size

        # Calculate font size based on cell size
        font_size = max(4, cell_size // 4)  # Minimum font size of 6
        small_font = ('Arial', font_size)
        
        # Draw empty grid
        for i in range(self.size):
            for j in range(self.size):
                x1, y1 = i * cell_size, j * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                canvas.create_rectangle(x1, y1, x2, y2, 
                                     fill=COLORS["empty"],
                                     outline="gray")

        # Draw parts with size-based colors
        for part in self.parts:
            x = part.x * cell_size
            y = part.y * cell_size
            color = part.size.value["color"]
            canvas.create_oval(x+4, y+4, x+cell_size-4, y+cell_size-4, 
                             fill=color,
                             outline="black")
            # Add size indicator
            size_text = part.size.name[0]  # First letter of size (S/M/L)
            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                             text=size_text, fill="black")


        # Draw stations
        for station in self.stations:
            x = station.x * cell_size
            y = station.y * cell_size
            canvas.create_rectangle(x+2, y+2, x+cell_size-2, y+cell_size-2, 
                                  fill=COLORS["recharge_station"])
            # Show number of stored parts
            num_parts = len(station.stored_parts)
            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                             text=str(num_parts), fill="white")

        # Draw bots
        for bot in self.bots:
            x = bot.x * cell_size
            y = bot.y * cell_size
            # Draw bot
            canvas.create_oval(x+2, y+2, x+cell_size-2, y+cell_size-2, 
                             fill=COLORS["bot"])
            
            # Show energy level
            energy_text = f"{int(bot.energy)}%"
            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                             text=energy_text, fill="white")
            
            # If bot is carrying a part, show indicator
            if bot.carried_part:
                canvas.create_oval(x+8, y+8, x+cell_size-8, y+cell_size-8, 
                                 fill=bot.carried_part.size.value["color"])

        # Update the canvas
        canvas.update()

