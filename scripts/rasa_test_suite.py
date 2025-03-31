from typing import List, Optional, Dict, Any

import yaml
from pydantic import BaseModel


class SlotWasSetItem(BaseModel):
    name: str
    value: Any


class Assertion(BaseModel):
    flow_started: Optional[str] = None
    slot_was_set: Optional[List[SlotWasSetItem]] = None


class Step(BaseModel):
    user: str
    assertions: List[Assertion]


class TestCase(BaseModel):
    test_case: str
    fixtures: Optional[List[str]] = None
    steps: List[Step]


class RasaTestSuite(BaseModel):
    fixtures: Optional[List[Dict[str, List[Dict[str, Any]]]]] = None
    test_cases: List[TestCase] = list()

    def serialize(self, path: str):
        print(f"serializing {path}, with {len(self.test_cases)} test cases...", end=' ')
        with open(path, 'w') as f:
            yaml.dump(self.dict(exclude_none=True), f, default_flow_style=False, sort_keys=False)
        print("DONE")
