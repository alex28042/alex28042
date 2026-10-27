from __future__ import annotations

import re

MODEL_ID = re.compile(r"^claude-(?P<family>[a-z]+)-(?P<version>\d+(?:-\d{1,2})*)(?:-\d{8})?(?:\[.*\])?$")


def model_display_name(model_id: str) -> str:
    match = MODEL_ID.match(model_id)
    if not match:
        return model_id
    family = match.group("family").capitalize()
    version = match.group("version").replace("-", ".")
    return f"{family} {version}"
