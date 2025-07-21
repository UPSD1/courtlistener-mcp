"""
CourtListener Opinion Cluster Analysis Tools

Comprehensive opinion cluster retrieval and analysis for grouped legal decisions.
Clusters represent cases with multiple opinions (majority, dissent, concurrence).
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import (
    get_cluster_source_display_enhanced, get_citation_type_display_enhanced,
    get_scdb_decision_direction_display_enhanced, get_precedential_status_display_enhanced,
    safe_extract_citation_objects, safe_extract_citations
)
from utils.formatters import format_cluster_analyses

logger = logging.getLogger(__name__)


def register_cluster_tools(mcp: FastMCP):
    """Register all cluster-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_cluster(
        cluster_id: Optional[int] = None,
        case_name: Optional[str] = None,
        court: Optional[str] = None,
        citation: Optional[str] = None,
        date_filed_after: Optional[str] = None,
        date_filed_before: Optional[str] = None,
        precedential_status: Optional[str] = None,
        scdb_id: Optional[str] = None,
        scdb_decision_direction: Optional[int] = None,
        scdb_votes_majority_min: Optional[int] = None,
        scdb_votes_majority_max: Optional[int] = None,
        scdb_votes_minority_min: Optional[int] = None,
        scdb_votes_minority_max: Optional[int] = None,
        citation_count_min: Optional[int] = None,
        citation_count_max: Optional[int] = None,
        source: Optional[str] = None,
        blocked: Optional[bool] = None,
        date_blocked_after: Optional[str] = None,
        date_blocked_before: Optional[str] = None,
        include_opinions: bool = True,
        include_docket: bool = True,
        limit: int = 10
    ) -> str:
        """
        Retrieve and analyze opinion clusters from CourtListener with comprehensive case information.
        
        Args:
            cluster_id: Specific cluster ID to retrieve
            case_name: Full or partial case name to search for (uses case_name__icontains)
            court: Court identifier (e.g., 'scotus', 'ca9', 'dcd') - filters by docket__court
            citation: Citation to search for (e.g., '576 U.S. 644') - searches in citations
            date_filed_after: Show clusters filed after this date (YYYY-MM-DD)
            date_filed_before: Show clusters filed before this date (YYYY-MM-DD)
            precedential_status: Status filter ('Published', 'Unpublished', 'Errata', etc.)
            scdb_id: Supreme Court Database ID (exact match)
            scdb_decision_direction: SCDB direction (1=Conservative, 2=Liberal, 3=Unspecifiable)
            scdb_votes_majority_min: Minimum majority votes in SCDB
            scdb_votes_majority_max: Maximum majority votes in SCDB
            scdb_votes_minority_min: Minimum minority votes in SCDB
            scdb_votes_minority_max: Maximum minority votes in SCDB
            citation_count_min: Minimum number of times case has been cited
            citation_count_max: Maximum number of times case has been cited
            source: Source of the cluster (e.g., 'C', 'U', 'Z', etc. - see source mapping)
            blocked: Filter for blocked/unblocked clusters (True/False)
            date_blocked_after: Show clusters blocked after this date (YYYY-MM-DD)
            date_blocked_before: Show clusters blocked before this date (YYYY-MM-DD)
            include_opinions: Whether to include individual opinion details
            include_docket: Whether to include related docket information
            limit: Maximum number of results (1-50)
        
        Returns:
            Comprehensive cluster analysis including case details, citations, legal significance, and SCDB data with all codes converted to human-readable values
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters with API-compliant filter names
            params = {}
            
            if cluster_id:
                # Direct cluster lookup by ID
                url = f"{courtlistener_ctx.base_url}/clusters/{cluster_id}/"
                logger.info(f"Fetching cluster by ID: {cluster_id}")
            else:
                # Build filtered search with correct API filter names
                url = f"{courtlistener_ctx.base_url}/clusters/"
                
                # Text search filters
                if case_name:
                    params['case_name__icontains'] = case_name
                
                # Related object filters (through docket)
                if court:
                    params['docket__court'] = court.lower()
                
                # Citation search (RelatedFilter)
                if citation:
                    # This searches within the citations relationship
                    params['citations__cite__icontains'] = citation
                
                # Date filters
                if date_filed_after:
                    params['date_filed__gte'] = date_filed_after
                if date_filed_before:
                    params['date_filed__lte'] = date_filed_before
                if date_blocked_after:
                    params['date_blocked__gte'] = date_blocked_after
                if date_blocked_before:
                    params['date_blocked__lte'] = date_blocked_before
                
                # Choice filters
                if precedential_status:
                    params['precedential_status'] = precedential_status
                if scdb_decision_direction is not None:
                    params['scdb_decision_direction'] = scdb_decision_direction
                if source:
                    params['source'] = source
                
                # Exact match filters
                if scdb_id:
                    params['scdb_id'] = scdb_id
                if blocked is not None:
                    params['blocked'] = blocked
                
                # Range filters
                if citation_count_min is not None:
                    params['citation_count__gte'] = citation_count_min
                if citation_count_max is not None:
                    params['citation_count__lte'] = citation_count_max
                if scdb_votes_majority_min is not None:
                    params['scdb_votes_majority__gte'] = scdb_votes_majority_min
                if scdb_votes_majority_max is not None:
                    params['scdb_votes_majority__lte'] = scdb_votes_majority_max
                if scdb_votes_minority_min is not None:
                    params['scdb_votes_minority__gte'] = scdb_votes_minority_min
                if scdb_votes_minority_max is not None:
                    params['scdb_votes_minority__lte'] = scdb_votes_minority_max
                
                # Order and limit results
                params['ordering'] = '-date_filed'  # Most recent first
                params['page_size'] = min(max(1, limit), 50)
                
                logger.info(f"Searching clusters with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if cluster_id:
                # Single cluster response
                clusters = [data]
            else:
                # Paginated response
                clusters = data.get('results', [])
                if not clusters:
                    return f"No clusters found matching the specified criteria."
            
            # Build comprehensive analysis
            result = {
                "total_found": len(clusters) if cluster_id else data.get('count', len(clusters)),
                "returned": len(clusters),
                "analyses": []
            }
            
            for cluster in clusters:
                # Get comprehensive cluster analysis
                analysis = await analyze_cluster_thoroughly_enhanced(
                    cluster, courtlistener_ctx, include_opinions, include_docket
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE CLUSTER ANALYSIS
Found {result['returned']} cluster(s) out of {result['total_found']} total matches:

{format_cluster_analyses(result['analyses'])}

💡 This analysis includes case significance, citations, SCDB data, and related opinions.
🔍 All codes converted to human-readable values including source, status, and SCDB data."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Cluster not found. Please check the cluster ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching cluster: {e}")
                return f"Error fetching cluster: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching cluster: {e}", exc_info=True)
            return f"Error fetching cluster: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_cluster_thoroughly_enhanced(cluster: dict, courtlistener_ctx, include_opinions: bool, include_docket: bool) -> dict:
    """Provide thorough analysis of a cluster including legal significance and context with enhanced code conversion."""
    
    # Basic cluster metadata with enhanced human-readable conversions
    analysis = {
        "id": cluster.get('id'),
        "absolute_url": f"https://www.courtlistener.com{cluster.get('absolute_url', '')}",
        "case_identification": {
            "case_name": cluster.get('case_name', ''),
            "case_name_short": cluster.get('case_name_short', ''),
            "case_name_full": cluster.get('case_name_full', ''),
            "slug": cluster.get('slug', ''),
            "scdb_id": cluster.get('scdb_id', '')
        },
        "filing_info": {
            "date_filed": cluster.get('date_filed'),
            "date_filed_is_approximate": cluster.get('date_filed_is_approximate', False),
            "other_dates": cluster.get('other_dates', '')
        },
        "legal_significance": {
            "precedential_status": cluster.get('precedential_status'),
            "precedential_status_display": get_precedential_status_display_enhanced(cluster.get('precedential_status')),
            "citation_count": cluster.get('citation_count', 0),
            "blocked": cluster.get('blocked', False),
            "date_blocked": cluster.get('date_blocked')
        },
        "procedural_info": {
            "disposition": cluster.get('disposition', ''),
            "procedural_history": cluster.get('procedural_history', ''),
            "posture": cluster.get('posture', ''),
            "nature_of_suit": cluster.get('nature_of_suit', ''),
            "attorneys": cluster.get('attorneys', '')
        },
        "judicial_panel": {
            "judges": cluster.get('judges', ''),
            "panel_ids": cluster.get('panel', []),
            "non_participating_judges": cluster.get('non_participating_judges', [])
        },
        "content_summary": {
            "syllabus": cluster.get('syllabus', ''),
            "summary": cluster.get('summary', ''),
            "headnotes": cluster.get('headnotes', ''),
            "history": cluster.get('history', ''),
            "arguments": cluster.get('arguments', ''),
            "headmatter": cluster.get('headmatter', ''),
            "cross_reference": cluster.get('cross_reference', ''),
            "correction": cluster.get('correction', '')
        },
        "source_info": {
            "source": cluster.get('source'),
            "source_display": get_cluster_source_display_enhanced(cluster.get('source', '')),
            "date_created": cluster.get('date_created'),
            "date_modified": cluster.get('date_modified')
        },
        "external_resources": {
            "filepath_json_harvard": cluster.get('filepath_json_harvard'),
            "filepath_pdf_harvard": cluster.get('filepath_pdf_harvard')
        }
    }
    
    # Process citations with detailed information and type mapping
    citations_raw = cluster.get('citations', [])
    if citations_raw:
        analysis["citations"] = {
            "count": len(citations_raw),
            "citation_strings": safe_extract_citations(citations_raw),
            "detailed_citations": []
        }
        
        # Enhanced citation processing with type mapping
        for citation in citations_raw:
            if isinstance(citation, dict):
                citation_info = {
                    "volume": citation.get('volume'),
                    "reporter": citation.get('reporter'),
                    "page": citation.get('page'),
                    "citation_string": f"{citation.get('volume', '')} {citation.get('reporter', '')} {citation.get('page', '')}".strip(),
                    "type": citation.get('type'),
                    "type_display": get_citation_type_display_enhanced(citation.get('type')) if citation.get('type') else None
                }
                analysis["citations"]["detailed_citations"].append(citation_info)
    
    # Enhanced Supreme Court Database information with human-readable conversions
    if cluster.get('scdb_id'):
        analysis["supreme_court_database"] = {
            "scdb_id": cluster.get('scdb_id'),
            "decision_direction": cluster.get('scdb_decision_direction'),
            "decision_direction_display": get_scdb_decision_direction_display_enhanced(cluster.get('scdb_decision_direction')) if cluster.get('scdb_decision_direction') else None,
            "votes_majority": cluster.get('scdb_votes_majority'),
            "votes_minority": cluster.get('scdb_votes_minority'),
            "vote_summary": f"{cluster.get('scdb_votes_majority', 0)}-{cluster.get('scdb_votes_minority', 0)}" if cluster.get('scdb_votes_majority') is not None and cluster.get('scdb_votes_minority') is not None else None
        }
    
    # Fetch related opinions if requested
    if include_opinions:
        sub_opinions = cluster.get('sub_opinions', [])
        analysis["opinions_summary"] = {
            "opinion_count": len(sub_opinions),
            "opinions": []
        }
        
        # Fetch details for each opinion
        for opinion_url in sub_opinions[:10]:  # Limit to first 10 opinions
            try:
                opinion_id = opinion_url.rstrip('/').split('/')[-1]
                opinion_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/opinions/{opinion_id}/"
                )
                if opinion_response.status_code == 200:
                    opinion_data = opinion_response.json()
                    opinion_info = {
                        "opinion_id": opinion_id,
                        "type": opinion_data.get('type'),
                        "type_display": get_opinion_type_display(opinion_data.get('type')) if opinion_data.get('type') else None,
                        "author": opinion_data.get('author_str', 'Unknown'),
                        "joined_by": opinion_data.get('joined_by_str', ''),
                        "per_curiam": opinion_data.get('per_curiam', False),
                        "page_count": opinion_data.get('page_count'),
                        "has_text": bool(opinion_data.get('plain_text') or opinion_data.get('html') or opinion_data.get('html_with_citations'))
                    }
                    analysis["opinions_summary"]["opinions"].append(opinion_info)
            except Exception as e:
                logger.warning(f"Failed to fetch opinion from {opinion_url}: {e}")
    
    # Fetch docket information if requested
    if include_docket:
        docket_url = cluster.get('docket')
        if docket_url:
            try:
                docket_id = docket_url.rstrip('/').split('/')[-1]
                docket_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/dockets/{docket_id}/"
                )
                if docket_response.status_code == 200:
                    docket_data = docket_response.json()
                    analysis["docket_info"] = {
                        "docket_id": docket_id,
                        "docket_number": docket_data.get('docket_number'),
                        "court_id": docket_data.get('court_id'),
                        "assigned_judge": docket_data.get('assigned_to_str'),
                        "nature_of_suit": docket_data.get('nature_of_suit'),
                        "cause": docket_data.get('cause'),
                        "jurisdiction_type": docket_data.get('jurisdiction_type'),
                        "date_filed": docket_data.get('date_filed'),
                        "date_terminated": docket_data.get('date_terminated'),
                        "pacer_case_id": docket_data.get('pacer_case_id')
                    }
                    
                    # Fetch court name
                    court_id = docket_data.get('court_id')
                    if court_id:
                        try:
                            court_response = await courtlistener_ctx.http_client.get(
                                f"{courtlistener_ctx.base_url}/courts/{court_id}/"
                            )
                            if court_response.status_code == 200:
                                court_data = court_response.json()
                                analysis["docket_info"]["court_name"] = court_data.get('full_name', court_id)
                                analysis["docket_info"]["court_jurisdiction"] = court_data.get('jurisdiction')
                        except Exception as e:
                            logger.warning(f"Failed to fetch court {court_id}: {e}")
            except Exception as e:
                logger.warning(f"Failed to fetch docket for cluster {cluster.get('id')}: {e}")
    
    return analysis


# Import the opinion type display function
from utils.mappings import get_opinion_type_display