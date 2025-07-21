"""
CourtListener MCP Server - Application Lifecycle Management

Handles server startup/shutdown and resource management.
"""

import os
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


@dataclass
class CourtListenerContext:
    """Application context for CourtListener resources."""
    http_client: httpx.AsyncClient
    api_token: Optional[str]
    base_url: str = "https://www.courtlistener.com/api/rest/v4"


@asynccontextmanager
async def courtlistener_lifespan(server: FastMCP) -> AsyncIterator[CourtListenerContext]:
    """
    Manage the lifecycle of CourtListener MCP server.
    
    Initializes HTTP client and API authentication on startup,
    and properly closes connections on shutdown.
    """
    logger.info("Starting CourtListener MCP Server...")
    
    # Get API token from environment
    api_token = os.getenv('COURTLISTENER_API_TOKEN')
    if not api_token:
        logger.warning("No COURTLISTENER_API_TOKEN found in environment. Some features may be limited.")
    
    # Initialize HTTP client with appropriate headers
    headers = {
        'User-Agent': 'CourtListener-MCP-Server/1.0.0',
        'Accept': 'application/json',
    }
    
    if api_token:
        headers['Authorization'] = f'Token {api_token}'
    
    timeout = httpx.Timeout(
        connect=10.0,   # 10 seconds to connect
        read=30.0,      # 30 seconds to read response
        write=10.0,     # 10 seconds to write request
        pool=5.0        # 5 seconds to get connection from pool
    )
    
    # Create HTTP client with connection pooling and timeouts
    async with httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        limits=httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100,
            keepalive_expiry=30.0
        )
    ) as http_client:
        logger.info("CourtListener MCP Server initialized successfully")
        
        try:
            yield CourtListenerContext(
                http_client=http_client,
                api_token=api_token,
                base_url=os.getenv('COURTLISTENER_BASE_URL', 'https://www.courtlistener.com/api/rest/v4')
            )
        except Exception as e:
            logger.error(f"Error in CourtListener MCP Server context: {e}")
            raise
        finally:
            logger.info("CourtListener MCP Server shutting down...")
