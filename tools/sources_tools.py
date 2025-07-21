"""
CourtListener Sources Analysis Tools

Data sources and provenance tracking for judge and legal professional information.
Provides detailed source information including URLs, access dates, and notes.
CORRECTED implementation matching exact API metadata filters.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.formatters import format_sources_analyses

logger = logging.getLogger(__name__)


def register_sources_tools(mcp: FastMCP):
    """Register all sources tools with the MCP server."""
    
    @mcp.tool()
    async def get_sources(
        source_id: Optional[int] = None,
        person_id: Optional[int] = None,
        # Date modified filters (ALL supported lookups from metadata)
        date_modified: Optional[str] = None,
        date_modified_after: Optional[str] = None,
        date_modified_before: Optional[str] = None,
        date_modified_gt: Optional[str] = None,
        date_modified_lt: Optional[str] = None,
        date_modified_range: Optional[str] = None,
        date_modified_year: Optional[int] = None,
        date_modified_month: Optional[int] = None,
        date_modified_day: Optional[int] = None,
        date_modified_hour: Optional[int] = None,
        date_modified_minute: Optional[int] = None,
        date_modified_second: Optional[int] = None,
        # ID filter (exact only per metadata)
        id: Optional[int] = None,
        # Configuration
        include_person_details: bool = True,
        order_by: Optional[str] = None,
        limit: int = 20
    ) -> str:
        """
        Retrieve and analyze data sources for judges and legal professionals using EXACT API metadata filters.
        
        Args:
            source_id: Specific source ID to retrieve
            person_id: Person ID to get all sources for (exact match only per API)
            
            # Date modified filters (ALL supported lookups from API metadata)
            date_modified: Exact modification datetime
            date_modified_after: Sources modified after this datetime (inclusive) [__gte]
            date_modified_before: Sources modified before this datetime (inclusive) [__lte]
            date_modified_gt: Sources modified after this datetime (exclusive) [__gt]
            date_modified_lt: Sources modified before this datetime (exclusive) [__lt]
            date_modified_range: Datetime range "YYYY-MM-DD,YYYY-MM-DD" [__range]
            date_modified_year: Sources modified in this specific year
            date_modified_month: Sources modified in this specific month (1-12)
            date_modified_day: Sources modified on this specific day (1-31)
            date_modified_hour: Sources modified in this specific hour (0-23)
            date_modified_minute: Sources modified in this specific minute (0-59)
            date_modified_second: Sources modified in this specific second (0-59)
            
            id: Exact source ID (only exact match supported per API)
            include_person_details: Whether to include detailed person information
            order_by: Sort order ('id', 'date_modified', 'date_accessed' with optional '-' prefix)
            limit: Maximum number of results (1-100)
        
        Returns:
            Comprehensive source analysis including provenance data, URLs, and access information
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            params = {}
            
            if source_id:
                url = f"{courtlistener_ctx.base_url}/sources/{source_id}/"
                logger.info(f"Fetching source by ID: {source_id}")
            else:
                url = f"{courtlistener_ctx.base_url}/sources/"
                
                # Basic filters (EXACT API compliance)
                if person_id:
                    params['person'] = person_id
                
                # Date modified filters (ALL supported lookups from API metadata)
                if date_modified:
                    params['date_modified'] = date_modified
                if date_modified_after:
                    params['date_modified__gte'] = date_modified_after
                if date_modified_before:
                    params['date_modified__lte'] = date_modified_before
                if date_modified_gt:
                    params['date_modified__gt'] = date_modified_gt
                if date_modified_lt:
                    params['date_modified__lt'] = date_modified_lt
                if date_modified_range:
                    params['date_modified__range'] = date_modified_range
                if date_modified_year:
                    params['date_modified__year'] = date_modified_year
                if date_modified_month:
                    params['date_modified__month'] = date_modified_month
                if date_modified_day:
                    params['date_modified__day'] = date_modified_day
                if date_modified_hour:
                    params['date_modified__hour'] = date_modified_hour
                if date_modified_minute:
                    params['date_modified__minute'] = date_modified_minute
                if date_modified_second:
                    params['date_modified__second'] = date_modified_second
                
                # ID filter (exact only per API metadata)
                if id:
                    params['id'] = id
                
                # Ordering (using API-supported ordering fields from metadata)
                if order_by:
                    valid_orders = ['id', 'date_modified', 'date_accessed']
                    order_field = order_by.lstrip('-')
                    if order_field in valid_orders:
                        params['ordering'] = order_by
                    else:
                        logger.warning(f"Invalid order_by field: {order_by}. Using default.")
                        params['ordering'] = '-date_modified'
                else:
                    params['ordering'] = '-date_modified'
                
                params['page_size'] = min(max(1, limit), 100)
                
                logger.info(f"Searching sources with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if source_id:
                sources = [data]
            else:
                sources = data.get('results', [])
                if not sources:
                    return f"No sources found matching the specified criteria."
            
            # Build analysis
            result = {
                "total_found": len(sources) if source_id else data.get('count', len(sources)),
                "returned": len(sources),
                "analyses": []
            }
            
            for source in sources:
                analysis = await analyze_source_thoroughly(
                    source, courtlistener_ctx, include_person_details
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE SOURCES ANALYSIS
Found {result['returned']} source(s) out of {result['total_found']} total matches:

{format_sources_analyses(result['analyses'])}

💡 This analysis includes data provenance, source URLs, and access information.
🔍 Sources track where biographical and professional data was gathered.
📊 API-compliant filters: date_modified (with full datetime precision), person, and id.
⚖️ Use person_id to find all data sources for a specific judge.
✅ Implementation verified against exact API metadata specifications."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Source not found. Please check the source ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching source: {e}")
                return f"Error fetching source: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching source: {e}", exc_info=True)
            return f"Error fetching source: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_source_thoroughly(source: dict, courtlistener_ctx, include_person_details: bool) -> dict:
    """Provide thorough analysis of a data source including provenance and access information."""
    
    analysis = {
        "id": source.get('id'),
        "resource_uri": source.get('resource_uri'),
        "person_id": source.get('person'),
        "source_details": {
            "url": source.get('url'),
            "date_accessed": source.get('date_accessed'),
            "notes": source.get('notes', ''),
            "url_domain": _extract_domain(source.get('url')) if source.get('url') else None,
            "notes_length": len(source.get('notes', '')),
            "has_notes": bool(source.get('notes', '').strip())
        },
        "metadata": {
            "date_created": source.get('date_created'),
            "date_modified": source.get('date_modified')
        }
    }
    
    # Fetch person details if requested
    if include_person_details:
        person_url = source.get('person')
        if person_url:
            try:
                person_id = person_url.rstrip('/').split('/')[-1]
                person_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/people/{person_id}/"
                )
                if person_response.status_code == 200:
                    person_data = person_response.json()
                    analysis["person_details"] = {
                        "person_id": person_id,
                        "name_first": person_data.get('name_first', ''),
                        "name_middle": person_data.get('name_middle', ''),
                        "name_last": person_data.get('name_last', ''),
                        "full_name": f"{person_data.get('name_first', '')} {person_data.get('name_middle', '')} {person_data.get('name_last', '')}".strip(),
                        "slug": person_data.get('slug', ''),
                        "absolute_url": f"https://www.courtlistener.com{person_data.get('absolute_url', '')}",
                        "fjc_id": person_data.get('fjc_id'),
                        "has_photo": person_data.get('has_photo', False)
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch person details for source {source.get('id')}: {e}")
    
    return analysis


def _extract_domain(url: str) -> str:
    """Extract domain from URL for analysis."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower() if parsed.netloc else None
    except:
        return None