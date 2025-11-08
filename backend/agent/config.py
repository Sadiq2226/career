import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    data_dir: str = os.getenv("DATA_DIR", os.path.join("backend", "data"))

    # Optional LLM keys
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY") or None
    hf_api_token: str | None = os.getenv("HUGGINGFACEHUB_API_TOKEN") or None

    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    @property
    def online_mode(self) -> bool:
        return any([self.openai_api_key, self.google_api_key, self.hf_api_token])


settings = Settings()
