"""
CourtListener Docket Analysis Tools

Comprehensive case docket retrieval, analysis, and context interpretation.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import (
    get_nature_of_suit_display, get_jurisdiction_display, get_disposition_display,
    get_procedural_progress_display, get_judgment_display, get_enhanced_source_display,
    get_dataset_source_display, get_origin_display, get_arbitration_display,
    get_termination_class_action_status_display, get_nature_of_judgement_display,
    get_pro_se_display, safe_extract_citations, extract_numeric_code
)
from utils.formatters import format_docket_cases

logger = logging.getLogger(__name__)


def register_docket_tools(mcp: FastMCP):
    """Register all docket-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_docket(
        docket_id: Optional[int] = None,
        docket_number: Optional[str] = None,
        docket_number_core: Optional[str] = None,
        case_name: Optional[str] = None,
        court: Optional[str] = None,
        nature_of_suit: Optional[str] = None,
        pacer_case_id: Optional[str] = None,
        assigned_judge: Optional[str] = None,
        referred_judge: Optional[str] = None,
        date_filed_after: Optional[str] = None,
        date_filed_before: Optional[str] = None,
        date_terminated_after: Optional[str] = None,
        date_terminated_before: Optional[str] = None,
        date_last_filing_after: Optional[str] = None,
        date_last_filing_before: Optional[str] = None,
        blocked: Optional[bool] = None,
        source: Optional[int] = None,
        include_clusters: bool = True,
        include_entries: bool = False,
        limit: int = 10
    ) -> str:
        """
        Retrieve case docket information from CourtListener with comprehensive filtering options.
        
        Args:
            docket_id: Specific docket ID to retrieve (e.g., 65663213)
            docket_number: Case docket number (e.g., '23A994', '1:16-cv-00745') - exact match
            docket_number_core: Core docket number for federal cases (e.g., '0734911') - supports startswith
            case_name: Full or partial case name to search for (uses icontains)
            court: Court identifier (e.g., 'scotus', 'ca9', 'dcd', 'cafc')
            nature_of_suit: Nature of suit description (e.g., 'Civil Rights', 'Contract') - supports icontains
            pacer_case_id: PACER case ID for federal cases - exact match
            assigned_judge: Name of assigned judge (uses assigned_to filter for People relation)
            referred_judge: Name of referred judge (uses referred_to filter for People relation)
            date_filed_after: Show cases filed after this date (YYYY-MM-DD)
            date_filed_before: Show cases filed before this date (YYYY-MM-DD)
            date_terminated_after: Show cases terminated after this date (YYYY-MM-DD)
            date_terminated_before: Show cases terminated before this date (YYYY-MM-DD)
            date_last_filing_after: Show cases with last filing after this date (YYYY-MM-DD)
            date_last_filing_before: Show cases with last filing before this date (YYYY-MM-DD)
            blocked: Filter for blocked/unblocked cases (True/False)
            source: Source filter (see source code mappings, e.g., 1=RECAP, 2=Scraper)
            include_clusters: Whether to include related opinion clusters
            include_entries: Whether to include docket entries (federal cases only)
            limit: Maximum number of results for searches (1-50)
        
        Returns:
            Comprehensive case information including timeline, parties, judges, and related documents with all codes converted to human-readable values
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters with API-compliant filter names
            params = {}
            
            if docket_id:
                # Direct docket lookup by ID
                url = f"{courtlistener_ctx.base_url}/dockets/{docket_id}/"
                logger.info(f"Fetching docket by ID: {docket_id}")
            else:
                # Build filtered search with correct API filter names
                url = f"{courtlistener_ctx.base_url}/dockets/"
                
                # Exact match filters
                if docket_number:
                    params['docket_number'] = docket_number
                if docket_number_core:
                    params['docket_number_core__startswith'] = docket_number_core
                if pacer_case_id:
                    params['pacer_case_id'] = pacer_case_id
                if source is not None:
                    params['source'] = source
                if blocked is not None:
                    params['blocked'] = blocked
                
                # String search filters
                if case_name:
                    params['case_name__icontains'] = case_name
                if court:
                    params['court'] = court.lower()
                if nature_of_suit:
                    params['nature_of_suit__icontains'] = nature_of_suit
                
                # Judge filters (these use RelatedFilter to People)
                if assigned_judge:
                    params['assigned_to_str__icontains'] = assigned_judge
                if referred_judge:
                    params['referred_to_str__icontains'] = referred_judge
                
                # Date range filters
                if date_filed_after:
                    params['date_filed__gte'] = date_filed_after
                if date_filed_before:
                    params['date_filed__lte'] = date_filed_before
                if date_terminated_after:
                    params['date_terminated__gte'] = date_terminated_after
                if date_terminated_before:
                    params['date_terminated__lte'] = date_terminated_before
                if date_last_filing_after:
                    params['date_last_filing__gte'] = date_last_filing_after
                if date_last_filing_before:
                    params['date_last_filing__lte'] = date_last_filing_before
                
                # Order and limit results
                params['ordering'] = '-date_filed'  # Most recent first
                params['page_size'] = min(max(1, limit), 50)
                
                logger.info(f"Searching dockets with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if docket_id:
                # Single docket response
                dockets = [data]
            else:
                # Paginated response
                dockets = data.get('results', [])
                if not dockets:
                    return f"No dockets found matching the specified criteria."
            
            # Format comprehensive response
            result = {
                "total_found": len(dockets) if docket_id else data.get('count', len(dockets)),
                "returned": len(dockets),
                "cases": []
            }
            
            for docket in dockets:
                # Build comprehensive case summary with enhanced code conversion
                case_summary = await build_enhanced_docket_summary(
                    docket, courtlistener_ctx, include_clusters, include_entries
                )
                result["cases"].append(case_summary)
            
            return f"""COMPREHENSIVE DOCKET ANALYSIS
