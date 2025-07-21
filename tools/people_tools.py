"""
CourtListener People/Judge Analysis Tools

Comprehensive judge and person information retrieval from CourtListener's legal database.
Provides detailed biographical, educational, professional, and political information about judges.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import (
    get_gender_display, get_religion_display, get_name_suffix_display,
    get_race_display, get_race_display_multiple, get_state_display, get_political_party_display,
    get_aba_rating_display, get_degree_level_display, get_political_source_display,
    get_date_granularity_display
)
from utils.formatters import format_judge_analyses

logger = logging.getLogger(__name__)


def register_people_tools(mcp: FastMCP):
    """Register people/judge tools with the MCP server."""
    
    @mcp.tool()
    async def get_judge(
        person_id: Optional[int] = None,
        name_first: Optional[str] = None,
        name_first_exact: Optional[str] = None,
        name_first_startswith: Optional[str] = None,
        name_first_endswith: Optional[str] = None,
        name_last: Optional[str] = None,
        name_last_exact: Optional[str] = None,
        name_last_startswith: Optional[str] = None,
        name_last_endswith: Optional[str] = None,
        name_middle: Optional[str] = None,
        name_middle_exact: Optional[str] = None,
        name_suffix: Optional[str] = None,
        fjc_id: Optional[int] = None,
        ftm_eid: Optional[str] = None,
        gender: Optional[str] = None,
        race: Optional[str] = None,  # Can be comma-separated for multiple races
        religion: Optional[str] = None,
        dob_city: Optional[str] = None,
        dob_city_exact: Optional[str] = None,
        dob_state: Optional[str] = None,
        dob_country: Optional[str] = None,
        dod_city: Optional[str] = None,
        dod_state: Optional[str] = None,
        dod_country: Optional[str] = None,
        date_dob_after: Optional[str] = None,
        date_dob_before: Optional[str] = None,
        date_dob_year: Optional[int] = None,
        date_dod_after: Optional[str] = None,
        date_dod_before: Optional[str] = None,
        date_dod_year: Optional[int] = None,
        has_photo: Optional[bool] = None,
        exclude_aliases: bool = True,
        # Related object filters
        education_degree_level: Optional[str] = None,
        education_school_name: Optional[str] = None,
        political_party: Optional[str] = None,
        political_source: Optional[str] = None,
        aba_rating: Optional[str] = None,
        position_type: Optional[str] = None,
        court_name: Optional[str] = None,
        # Include options
        include_positions: bool = True,
        include_educations: bool = True,
        include_political_affiliations: bool = True,
        include_aba_ratings: bool = True,
        limit: int = 10
    ) -> str:
        """
        Retrieve comprehensive judge and person information from CourtListener's database with full filtering support.
        
        Args:
            person_id: Specific person ID to retrieve
            name_first: First name partial match (icontains)
            name_first_exact: First name exact match
            name_first_startswith: First name starts with
            name_first_endswith: First name ends with
            name_last: Last name partial match (icontains)
            name_last_exact: Last name exact match
            name_last_startswith: Last name starts with
            name_last_endswith: Last name ends with
            name_middle: Middle name partial match (icontains)
            name_middle_exact: Middle name exact match
            name_suffix: Name suffix ('jr', 'sr', '1', '2', '3', '4')
            fjc_id: Federal Judicial Center ID (exact match)
            ftm_eid: Follow The Money database ID (exact match)
            gender: Gender filter ('m'=Male, 'f'=Female, 'o'=Other)
            race: Race filter - single or comma-separated multiple ('w','b','i','a','p','mena','h','o')
            religion: Religion filter ('ca','pr','je','mu','at','ag','mo','bu','hi','ep','ro','me','pe','un')
            dob_city: Birth city partial match (icontains)
            dob_city_exact: Birth city exact match
            dob_state: Birth state (US state abbreviations like 'CA', 'NY')
            dob_country: Birth country partial match
            dod_city: Death city partial match
            dod_state: Death state (US state abbreviations)
            dod_country: Death country partial match
            date_dob_after: Born after this date (YYYY-MM-DD)
            date_dob_before: Born before this date (YYYY-MM-DD)
            date_dob_year: Born in this specific year
            date_dod_after: Died after this date (YYYY-MM-DD)
            date_dod_before: Died before this date (YYYY-MM-DD)
            date_dod_year: Died in this specific year
            has_photo: Whether person has a photo in the database
            exclude_aliases: Whether to exclude alias records (recommended: True)
            education_degree_level: Filter by education degree ('ba','ma','jd','llm','phd',etc.)
            education_school_name: Filter by school name (partial match)
            political_party: Filter by political party ('d','r','i','g','l','f','w','j','u','z')
            political_source: Filter by political affiliation source ('b','a','o')
            aba_rating: Filter by ABA rating ('ewq','wq','q','nq','nqa')
            position_type: Filter by position type
            court_name: Filter by court name (partial match)
            include_positions: Whether to include positions held by the person
            include_educations: Whether to include educational history
            include_political_affiliations: Whether to include political party data
            include_aba_ratings: Whether to include American Bar Association ratings
            limit: Maximum number of results (1-50)
        
        Returns:
            Comprehensive judge information including biographical data, career positions, education, and political affiliations with all codes converted to human-readable values
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters with API-compliant filter names
            params = {}
            
            if person_id:
                # Direct person lookup by ID
                url = f"{courtlistener_ctx.base_url}/people/{person_id}/"
                logger.info(f"Fetching person by ID: {person_id}")
            else:
                # Build filtered search with correct API filter names
                url = f"{courtlistener_ctx.base_url}/people/"
                
                # Advanced name filters with all lookup types
                if name_first:
                    params['name_first__icontains'] = name_first
                if name_first_exact:
                    params['name_first__iexact'] = name_first_exact
                if name_first_startswith:
                    params['name_first__istartswith'] = name_first_startswith
                if name_first_endswith:
                    params['name_first__iendswith'] = name_first_endswith
                
                if name_last:
                    params['name_last__icontains'] = name_last
                if name_last_exact:
                    params['name_last__iexact'] = name_last_exact
                if name_last_startswith:
                    params['name_last__istartswith'] = name_last_startswith
                if name_last_endswith:
                    params['name_last__iendswith'] = name_last_endswith
                
                if name_middle:
                    params['name_middle__icontains'] = name_middle
                if name_middle_exact:
                    params['name_middle__iexact'] = name_middle_exact
                
                if name_suffix:
                    params['name_suffix'] = name_suffix.lower()
                
                # Professional identifiers
                if fjc_id is not None:
                    params['fjc_id'] = fjc_id
                if ftm_eid:
                    params['ftm_eid'] = ftm_eid
                
                # Demographic filters
                if gender:
                    params['gender'] = gender.lower()
                
                # Handle multiple race values (MultipleChoiceFilter)
                if race:
                    race_values = [r.strip().lower() for r in race.split(',')]
                    # For MultipleChoiceFilter, pass as comma-separated string
                    params['race'] = ','.join(race_values)
                
                if religion:
                    params['religion'] = religion.lower()
                
                # Birth location filters with advanced matching
                if dob_city:
                    params['dob_city__icontains'] = dob_city
                if dob_city_exact:
                    params['dob_city__iexact'] = dob_city_exact
                if dob_state:
                    params['dob_state'] = dob_state.upper()
                if dob_country:
                    params['dob_country__icontains'] = dob_country
                
                # Death location filters
                if dod_city:
                    params['dod_city__icontains'] = dod_city
                if dod_state:
                    params['dod_state'] = dod_state.upper()
                if dod_country:
                    params['dod_country__icontains'] = dod_country
                
                # Enhanced date range filters
                if date_dob_after:
                    params['date_dob__gte'] = date_dob_after
                if date_dob_before:
                    params['date_dob__lte'] = date_dob_before
                if date_dob_year:
                    params['date_dob__year'] = date_dob_year
                
                if date_dod_after:
                    params['date_dod__gte'] = date_dod_after
                if date_dod_before:
                    params['date_dod__lte'] = date_dod_before
                if date_dod_year:
                    params['date_dod__year'] = date_dod_year
                
                # Photo availability
                if has_photo is not None:
                    params['has_photo'] = has_photo
                
                # Related object filters (RelatedFilter support)
                if education_degree_level:
                    params['educations__degree_level'] = education_degree_level.lower()
                if education_school_name:
                    params['educations__school__name__icontains'] = education_school_name
                if political_party:
                    params['political_affiliations__political_party'] = political_party.lower()
                if political_source:
                    params['political_affiliations__source'] = political_source.lower()
                if aba_rating:
                    params['aba_ratings__rating'] = aba_rating.lower()
                if position_type:
                    params['positions__position_type__icontains'] = position_type
                if court_name:
                    params['positions__court__full_name__icontains'] = court_name
                
                # Exclude aliases (recommended)
                if exclude_aliases:
                    params['is_alias_of__isnull'] = True
                
                # Order and limit results
                params['ordering'] = 'name_last,name_first'  # Alphabetical by name
                params['page_size'] = min(max(1, limit), 50)
                
                logger.info(f"Searching people with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if person_id:
                # Single person response
                people = [data]
            else:
                # Paginated response
                people = data.get('results', [])
                if not people:
                    return f"No people found matching the specified criteria."
            
            # Build comprehensive analysis
            result = {
                "total_found": len(people) if person_id else data.get('count', len(people)),
                "returned": len(people),
                "analyses": []
            }
            
            for person in people:
                # Get comprehensive person analysis
                analysis = await analyze_person_thoroughly(
                    person, courtlistener_ctx, include_positions, include_educations, 
                    include_political_affiliations, include_aba_ratings
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE JUDGE/PERSON ANALYSIS
Found {result['returned']} person(s) out of {result['total_found']} total matches:

{format_judge_analyses(result['analyses'])}

💡 This analysis includes biographical data, career positions, education, and political affiliations.
🔍 All codes converted to human-readable values including gender, race, religion, and professional ratings.
⚖️ Advanced filtering: exact matches, starts/ends with, related objects, and multiple race selection."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Person not found. Please check the person ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching person: {e}")
                return f"Error fetching person: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching person: {e}", exc_info=True)
            return f"Error fetching person: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_person_thoroughly(person: dict, courtlistener_ctx, include_positions: bool, include_educations: bool, include_political_affiliations: bool, include_aba_ratings: bool) -> dict:
    """Provide thorough analysis of a person including all biographical and professional information."""
    
    # Basic person information with human-readable conversions
    analysis = {
        "id": person.get('id'),
        "resource_uri": person.get('resource_uri'),
        "slug": person.get('slug'),
        "absolute_url": f"https://www.courtlistener.com{person.get('absolute_url', '')}",
        "identification": {
            "name_first": person.get('name_first', ''),
            "name_middle": person.get('name_middle', ''),
            "name_last": person.get('name_last', ''),
            "name_suffix": person.get('name_suffix'),
            "name_suffix_display": get_name_suffix_display(person.get('name_suffix')) if person.get('name_suffix') else None,
            "full_name": f"{person.get('name_first', '')} {person.get('name_middle', '')} {person.get('name_last', '')}".strip(),
            "is_alias_of": person.get('is_alias_of'),
            "is_alias": person.get('is_alias_of') is not None
        },
        "biographical_info": {
            "date_dob": person.get('date_dob'),
            "date_granularity_dob": person.get('date_granularity_dob'),
            "date_granularity_dob_display": get_date_granularity_display(person.get('date_granularity_dob')) if person.get('date_granularity_dob') else None,
            "date_dod": person.get('date_dod'),
            "date_granularity_dod": person.get('date_granularity_dod'),
            "date_granularity_dod_display": get_date_granularity_display(person.get('date_granularity_dod')) if person.get('date_granularity_dod') else None,
            "birth_location": {
                "city": person.get('dob_city'),
                "state": person.get('dob_state'),
                "state_display": get_state_display(person.get('dob_state')) if person.get('dob_state') else None,
                "country": person.get('dob_country')
            },
            "death_location": {
                "city": person.get('dod_city'),
                "state": person.get('dod_state'),
                "state_display": get_state_display(person.get('dod_state')) if person.get('dod_state') else None,
                "country": person.get('dod_country')
            },
            "gender": person.get('gender'),
            "gender_display": get_gender_display(person.get('gender')) if person.get('gender') else None,
            "race": person.get('race'),
            "race_display": get_race_display_multiple(person.get('race')) if person.get('race') else None,
            "religion": person.get('religion'),
            "religion_display": get_religion_display(person.get('religion')) if person.get('religion') else None
        },
        "professional_identifiers": {
            "fjc_id": person.get('fjc_id'),
            "ftm_eid": person.get('ftm_eid'),
            "ftm_total_received": person.get('ftm_total_received'),
            "has_photo": person.get('has_photo', False)
        },
        "metadata": {
            "date_created": person.get('date_created'),
            "date_modified": person.get('date_modified'),
            "date_completed": person.get('date_completed')
        }
    }
    
    # Process nested political affiliations
    if include_political_affiliations and person.get('political_affiliations'):
        analysis["political_affiliations"] = {
            "count": len(person['political_affiliations']),
            "affiliations": []
        }
        
        for affiliation in person['political_affiliations'][:10]:  # Limit to first 10
            affiliation_info = {
                "political_party": affiliation.get('political_party'),
                "political_party_display": get_political_party_display(affiliation.get('political_party')) if affiliation.get('political_party') else None,
                "source": affiliation.get('source'),
                "source_display": get_political_source_display(affiliation.get('source')) if affiliation.get('source') else None,
                "date_start": affiliation.get('date_start'),
                "date_granularity_start": affiliation.get('date_granularity_start'),
                "date_granularity_start_display": get_date_granularity_display(affiliation.get('date_granularity_start')) if affiliation.get('date_granularity_start') else None,
                "date_end": affiliation.get('date_end'),
                "date_granularity_end": affiliation.get('date_granularity_end'),
                "date_granularity_end_display": get_date_granularity_display(affiliation.get('date_granularity_end')) if affiliation.get('date_granularity_end') else None
            }
            analysis["political_affiliations"]["affiliations"].append(affiliation_info)
    
    # Process nested ABA ratings
    if include_aba_ratings and person.get('aba_ratings'):
        analysis["aba_ratings"] = {
            "count": len(person['aba_ratings']),
            "ratings": []
        }
        
        for rating in person['aba_ratings']:
            rating_info = {
                "year_rated": rating.get('year_rated'),
                "rating": rating.get('rating'),
                "rating_display": get_aba_rating_display(rating.get('rating')) if rating.get('rating') else None,
                "date_created": rating.get('date_created'),
                "date_modified": rating.get('date_modified')
            }
            analysis["aba_ratings"]["ratings"].append(rating_info)
    
    # Process nested educations
    if include_educations and person.get('educations'):
        analysis["educations"] = {
            "count": len(person['educations']),
            "education_history": []
        }
        
        for education in person['educations']:
            education_info = {
                "school_name": education.get('school', {}).get('name') if education.get('school') else None,
                "school_ein": education.get('school', {}).get('ein') if education.get('school') else None,
                "degree_level": education.get('degree_level'),
                "degree_level_display": get_degree_level_display(education.get('degree_level')) if education.get('degree_level') else None,
                "degree_detail": education.get('degree_detail'),
                "degree_year": education.get('degree_year'),
                "date_created": education.get('date_created'),
                "date_modified": education.get('date_modified')
            }
            analysis["educations"]["education_history"].append(education_info)
    
    # Fetch positions if requested (since positions are linked, not nested)
    if include_positions:
        try:
            positions_response = await courtlistener_ctx.http_client.get(
                f"{courtlistener_ctx.base_url}/positions/",
                params={'person': person.get('id'), 'page_size': 20}  # Get up to 20 positions
            )
            if positions_response.status_code == 200:
                positions_data = positions_response.json()
                analysis["positions"] = {
                    "count": positions_data.get('count', 0),
                    "positions_held": []
                }
                
                for position in positions_data.get('results', []):
                    position_info = {
                        "position_type": position.get('position_type'),
                        "job_title": position.get('job_title'),
                        "organization_name": position.get('organization_name'),
                        "court": position.get('court'),
                        "date_nominated": position.get('date_nominated'),
                        "date_elected": position.get('date_elected'),
                        "date_recess_appointment": position.get('date_recess_appointment'),
                        "date_referred_to_judicial_committee": position.get('date_referred_to_judicial_committee'),
                        "date_judicial_committee_action": position.get('date_judicial_committee_action'),
                        "date_hearing": position.get('date_hearing'),
                        "date_confirmation": position.get('date_confirmation'),
                        "date_start": position.get('date_start'),
                        "date_granularity_start": position.get('date_granularity_start'),
                        "date_retirement": position.get('date_retirement'),
                        "date_termination": position.get('date_termination'),
                        "date_granularity_termination": position.get('date_granularity_termination'),
                        "appointer": position.get('appointer'),
                        "supervisor": position.get('supervisor'),
                        "predecessor": position.get('predecessor'),
                        "successor": position.get('successor'),
                        "how_selected": position.get('how_selected'),
                        "termination_reason": position.get('termination_reason')
                    }
                    analysis["positions"]["positions_held"].append(position_info)
        except Exception as e:
            logger.warning(f"Failed to fetch positions for person {person.get('id')}: {e}")
    
    # Process sources information
    if person.get('sources'):
        analysis["sources"] = {
            "count": len(person['sources']),
            "source_info": []
        }
        
        for source in person['sources'][:5]:  # Limit to first 5 sources
            source_info = {
                "url": source.get('url'),
                "date_accessed": source.get('date_accessed'),
                "notes": source.get('notes'),
                "date_created": source.get('date_created'),
                "date_modified": source.get('date_modified')
            }
            analysis["sources"]["source_info"].append(source_info)
    
    return analysis