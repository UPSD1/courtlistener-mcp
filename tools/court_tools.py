"""
CourtListener Court Information Tools

Comprehensive court data retrieval and analysis for understanding the judicial system.
Provides detailed information about federal, state, tribal, and specialty courts.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import get_court_jurisdiction_display
from utils.formatters import format_court_analyses

logger = logging.getLogger(__name__)


def register_court_tools(mcp: FastMCP):
    """Register all court-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_court(
        court_id: Optional[str] = None,
        court_name: Optional[str] = None,
        short_name: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        citation_string: Optional[str] = None,
        in_use: Optional[bool] = None,
        has_opinion_scraper: Optional[bool] = None,
        has_oral_argument_scraper: Optional[bool] = None,
        position_min: Optional[float] = None,
        position_max: Optional[float] = None,
        start_date_after: Optional[str] = None,
        start_date_before: Optional[str] = None,
        end_date_after: Optional[str] = None,
        end_date_before: Optional[str] = None,
        parent_court: Optional[str] = None,
        include_hierarchy: bool = True,
        include_stats: bool = True,
        limit: int = 20
    ) -> str:
        """
        Retrieve comprehensive court information from CourtListener's judicial database.
        
        Args:
            court_id: Specific court ID (e.g., 'scotus', 'ca9', 'dcd')
            court_name: Full court name search (e.g., 'Supreme Court') - uses full_name__icontains
            short_name: Short court name search (e.g., 'SCOTUS') - uses short_name__icontains
            jurisdiction: Court jurisdiction type ('F', 'FD', 'S', 'SA', 'ST', etc.)
            citation_string: Citation abbreviation search (e.g., 'U.S.', 'F.3d') - uses citation_string__icontains
            in_use: Whether court is actively in use in CourtListener
            has_opinion_scraper: Whether court has automated opinion collection
            has_oral_argument_scraper: Whether court has automated oral argument collection
            position_min: Minimum hierarchical position (dewey-decimal style)
            position_max: Maximum hierarchical position (dewey-decimal style)
            start_date_after: Show courts established after this date (YYYY-MM-DD)
            start_date_before: Show courts established before this date (YYYY-MM-DD)
            end_date_after: Show courts that ended after this date (YYYY-MM-DD)
            end_date_before: Show courts that ended before this date (YYYY-MM-DD)
            parent_court: Parent court ID for court subdivisions
            include_hierarchy: Whether to include parent/child court relationships
            include_stats: Whether to include court activity statistics
            limit: Maximum number of results (1-100)
        
        Returns:
            Comprehensive court information including jurisdiction, hierarchy, and activity data with all codes converted to human-readable values
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters with API-compliant filter names
            params = {}
            
            if court_id:
                # Direct court lookup by ID
                url = f"{courtlistener_ctx.base_url}/courts/{court_id}/"
                logger.info(f"Fetching court by ID: {court_id}")
            else:
                # Build filtered search with correct API filter names
                url = f"{courtlistener_ctx.base_url}/courts/"
                
                # Text search filters (using correct API filter names)
                if court_name:
                    params['full_name__icontains'] = court_name
                if short_name:
                    params['short_name__icontains'] = short_name
                if citation_string:
                    params['citation_string__icontains'] = citation_string
                
                # Exact match filters
                if jurisdiction:
                    params['jurisdiction'] = jurisdiction.upper()
                if parent_court:
                    params['parent_court'] = parent_court
                
                # Boolean filters
                if in_use is not None:
                    params['in_use'] = in_use
                if has_opinion_scraper is not None:
                    params['has_opinion_scraper'] = has_opinion_scraper
                if has_oral_argument_scraper is not None:
                    params['has_oral_argument_scraper'] = has_oral_argument_scraper
                
                # Position range filters
                if position_min is not None:
                    params['position__gte'] = position_min
                if position_max is not None:
                    params['position__lte'] = position_max
                
                # Date range filters
                if start_date_after:
                    params['start_date__gte'] = start_date_after
                if start_date_before:
                    params['start_date__lte'] = start_date_before
                if end_date_after:
                    params['end_date__gte'] = end_date_after
                if end_date_before:
                    params['end_date__lte'] = end_date_before
                
                # Order and limit results
                params['ordering'] = 'position'  # Hierarchical order
                params['page_size'] = min(max(1, limit), 100)
                
                logger.info(f"Searching courts with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if court_id:
                # Single court response
                courts = [data]
            else:
                # Paginated response
                courts = data.get('results', [])
                if not courts:
                    return f"No courts found matching the specified criteria."
            
            # Build comprehensive analysis
            result = {
                "total_found": len(courts) if court_id else data.get('count', len(courts)),
                "returned": len(courts),
                "analyses": []
            }
            
            for court in courts:
                # Get comprehensive court analysis
                analysis = await analyze_court_thoroughly(
                    court, courtlistener_ctx, include_hierarchy, include_stats
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE COURT ANALYSIS
Found {result['returned']} court(s) out of {result['total_found']} total matches:

{format_court_analyses(result['analyses'])}

💡 This analysis includes court hierarchy, jurisdiction details, and activity statistics.
🔍 All jurisdiction codes converted to human-readable values."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Court not found. Please check the court ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching court: {e}")
                return f"Error fetching court: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching court: {e}", exc_info=True)
            return f"Error fetching court: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_court_thoroughly(court: dict, courtlistener_ctx, include_hierarchy: bool, include_stats: bool) -> dict:
    """Provide thorough analysis of a court including hierarchy and activity statistics."""
    
    # Basic court information with human-readable jurisdiction conversion
    analysis = {
        "id": court.get('id'),
        "identification": {
            "short_name": court.get('short_name', ''),
            "full_name": court.get('full_name', ''),
            "citation_string": court.get('citation_string', ''),
            "url": court.get('url', '')
        },
        "jurisdiction_info": {
            "jurisdiction": court.get('jurisdiction'),
            "jurisdiction_display": get_court_jurisdiction_display(court.get('jurisdiction', '')),
            "position": court.get('position')  # Hierarchical position
        },
        "operational_dates": {
            "start_date": court.get('start_date'),
            "end_date": court.get('end_date'),
            "date_modified": court.get('date_modified')
        },
        "activity_status": {
            "in_use": court.get('in_use', False),
            "has_opinion_scraper": court.get('has_opinion_scraper', False),
            "has_oral_argument_scraper": court.get('has_oral_argument_scraper', False)
        },
        "federal_integration": {
            "pacer_court_id": court.get('pacer_court_id'),
            "pacer_has_rss_feed": court.get('pacer_has_rss_feed'),
            "pacer_rss_entry_types": court.get('pacer_rss_entry_types', ''),
            "date_last_pacer_contact": court.get('date_last_pacer_contact'),
            "fjc_court_id": court.get('fjc_court_id', '')
        }
    }
    
    # Determine court type and level based on jurisdiction
    jurisdiction = court.get('jurisdiction', '')
    court_type_info = _analyze_court_type(jurisdiction)
    analysis["court_classification"] = court_type_info
    
    # Fetch hierarchy information if requested
    if include_hierarchy:
        hierarchy_info = await _fetch_court_hierarchy(court, courtlistener_ctx)
        if hierarchy_info:
            analysis["hierarchy"] = hierarchy_info
    
    # Fetch activity statistics if requested
    if include_stats:
        stats_info = await _fetch_court_statistics(court, courtlistener_ctx)
        if stats_info:
            analysis["activity_statistics"] = stats_info
    
    return analysis


def _analyze_court_type(jurisdiction: str) -> dict:
    """Analyze court type and provide classification details with enhanced mapping."""
    court_type_info = {
        "jurisdiction_code": jurisdiction,
        "court_system": "Unknown",
        "court_level": "Unknown", 
        "court_type": "Unknown"
    }
    
    if not jurisdiction:
        return court_type_info
    
    # Determine court system
    if jurisdiction.startswith('F'):
        court_type_info["court_system"] = "Federal"
    elif jurisdiction.startswith('S'):
        court_type_info["court_system"] = "State"
    elif jurisdiction.startswith('TR'):
        court_type_info["court_system"] = "Tribal"
    elif jurisdiction.startswith('T') and not jurisdiction.startswith('TR'):
        court_type_info["court_system"] = "Territory"
    elif jurisdiction.startswith('M'):
        court_type_info["court_system"] = "Military"
    elif jurisdiction == 'SAG':
        court_type_info["court_system"] = "State Attorney General"
    elif jurisdiction in ['C', 'I']:
        court_type_info["court_system"] = "Special"
    
    # Determine court level
    if jurisdiction in ['F', 'S', 'TRS', 'TS']:
        court_type_info["court_level"] = "Supreme/Appellate"
    elif jurisdiction in ['SA', 'TRA', 'TA', 'MA']:
        court_type_info["court_level"] = "Appellate"
    elif jurisdiction in ['FD', 'ST', 'TRT', 'TT', 'MT']:
        court_type_info["court_level"] = "Trial"
    elif jurisdiction in ['FB', 'FBP']:
        court_type_info["court_level"] = "Bankruptcy"
    elif jurisdiction in ['FS', 'SS', 'TRX', 'TSP']:
        court_type_info["court_level"] = "Special"
    
    # Determine specific court type (using complete API mapping)
    type_mapping = {
        'F': 'Federal Appellate',
        'FD': 'Federal District',
        'FB': 'Federal Bankruptcy',
        'FBP': 'Federal Bankruptcy Panel',
        'FS': 'Federal Special',
        'S': 'State Supreme',
        'SA': 'State Appellate', 
        'ST': 'State Trial',
        'SS': 'State Special',
        'TRS': 'Tribal Supreme',
        'TRA': 'Tribal Appellate',
        'TRT': 'Tribal Trial',
        'TRX': 'Tribal Special',
        'TS': 'Territory Supreme',
        'TA': 'Territory Appellate',
        'TT': 'Territory Trial',
        'TSP': 'Territory Special',
        'SAG': 'State Attorney General',
        'MA': 'Military Appellate',
        'MT': 'Military Trial',
        'C': 'Committee',
        'I': 'International',
        'T': 'Testing'
    }
    
    court_type_info["court_type"] = type_mapping.get(jurisdiction, f"Unknown ({jurisdiction})")
    
    return court_type_info


async def _fetch_court_hierarchy(court: dict, courtlistener_ctx) -> dict:
    """Fetch parent and child court relationships."""
    hierarchy = {
        "parent_courts": [],
        "child_courts": [],
        "appeals_to": []
    }
    
    try:
        # Fetch parent court if exists
        parent_court_id = court.get('parent_court')
        if parent_court_id:
            parent_response = await courtlistener_ctx.http_client.get(
                f"{courtlistener_ctx.base_url}/courts/{parent_court_id}/"
            )
            if parent_response.status_code == 200:
                parent_data = parent_response.json()
                hierarchy["parent_courts"].append({
                    "id": parent_data.get('id'),
                    "name": parent_data.get('full_name'),
                    "jurisdiction": parent_data.get('jurisdiction'),
                    "jurisdiction_display": get_court_jurisdiction_display(parent_data.get('jurisdiction', ''))
                })
        
        # Fetch appeals destination courts
        appeals_to = court.get('appeals_to', [])
        for appeal_court_url in appeals_to:
            try:
                appeal_court_id = appeal_court_url.rstrip('/').split('/')[-1]
                appeal_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/courts/{appeal_court_id}/"
                )
                if appeal_response.status_code == 200:
                    appeal_data = appeal_response.json()
                    hierarchy["appeals_to"].append({
                        "id": appeal_data.get('id'),
                        "name": appeal_data.get('full_name'),
                        "jurisdiction": appeal_data.get('jurisdiction'),
                        "jurisdiction_display": get_court_jurisdiction_display(appeal_data.get('jurisdiction', ''))
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch appeals court {appeal_court_url}: {e}")
    
    except Exception as e:
        logger.warning(f"Failed to fetch hierarchy for court {court.get('id')}: {e}")
    
    return hierarchy if any(hierarchy.values()) else None


async def _fetch_court_statistics(court: dict, courtlistener_ctx) -> dict:
    """Fetch basic activity statistics for the court."""
    stats = {
        "docket_count": 0,
        "opinion_cluster_count": 0,
        "recent_activity": False
    }
    
    try:
        court_id = court.get('id')
        if not court_id:
            return None
        
        # Get count of dockets for this court
        docket_response = await courtlistener_ctx.http_client.get(
            f"{courtlistener_ctx.base_url}/dockets/",
            params={'court': court_id, 'page_size': 1}
        )
        if docket_response.status_code == 200:
            docket_data = docket_response.json()
            stats["docket_count"] = docket_data.get('count', 0)
        
        # Get count of opinion clusters for this court
        cluster_response = await courtlistener_ctx.http_client.get(
            f"{courtlistener_ctx.base_url}/clusters/",
            params={'docket__court': court_id, 'page_size': 1}
        )
        if cluster_response.status_code == 200:
            cluster_data = cluster_response.json()
            stats["opinion_cluster_count"] = cluster_data.get('count', 0)
        
        # Check for recent activity (dockets filed in last year)
        from datetime import datetime, timedelta
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        recent_response = await courtlistener_ctx.http_client.get(
            f"{courtlistener_ctx.base_url}/dockets/",
            params={'court': court_id, 'date_filed__gte': one_year_ago, 'page_size': 1}
        )
        if recent_response.status_code == 200:
            recent_data = recent_response.json()
            stats["recent_activity"] = recent_data.get('count', 0) > 0
    
    except Exception as e:
        logger.warning(f"Failed to fetch statistics for court {court.get('id')}: {e}")
        return None
    
    return stats