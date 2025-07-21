"""
CourtListener MCP Server Factory

Factory function to create and configure the MCP server.
This separates server creation from the main entry point to avoid circular imports.
"""

import logging
from mcp.server.fastmcp import FastMCP

from core.lifespan import courtlistener_lifespan
from tools.opinion_tools import register_opinion_tools
from tools.docket_tools import register_docket_tools
from tools.cluster_tools import register_cluster_tools
from tools.court_tools import register_court_tools
from tools.search_tools import register_search_tools
from tools.people_tools import register_people_tools
from tools.political_affiliation_tools import register_political_affiliation_tools
from tools.aba_ratings_tools import register_aba_ratings_tools
from tools.retention_events_tools import register_retention_events_tools
from tools.sources_tools import register_sources_tools
from tools.education_tools import register_education_tools
from tools.citation_tools import register_citation_tools
from tools.opinions_cited_tools import register_opinions_cited_tools
from tools.position_tools import register_position_tools

logger = logging.getLogger(__name__)


def create_courtlistener_server() -> FastMCP:
    """
    Create and configure the CourtListener MCP server.
    
    Returns:
        FastMCP: Configured server with all tools registered
    """
    # Initialize the FastMCP server with production configuration
    mcp = FastMCP(
        name="CourtListener",
        lifespan=courtlistener_lifespan,
        dependencies=[
            "httpx>=0.24.0",
            "python-dotenv>=1.0.0"
        ]
    )
    
    # Register all available tools
    register_opinion_tools(mcp)
    register_docket_tools(mcp)
    register_cluster_tools(mcp)
    register_court_tools(mcp)
    register_search_tools(mcp)
    register_people_tools(mcp)
    register_political_affiliation_tools(mcp)
    register_aba_ratings_tools(mcp)
    register_retention_events_tools(mcp)
    register_sources_tools(mcp)
    register_education_tools(mcp)
    register_citation_tools(mcp)
    register_opinions_cited_tools(mcp)
    register_position_tools(mcp)
    
    logger.info("All CourtListener tools registered successfully")
    
    return mcp


def get_registered_tools(mcp_server: FastMCP) -> list[str]:
    """
    Get list of all registered tool names.
    
    Args:
        mcp_server: The configured MCP server
        
    Returns:
        List of tool names
    """
    # Return the known tools from your implementation
    return [
        'get_opinion',
        'get_cluster', 
        'get_docket',
        'get_court',
        'search_legal_cases',
        'advanced_legal_search',
        'get_judge',
        'get_political_affiliations',
        'get_aba_ratings',
        'get_retention_events',
        'get_sources',
        'get_educations',
        'verify_citations',
        'find_authorities_cited',
        'find_citing_opinions',
        'analyze_citation_network',
        'get_positions'
    ]
