from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from entities.types import *


@dataclass
class Teacher:
    handle: Handle
    name: Name
    lunches: Dict[Semester, SemesterLunches] = field(default_factory=dict)

    def lunch_number(self, semester: Semester, block: Block) -> Optional[LunchNumber]:
        return self.lunches.get(semester, {}).get(block)
