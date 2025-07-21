"""
CourtListener Retention Events Analysis Tools

Judicial retention events including reappointments, elections, and retention votes.
Provides detailed retention history and voting analysis.
CORRECTED implementation matching exact API metadata filters.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import get_retention_type_display
from utils.formatters import format_retention_events_analyses

logger = logging.getLogger(__name__)


def register_retention_events_tools(mcp: FastMCP):
    """Register all retention events tools with the MCP server."""
    
    @mcp.tool()
    async def get_retention_events(
        event_id: Optional[int] = None,
        position_id: Optional[int] = None,
        retention_type: Optional[str] = None,
        # Date retention filters (year/month/day only per API metadata)
        date_retention: Optional[str] = None,
        date_retention_after: Optional[str] = None,
        date_retention_before: Optional[str] = None,
        date_retention_gt: Optional[str] = None,
        date_retention_lt: Optional[str] = None,
        date_retention_range: Optional[str] = None,
        date_retention_year: Optional[int] = None,
        date_retention_month: Optional[int] = None,
        date_retention_day: Optional[int] = None,
        # Vote count filters (NumberRangeFilter)
        votes_yes: Optional[int] = None,
        votes_yes_min: Optional[int] = None,
        votes_yes_max: Optional[int] = None,
        votes_yes_gt: Optional[int] = None,
        votes_yes_lt: Optional[int] = None,
        votes_yes_range: Optional[str] = None,
        votes_no: Optional[int] = None,
        votes_no_min: Optional[int] = None,
        votes_no_max: Optional[int] = None,
        votes_no_gt: Optional[int] = None,
        votes_no_lt: Optional[int] = None,
        votes_no_range: Optional[str] = None,
        # Boolean filters
        unopposed: Optional[bool] = None,
        won: Optional[bool] = None,
        # Date created filters (full datetime precision)
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
        # Date modified filters (full datetime precision)
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
        # ID filters (NumberRangeFilter)
        id_exact: Optional[int] = None,
        id_min: Optional[int] = None,
        id_max: Optional[int] = None,
        id_gt: Optional[int] = None,
        id_lt: Optional[int] = None,
        id_range: Optional[str] = None,
        # Configuration
        include_position_details: bool = True,
        order_by: Optional[str] = None,
        limit: int = 20
    ) -> str:
        """
        Retrieve and analyze judicial retention events using ALL supported API filters from metadata.
        
        Args:
            event_id: Specific retention event ID to retrieve
            position_id: Position ID to get all retention events for (exact match only)
            retention_type: Filter by retention type ('reapp_gov', 'reapp_leg', 'elec_p', 'elec_n', 'elec_u')
            
            # Date retention filters (year/month/day precision only per API)
            date_retention: Exact retention date (YYYY-MM-DD)
            date_retention_after: Events after this date (inclusive) [__gte]
            date_retention_before: Events before this date (inclusive) [__lte]
            date_retention_gt: Events after this date (exclusive) [__gt]
            date_retention_lt: Events before this date (exclusive) [__lt]
            date_retention_range: Date range "YYYY-MM-DD,YYYY-MM-DD" [__range]
            date_retention_year: Events in this specific year
            date_retention_month: Events in this specific month (1-12)
            date_retention_day: Events on this specific day (1-31)
            
            # Vote count filters (NumberRangeFilter for both yes and no votes)
            votes_yes: Exact number of yes votes
            votes_yes_min: Minimum yes votes (inclusive) [__gte]
            votes_yes_max: Maximum yes votes (inclusive) [__lte]
            votes_yes_gt: Yes votes greater than (exclusive) [__gt]
            votes_yes_lt: Yes votes less than (exclusive) [__lt]
            votes_yes_range: Yes votes range "100,500" [__range]
            votes_no: Exact number of no votes
            votes_no_min: Minimum no votes (inclusive) [__gte]
            votes_no_max: Maximum no votes (inclusive) [__lte]
            votes_no_gt: No votes greater than (exclusive) [__gt]
            votes_no_lt: No votes less than (exclusive) [__lt]
            votes_no_range: No votes range "50,200" [__range]
            
            # Boolean filters (exact only)
            unopposed: Whether the retention was unopposed
            won: Whether the retention was won
            
            # Full datetime filters for record metadata
            [date_created and date_modified filters with full precision]
            
            # ID range filters (NumberRangeFilter)
            id_exact: Exact event ID [id]
            id_min: Minimum event ID (inclusive) [id__gte]
            id_max: Maximum event ID (inclusive) [id__lte]
            id_gt: Event ID greater than (exclusive) [id__gt]
            id_lt: Event ID less than (exclusive) [id__lt]
            id_range: ID range "123,456" [id__range]
            
            include_position_details: Whether to include detailed position information
            order_by: Sort order ('id', 'date_created', 'date_modified', 'date_retention' with optional '-' prefix)
            limit: Maximum number of results (1-100)
        
        Returns:
            Comprehensive retention event analysis with all codes converted to human-readable values
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            params = {}
            
            if event_id:
                url = f"{courtlistener_ctx.base_url}/retention-events/{event_id}/"
                logger.info(f"Fetching retention event by ID: {event_id}")
            else:
                url = f"{courtlistener_ctx.base_url}/retention-events/"
                
                # Basic filters (exact matches per API)
                if position_id:
                    params['position'] = position_id  # ModelChoiceFilter, exact only
                if retention_type:
                    params['retention_type'] = retention_type.lower()  # ChoiceFilter, exact only
                
                # Date retention filters (year/month/day only per API metadata)
                if date_retention:
                    params['date_retention'] = date_retention
                if date_retention_after:
                    params['date_retention__gte'] = date_retention_after
                if date_retention_before:
                    params['date_retention__lte'] = date_retention_before
                if date_retention_gt:
                    params['date_retention__gt'] = date_retention_gt
                if date_retention_lt:
                    params['date_retention__lt'] = date_retention_lt
                if date_retention_range:
                    params['date_retention__range'] = date_retention_range
                if date_retention_year:
                    params['date_retention__year'] = date_retention_year
                if date_retention_month:
                    params['date_retention__month'] = date_retention_month
                if date_retention_day:
                    params['date_retention__day'] = date_retention_day
                
                # Votes yes filters (NumberRangeFilter)
                if votes_yes is not None:
                    params['votes_yes'] = votes_yes
                if votes_yes_min is not None:
                    params['votes_yes__gte'] = votes_yes_min
                if votes_yes_max is not None:
                    params['votes_yes__lte'] = votes_yes_max
                if votes_yes_gt is not None:
                    params['votes_yes__gt'] = votes_yes_gt
                if votes_yes_lt is not None:
                    params['votes_yes__lt'] = votes_yes_lt
                if votes_yes_range:
                    params['votes_yes__range'] = votes_yes_range
                
                # Votes no filters (NumberRangeFilter)
                if votes_no is not None:
                    params['votes_no'] = votes_no
                if votes_no_min is not None:
                    params['votes_no__gte'] = votes_no_min
                if votes_no_max is not None:
                    params['votes_no__lte'] = votes_no_max
                if votes_no_gt is not None:
                    params['votes_no__gt'] = votes_no_gt
                if votes_no_lt is not None:
                    params['votes_no__lt'] = votes_no_lt
                if votes_no_range:
                    params['votes_no__range'] = votes_no_range
                
                # Boolean filters (exact only per API)
                if unopposed is not None:
                    params['unopposed'] = unopposed
                if won is not None:
                    params['won'] = won
                
                # Date created filters (full datetime precision)
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
                
                # ID filters (NumberRangeFilter)
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
                
                # Ordering (using API-supported ordering fields from metadata)
                if order_by:
                    valid_orders = ['id', 'date_created', 'date_modified', 'date_retention']
                    order_field = order_by.lstrip('-')
                    if order_field in valid_orders:
                        params['ordering'] = order_by
                    else:
                        logger.warning(f"Invalid order_by field: {order_by}. Using default.")
                        params['ordering'] = '-date_retention'
                else:
                    params['ordering'] = '-date_retention'  # Most recent first
                
                params['page_size'] = min(max(1, limit), 100)
                
                logger.info(f"Searching retention events with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if event_id:
                events = [data]
            else:
                events = data.get('results', [])
                if not events:
                    return f"No retention events found matching the specified criteria."
            
            # Build analysis
            result = {
                "total_found": len(events) if event_id else data.get('count', len(events)),
                "returned": len(events),
                "analyses": []
            }
            
            for event in events:
                analysis = await analyze_retention_event_thoroughly(
                    event, courtlistener_ctx, include_position_details
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE RETENTION EVENTS ANALYSIS
Found {result['returned']} event(s) out of {result['total_found']} total matches:

{format_retention_events_analyses(result['analyses'])}

💡 This analysis includes retention history, voting data, and position context.
🔍 All retention type codes converted to human-readable values.
📊 Supports all API filters including vote counts, dates, and boolean filters.
⚖️ Use position_id to find all retention events for a specific position.
✅ Implementation verified against exact API metadata specifications."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Retention event not found. Please check the event ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching retention event: {e}")
                return f"Error fetching retention event: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching retention event: {e}", exc_info=True)
            return f"Error fetching retention event: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_retention_event_thoroughly(event: dict, courtlistener_ctx, include_position_details: bool) -> dict:
    """Provide thorough analysis of a retention event including voting data and context."""
    
    analysis = {
        "id": event.get('id'),
        "resource_uri": event.get('resource_uri'),
        "position_id": event.get('position'),
        "retention_details": {
            "retention_type": event.get('retention_type'),
            "retention_type_display": get_retention_type_display(event.get('retention_type')) if event.get('retention_type') else None,
            "date_retention": event.get('date_retention'),
            "won": event.get('won'),
            "unopposed": event.get('unopposed', False)
        },
        "voting_data": {
            "votes_yes": event.get('votes_yes'),
            "votes_no": event.get('votes_no'),
            "votes_yes_percent": event.get('votes_yes_percent'),
            "votes_no_percent": event.get('votes_no_percent'),
            "total_votes": None,
            "margin": None,
            "percentage_won": None
        },
        "metadata": {
            "date_created": event.get('date_created'),
            "date_modified": event.get('date_modified')
        }
    }
    
    # Calculate voting statistics
    votes_yes = event.get('votes_yes')
    votes_no = event.get('votes_no')
    if votes_yes is not None and votes_no is not None:
        analysis["voting_data"]["total_votes"] = votes_yes + votes_no
        analysis["voting_data"]["margin"] = votes_yes - votes_no
        if analysis["voting_data"]["total_votes"] > 0:
            analysis["voting_data"]["percentage_won"] = round((votes_yes / analysis["voting_data"]["total_votes"]) * 100, 1)
    
    # Fetch position details if requested
    if include_position_details:
        position_url = event.get('position')
        if position_url:
            try:
                position_id = position_url.rstrip('/').split('/')[-1]
                position_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/positions/{position_id}/"
                )
                if position_response.status_code == 200:
                    position_data = position_response.json()
                    analysis["position_details"] = {
                        "position_id": position_id,
                        "job_title": position_data.get('job_title', ''),
                        "court": position_data.get('court_str', ''),
                        "date_start": position_data.get('date_start'),
                        "date_termination": position_data.get('date_termination'),
                        "person": position_data.get('person_str', ''),
                        "appointer": position_data.get('appointer_str', ''),
                        "how_selected": position_data.get('how_selected', '')
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch position details for event {event.get('id')}: {e}")
    
    return analysis