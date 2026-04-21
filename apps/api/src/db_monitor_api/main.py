from fastapi import FastAPI

from db_monitor_api.app import create_app
from db_monitor_api.bootstrap import build_runtime_from_settings
from db_monitor_api.settings import load_api_settings


def build_app_from_environment() -> FastAPI:
    return create_app(runtime=build_runtime_from_settings(load_api_settings()))


app = build_app_from_environment()
