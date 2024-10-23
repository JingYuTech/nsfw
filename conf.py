#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: 李权威
Email: cnlqws@gmail.com
Date: 2024-10-23
Description: A library for detecting NSFW content in images.
"""

from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BasePath = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """AI插件 配置"""
    model_config = SettingsConfigDict(env_file=f'{BasePath}/.env', env_file_encoding='utf-8', extra='ignore')

    MODELS_DIR: str = os.path.join(BasePath, 'models')

    NSFW_WEIGHTS: str = os.path.join(BasePath, 'models', 'lqw_nsfw_v15_weights.onnx')


@lru_cache
def settings() -> Settings:
    """获取配置"""
    return Settings()


settings_aiplugs = settings()
