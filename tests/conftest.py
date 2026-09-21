import pytest
import app as app_module


@pytest.fixture
def client():
    """کلاینت تست Flask"""
    app_module.app.config['TESTING'] = True
    return app_module.app.test_client()


@pytest.fixture(autouse=True)
def reset_tasks():
    """قبل و بعد از هر تست، لیست tasks رو خالی کن"""
    app_module.tasks.clear()
    yield
    app_module.tasks.clear()


@pytest.fixture
def sample_tasks():
    """سه تسک نمونه برای تست‌های سریع"""
    app_module.tasks.extend([
        {"id": 1, "title": "خرید نان", "done": False},
        {"id": 2, "title": "تمیز کردن خانه", "done": True},
        {"id": 3, "title": "خواندن کتاب", "done": False},
    ])
    return app_module.tasks
