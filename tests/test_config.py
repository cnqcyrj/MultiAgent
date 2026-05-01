"""
配置测试
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from config.settings import (
    Settings,
    load_settings,
    get_settings,
    update_settings,
    reset_settings,
)


class TestSettings:
    """配置类测试"""

    def test_default_settings(self):
        """测试默认配置"""
        settings = Settings()

        assert settings.app_name == "MultiAgent-CodeForge"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.max_concurrent_tasks == 10
        assert settings.task_timeout == 300
        assert settings.retry_attempts == 3
        assert settings.retry_delay == 1.0

    def test_custom_settings(self):
        """测试自定义配置"""
        settings = Settings(
            debug=True,
            log_level="DEBUG",
            max_concurrent_tasks=20,
        )

        assert settings.debug is True
        assert settings.log_level == "DEBUG"
        assert settings.max_concurrent_tasks == 20

    def test_settings_to_dict(self):
        """测试配置转字典"""
        settings = Settings()
        config_dict = settings.to_dict()

        assert isinstance(config_dict, dict)
        assert "app_name" in config_dict
        assert "app_version" in config_dict
        assert "debug" in config_dict


class TestLoadSettings:
    """加载配置测试"""

    def test_load_settings_from_env(self):
        """测试从环境变量加载配置"""
        with patch.dict(os.environ, {
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "MAX_CONCURRENT_TASKS": "20",
        }):
            settings = load_settings()

            assert settings.debug is True
            assert settings.log_level == "DEBUG"
            assert settings.max_concurrent_tasks == 20

    def test_load_settings_defaults(self):
        """测试加载默认配置"""
        # 清除环境变量
        env_vars = [
            "DEBUG", "LOG_LEVEL", "MAX_CONCURRENT_TASKS",
            "TASK_TIMEOUT", "RETRY_ATTEMPTS",
        ]
        with patch.dict(os.environ, {k: "" for k in env_vars}, clear=False):
            settings = load_settings()

            assert settings.debug is False
            assert settings.log_level == "INFO"
            assert settings.max_concurrent_tasks == 10


class TestGlobalSettings:
    """全局配置测试"""

    def setup_method(self):
        """测试前重置"""
        reset_settings()

    def test_get_settings(self):
        """测试获取全局配置"""
        settings = get_settings()

        assert settings is not None
        assert isinstance(settings, Settings)

    def test_get_settings_singleton(self):
        """测试全局配置单例"""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_update_settings(self):
        """测试更新配置"""
        settings = get_settings()
        original_debug = settings.debug

        update_settings(debug=not original_debug)

        updated_settings = get_settings()
        assert updated_settings.debug == (not original_debug)

    def test_reset_settings(self):
        """测试重置配置"""
        settings1 = get_settings()
        update_settings(debug=True)

        reset_settings()

        settings2 = get_settings()
        assert settings2.debug is False

    def teardown_method(self):
        """测试后重置"""
        reset_settings()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
