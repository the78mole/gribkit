"""@relation(SWA-GRIB-BBOX, scope=file)"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BBox:
    """Geographic region in degrees. ``west``/``east`` may be negative;
    ``west > east`` is not allowed (for regions across the antimeridian, give
    ``east`` greater than 180).

    @relation(SWR-GRIB-006, scope=class)
    """

    north: float
    south: float
    west: float
    east: float

    def __post_init__(self) -> None:
        if not -90 <= self.south < self.north <= 90:
            raise ValueError(f"Invalid latitudes: south={self.south}, north={self.north}")
        if not self.west < self.east or self.east - self.west > 360:
            raise ValueError(f"Invalid longitudes: west={self.west}, east={self.east}")

    @property
    def width(self) -> float:
        return self.east - self.west
