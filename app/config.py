import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from langchain_ollama import ChatOllama


load_dotenv()


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("MODEL_NAME", "qwen2.5:0.5b")
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/expenses.db"))


settings = Settings()


def create_llm() -> ChatOllama:
    return ChatOllama(model=settings.model_name, temperature=0)
