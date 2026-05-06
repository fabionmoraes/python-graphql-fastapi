import secrets

from app.core.config import settings


def verify_basic_credentials(username: str, password: str) -> bool:
    correct_username = secrets.compare_digest(username, settings.API_USERNAME)
    correct_password = secrets.compare_digest(password, settings.API_PASSWORD)
    return correct_username and correct_password