Found {result['returned']} case(s) out of {result['total_found']} total matches:

{format_docket_cases(result['cases'])}

💡 All legal codes converted to human-readable values.
🔍 Use include_clusters=true for related opinions, include_entries=true for docket entries (federal cases)."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Docket not found. Please check the docket ID ({docket_id}) or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching docket: {e}")
                return f"Error fetching docket: HTTP {e.response.status_code} - {e.response.text[:200]}"
        except Exception as e:
            logger.error(f"Error fetching docket: {e}", exc_info=True)
            return f"Error fetching docket: {str(e)}\n\nDetails: {type(e).__name__} - Check logs for more information."


async def build_enhanced_docket_summary(docket: dict, courtlistener_ctx, include_clusters: bool, include_entries: bool) -> dict:
    """Build comprehensive docket summary with enhanced human-readable code translations."""
    
    # Extract and translate coded values
    nature_of_suit_raw = docket.get('nature_of_suit', '')
    nature_of_suit_display = nature_of_suit_raw
    
    # Try to extract numeric code from nature_of_suit string if it contains one
    numeric_code = extract_numeric_code(nature_of_suit_raw)
    if numeric_code:
        nature_of_suit_display = f"{get_nature_of_suit_display(numeric_code)} ({numeric_code})"
    
    # Basic docket information with enhanced human-readable values
    case_summary = {
        "id": docket.get('id'),
        "absolute_url": f"https://www.courtlistener.com{docket.get('absolute_url', '')}",
        "court_info": {
            "court_id": docket.get('court_id'),
            "court_name": "Loading...",
            "appeal_from": docket.get('appeal_from_str', '')
        },
        "case_details": {
            "docket_number": docket.get('docket_number'),
            "docket_number_core": docket.get('docket_number_core'),
            "case_name": docket.get('case_name'),
            "case_name_full": docket.get('case_name_full'),
            "case_name_short": docket.get('case_name_short'),
            "slug": docket.get('slug'),
            "pacer_case_id": docket.get('pacer_case_id')
        },
        "timeline": {
            "date_filed": docket.get('date_filed'),
            "date_terminated": docket.get('date_terminated'),
            "date_last_filing": docket.get('date_last_filing'),
            "date_argued": docket.get('date_argued'),
            "date_reargued": docket.get('date_reargued'),
            "date_cert_granted": docket.get('date_cert_granted'),
            "date_cert_denied": docket.get('date_cert_denied'),
            "date_reargument_denied": docket.get('date_reargument_denied')
        },
        "case_classification": {
            "nature_of_suit": nature_of_suit_display,
            "nature_of_suit_raw": nature_of_suit_raw,
            "cause": docket.get('cause'),
            "jurisdiction_type": docket.get('jurisdiction_type'),
            "jury_demand": docket.get('jury_demand'),
            "appellate_case_type": docket.get('appellate_case_type_information'),
            "appellate_fee_status": docket.get('appellate_fee_status'),
            "mdl_status": docket.get('mdl_status')
        },
        "judges_and_panel": {
            "assigned_to": docket.get('assigned_to_str'),
            "referred_to": docket.get('referred_to_str'),
            "panel": docket.get('panel_str')
        },
        "federal_details": {
            "office_code": docket.get('federal_dn_office_code'),
            "case_type": docket.get('federal_dn_case_type'),
            "judge_initials_assigned": docket.get('federal_dn_judge_initials_assigned'),
            "judge_initials_referred": docket.get('federal_dn_judge_initials_referred'),
            "defendant_number": docket.get('federal_defendant_number')
        },
        "status_and_source": {
            "blocked": docket.get('blocked', False),
            "date_blocked": docket.get('date_blocked'),
            "source": get_enhanced_source_display(docket.get('source', 0)),
            "source_code": docket.get('source'),
            "date_created": docket.get('date_created'),
            "date_modified": docket.get('date_modified')
        }
    }
    
    # Add enhanced IDB data analysis with all code conversions
    idb_data = docket.get('idb_data')
    if idb_data:
        case_summary["integrated_database_info"] = {
            "dataset_source": get_dataset_source_display(idb_data.get('dataset_source')) if idb_data.get('dataset_source') else None,
            "dataset_source_code": idb_data.get('dataset_source'),
            
            "origin": get_origin_display(idb_data.get('origin')) if idb_data.get('origin') else None,
            "origin_code": idb_data.get('origin'),
            
            "jurisdiction": get_jurisdiction_display(idb_data.get('jurisdiction')) if idb_data.get('jurisdiction') else None,
            "jurisdiction_code": idb_data.get('jurisdiction'),
            
            "nature_of_suit": get_nature_of_suit_display(idb_data.get('nature_of_suit')) if idb_data.get('nature_of_suit') else None,
            "nature_of_suit_code": idb_data.get('nature_of_suit'),
            
            "disposition": get_disposition_display(idb_data.get('disposition')) if idb_data.get('disposition') else None,
            "disposition_code": idb_data.get('disposition'),
            
            "procedural_progress": get_procedural_progress_display(idb_data.get('procedural_progress')) if idb_data.get('procedural_progress') else None,
            "procedural_progress_code": idb_data.get('procedural_progress'),
            
            "judgment": get_judgment_display(idb_data.get('judgment')) if idb_data.get('judgment') else None,
            "judgment_code": idb_data.get('judgment'),
            
            "nature_of_judgement": get_nature_of_judgement_display(idb_data.get('nature_of_judgement')) if idb_data.get('nature_of_judgement') else None,
            "nature_of_judgement_code": idb_data.get('nature_of_judgement'),
            
            "arbitration_at_filing": get_arbitration_display(idb_data.get('arbitration_at_filing')) if idb_data.get('arbitration_at_filing') else None,
            "arbitration_at_termination": get_arbitration_display(idb_data.get('arbitration_at_termination')) if idb_data.get('arbitration_at_termination') else None,
            
            "termination_class_action_status": get_termination_class_action_status_display(idb_data.get('termination_class_action_status')) if idb_data.get('termination_class_action_status') else None,
            
            "pro_se": get_pro_se_display(idb_data.get('pro_se')) if idb_data.get('pro_se') is not None else None,
            "pro_se_code": idb_data.get('pro_se'),
            
            # Financial and case details
            "monetary_demand": idb_data.get('monetary_demand'),
            "amount_received": idb_data.get('amount_received'),
            "class_action": idb_data.get('class_action'),
            "plaintiff": idb_data.get('plaintiff'),
            "defendant": idb_data.get('defendant'),
            "date_filed": idb_data.get('date_filed'),
            "date_terminated": idb_data.get('date_terminated'),
            
            # Additional metadata
            "office": idb_data.get('office'),
            "docket_number": idb_data.get('docket_number'),
            "title": idb_data.get('title'),
            "section": idb_data.get('section'),
            "subsection": idb_data.get('subsection'),
            "diversity_of_residence": idb_data.get('diversity_of_residence'),
            "county_of_residence": idb_data.get('county_of_residence'),
            "multidistrict_litigation_docket_number": idb_data.get('multidistrict_litigation_docket_number'),
            "year_of_tape": idb_data.get('year_of_tape'),
            "nature_of_offense": idb_data.get('nature_of_offense'),
            "version": idb_data.get('version')
        }
    
    # Fetch court information
    court_id = docket.get('court_id')
    if court_id:
        try:
            court_response = await courtlistener_ctx.http_client.get(
                f"{courtlistener_ctx.base_url}/courts/{court_id}/"
            )
            if court_response.status_code == 200:
                court_data = court_response.json()
                case_summary["court_info"]["court_name"] = court_data.get('full_name', court_id)
                case_summary["court_info"]["jurisdiction"] = court_data.get('jurisdiction')
                case_summary["court_info"]["court_type"] = court_data.get('position')
        except Exception as e:
            logger.warning(f"Failed to fetch court {court_id}: {e}")
            case_summary["court_info"]["court_name"] = court_id
    
    # Fetch related opinion clusters if requested
    if include_clusters:
        clusters = docket.get('clusters', [])
        case_summary["opinions_summary"] = {
            "cluster_count": len(clusters),
            "clusters": []
        }
        
        for cluster_url in clusters[:5]:
            try:
                cluster_id = cluster_url.rstrip('/').split('/')[-1]
                cluster_response = await courtlistener_ctx.http_client.get(
                    f"{courtlistener_ctx.base_url}/clusters/{cluster_id}/"
                )
                if cluster_response.status_code == 200:
                    cluster_data = cluster_response.json()
                    
                    citations = safe_extract_citations(cluster_data.get('citations', []))
                    
                    cluster_info = {
                        "cluster_id": cluster_id,
                        "date_filed": cluster_data.get('date_filed'),
                        "citations": citations,
                        "judges": cluster_data.get('judges'),
                        "opinion_count": len(cluster_data.get('sub_opinions', [])),
                        "case_name": cluster_data.get('case_name'),
                        "precedential_status": cluster_data.get('precedential_status')
                    }
                    case_summary["opinions_summary"]["clusters"].append(cluster_info)
            except Exception as e:
                logger.warning(f"Failed to fetch cluster from {cluster_url}: {e}")
    
    # Add Internet Archive links if available
    if docket.get('filepath_ia') or docket.get('filepath_ia_json'):
        case_summary["archive_links"] = {
            "ia_docket_xml": docket.get('filepath_ia'),
            "ia_docket_json": docket.get('filepath_ia_json')
        }
    
    return case_summary