from fastapi import APIRouter

from .routes import users
from .routes import hook

router = APIRouter()

# router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(hook.router)