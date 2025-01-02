from Entity import Entity
from enum import Enum
from Colors import COLORS


class PartSize(Enum):
    SMALL = {"boost": 0.03, "energy": 0.01, "color": COLORS["spare_part_small"]}
    MEDIUM = {"boost": 0.05, "energy": 0.02, "color": COLORS["spare_part_medium"]}
    LARGE = {"boost": 0.07, "energy": 0.03, "color": COLORS["spare_part_large"]}


class SparePart(Entity):
    def __init__(self, x: int, y: int, size: PartSize):
        super().__init__(x, y)
        self.size = size
        self.enhancement_value = size.value["boost"]
        
    def corrode(self):
        self.enhancement_value = max(0, self.enhancement_value - 0.001)  # 0.1% corrosion
