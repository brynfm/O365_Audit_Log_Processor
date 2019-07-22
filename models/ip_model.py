import uuid
from typing import Dict, List
from dataclasses import dataclass, field
from models.model import Model
from datetime import date

@dataclass(eq=False)
class IpModel(Model):
    collection: str = field(init=False, default="ip")
    ip: str
    city: str
    region: str
    country: str
    latitude: float
    longitude: float
    loc: Dict
    postal: str
    org: str
    expiry_date: date
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self) -> Dict:
        return {
            '_id': self._id,
            'ip': self.ip,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'loc': self.loc,
            'postal': self.postal,
            'org': self.org,
            'expiry_date': self.expiry_date
        }
