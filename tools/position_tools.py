"""
CourtListener Position Analysis Tools

Judicial and professional position tracking for judges and legal professionals.
Provides detailed position history, appointment processes, and career timeline analysis.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import (
    get_position_type_display, get_how_selected_display, get_termination_reason_display,
    get_nomination_process_display, get_vote_type_display, get_date_granularity_display
)
from utils.formatters import format_position_analyses

logger = logging.getLogger(__name__)


def register_position_tools(mcp: FastMCP):
    """Register all position-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_positions(
        position_id: Optional[int] = None,
        person_id: Optional[int] = None,
        court_id: Optional[str] = None,
        position_type: Optional[str] = None,
        job_title: Optional[str] = None,
        organization_name: Optional[str] = None,
        location_city: Optional[str] = None,
        location_state: Optional[str] = None,
        # Date filters for key position dates
        date_start_after: Optional[str] = None,
        date_start_before: Optional[str] = None,
        date_termination_after: Optional[str] = None,
        date_termination_before: Optional[str] = None,
        date_nominated_after: Optional[str] = None,
        date_nominated_before: Optional[str] = None,
        date_confirmation_after: Optional[str] = None,
        date_confirmation_before: Optional[str] = None,
        # Selection and appointment filters
        how_selected: Optional[str] = None,
        appointer_id: Optional[int] = None,
        termination_reason: Optional[str] = None,
        # Vote information filters
        votes_yes_min: Optional[int] = None,
        votes_yes_max: Optional[int] = None,
        votes_no_min: Optional[int] = None,
        votes_no_max: Optional[int] = None,
        voice_vote: Optional[bool] = None,
        # Configuration options
        include_person_details: bool = True,
        include_court_details: bool = True,
        include_appointer_details: bool = True,
        include_retention_events: bool = True,
        order_by: Optional[str] = None,
        limit: int = 20
    ) -> str:
        """
        Retrieve and analyze judicial and professional positions from CourtListener's database.
        
        Args:
            position_id: Specific position ID to retrieve
            person_id: Person ID to get all positions for (exact match)
            court_id: Court identifier to filter positions by court
            position_type: Type of position (e.g., 'jud', 'chief', 'pres', etc.)
            job_title: Job title filter (partial match)
            organization_name: Organization name filter (partial match)
            location_city: City where position is located
            location_state: State where position is located (US state codes)
            
            # Date range filters for position timeline
            date_start_after: Positions starting after this date (YYYY-MM-DD)
            date_start_before: Positions starting before this date (YYYY-MM-DD)
            date_termination_after: Positions ending after this date (YYYY-MM-DD)
            date_termination_before: Positions ending before this date (YYYY-MM-DD)
            date_nominated_after: Positions nominated after this date (YYYY-MM-DD)
            date_nominated_before: Positions nominated before this date (YYYY-MM-DD)
            date_confirmation_after: Positions confirmed after this date (YYYY-MM-DD)
            date_confirmation_before: Positions confirmed before this date (YYYY-MM-DD)
            
            # Selection and appointment process filters
            how_selected: Method of selection/appointment
            appointer_id: Person ID of the appointer (for appointed positions)
            termination_reason: Reason for position termination
            
            # Vote information filters (for confirmed positions)
            votes_yes_min: Minimum yes votes received
            votes_yes_max: Maximum yes votes received
            votes_no_min: Minimum no votes received
            votes_no_max: Maximum no votes received
            voice_vote: Whether confirmation was by voice vote
            
            include_person_details: Whether to include detailed person information
            include_court_details: Whether to include detailed court information
            include_appointer_details: Whether to include appointer information
            include_retention_events: Whether to include retention event history
            order_by: Sort order ('id', 'date_start', 'date_nominated' with optional '-' prefix)
            limit: Maximum number of results (1-100)
        
        Returns:
            Comprehensive position analysis including appointment process, timeline, and career context
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters
            params = {}
            
            if position_id:
                # Direct position lookup by ID
                url = f"{courtlistener_ctx.base_url}/positions/{position_id}/"
                logger.info(f"Fetching position by ID: {position_id}")
            else:
                # Build filtered search
                url = f"{courtlistener_ctx.base_url}/positions/"
                
                # Basic filters
                if person_id:
                    params['person'] = person_id
                if court_id:
                    params['court'] = court_id
                if position_type:
                    params['position_type'] = position_type
                if how_selected:
                    params['how_selected'] = how_selected
                if appointer_id:
                    params['appointer'] = appointer_id
                if termination_reason:
                    params['termination_reason'] = termination_reason
                
                # Text search filters
                if job_title:
                    params['job_title__icontains'] = job_title
                if organization_name:
                    params['organization_name__icontains'] = organization_name
                if location_city:
                    params['location_city__icontains'] = location_city
                if location_state:
                    params['location_state'] = location_state
                
                # Date range filters
                if date_start_after:
                    params['date_start__gte'] = date_start_after
                if date_start_before:
                    params['date_start__lte'] = date_start_before
                if date_termination_after:
                    params['date_termination__gte'] = date_termination_after
                if date_termination_before:
                    params['date_termination__lte'] = date_termination_before
                if date_nominated_after:
                    params['date_nominated__gte'] = date_nominated_after
                if date_nominated_before:
                    params['date_nominated__lte'] = date_nominated_before
                if date_confirmation_after:
                    params['date_confirmation__gte'] = date_confirmation_after
                if date_confirmation_before:
                    params['date_confirmation__lte'] = date_confirmation_before
                
                # Vote count filters
                if votes_yes_min is not None:
                    params['votes_yes__gte'] = votes_yes_min
                if votes_yes_max is not None:
                    params['votes_yes__lte'] = votes_yes_max
                if votes_no_min is not None:
                    params['votes_no__gte'] = votes_no_min
                if votes_no_max is not None:
                    params['votes_no__lte'] = votes_no_max
                if voice_vote is not None:
                    params['voice_vote'] = voice_vote
                
                # Order and limit results
                if order_by:
                    valid_orders = ['id', 'date_start', 'date_nominated', 'date_confirmation', 'date_termination']
                    order_field = order_by.lstrip('-')
                    if order_field in valid_orders:
                        params['ordering'] = order_by
                    else:
                        logger.warning(f"Invalid order_by field: {order_by}. Using default.")
                        params['ordering'] = '-date_start'
                else:
                    params['ordering'] = '-date_start'  # Most recent first
                
                params['page_size'] = min(max(1, limit), 100)
                
                logger.info(f"Searching positions with filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if position_id:
                # Single position response
                positions = [data]
            else:
                # Paginated response
                positions = data.get('results', [])
                if not positions:
                    return f"No positions found matching the specified criteria."
            
            # Build comprehensive analysis
            result = {
                "total_found": len(positions) if position_id else data.get('count', len(positions)),
                "returned": len(positions),
                "analyses": []
            }
            
            for position in positions:
                # Get comprehensive position analysis
                analysis = await analyze_position_thoroughly(
                    position, courtlistener_ctx, include_person_details, 
                    include_court_details, include_appointer_details, include_retention_events
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE POSITION ANALYSIS
Found {result['returned']} position(s) out of {result['total_found']} total matches:

{format_position_analyses(result['analyses'])}

💡 This analysis includes appointment processes, career timelines, and confirmation details.
🔍 All position codes converted to human-readable values (position types, selection methods, etc.).
⚖️ Timeline includes nomination, confirmation, service, and termination phases."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Position not found. Please check the position ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching position: {e}")
                return f"Error fetching position: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching position: {e}", exc_info=True)
            return f"Error fetching position: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_position_thoroughly(position: dict, courtlistener_ctx, include_person_details: bool, 
                                    include_court_details: bool, include_appointer_details: bool, 
                                    include_retention_events: bool) -> dict:
    """Provide thorough analysis of a position including appointment process and career context."""
    
    # Basic position information with human-readable conversions
    analysis = {
        "id": position.get('id'),
        "resource_uri": position.get('resource_uri'),
        "person_id": position.get('person'),
        "position_details": {
            "position_type": position.get('position_type'),
            "position_type_display": get_position_type_display(position.get('position_type')) if position.get('position_type') else None,
            "job_title": position.get('job_title', ''),
            "sector": position.get('sector'),
            "organization_name": position.get('organization_name', ''),
            "court": position.get('court'),
            "school": position.get('school')
        },
        "location": {
            "city": position.get('location_city', ''),
            "state": position.get('location_state', '')
        },
        "appointment_process": {
            "how_selected": position.get('how_selected'),
            "how_selected_display": get_how_selected_display(position.get('how_selected')) if position.get('how_selected') else None,
            "appointer": position.get('appointer'),
            "supervisor": position.get('supervisor'),
            "predecessor": position.get('predecessor'),
            "nomination_process": position.get('nomination_process', ''),
            "nomination_process_display": get_nomination_process_display(position.get('nomination_process')) if position.get('nomination_process') else None
        },
        "timeline": {
            "date_nominated": position.get('date_nominated'),
            "date_elected": position.get('date_elected'),
            "date_recess_appointment": position.get('date_recess_appointment'),
            "date_referred_to_judicial_committee": position.get('date_referred_to_judicial_committee'),
            "date_judicial_committee_action": position.get('date_judicial_committee_action'),
            "judicial_committee_action": position.get('judicial_committee_action', ''),
            "date_hearing": position.get('date_hearing'),
            "date_confirmation": position.get('date_confirmation'),
            "date_start": position.get('date_start'),
            "date_granularity_start": position.get('date_granularity_start'),
            "date_granularity_start_display": get_date_granularity_display(position.get('date_granularity_start')) if position.get('date_granularity_start') else None,
            "date_termination": position.get('date_termination'),
            "date_granularity_termination": position.get('date_granularity_termination'),
            "date_granularity_termination_display": get_date_granularity_display(position.get('date_granularity_termination')) if position.get('date_granularity_termination') else None,
            "date_retirement": position.get('date_retirement'),
            "termination_reason": position.get('termination_reason'),
            "termination_reason_display": get_termination_reason_display(position.get('termination_reason')) if position.get('termination_reason') else None,
            "is_current": position.get('date_termination') is None
        },
        "confirmation_details": {
            "vote_type": position.get('vote_type'),
            "vote_type_display": get_vote_type_display(position.get('vote_type')) if position.get('vote_type') else None,
            "voice_vote": position.get('voice_vote'),
            "votes_yes": position.get('votes_yes'),
            "votes_no": position.get('votes_no'),
            "votes_yes_percent": position.get('votes_yes_percent'),
            "votes_no_percent": position.get('votes_no_percent'),
            "vote_analysis": None
        },
        "metadata": {
            "date_created": position.get('date_created'),
            "date_modified": position.get('date_modified'),
            "has_inferred_values": position.get('has_inferred_values', False)
        }
    }
    
    # Calculate vote analysis if vote data is available
    votes_yes = position.get('votes_yes')
    votes_no = position.get('votes_no')
    if votes_yes is not None and votes_no is not None:
        total_votes = votes_yes + votes_no
        margin = votes_yes - votes_no
        if total_votes > 0:
            percentage = round((votes_yes / total_votes) * 100, 1)
            analysis["confirmation_details"]["vote_analysis"] = {
                "total_votes": total_votes,
                "margin": margin,
                "percentage_approved": percentage,
                "was_close": margin <= 5,  # Close vote if margin <= 5
                "was_unanimous": votes_no == 0
            }
    
    # Calculate service duration if dates are available
    if position.get('date_start'):
        from datetime import datetime
        try:
            start_date = datetime.strptime(position['date_start'], '%Y-%m-%d')
            if position.get('date_termination'):
                end_date = datetime.strptime(position['date_termination'], '%Y-%m-%d')
                duration = end_date - start_date
                analysis["timeline"]["service_duration"] = {
                    "days": duration.days,
                    "years": round(duration.days / 365.25, 1)
                }
            else:
                # Current position - calculate from start to now
                current_date = datetime.now()
                duration = current_date - start_date
                analysis["timeline"]["current_service_duration"] = {
                    "days": duration.days,
                    "years": round(duration.days / 365.25, 1)
                }
        except ValueError as e:
            logger.warning(f"Failed to parse dates for position {position.get('id')}: {e}")
    
    # Fetch nested person details if requested
    if include_person_details:
        person_data = position.get('person')
        if isinstance(person_data, dict):
            # Person data is already nested in the response
            analysis["person_details"] = {
                "person_id": person_data.get('id'),
                "name_first": person_data.get('name_first', ''),
                "name_middle": person_data.get('name_middle', ''),
                "name_last": person_data.get('name_last', ''),
                "full_name": f"{person_data.get('name_first', '')} {person_data.get('name_middle', '')} {person_data.get('name_last', '')}".strip(),
                "slug": person_data.get('slug', ''),
                "date_dob": person_data.get('date_dob'),
                "gender": person_data.get('gender'),
                "race": person_data.get('race', []),
                "fjc_id": person_data.get('fjc_id'),
                "has_photo": person_data.get('has_photo', False)
            }
        elif isinstance(person_data, str) and person_data.startswith('https://'):
            # Person data is a URL reference - fetch it
            try:
                person_id = person_data.rstrip('/').split('/')[-1]
                person_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/people/{person_id}/"
                )
                if person_response.status_code == 200:
                    person_info = person_response.json()
                    analysis["person_details"] = {
                        "person_id": person_id,
                        "name_first": person_info.get('name_first', ''),
                        "name_middle": person_info.get('name_middle', ''),
                        "name_last": person_info.get('name_last', ''),
                        "full_name": f"{person_info.get('name_first', '')} {person_info.get('name_middle', '')} {person_info.get('name_last', '')}".strip(),
                        "slug": person_info.get('slug', ''),
                        "date_dob": person_info.get('date_dob'),
                        "gender": person_info.get('gender'),
                        "race": person_info.get('race', []),
                        "fjc_id": person_info.get('fjc_id'),
                        "has_photo": person_info.get('has_photo', False)
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch person details for position {position.get('id')}: {e}")
    
    # Fetch court details if requested
    if include_court_details and position.get('court'):
        try:
            court_url = position['court']
            if court_url.startswith('https://'):
                court_id = court_url.rstrip('/').split('/')[-1]
                court_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/courts/{court_id}/"
                )
                if court_response.status_code == 200:
                    court_data = court_response.json()
                    analysis["court_details"] = {
                        "court_id": court_id,
                        "short_name": court_data.get('short_name', ''),
                        "full_name": court_data.get('full_name', ''),
                        "jurisdiction": court_data.get('jurisdiction', ''),
                        "in_use": court_data.get('in_use', False)
                    }
        except Exception as e:
            logger.warning(f"Failed to fetch court details for position {position.get('id')}: {e}")
    
    # Fetch appointer details if requested
    if include_appointer_details and position.get('appointer'):
        try:
            appointer_url = position['appointer']
            if appointer_url.startswith('https://'):
                appointer_id = appointer_url.rstrip('/').split('/')[-1]
                appointer_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/people/{appointer_id}/"
                )
                if appointer_response.status_code == 200:
                    appointer_data = appointer_response.json()
                    analysis["appointer_details"] = {
                        "appointer_id": appointer_id,
                        "name_first": appointer_data.get('name_first', ''),
                        "name_last": appointer_data.get('name_last', ''),
                        "full_name": f"{appointer_data.get('name_first', '')} {appointer_data.get('name_last', '')}".strip(),
                        "slug": appointer_data.get('slug', '')
                    }
        except Exception as e:
            logger.warning(f"Failed to fetch appointer details for position {position.get('id')}: {e}")
    
    # Include retention events if requested
    if include_retention_events:
        retention_events = position.get('retention_events', [])
        if retention_events:
            analysis["retention_events"] = {
                "event_count": len(retention_events),
                "events": retention_events[:5]  # Show first 5 events
            }
    
    return analysis
