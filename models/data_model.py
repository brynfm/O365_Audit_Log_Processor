import uuid
import datetime
from typing import Dict, List
from dataclasses import dataclass, field
from models.model import Model


@dataclass(eq=False)
class DataModel(Model):
    collection: str = field(init=False, default="file")
    record_type: str
    creation_date: datetime
    CreationTime: str
    Id: str
    Operation: str
    OrganizationId: str
    RecordType: int
    ResultStatus: str
    UserKey: str
    UserType: int
    Version: int
    Workload: int
    ClientIP: str
    ObjectId: str
    UserId: str
    raw_data: str
    city: str
    region: str
    country: str
    latitude: float
    longitude: float
    location: Dict
    postal: str
    org: str
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self) -> Dict:
        return {
            '_id': self._id,
            'record_type': self.record_type,
            'creation_date': self.creation_date,
            'CreationTime': self.CreationTime,
            'Id': self.Id,
            'Operation': self.Operation,
            'OrganizationId': self.OrganizationId,
            'RecordType': self.RecordType,
            'ResultStatus': self.ResultStatus,
            'UserKey': self.UserKey,
            'UserType': self.UserType,
            'Version': self.Version,
            'Workload': self.Workload,
            'ClientIP': self.ClientIP,
            'ObjectId': self.ObjectId,
            'UserId': self.UserId,
            'raw_data': self.raw_data,
            'city': self.city,
            'region': self.region,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'country': self.country,
            'location': self.loc,
            'postal': self.postal,
            'org': self.org,
        }
