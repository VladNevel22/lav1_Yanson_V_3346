from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import os
from .redis_client import cache

NEWS_CACHE_TTL = int(os.getenv("NEWS_CACHE_TTL", 300))  # 5 минут
SESSION_CACHE_TTL = int(os.getenv("SESSION_CACHE_TTL", 604800))  # 7 дней
USER_CACHE_TTL = int(os.getenv("USER_CACHE_TTL", 600))  # 10 минут

class CacheService:
    @staticmethod
    def get_news_key(news_id: int) -> str:
        return f"news:{news_id}"
    
    @staticmethod
    def get_user_key(user_id: int) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def get_session_key(refresh_token: str) -> str:
        return f"session:{refresh_token}"
    
    @staticmethod
    def get_user_sessions_key(user_id: int) -> str:
        return f"user_sessions:{user_id}"
    
    def get_news(self, news_id: int) -> Optional[Dict]:
        """Получить новость из кэша"""
        key = self.get_news_key(news_id)
        return cache.get(key)
    
    def set_news(self, news_id: int, news_data: Dict) -> bool:
        """Сохранить новость в кэш"""
        key = self.get_news_key(news_id)
        safe_data = {
            'id': news_data.get('id'),
            'title': news_data.get('title'),
            'content': news_data.get('content'),
            'published_at': news_data.get('published_at'),
            'author_id': news_data.get('author_id'),
            'cover': news_data.get('cover'),
            'cached_at': datetime.utcnow().isoformat()
        }
        return cache.set(key, safe_data, NEWS_CACHE_TTL)
    
    def delete_news(self, news_id: int) -> bool:
        """Удалить новость из кэша"""
        key = self.get_news_key(news_id)
        return cache.delete(key)

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя из кэша (без чувствительных данных)"""
        key = self.get_user_key(user_id)
        return cache.get(key)
    
    def set_user(self, user: Any) -> bool:
        """Сохранить пользователя в кэш (без пароля)"""
        key = self.get_user_key(user.id)
        safe_user = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_author': user.is_author,
            'is_admin': user.is_admin,
            'avatar': user.avatar,
            'github_id': user.github_id,
            'cached_at': datetime.utcnow().isoformat()
        }
        return cache.set(key, safe_user, USER_CACHE_TTL)
    
    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя из кэша"""
        key = self.get_user_key(user_id)
        return cache.delete(key)
    
    def get_session(self, refresh_token: str) -> Optional[Dict]:
        """Получить сессию из кэша"""
        key = self.get_session_key(refresh_token)
        return cache.get(key)
    
    def set_session(self, refresh_token: str, session_data: Dict) -> bool:
        """Сохранить сессию в кэш"""
        key = self.get_session_key(refresh_token)
        session_data['cached_at'] = datetime.utcnow().isoformat()
        return cache.set(key, session_data, SESSION_CACHE_TTL)
    
    def delete_session(self, refresh_token: str) -> bool:
        """Удалить сессию из кэша"""
        key = self.get_session_key(refresh_token)
        return cache.delete(key)
    
    def get_user_sessions(self, user_id: int) -> list:
        """Получить все сессии пользователя"""
        key = self.get_user_sessions_key(user_id)
        sessions = cache.get(key) or []
        return sessions
    
    def add_user_session(self, user_id: int, refresh_token: str) -> bool:
        """Добавить сессию в список сессий пользователя"""
        key = self.get_user_sessions_key(user_id)
        sessions = self.get_user_sessions(user_id)
        if refresh_token not in sessions:
            sessions.append(refresh_token)
            return cache.set(key, sessions, SESSION_CACHE_TTL)
        return True
    
    def remove_user_session(self, user_id: int, refresh_token: str) -> bool:
        """Удалить сессию из списка сессий пользователя"""
        key = self.get_user_sessions_key(user_id)
        sessions = self.get_user_sessions(user_id)
        if refresh_token in sessions:
            sessions.remove(refresh_token)
            return cache.set(key, sessions, SESSION_CACHE_TTL)
        return True
    
    def delete_all_user_sessions(self, user_id: int) -> bool:
        """Удалить все сессии пользователя"""
        sessions_key = self.get_user_sessions_key(user_id)
        sessions = self.get_user_sessions(user_id)
        
        for token in sessions:
            self.delete_session(token)
        
        return cache.delete(sessions_key)


cache_service = CacheService()