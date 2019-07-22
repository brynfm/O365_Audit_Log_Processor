import uuid
import datetime
from typing import Dict, List
from dataclasses import dataclass, field
from models.model import Model


@dataclass(eq=False)
class AlertModel(Model):
    collection: str = field(init=False, default="alert")
    CreationTime: str
    Id: str
    Operation: str
    SourceFileName: str
    RecordType: int
    UserKey: str
    UserType: int
    Version: int
    Workload: int
    ClientIP: str
    ObjectId: str
    UserId: str
    city: str
    region: str
    country: str
    location: Dict
    postal: str
    org: str
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self) -> Dict:
        return {
            '_id': self._id,
            'CreationTime': self.CreationTime,
            'Id': self.Id,
            'Operation': self.Operation,
            'SourceFileName': self.Operation,
            'RecordType': self.RecordType,
            'UserKey': self.UserKey,
            'UserType': self.UserType,
            'Version': self.Version,
            'Workload': self.Workload,
            'ClientIP': self.ClientIP,
            'ObjectId': self.ObjectId,
            'UserId': self.UserId,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'location': self.loc,
            'postal': self.postal,
            'org': self.org,
        }
