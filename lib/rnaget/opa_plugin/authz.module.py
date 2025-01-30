from logging import Logger
from typing import Any, Awaitable, Callable, Coroutine

from authx.auth import (
    verify_service_token,
)
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from transcriptomics_data_service.authz.middleware_base import BaseAuthzMiddleware
from transcriptomics_data_service.config import Config, get_config
from transcriptomics_data_service.logger import get_logger

config = get_config()
logger = get_logger(config)

"""
CUSTOM PLUGIN DEPENDENCY
Extra dependencies can be added if the authz plugin requires them.
In this example, the authz module imports the OPA client.
Since OPA does not ship with TDS, a requirements.txt file must be placed under 'lib'.
"""


class OPAAuthzMiddleware(BaseAuthzMiddleware):
    """
    Concrete implementation of BaseAuthzMiddleware to authorize requests with OPA.
    """

    def __init__(self, config: Config, logger: Logger) -> None:
        super().__init__()
        self.enabled = config.bento_authz_enabled
        self.logger = logger

    # Middleware lifecycle
    def attach(self, app: FastAPI):
        app.middleware("http")(self.dispatch)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Coroutine[Any, Any, Response]:
        if not self.enabled:
            return await call_next(request)

        try:
            res = await call_next(request)
        except HTTPException as e:
            # Catch exceptions raised by authz functions
            self.logger.error(e)
            return JSONResponse(status_code=e.status_code, content=e.detail)

        return res

    # OPA authorization function
    def _dep_check_opa(self, service_name: str):
        async def inner(request: Request):
            service_token = request.headers.get("x-service-token")
            if not service_token:
                raise HTTPException(
                    status_code=401, detail="Unauthorized: Missing service token"
                )

            try:
                is_valid_token = verify_service_token(
                    service=service_name, token=service_token
                )
            except Exception as e:
                self.logger.error(f"Error validating token for {service_name}: {e}")
                raise HTTPException(status_code=500, detail="OPA service error")

            if not is_valid_token:
                raise HTTPException(
                    status_code=401, detail="Unauthorized: Service token invalid"
                )

            return True

        return Depends(inner)

    # Authz logic: OPA check injected at endpoint levels
    def dep_authz_ingest(self):
        return [self._dep_check_opa(service_name="candig-ingest")]

    def dep_authz_normalize(self):
        return [self._dep_check_opa(service_name="htsget")]

    def dep_authz_delete_experiment_result(self):
        return [self._dep_check_opa(service_name="htsget")]

    def dep_authz_expressions_list(self):
        return [self._dep_check_opa(service_name="htsget")]

    def dep_authz_get_experiment_result(self):
        return [self._dep_check_opa(service_name="htsget")]


authz_middleware = OPAAuthzMiddleware(config, logger)
