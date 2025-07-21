"""
CourtListener Citation Lookup and Verification Tools

Citation parsing, lookup, and verification using CourtListener's comprehensive citation database.
Powered by Eyecite - analyzes 18,219,417 citations across 200+ years of American case law.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.formatters import format_citation_verification_simple

logger = logging.getLogger(__name__)


def register_citation_tools(mcp: FastMCP):
    """Register citation lookup and verification tools with the MCP server."""
    
    @mcp.tool()
    async def verify_citations(
        text: Optional[str] = None,
        volume: Optional[str] = None,
        reporter: Optional[str] = None,
        page: Optional[str] = None
    ) -> str:
        """
        Verify and lookup legal citations using CourtListener's comprehensive citation database.
        
        Can parse citations from text or lookup specific volume/reporter/page combinations.
        Uses Eyecite parsing engine with 18,219,417 citations from 200+ years of case law.
        
        Args:
            text: Block of text to parse for citations (max 64,000 characters)
            volume: Specific volume number to lookup (e.g., "576")
            reporter: Specific reporter abbreviation (e.g., "U.S.", "F.3d")
            page: Specific page number to lookup (e.g., "644")
        
        Returns:
            Citation verification results with case details and validation status
        
        Examples:
            # Parse citations from text
            verify_citations(text="See Obergefell v. Hodges (576 U.S. 644)")
            
            # Lookup specific citation
            verify_citations(volume="576", reporter="U.S.", page="644")
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Validate input parameters
            if not text and not (volume and reporter and page):
                return "❌ Error: Must provide either 'text' to parse OR volume/reporter/page for specific lookup."
            
            if text and (volume or reporter or page):
                return "❌ Error: Use either 'text' parameter OR volume/reporter/page parameters, not both."
            
            # Build request data
            data = {}
            is_text_parsing = bool(text)
            
            if text:
                if len(text) > 64000:
                    return "❌ Error: Text exceeds 64,000 character limit."
                data['text'] = text
                logger.info(f"Parsing citations from text ({len(text)} characters)")
            else:
                data['volume'] = volume
                data['reporter'] = reporter
                data['page'] = page
                logger.info(f"Looking up citation: {volume} {reporter} {page}")
            
            # Make API request
            url = f"{courtlistener_ctx.base_url}/citation-lookup/"
            response = await courtlistener_ctx.http_client.post(url, data=data)
            response.raise_for_status()
            results = response.json()
            
            # Handle empty results
            if not results:
                if text:
                    return f"❌ No citations found in the provided text.\n\n📝 Text analyzed: {len(text)} characters\n💡 Note: Only validates case law citations, not statutes or law journals."
                else:
                    return f"❌ Citation not found: {volume} {reporter} {page}\n\n📊 Database searched: 18,219,417 citations"
            
            # Use shared formatter
            return format_citation_verification_simple(results, is_text_parsing)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                try:
                    error_data = e.response.json()
                    wait_until = error_data.get('wait_until', 'unknown time')
                    return f"⏳ Rate limit exceeded: 60 citations per minute\n🕒 Wait until: {wait_until}"
                except:
                    return "⏳ Rate limit exceeded: Please wait before making additional requests."
            elif e.response.status_code == 401:
                return "🔐 Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error in citation lookup: {e}")
                return f"❌ Citation lookup error: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error in citation lookup: {e}", exc_info=True)
            return f"❌ Citation lookup error: {str(e)}"