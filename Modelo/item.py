from dataclasses import dataclass

@dataclass
class Item:
    id: str
    title: str
    price: str
    description: str
    brand_title: str
    photo: str
    url: str
    raw_timestamp: float