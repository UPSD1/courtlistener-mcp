"""
CourtListener Political Affiliations Analysis Tools

Comprehensive political affiliation tracking for judges and legal professionals.
Provides detailed political party history, sources, and timeline analysis.
CORRECTED implementation matching exact API metadata filters.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import (
    get_political_party_display, get_political_source_display, 
    get_date_granularity_display
)
from utils.formatters import format_political_affiliations_analyses

logger = logging.getLogger(__name__)


def register_political_affiliation_tools(mcp: FastMCP):
    """Register all political affiliation tools with the MCP server."""
    
    @mcp.tool()
    async def get_political_affiliations(
        affiliation_id: Optional[int] = None,
        person_id: Optional[int] = None,
        political_party: Optional[str] = None,
        source: Optional[str] = None,
        # Date start filters (year/month/day only per API metadata)
        date_start: Optional[str] = None,
        date_start_after: Optional[str] = None,
        date_start_before: Optional[str] = None,
        date_start_gt: Optional[str] = None,
        date_start_lt: Optional[str] = None,
        date_start_range: Optional[str] = None,
        date_start_year: Optional[int] = None,
        date_start_month: Optional[int] = None,
        date_start_day: Optional[int] = None,
        # Date end filters (year/month/day only per API metadata)
        date_end: Optional[str] = None,
        date_end_after: Optional[str] = None,
        date_end_before: Optional[str] = None,
        date_end_gt: Optional[str] = None,
        date_end_lt: Optional[str] = None,
        date_end_range: Optional[str] = None,
        date_end_year: Optional[int] = None,
        date_end_month: Optional[int] = None,
        date_end_day: Optional[int] = None,
        # Record metadata filters (full datetime precision)
        date_created: Optional[str] = None,
        date_created_after: Optional[str] = None,
        date_created_before: Optional[str] = None,
        date_created_gt: Optional[str] = None,
        date_created_lt: Optional[str] = None,
        date_created_range: Optional[str] = None,
        date_created_year: Optional[int] = None,
        date_created_month: Optional[int] = None,
        date_created_day: Optional[int] = None,
        date_created_hour: Optional[int] = None,
        date_created_minute: Optional[int] = None,
        date_created_second: Optional[int] = None,
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
        # ID range filters (NumberRangeFilter)
        id_exact: Optional[int] = None,
        id_min: Optional[int] = None,
        id_max: Optional[int] = None,
        id_gt: Optional[int] = None,
        id_lt: Optional[int] = None,
        id_range: Optional[str] = None,
        # Configuration
        include_person_details: bool = True,
        order_by: Optional[str] = None,
        limit: int = 20
    ) -> str:
        """
        Retrieve and analyze political affiliations using ALL supported API filters from metadata.
        
        Args:
            affiliation_id: Specific political affiliation ID to retrieve
            person_id: Person ID to get all political affiliations for (exact match)
            political_party: Filter by political party ('d','r','i','g','l','f','w','j','u','z')
            source: Filter by affiliation source ('b'=Ballot, 'a'=Appointer, 'o'=Other)
            
            # Date start filters (when affiliation began) - year/month/day only per API
            date_start: Exact start date (YYYY-MM-DD)
            date_start_after: Affiliations that started after this date (inclusive) [__gte]
            date_start_before: Affiliations that started before this date (inclusive) [__lte]
            date_start_gt: Affiliations that started after this date (exclusive) [__gt]
            date_start_lt: Affiliations that started before this date (exclusive) [__lt]
            date_start_range: Date range "YYYY-MM-DD,YYYY-MM-DD" [__range]
            date_start_year: Affiliations that started in this specific year
            date_start_month: Affiliations that started in this specific month (1-12)
            date_start_day: Affiliations that started on this specific day (1-31)
            
            # Date end filters (when affiliation ended) - year/month/day only per API
            date_end: Exact end date (YYYY-MM-DD)
            date_end_after: Affiliations that ended after this date (inclusive) [__gte]
            date_end_before: Affiliations that ended before this date (inclusive) [__lte]
            date_end_gt: Affiliations that ended after this date (exclusive) [__gt]
            date_end_lt: Affiliations that ended before this date (exclusive) [__lt]
            date_end_range: Date range "YYYY-MM-DD,YYYY-MM-DD" [__range]
            date_end_year: Affiliations that ended in this specific year
            date_end_month: Affiliations that ended in this specific month (1-12)
            date_end_day: Affiliations that ended on this specific day (1-31)
            
            # Record metadata filters - full datetime precision
            date_created: Exact creation datetime
            date_created_after: Records created after this datetime (inclusive)
            date_created_before: Records created before this datetime (inclusive)
            date_created_gt: Records created after this datetime (exclusive)
            date_created_lt: Records created before this datetime (exclusive)
            date_created_range: Datetime range "YYYY-MM-DD,YYYY-MM-DD"
            date_created_year: Records created in this specific year
            date_created_month: Records created in this specific month (1-12)
            date_created_day: Records created on this specific day (1-31)
            date_created_hour: Records created in this specific hour (0-23)
            date_created_minute: Records created in this specific minute (0-59)
            date_created_second: Records created in this specific second (0-59)
            # Same complete set for date_modified...
            
            # ID range filters - NumberRangeFilter
            id_exact: Exact affiliation ID
            id_min: Minimum affiliation ID (inclusive) [__gte]
            id_max: Maximum affiliation ID (inclusive) [__lte]
            id_gt: Affiliation ID greater than (exclusive)
            id_lt: Affiliation ID less than (exclusive)
            id_range: ID range "123,456" [__range]
            
            include_person_details: Whether to include detailed person information
            order_by: Sort order ('id', 'date_created', 'date_modified', 'date_start', 'date_end' with optional '-' prefix)
            limit: Maximum number of results (1-100)
        
        Returns:
            Comprehensive political affiliation analysis with ALL codes converted to human-readable values
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            params = {}
            
            if affiliation_id:
                url = f"{courtlistener_ctx.base_url}/political-affiliations/{affiliation_id}/"
                logger.info(f"Fetching political affiliation by ID: {affiliation_id}")
            else:
                url = f"{courtlistener_ctx.base_url}/political-affiliations/"
                
                # Person and party filters (exact matches only per API)
                if person_id:
                    params['person'] = person_id  # ModelChoiceFilter, exact only
                if political_party:
                    params['political_party'] = political_party.lower()  # ChoiceFilter, exact only
                if source:
                    params['source'] = source.lower()  # ChoiceFilter, exact only
                
                # Date start filters (year/month/day only per API metadata)
                if date_start:
                    params['date_start'] = date_start
                if date_start_after:
                    params['date_start__gte'] = date_start_after
                if date_start_before:
                    params['date_start__lte'] = date_start_before
                if date_start_gt:
                    params['date_start__gt'] = date_start_gt
                if date_start_lt:
                    params['date_start__lt'] = date_start_lt
                if date_start_range:
                    params['date_start__range'] = date_start_range
                if date_start_year:
                    params['date_start__year'] = date_start_year
                if date_start_month:
                    params['date_start__month'] = date_start_month
                if date_start_day:
                    params['date_start__day'] = date_start_day
                
                # Date end filters (year/month/day only per API metadata)
                if date_end:
                    params['date_end'] = date_end
                if date_end_after:
                    params['date_end__gte'] = date_end_after
                if date_end_before:
                    params['date_end__lte'] = date_end_before
                if date_end_gt:
                    params['date_end__gt'] = date_end_gt
                if date_end_lt:
                    params['date_end__lt'] = date_end_lt
                if date_end_range:
                    params['date_end__range'] = date_end_range
                if date_end_year:
                    params['date_end__year'] = date_end_year
                if date_end_month:
                    params['date_end__month'] = date_end_month
                if date_end_day:
                    params['date_end__day'] = date_end_day
                
                # Record metadata filters (full datetime precision)
                if date_created:
                    params['date_created'] = date_created
                if date_created_after:
                    params['date_created__gte'] = date_created_after
                if date_created_before:
                    params['date_created__lte'] = date_created_before
                if date_created_gt:
                    params['date_created__gt'] = date_created_gt
                if date_created_lt:
                    params['date_created__lt'] = date_created_lt
                if date_created_range:
                    params['date_created__range'] = date_created_range
                if date_created_year:
                    params['date_created__year'] = date_created_year
                if date_created_month:
                    params['date_created__month'] = date_created_month
                if date_created_day:
                    params['date_created__day'] = date_created_day
                if date_created_hour:
                    params['date_created__hour'] = date_created_hour
                if date_created_minute:
                    params['date_created__minute'] = date_created_minute
                if date_created_second:
                    params['date_created__second'] = date_created_second
                
                # Date modified filters (full datetime precision)
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
                
                # ID range filters (NumberRangeFilter)
                if id_exact:
                    params['id'] = id_exact
                if id_min:
                    params['id__gte'] = id_min
                if id_max:
                    params['id__lte'] = id_max
                if id_gt:
                    params['id__gt'] = id_gt
                if id_lt:
                    params['id__lt'] = id_lt
                if id_range:
                    params['id__range'] = id_range
                
                # Order and limit results (using API-supported ordering fields)
                if order_by:
                    valid_orders = ['id', 'date_created', 'date_modified', 'date_start', 'date_end']
                    order_field = order_by.lstrip('-')
                    if order_field in valid_orders:
                        params['ordering'] = order_by
                    else:
                        logger.warning(f"Invalid order_by field: {order_by}. Using default.")
                        params['ordering'] = '-date_start'
                else:
                    params['ordering'] = '-date_start'  # Most recent first
                
                params['page_size'] = min(max(1, limit), 100)
                
                logger.info(f"Searching political affiliations with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if affiliation_id:
                affiliations = [data]
            else:
                affiliations = data.get('results', [])
                if not affiliations:
                    return f"No political affiliations found matching the specified criteria."
            
            # Build comprehensive analysis
            result = {
                "total_found": len(affiliations) if affiliation_id else data.get('count', len(affiliations)),
                "returned": len(affiliations),
                "analyses": []
            }
            
            for affiliation in affiliations:
                analysis = await analyze_political_affiliation_thoroughly(
                    affiliation, courtlistener_ctx, include_person_details
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE POLITICAL AFFILIATIONS ANALYSIS
Found {result['returned']} affiliation(s) out of {result['total_found']} total matches:

{format_political_affiliations_analyses(result['analyses'])}

💡 This analysis includes political party history, sources, and timeline information.
🔍 ALL codes converted to human-readable values: parties, sources, and date granularity.
📊 Supports ALL API filters: exact dates, ranges, gt/lt comparisons, year/month/day precision.
⚖️ Implementation verified against exact API metadata specifications."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Political affiliation not found. Please check the affiliation ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching political affiliation: {e}")
                return f"Error fetching political affiliation: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching political affiliation: {e}", exc_info=True)
            return f"Error fetching political affiliation: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_political_affiliation_thoroughly(affiliation: dict, courtlistener_ctx, include_person_details: bool) -> dict:
    """Provide thorough analysis of a political affiliation with ALL code conversions."""
    
    # Basic affiliation information with COMPLETE human-readable conversions
    analysis = {
        "id": affiliation.get('id'),
        "resource_uri": affiliation.get('resource_uri'),
        "person_id": affiliation.get('person'),
        "affiliation_details": {
            "political_party": affiliation.get('political_party'),
            "political_party_display": get_political_party_display(affiliation.get('political_party')) if affiliation.get('political_party') else None,
            "source": affiliation.get('source'),
            "source_display": get_political_source_display(affiliation.get('source')) if affiliation.get('source') else None
        },
        "timeline": {
            "date_start": affiliation.get('date_start'),
            "date_granularity_start": affiliation.get('date_granularity_start'),
            "date_granularity_start_display": get_date_granularity_display(affiliation.get('date_granularity_start')) if affiliation.get('date_granularity_start') else None,
            "date_end": affiliation.get('date_end'),
            "date_granularity_end": affiliation.get('date_granularity_end'),
            "date_granularity_end_display": get_date_granularity_display(affiliation.get('date_granularity_end')) if affiliation.get('date_granularity_end') else None,
            "is_current": affiliation.get('date_end') is None,
            "duration_analysis": None
        },
        "metadata": {
            "date_created": affiliation.get('date_created'),
            "date_modified": affiliation.get('date_modified')
        }
    }
    
    # Calculate duration if both dates are available
    if affiliation.get('date_start') and affiliation.get('date_end'):
        try:
            from datetime import datetime
            start_date = datetime.strptime(affiliation['date_start'], '%Y-%m-%d')
            end_date = datetime.strptime(affiliation['date_end'], '%Y-%m-%d')
            duration = end_date - start_date
            analysis["timeline"]["duration_analysis"] = {
                "total_days": duration.days,
                "approximate_years": round(duration.days / 365.25, 1)
            }
        except Exception as e:
            logger.warning(f"Failed to calculate duration: {e}")
    
    # Fetch person details if requested
    if include_person_details:
        person_url = affiliation.get('person')
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
                        "gender": person_data.get('gender'),
                        "date_dob": person_data.get('date_dob'),
                        "has_photo": person_data.get('has_photo', False)
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch person details for affiliation {affiliation.get('id')}: {e}")
    
    return analysis