from fastapi import APIRouter, HTTPException
from app.repositories.wishlist_repository import WishlistRepository
from app.models.wishlist_model import WishlistItem, WishlistItemUpdate

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.post("/", status_code=201)
async def add_to_wishlist(item: WishlistItem):
    """Add a product to a user's wishlist."""
    created = await WishlistRepository.add_item(item)
    return created


@router.get("/{user_id}")
async def get_wishlist(user_id: str):
    """Get all wishlist items for a user."""
    items = await WishlistRepository.get_by_user(user_id)
    return items


@router.put("/{user_id}/{product_id}")
async def update_wishlist_item(user_id: str, product_id: str, update: WishlistItemUpdate):
    """Update fields of a wishlist item (e.g. refreshed price, notes)."""
    updated = await WishlistRepository.update_item(user_id, product_id, update.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    return updated


@router.delete("/{user_id}/{product_id}")
async def remove_from_wishlist(user_id: str, product_id: str):
    """Remove a product from a user's wishlist."""
    deleted = await WishlistRepository.delete(user_id, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True}


@router.delete("/{user_id}")
async def clear_wishlist(user_id: str):
    """Remove ALL items from a user's wishlist."""
    count = await WishlistRepository.clear_all(user_id)
    return {"deleted_count": count}
