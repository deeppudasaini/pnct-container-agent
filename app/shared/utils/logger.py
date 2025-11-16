import logging
import sys
from logging import Logger
from pathlib import Path
from typing import Optional

from app.shared.config.settings.base import get_settings

settings = get_settings()



def get_logger(name: str):
    return Logger

