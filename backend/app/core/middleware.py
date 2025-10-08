"""
Middleware para UNS-ClaudeJP 2.0
"""
import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from app.core.exceptions import UNSException, http_exception_from_uns

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de peticiones"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Log de petición
        logger.info(f"Request: {request.method} {request.url}")
        
        # Procesar petición
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Log de respuesta
        logger.info(
            f"Response: {response.status_code} - Time: {process_time:.4f}s"
        )
        
        # Añadir header de tiempo de procesamiento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware para manejo centralizado de excepciones"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except UNSException as exc:
            # Convertir excepción UNS a HTTPException
            http_exc = http_exception_from_uns(exc)
            logger.error(f"UNS Exception: {exc.message} - Details: {exc.details}")
            raise http_exc
        except Exception as exc:
            # Capturar excepciones no controladas
            logger.exception(f"Unhandled exception: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail={"message": "Internal server error", "details": str(exc)}
            )


from fastapi import HTTPException