import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_config_imports():
    from src.config import settings
    assert settings.SERVER_PORT > 0


def test_models_module_exists():
    import src.db.models
    assert hasattr(src.db.models, 'Base')


def test_core_modules_exist():
    import src.core.storage
    import src.core.feedback
    assert True
