from typing import List, Tuple, Optional
from SurvivorBot import SurvivorBot
from SparePart import SparePart, PartSize
from RechargeStation import RechargeStation
import random
from Colors import COLORS

from Drone import Drone



class TechburgGrid:
    def __init__(self, size: int):
        self.size = size
        self.stations: List[RechargeStation] = []
        self.bots: List[SurvivorBot] = []
        self.parts: List[SparePart] = []
        self.drones = []

    def initialize_simulation(self, num_stations: int, num_bots: int, num_parts: int, num_drones: int = 2):
        """
        This initializes the simulation grid by
        - placing recharge stations in the grid at random places 
        - placing survivor bots in the grid at random places
        - placing the spare parts randomly
        - placing the drones in the grid
        """

        # recharge stations
        # for _ in range(num_stations):
        #     x, y = self._get_random_empty_position()
        #     self.stations.append(RechargeStation(x, y))

        station_spacing = self.size // num_stations
        for i in range(num_stations):
            x = i * station_spacing + station_spacing // 2  # Evenly space stations
            y = self.size - 1  # Last row
            self.stations.append(RechargeStation(x, y))


        # survivor bots
        for _ in range(num_bots):
            x, y = self._get_random_empty_position()
            self.bots.append(SurvivorBot(x, y))

        # spare parts
        for _ in range(num_parts):
            x, y = self._get_random_empty_position()
            size = random.choice(list(PartSize))
            self.parts.append(SparePart(x, y, size))

        # drones
        for _ in range(num_drones):
            while True:
                x, y = self._get_random_empty_position()
                if self._is_position_empty(x, y):
                    self.drones.append(Drone(x, y))
                    break


    def _get_random_empty_position(self) -> Tuple[int, int]:
        """ returns two random values x and y between 0 and {size} representing the coordinates in grid"""
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self._is_position_empty(x, y):
                return x, y

    def _is_position_empty(self, x: int, y: int) -> bool:
        """ checks if provided coordinats have anything or not """
        for entity in self.stations + self.bots + self.parts:
            if entity.x == x and entity.y == y:
                return False
        return True

    def clear_entities(self):
        """ clear all entities from the grid """
        self.stations = []
        self.bots = []
        self.parts = []
        self.drones = []


    def simulate_step(self):
        # updates drones
        for drone in self.drones:
            drone.update(self.size, self.bots)
            

        for bot in self.bots:
            if hasattr(bot, 'dropped_part') and bot.dropped_part:
                if bot.dropped_part not in self.parts:
                    self.parts.append(bot.dropped_part)
                bot.dropped_part = None

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

    def restore_from_state(self, state):
        """ restore grid state from saved state (type: SimulationState) """

        # restore stations
        for x, y, stored_parts_data in state.stations:
            station = RechargeStation(x, y)
            # Recreate stored parts
            for part_data in stored_parts_data:
                part = SparePart(part_data.x, part_data.y, part_data.size)
                station.stored_parts.append(part)
            self.stations.append(station)

        # restore bots
        for x, y, energy, carried_part_data in state.bots:
            bot = SurvivorBot(x, y)
            bot.energy = energy
            if carried_part_data:
                # recreate carried part if it exists
                carried_part = SparePart(carried_part_data.x, carried_part_data.y, carried_part_data.size)
                bot.carried_part = carried_part
            self.bots.append(bot)

        # restore parts
        for x, y, size in state.parts:
            # convert size string to PartSize enum if needed
            if isinstance(size, str):
                size = PartSize[size.upper()]
            part = SparePart(x, y, size)
            self.parts.append(part)

        # restore drones
        for x, y, energy, is_hibernating in state.drones:
            drone = Drone(x, y)
            drone.energy = energy
            drone.is_hibernating = is_hibernating
            self.drones.append(drone)

    def display_tkinter(self, canvas):
        """Display the current state of the grid using Tkinter"""
        canvas.delete("all")  # clear previous frame
        cell_size = min(1000 // self.size, 1000 // self.size)  # calculate cell size
        
        # empty grid
        for i in range(self.size + 1):
            canvas.create_line(i * cell_size, 0, i * cell_size, self.size * cell_size)
            canvas.create_line(0, i * cell_size, self.size * cell_size, i * cell_size)

        # parts with size-based colors
        for part in self.parts:
            x = part.x * cell_size
            y = part.y * cell_size
            color = part.size.value["color"]
            canvas.create_oval(x+4, y+4, x+cell_size-4, y+cell_size-4, 
                             fill=color,
                             outline="black")
            # size indicator for the spare parts
            size_text = part.size.name[0]  # first letter of size (S/M/L) - (SMALL/MEDIUM/Large)
            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                             text=size_text, fill="black")


        # create stations in the grid
        for station in self.stations:
            x = station.x * cell_size
            y = station.y * cell_size
            canvas.create_rectangle(x+2, y+2, x+cell_size-2, y+cell_size-2, 
                                  fill=COLORS["recharge_station"])
            # Show number of stored parts
            num_parts = len(station.stored_parts)
            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                             text=str(num_parts), fill="white")

        # create bots in the grid
        for bot in self.bots:
            x = bot.x * cell_size
            y = bot.y * cell_size

            # oval shaped bots
            canvas.create_oval(x+2, y+2, x+cell_size-2, y+cell_size-2, 
                             fill=COLORS["bot"])

            # put the energy level on the bot
            energy_text = f"{int(bot.energy)}%"
            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                             text=energy_text, fill="white")
            
            # If bot is carrying a part, show indicator by putting orange colored border around the survivor bot
            if bot.carried_part:
                # thick highlighted border for bots carrying parts
                # outer border (highlight)
                border_width = 3
                canvas.create_rectangle(x, y, x+cell_size, y+cell_size, 
                                  outline="orange", width=border_width+1)

                # inner bot rectangle
                canvas.create_rectangle(x+2, y+2, x+cell_size-2, y+cell_size-2, 
                                  fill=COLORS["bot"], outline="black", width=1)
                
            else:
                # Normal bot without carried part
                canvas.create_rectangle(x+2, y+2, x+cell_size-2, y+cell_size-2, 
                                    fill=COLORS["bot"], outline="black", width=1)


            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                            text=energy_text, fill="white", font=("Arial", max(8, cell_size//4)))


        # draw drones to tkinter canvas
        for drone in self.drones:
            x = drone.x * cell_size
            y = drone.y * cell_size
            color = "purple" if drone.is_hibernating else "red"
            
            # drone
            canvas.create_rectangle(x+2, y+2, x+cell_size-2, y+cell_size-2, 
                                 fill=color, outline="black")
            
            # energy level for drone
            energy_text = f"{int(drone.energy)}%"
            canvas.create_text(x + cell_size//2, y + cell_size//2, 
                             text=energy_text, fill="white", 
                             font=('Arial', max(8, cell_size // 4)))


        canvas.update()

