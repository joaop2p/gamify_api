from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
from supabase_auth._sync.storage import SyncMemoryStorage
from fastapi import Request
from config.config import Config

CONFIG = Config()


class StarletteSessionStorage(SyncMemoryStorage):
    """Storage backed by Starlette's request.session for PKCE persistence across requests."""

    def __init__(self, request: Request, namespace: str = "supabase_oauth") -> None:
        self._session = request.session
        self._namespace = namespace

    def _bucket(self) -> dict:
        if self._namespace not in self._session:
            self._session[self._namespace] = {}
        return self._session[self._namespace]

    def get_item(self, key: str) -> str | None:
        return self._bucket().get(key)

    def set_item(self, key: str, value: str) -> None:
        bucket = self._bucket()
        bucket[key] = value
        self._session[self._namespace] = bucket

    def remove_item(self, key: str) -> None:
        bucket = self._bucket()
        bucket.pop(key, None)
        self._session[self._namespace] = bucket


class SessionStorage:
    def __init__(self, request: Request, space_name: str) -> None:
        self.session = request.session
        self.space_name = space_name

    @property
    def _bucket(self) -> dict:
        if self.space_name not in self.session:
            self.session[self.space_name] = {}
        return self.session[self.space_name]
    
    def get(self, key: str) -> str | None:
        return self._bucket.get(key)
    
    def set(self, key: str, value: str) -> None:
        self._bucket[key] = value

    def delete(self, key: str) -> None:
        self._bucket.pop(key, None)

class SupabaseAuth:
    def __init__(self, client: Client, storage: SessionStorage) -> None:
        self.client = client
        self.storage = storage

    @classmethod
    def from_request(cls, request: Request, space_name: str = "supabase_auth") -> "SupabaseAuth":
        url = CONFIG.get_env("SUPABASE_URL")
        key = CONFIG.get_env("SUPABASE_KEY")
        session_storage = StarletteSessionStorage(request)
        options = SyncClientOptions(storage=session_storage, flow_type="pkce", auto_refresh_token=False, persist_session=False)
        client = create_client(url, key, options)
        storage = SessionStorage(request, space_name)
        return cls(client, storage)

    def sign_up(self, email: str, password: str, metadata: dict | None = None) -> dict:
        if metadata is None:
            metadata = {}
        try:
            response = self.client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": metadata
                    }
                }
            )
        except Exception as e:
            raise RuntimeError(f"Sign up failed: {str(e)}") from e
        return response.model_dump()
    
    def sign_in(self, email: str, password: str) -> dict:
        try:
            response = self.client.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )
            if response.session is None:
                raise RuntimeError("Sign in failed: No session returned.")
        except Exception as e:
            raise RuntimeError(f"Sign in failed: {str(e)}") from e
        return response.model_dump()
    
    def start_oauth(self, provider: str, redirect_to: str | None = None, scopes: str | None = None) -> dict:
        provider = provider.lower().strip()
        if provider not in CONFIG.get_config("auth", "providers", "supabase", "providers"):
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        options: dict = {
            "redirect_to": redirect_to or CONFIG.get_env("SUPABASE_OAUTH_REDIRECT_URL"),
        }
        if scopes:
            options["scopes"] = scopes
        try:
            response = self.client.auth.sign_in_with_oauth(
                {
                    "provider": provider, #type: ignore
                    "options": options
                }
            )
        except Exception as e:
            raise RuntimeError(f"OAuth sign in failed: {str(e)}") from e
        return response.model_dump()
    
    def exchange_oauth_code(self, auth_code: str, redirect_to: str | None = None) -> dict:
        redirect_to = redirect_to or CONFIG.get_env("SUPABASE_OAUTH_REDIRECT_URL")
        try:
            response = self.client.auth.exchange_code_for_session(
                {
                    "auth_code": auth_code,
                    "redirect_to": redirect_to
                } # type: ignore
            )
            if response.session is None:
                raise RuntimeError("OAuth code exchange failed: No session returned.")
        except Exception as e:
            raise RuntimeError(f"OAuth code exchange failed: {str(e)}") from e
        return response.model_dump(mode="json")