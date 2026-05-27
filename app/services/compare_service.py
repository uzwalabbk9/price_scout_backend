from typing import Optional
from app.utils.best_deal_finder import find_best_deal
from app.services.search_service import SearchService, REGIONS
from app.repositories.product_repository import ProductRepository


class CompareService:

    @staticmethod
    async def compare_product(query: str, region: str = "all") -> dict:
        """
        Search all stores for a query and region.
        Returns not_found=True when no product matches.
        """
        results = await SearchService.search_all_stores(query, region)

        if not results:
            return {
                "query": query,
                "region": region,
                "not_found": True,
                "best_deal": None,
                "all_results": [],
                "message": f'No products found for "{query}" in {REGIONS.get(region, {}).get("name", region)}. Try a different search term.',
            }

        best = find_best_deal(results)
        in_stock  = [r for r in results if r.get("in_stock", True)]
        out_stock = [r for r in results if not r.get("in_stock", True)]

        return {
            "query": query,
            "region": region,
            "not_found": False,
            "best_deal": best,
            "all_results": results,
            "in_stock_count": len(in_stock),
            "out_of_stock_count": len(out_stock),
        }

    @staticmethod
    async def compare_product_prices(product_id: str) -> Optional[dict]:
        product = await ProductRepository.get_by_id(product_id)
        if not product:
            return None
        store_prices = [sp.model_dump() for sp in product.store_prices]
        best_deal = find_best_deal(store_prices)
        return {
            "product_id": product.id,
            "title": product.title,
            "description": product.description,
            "image": product.image,
            "prices": store_prices,
            "best_deal": best_deal,
        }
