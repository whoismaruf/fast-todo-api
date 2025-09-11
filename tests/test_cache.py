import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock, patch

from app.dependencies import get_db, get_current_user
from app.redis_client import get_cache_service
from main import app
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


class TestCacheService:
    """Test the cache service functionality"""
    
    def test_cache_service_creation(self):
        """Test that cache service can be created even when Redis is unavailable"""
        from app.redis_client import CacheService
        cache = CacheService()
        assert cache is not None
        # Should handle Redis being unavailable gracefully
        assert cache.get("test_key") is None
        assert cache.set("test_key", "test_value") is False
        assert cache.delete("test_key") is False

    def test_cache_operations_with_mock_redis(self):
        """Test cache operations with a mocked Redis client"""
        from app.redis_client import CacheService
        
        # Mock Redis client
        mock_redis = Mock()
        mock_redis.get.return_value = '{"test": "data"}'
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.keys.return_value = ["test_key_1", "test_key_2"]
        
        cache = CacheService()
        cache.client = mock_redis
        
        # Test get
        result = cache.get("test_key")
        assert result == {"test": "data"}
        mock_redis.get.assert_called_with("test_key")
        
        # Test set
        success = cache.set("test_key", {"test": "data"})
        assert success is True
        mock_redis.setex.assert_called_with("test_key", 300, '{"test": "data"}')
        
        # Test delete
        success = cache.delete("test_key")
        assert success is True
        mock_redis.delete.assert_called_with("test_key")
        
        # Test delete pattern
        count = cache.delete_pattern("test_key_*")
        assert count == 1
        mock_redis.keys.assert_called_with("test_key_*")
        mock_redis.delete.assert_called_with("test_key_1", "test_key_2")


class TestTodosCaching:
    """Test caching behavior in todos endpoints"""
    
    def test_get_todos_with_cache_mock(self, test_todo):
        """Test that get todos uses cache when available"""
        mock_cache = Mock()
        mock_cache.get.return_value = None  # First call - cache miss
        mock_cache.set.return_value = True
        
        app.dependency_overrides[get_cache_service] = lambda: mock_cache
        
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify cache was checked and set
        mock_cache.get.assert_called_with("user_todos:1")
        mock_cache.set.assert_called_once()
        
        # Clean up
        if get_cache_service in app.dependency_overrides:
            del app.dependency_overrides[get_cache_service]
    
    def test_get_todo_with_cache_mock(self, test_todo):
        """Test that get specific todo uses cache when available"""
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.set.return_value = True
        
        app.dependency_overrides[get_cache_service] = lambda: mock_cache
        
        response = client.get(f"/{test_todo.id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify cache was checked and set
        mock_cache.get.assert_called_with(f"todo:{test_todo.id}:1")
        mock_cache.set.assert_called_once()
        
        # Clean up
        if get_cache_service in app.dependency_overrides:
            del app.dependency_overrides[get_cache_service]
    
    def test_create_todo_invalidates_cache(self, test_todo):
        """Test that creating a todo invalidates the user's todos cache"""
        mock_cache = Mock()
        mock_cache.delete.return_value = True
        
        app.dependency_overrides[get_cache_service] = lambda: mock_cache
        
        response = client.post(
            "/",
            json={
                "title": "Cache Test Todo",
                "description": "Test cache invalidation",
                "priority": 1,
                "completed": False,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify cache invalidation was called
        mock_cache.delete.assert_called_with("user_todos:1")
        
        # Clean up
        if get_cache_service in app.dependency_overrides:
            del app.dependency_overrides[get_cache_service]
    
    def test_update_todo_invalidates_cache(self, test_todo):
        """Test that updating a todo invalidates both specific and list cache"""
        mock_cache = Mock()
        mock_cache.delete.return_value = True
        
        app.dependency_overrides[get_cache_service] = lambda: mock_cache
        
        response = client.put(
            f"/{test_todo.id}",
            json={
                "title": "Updated Todo",
                "description": "Updated description",
                "priority": 2,
                "completed": True,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify both cache keys were invalidated
        expected_calls = [
            (f"todo:{test_todo.id}:1",),
            ("user_todos:1",)
        ]
        actual_calls = [call[0] for call in mock_cache.delete.call_args_list]
        assert all(call in actual_calls for call in expected_calls)
        
        # Clean up
        if get_cache_service in app.dependency_overrides:
            del app.dependency_overrides[get_cache_service]
    
    def test_delete_todo_invalidates_cache(self, test_todo):
        """Test that deleting a todo invalidates both specific and list cache"""
        mock_cache = Mock()
        mock_cache.delete.return_value = True
        
        app.dependency_overrides[get_cache_service] = lambda: mock_cache
        
        response = client.delete(f"/{test_todo.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify both cache keys were invalidated
        expected_calls = [
            (f"todo:{test_todo.id}:1",),
            ("user_todos:1",)
        ]
        actual_calls = [call[0] for call in mock_cache.delete.call_args_list]
        assert all(call in actual_calls for call in expected_calls)
        
        # Clean up
        if get_cache_service in app.dependency_overrides:
            del app.dependency_overrides[get_cache_service]


class TestAuthCaching:
    """Test caching behavior in auth endpoints"""
    
    def test_get_me_with_cache_mock(self, test_user):
        """Test that get user profile uses cache when available"""
        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.set.return_value = True
        
        app.dependency_overrides[get_cache_service] = lambda: mock_cache
        
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify cache was checked and set
        mock_cache.get.assert_called_with("user_profile:1")
        mock_cache.set.assert_called_once()
        
        # Clean up
        if get_cache_service in app.dependency_overrides:
            del app.dependency_overrides[get_cache_service]
    
    def test_change_password_invalidates_cache(self, test_user):
        """Test that changing password invalidates user profile cache"""
        mock_cache = Mock()
        mock_cache.delete.return_value = True
        
        app.dependency_overrides[get_cache_service] = lambda: mock_cache
        
        response = client.post(
            "/auth/change_password",
            json={
                "old_password": "test.password",
                "new_password": "new.password"
            },
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify cache invalidation was called
        mock_cache.delete.assert_called_with("user_profile:1")
        
        # Clean up
        if get_cache_service in app.dependency_overrides:
            del app.dependency_overrides[get_cache_service]