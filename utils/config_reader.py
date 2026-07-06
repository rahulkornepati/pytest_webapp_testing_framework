from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
TEST_DATA_DIR = ROOT_DIR / "test_data"


def read_json(file_name: str) -> dict[str, Any]:
    file_path = TEST_DATA_DIR / file_name
    with file_path.open(encoding="utf-8") as data_file:
        return json.load(data_file)
