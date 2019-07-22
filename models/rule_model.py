import uuid
from typing import Dict, List
from dataclasses import dataclass, field
from models.model import Model


@dataclass(eq=False)
class RuleModel(Model):
    collection: str = field(init=False, default="rule")
    rule: str
    type: str
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self) -> Dict:
        return {
            '_id': self._id,
            'rule': self.rule,
            'type': self.type
        }
