from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Genie Cloud client settings"""

    base_url: str = "https://genie.stanford.edu"

    # OAuth2 connect:
    auth_url: str = "/me/api/oauth2/authorize"
    token_url: str = "/me/api/oauth2/token"
    client_id: str = "client-id"
    client_secret: str = "client-secret"
    redirect_uri: str = "https://based.at/oauth2.html"

    conversation_url: str = "/me/api/conversation"
    authorization_code: str = "authorization-code"
    access_token: str = "access-token"

    class Config:
        env_file = Path(__file__).parent / ".env"


settings = Settings()
