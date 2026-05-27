from typing import Optional, List
from app.models.product_model import Product, ProductCreate
from app.repositories.product_repository import ProductRepository
from app.repositories.store_price_repository import StorePriceRepository


class ProductService:

    @staticmethod
    async def create_product(data: dict) -> dict:
        return await ProductRepository.create(data)

    @staticmethod
    async def get_product(product_id: str) -> Optional[Product]:
        return await ProductRepository.get_by_id(product_id)

    @staticmethod
    async def search_products(query: str) -> List[Product]:
        return await ProductRepository.search_by_title(query)

    @staticmethod
    async def delete_product(product_id: str) -> bool:
        return await ProductRepository.delete(product_id)

    @staticmethod
    async def get_product_with_prices(product_id: str):
        product = await ProductRepository.get_by_id(product_id)
        if not product:
            return None
        prices = await StorePriceRepository.get_prices_for_product(product_id)
        return {"product": product, "prices": prices}
