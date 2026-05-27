from fastapi import APIRouter, HTTPException
from app.services.search_service import SearchService
from app.utils.validators import validate_query

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/{query}")
async def search(query: str):
    """
    Live search across all stores (Amazon, Argos, Currys, eBay).
    GET /search/iphone
    Returns a flat list of results with store, title, price, url.
    """
    try:
        validated = validate_query(query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results = await SearchService.search_all_stores(validated)
    if not results:
        raise HTTPException(status_code=404, detail="No results found")
    return results


@router.get("/")
async def search_with_param(q: str):
    """
    Alternative: GET /search?q=iphone
    """
    try:
        validated = validate_query(q)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results = await SearchService.search_all_stores(validated)
    return results
