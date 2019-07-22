from typing import Dict, List, TypeVar, Type, Union
from abc import ABCMeta, abstractmethod
from common.database import Database
from datetime import datetime
import math
import mpu

T = TypeVar('T', bound='Model')


class Model(metaclass=ABCMeta):

    collection: str
    _id: str

    def __init__(self, *args, **kwargs):
        from pprint import pprint
        pprint(self)
        pass

    def insert_to_db(self, data):
        Database.insert(self.collection, data)

    def replace_or_create_to_db(self, query, data):
        Database.replace(self.collection, query, data)

    def save_to_db(self):
        Database.update(self.collection, {"_id": self._id}, self.json())

    def remove_from_db(self):
        Database.remove(self.collection, {"_id": self._id})

    @classmethod
    def get_by_id(cls: Type[T], _id: str) -> T:
        return cls.find_one_by("_id", _id)

    @abstractmethod
    def json(self) -> Dict:
        raise NotImplementedError()

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        elements_from_db = Database.find(cls.collection, {})
        return [cls(**elem) for elem in elements_from_db]

    @classmethod
    def find_one_by(cls: Type[T], attribute: str, value: Union[str, Dict]) -> T:
        return cls(**Database.find_one(cls.collection, {attribute: value}))

    @classmethod
    def find_many_by(cls: Type[T], attribute: str, value: Union[str, Dict]) -> List[T]:
        return [cls(**elem) for elem in Database.find(cls.collection, {attribute: value})]

    @classmethod
    def find_many_by_filter(cls: Type[T], filter_query, query_values) -> List[T]:
        query_function = {}
        is_distance = False
        for idx, filter in enumerate(filter_query):
            query_string = ""
            distance = ''
            if filter == "creation_date":
                earliest = datetime.fromisoformat(query_values[idx][0])
                latest = datetime.fromisoformat(query_values[idx][1])
                query = {"$gte": earliest, "$lte": latest}
                query_function[filter] = query
            elif filter == 'distance':
                distance = query_values[idx]
                is_distance = True
            else:
                filter_temp = filter
                temp = query_values[idx]
                query_function[filter_temp] = temp

        if is_distance == True:
            result = []
            elements = [cls(**elem) for elem in Database.find(cls.collection, query_function)]
            for element in elements:
                latt, long = element.loc
                distance_ = mpu.haversine_distance((long,latt), (-4.14127,50.3755))
                if distance_ > float(distance):
                    result.append(element)
        else:
            result = [cls(**elem)for elem in Database.find(cls.collection, query_function)]

        return result

    @classmethod
    def find_oddities(cls: Type[T]) ->List[T]:
        elements_from_db = Database.find(cls.collection, {})
        elements = [cls(**elem) for elem in elements_from_db]
        result = []
        for element in elements:
            if not element.ResultStatus == 'Succeeded':
              if not element.org == 'AS786 Jisc Services Limited':
                    long, latt = element.loc
                    distance = (long - 50.3755) /(latt - 4.1427)
                    distance = math.sqrt(distance*distance)
                    if distance > 0.1:
                        result.append(element)
        return result