from env_data import AdminEnv


def is_admin(user_id: int) -> bool:
    """Telegram user ID .env fayldagi ADMIN_IDS ro'yxatida bo'lsa, u Admin hisoblanadi."""
    return user_id in AdminEnv.ADMIN_IDS
