from typing import Any
from fastapi import HTTPException, Request
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from ..services.supabase_auth import SupabaseAuth
from config.config import Config

CONFIG = Config()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/")
def status() -> dict[str, str]:
    return {"message": "Route is working."}


@router.get("/providers")
def get_providers() -> dict[str, Any]:
    return {"providers": CONFIG.get_config("auth", "providers", "supabase", "providers")}


@router.get("/oauth/{provider}/sign-in")
async def oauth_sign_in(
    provider: str,
    request: Request,
    redirect_to: str | None = None,
    scopes: str | None = None,
    app_redirect: str | None = None,
) -> RedirectResponse:
    if app_redirect:
        request.session["app_redirect"] = app_redirect
    auth = SupabaseAuth.from_request(request)
    res = auth.start_oauth(provider, redirect_to=redirect_to, scopes=scopes)
    oauth_url = res.get("url")
    if not oauth_url:
        raise HTTPException(status_code=502, detail="OAuth provider did not return a redirect URL.")
    return RedirectResponse(url=oauth_url)


@router.get("/oauth/callback")
async def oauth_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
) -> Any:
    if error:
        raise HTTPException(status_code=400, detail=error_description or error)
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided.")
    auth = SupabaseAuth.from_request(request)
    response = auth.exchange_oauth_code(code)

    app_redirect = request.session.pop("app_redirect", None)
    if app_redirect:
        tokens = response.get("session") or {}
        access_token = tokens.get("access_token", "")
        refresh_token = tokens.get("refresh_token", "")
        return RedirectResponse(url=f"{app_redirect}#access_token={access_token}&refresh_token={refresh_token}")

    return response