from fastapi import APIRouter, HTTPException
from app.services.product_service import ProductService
from app.models.product_model import ProductCreate

router = APIRouter(prefix="/products", tags=["Products"])


# ✅ /search/{query} MUST be declared BEFORE /{product_id}
# Otherwise FastAPI matches "search" as a product_id and hits a DB error.
@router.get("/search/{query}")
async def search_products(query: str):
    """
    Search products stored in MongoDB by title (case-insensitive).
    GET /products/search/iphone
    """
    results = await ProductService.search_products(query)
    return [r.model_dump() for r in results]


@router.post("/", status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product in the database."""
    created = await ProductService.create_product(product.model_dump())
    return created


@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get a single product by its MongoDB ObjectId."""
    product = await ProductService.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.model_dump()


@router.get("/{product_id}/prices")
async def get_product_with_prices(product_id: str):
    """Get a product with all its stored store prices."""
    result = await ProductService.get_product_with_prices(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """Delete a product by its MongoDB ObjectId."""
    deleted = await ProductService.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"deleted": True}
