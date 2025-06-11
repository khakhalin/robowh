"""Useful types to reuse across the project."""

import logging
logger = logging.getLogger(__name__)

from typing import List, Tuple, Literal, Any, TypeAlias, Optional

Product: TypeAlias = str

Coords: TypeAlias = Tuple[int, int]

RobotAction: TypeAlias = Tuple[
    Literal["go", "pick", "drop"],
    Optional[Coords],
    Optional[Product],
]