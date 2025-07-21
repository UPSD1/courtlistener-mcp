"""
CourtListener ABA Ratings Analysis Tools

American Bar Association ratings for judges and legal professionals.
Provides detailed rating history and evaluation timeline analysis.
COMPLETE implementation matching ALL API metadata filters.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import get_aba_rating_display
from utils.formatters import format_aba_ratings_analyses

logger = logging.getLogger(__name__)


def register_aba_ratings_tools(mcp: FastMCP):
    """Register all ABA ratings tools with the MCP server."""
    
    @mcp.tool()
    async def get_aba_ratings(
        rating_id: Optional[int] = None,
        person_id: Optional[int] = None,
        rating: Optional[str] = None,
        # Year rated filters (ALL supported lookups from metadata)
        year_rated: Optional[int] = None,
        year_rated_after: Optional[int] = None,
        year_rated_before: Optional[int] = None,
        year_rated_gt: Optional[int] = None,
        year_rated_lt: Optional[int] = None,
        year_rated_range: Optional[str] = None,
        # Record metadata filters (ALL supported lookups including hour/minute/second)
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
        # ID range filters (ALL supported lookups from metadata)
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
        Retrieve and analyze American Bar Association ratings using ALL supported API filters from metadata.
        
        Args:
            rating_id: Specific ABA rating ID to retrieve
            person_id: Person ID to get all ABA ratings for (exact match)
            rating: Filter by specific rating ('ewq', 'wq', 'q', 'nq', 'nqa')
            
            # Year rated filters (ALL NumberRangeFilter lookups from metadata)
            year_rated: Exact year the rating was given
            year_rated_after: Ratings given after this year (inclusive) [__gte]
            year_rated_before: Ratings given before this year (inclusive) [__lte]
            year_rated_gt: Ratings given after this year (exclusive) [__gt]
            year_rated_lt: Ratings given before this year (exclusive) [__lt]
            year_rated_range: Year range "2020,2024" [__range]
            
            # Record metadata filters (ALL NumberFilter lookups including time precision)
            date_created: Exact creation datetime
            date_created_after: Records created after this datetime (inclusive) [__gte]
            date_created_before: Records created before this datetime (inclusive) [__lte]
            date_created_gt: Records created after this datetime (exclusive) [__gt]
            date_created_lt: Records created before this datetime (exclusive) [__lt]
            date_created_range: Datetime range "YYYY-MM-DD,YYYY-MM-DD" [__range]
            date_created_year: Records created in this specific year
            date_created_month: Records created in this specific month (1-12)
            date_created_day: Records created on this specific day (1-31)
            date_created_hour: Records created in this specific hour (0-23)
            date_created_minute: Records created in this specific minute (0-59)
            date_created_second: Records created in this specific second (0-59)
            # Complete identical set for date_modified...
            
            # ID range filters (ALL NumberRangeFilter lookups from metadata)
            id_exact: Exact rating ID
            id_min: Minimum rating ID (inclusive) [__gte]
            id_max: Maximum rating ID (inclusive) [__lte]
            id_gt: Rating ID greater than (exclusive) [__gt]
            id_lt: Rating ID less than (exclusive) [__lt]
            id_range: ID range "123,456" [__range]
            
            include_person_details: Whether to include detailed person information
            order_by: Sort order ('id', 'date_created', 'date_modified', 'year_rated' with optional '-' prefix)
            limit: Maximum number of results (1-100)
        
        Returns:
            Comprehensive ABA rating analysis with ALL codes converted to human-readable values
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters with COMPLETE API-compliant filter names
            params = {}
            
            if rating_id:
                # Direct rating lookup by ID
                url = f"{courtlistener_ctx.base_url}/aba-ratings/{rating_id}/"
                logger.info(f"Fetching ABA rating by ID: {rating_id}")
            else:
                # Build filtered search with ALL supported API filter names
                url = f"{courtlistener_ctx.base_url}/aba-ratings/"
                
                # Person and rating filters (exact matches only per API)
                if person_id:
                    params['person'] = person_id
                if rating:
                    params['rating'] = rating.lower()
                
                # Year rated filters (ALL NumberRangeFilter lookups from metadata)
                if year_rated:
                    params['year_rated'] = year_rated
                if year_rated_after:
                    params['year_rated__gte'] = year_rated_after
                if year_rated_before:
                    params['year_rated__lte'] = year_rated_before
                if year_rated_gt:
                    params['year_rated__gt'] = year_rated_gt
                if year_rated_lt:
                    params['year_rated__lt'] = year_rated_lt
                if year_rated_range:
                    params['year_rated__range'] = year_rated_range
                
                # Record metadata filters (ALL NumberFilter datetime lookups from metadata)
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
                
                # Date modified filters (complete identical set)
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
                
                # ID range filters (ALL NumberRangeFilter lookups from metadata)
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
                
                # Order and limit results (using API-supported ordering fields from metadata)
                if order_by:
                    # Validate order_by against supported fields from metadata
                    valid_orders = ['id', 'date_created', 'date_modified', 'year_rated']
                    order_field = order_by.lstrip('-')
                    if order_field in valid_orders:
                        params['ordering'] = order_by
                    else:
                        logger.warning(f"Invalid order_by field: {order_by}. Using default.")
                        params['ordering'] = '-year_rated'
                else:
                    params['ordering'] = '-year_rated'  # Most recent ratings first
                
                params['page_size'] = min(max(1, limit), 100)
                
                logger.info(f"Searching ABA ratings with COMPLETE API filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if rating_id:
                # Single rating response
                ratings = [data]
            else:
                # Paginated response
                ratings = data.get('results', [])
                if not ratings:
                    return f"No ABA ratings found matching the specified criteria."
            
            # Build comprehensive analysis
            result = {
                "total_found": len(ratings) if rating_id else data.get('count', len(ratings)),
                "returned": len(ratings),
                "analyses": []
            }
            
            for rating in ratings:
                # Get comprehensive rating analysis
                analysis = await analyze_aba_rating_thoroughly(
                    rating, courtlistener_ctx, include_person_details
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE ABA RATINGS ANALYSIS
Found {result['returned']} rating(s) out of {result['total_found']} total matches:

{format_aba_ratings_analyses(result['analyses'])}

💡 This analysis includes ABA rating history, evaluation timeline, and person context.
🔍 ALL rating codes converted to human-readable values (EWQ → Exceptionally Well Qualified, etc.).
📊 Supports ALL API filters: year ranges, exact values, gt/lt comparisons, datetime precision to second.
⚖️ Complete API metadata compliance with all NumberRangeFilter and NumberFilter lookup types."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"ABA rating not found. Please check the rating ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching ABA rating: {e}")
                return f"Error fetching ABA rating: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching ABA rating: {e}", exc_info=True)
            return f"Error fetching ABA rating: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_aba_rating_thoroughly(rating: dict, courtlistener_ctx, include_person_details: bool) -> dict:
    """Provide thorough analysis of an ABA rating with ALL code conversions."""
    
    # Basic rating information with COMPLETE human-readable conversions
    analysis = {
        "id": rating.get('id'),
        "resource_uri": rating.get('resource_uri'),
        "person_id": rating.get('person'),
        "rating_details": {
            "rating": rating.get('rating'),
            "rating_display": get_aba_rating_display(rating.get('rating')) if rating.get('rating') else None,
            "year_rated": rating.get('year_rated'),
            "rating_context": _get_rating_context(rating.get('rating'))
        },
        "timeline": {
            "year_rated": rating.get('year_rated'),
            "approximate_date": f"{rating.get('year_rated')}-01-01" if rating.get('year_rated') else None,
            "years_ago": _calculate_years_ago(rating.get('year_rated')) if rating.get('year_rated') else None
        },
        "metadata": {
            "date_created": rating.get('date_created'),
            "date_modified": rating.get('date_modified')
        }
    }
    
    # Fetch person details if requested
    if include_person_details:
        person_url = rating.get('person')
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
                logger.warning(f"Failed to fetch person details for rating {rating.get('id')}: {e}")
    
    return analysis


def _get_rating_context(rating_code: str) -> dict:
    """Provide additional context about the ABA rating with complete information."""
    context_map = {
        "ewq": {
            "significance": "Highest possible rating",
            "description": "Demonstrates exceptional legal ability, breadth of experience, and highest character",
            "rarity": "Very rare, reserved for outstanding nominees"
        },
        "wq": {
            "significance": "Strong positive rating",
            "description": "Demonstrates competence, experience, and integrity for judicial service",
            "rarity": "Common for successful judicial nominees"
        },
        "q": {
            "significance": "Acceptable rating",
            "description": "Meets minimum standards for judicial competence and integrity",
            "rarity": "Baseline acceptable rating"
        },
        "nq": {
            "significance": "Negative rating",
            "description": "Does not meet standards for judicial appointment",
            "rarity": "Indicates significant concerns about qualifications"
        },
        "nqa": {
            "significance": "Age-based disqualification",
            "description": "Not qualified due to age considerations (historical rating)",
            "rarity": "Rare, largely discontinued practice"
        }
    }
    
    return context_map.get(rating_code, {
        "significance": "Unknown rating",
        "description": "Rating code not recognized",
        "rarity": "Unknown"
    })


def _calculate_years_ago(year_rated: int) -> int:
    """Calculate how many years ago the rating was given."""
    try:
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - year_rated
    except:
        return None