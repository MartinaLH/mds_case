from typing import List


class Trial:
    utn: str
    phase: List
    status: str
    conditions: List

    def __init__(self, utn: str, phase: str, status: str, conditions: List):
        self.utn = utn
        self.phase = phase
        self.status = status
        self.conditions = conditions
