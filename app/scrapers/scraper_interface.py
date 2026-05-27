from abc import ABC, abstractmethod
from typing import Optional
from app.models.product_model import StorePrice


class ScraperInterface(ABC):
    @abstractmethod
    def scrape(self, url: str) -> Optional[StorePrice]:
        pass
