"""The one number worth trending for each task in this service."""
from typing import Callable, Dict, Optional, Tuple


def _number(value) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _ejection_fraction(result: dict) -> Optional[float]:
    return _number(result.get("ejection_fraction"))


# task name -> (label shown on the chart, unit, function that reads the value from a saved result)
METRICS: Dict[str, Tuple[str, str, Callable[[dict], Optional[float]]]] = {
    "ef-estimation": ("Ejection fraction", "%", _ejection_fraction),
}
