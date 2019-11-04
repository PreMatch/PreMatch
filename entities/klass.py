from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from entities.types import *


@dataclass
class Class:
    teacher: Name
    block: Block
    semester: Semester

    lunch: Optional[LunchNumber] = None
    location: Optional[Location] = None
