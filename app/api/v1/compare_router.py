from fastapi import APIRouter, HTTPException, Query
from app.services.compare_service import CompareService

router = APIRouter(prefix="/compare", tags=["Compare"])


@router.get("/search/{query}")
async def compare_product(
    query: str,
    region: str = Query(default="all", description="Region: uk | us | in | all"),
):
    """
    Search all stores for query in the given region.
    GET /compare/search/iphone?region=uk
    GET /compare/search/samsung?region=us
    GET /compare/search/airpods?region=in
    GET /compare/search/macbook        (defaults to all regions)
    """
    result = await CompareService.compare_product(query, region.lower())
    return result


@router.get("/product/{product_id}")
async def compare_prices(product_id: str):
    result = await CompareService.compare_product_prices(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result
