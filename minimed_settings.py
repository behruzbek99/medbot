"""
MiniMed Application Settings
"""
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", env="GROQ_MODEL")
    groq_max_tokens: int = Field(default=1024, env="GROQ_MAX_TOKENS")
    groq_temperature: float = Field(default=0.7, env="GROQ_TEMPERATURE")
    admin_usernames: Optional[str] = Field(default="Rakh_matova19,CEO_Bekhruz", env="ADMIN_USERNAMES")
    app_env: str = Field(default="production", env="APP_ENV")
    app_debug: bool = Field(default=False, env="APP_DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    force_subscribe_channels: Optional[str] = Field(default="https://t.me/+YVKl_R-uUSwxNGIy,https://t.me/+6CYVuWlbS803Y2Vi", env="FORCE_SUBSCRIBE_CHANNELS")

    @property
    def admin_usernames_set(self) -> set:
        return set(u.strip() for u in (self.admin_usernames or "").split(",") if u.strip())
    
    @property
    def channel_invite_links(self) -> List[str]:
        return [link.strip() for link in (self.force_subscribe_channels or "").split(",") if link.strip()]


settings = AppSettings()
