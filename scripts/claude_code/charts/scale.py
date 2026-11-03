from __future__ import annotations

from math import ceil, floor, log10

NICE_STEPS = (1, 2, 2.5, 5, 10)


def nice_ticks(peak: float, intervals: int = 4) -> list[int]:
    if peak <= 0:
        return [0, 1]
    magnitude = max(10 ** floor(log10(peak / intervals)), 1)
    candidates = [multiple * magnitude for multiple in NICE_STEPS] + [multiple * magnitude * 10 for multiple in NICE_STEPS]
    step = next(candidate for candidate in candidates if ceil(peak / candidate) <= intervals)
    return [round(step * index) for index in range(ceil(peak / step) + 1)]


class LinearScale:
    def __init__(self, domain_max: float, range_start: float, range_end: float) -> None:
        self._domain_max = domain_max or 1
        self._range_start = range_start
        self._range_end = range_end

    def __call__(self, value: float) -> float:
        return self._range_start + (self._range_end - self._range_start) * value / self._domain_max
