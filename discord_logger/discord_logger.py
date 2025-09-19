import time
from datetime import datetime
from typing import Literal

import httpx
import requests
import urllib3
from fastapi import (
    FastAPI,
    Request,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def add_monitoring(app: FastAPI, logger_base_url: str, service_name: str, channel_id: int, verify: bool = True):
    data = {
        "service_name": service_name,
        "channel_id": channel_id,
    }
    requests.post(
        f"{logger_base_url}/monitoring/add-service",
        data=data,
        verify=verify,
    )
    httpx_client = httpx.AsyncClient(verify=verify)
    @app.middleware("http")
    async def logger(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        end_time = time.perf_counter() - start_time
        data = {
            "service_name": service_name,
            "route_name": str(request.url)[len(str(request.base_url)):].split("?")[0],
            "request" : {
                "timestamp": datetime.now(),
                "response_time": end_time,
            }
        }
        await httpx_client.post(
            f"{logger_base_url}/monitoring/add-request",
            data=data,
        )
        return response


async def log(logger_base_url: str, channel_id: int, message: str, level: Literal["INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"):
    data = {
        "channel_id": channel_id,
        "logging_message" : {
            "message": message,
            "level": level,
        }
    }
    await httpx_client.post(
        f"{logger_base_url}/monitoring/add-request",
        data=data,
    )
