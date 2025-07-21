"""
CourtListener Opinion Analysis Tools

Comprehensive court opinion retrieval, analysis, and content interpretation.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import get_opinion_type_display, safe_extract_citations
from utils.formatters import format_opinion_analyses

logger = logging.getLogger(__name__)


def register_opinion_tools(mcp: FastMCP):
    """Register all opinion-related tools with the MCP server."""
    
    @mcp.tool()
    async def get_opinion(
        opinion_id: Optional[int] = None,
        court: Optional[str] = None,
        docket_number: Optional[str] = None,
        opinion_type: Optional[str] = None,
        author_name: Optional[str] = None,
        date_filed_after: Optional[str] = None,
        date_filed_before: Optional[str] = None,
        per_curiam: Optional[bool] = None,
        extracted_by_ocr: Optional[bool] = None,
        date_created_after: Optional[str] = None,
        date_created_before: Optional[str] = None,
        include_full_text: bool = True,
        include_citations: bool = True,
        analyze_content: bool = True,
        limit: int = 10
    ) -> str:
        """
        Retrieve and analyze court opinions from CourtListener with comprehensive content analysis.
        
        Args:
            opinion_id: Specific opinion ID to retrieve
            court: Court identifier (e.g., 'scotus', 'ca9', 'dcd') - filters by cluster__docket__court
            docket_number: Case docket number (e.g., '23A994', '1:16-cv-00745') - filters by cluster__docket__docket_number
            opinion_type: Type of opinion ('010combined', '020lead', '030concurrence', '040dissent', etc.)
            author_name: Name of opinion author (partial match in author_str field)
            date_filed_after: Filter opinions filed after this date (YYYY-MM-DD) - uses cluster__date_filed__gte
            date_filed_before: Filter opinions filed before this date (YYYY-MM-DD) - uses cluster__date_filed__lte
            per_curiam: Filter for per curiam opinions (True/False)
            extracted_by_ocr: Filter for OCR-extracted opinions (True/False)
            date_created_after: Filter opinions created after this date (YYYY-MM-DD)
            date_created_before: Filter opinions created before this date (YYYY-MM-DD)
            include_full_text: Whether to include the complete opinion text for LLM analysis
            include_citations: Whether to include cited opinions analysis
            analyze_content: Whether to provide detailed content analysis and summary
            limit: Maximum number of results (1-20)
        
        Returns:
            Comprehensive opinion analysis including case summary, legal holdings, and full text for LLM analysis
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters with CORRECT API filter names
            params = {}
            
            if opinion_id:
                # Direct opinion lookup
                url = f"{courtlistener_ctx.base_url}/opinions/{opinion_id}/"
                logger.info(f"Fetching opinion by ID: {opinion_id}")
            else:
                # Build filtered query with CORRECT filter names per API metadata
                url = f"{courtlistener_ctx.base_url}/opinions/"
                
                # Nested filters for related objects (cluster, docket, court)
                if court:
                    params['cluster__docket__court'] = court.lower()
                if docket_number:
                    params['cluster__docket__docket_number'] = docket_number
                if date_filed_after:
                    params['cluster__date_filed__gte'] = date_filed_after
                if date_filed_before:
                    params['cluster__date_filed__lte'] = date_filed_before
                
                # Direct opinion filters
                if opinion_type:
                    params['type'] = opinion_type
                if author_name:
                    params['author_str__icontains'] = author_name
                if per_curiam is not None:
                    params['per_curiam'] = per_curiam
                if extracted_by_ocr is not None:
                    params['extracted_by_ocr'] = extracted_by_ocr
                if date_created_after:
                    params['date_created__gte'] = date_created_after
                if date_created_before:
                    params['date_created__lte'] = date_created_before
                
                # Limit results for thorough analysis
                params['ordering'] = '-cluster__date_filed'  # Most recent first
                params['page_size'] = min(max(1, limit), 20)  # Limit for thorough analysis
                
                logger.info(f"Searching opinions with API-compliant filters: {params}")
            
            # Make API request
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            if opinion_id:
                opinions = [data]
            else:
                opinions = data.get('results', [])
                if not opinions:
                    return f"No opinions found matching the specified criteria."
            
            # Build comprehensive analysis
            result = {
                "total_found": len(opinions) if opinion_id else data.get('count', len(opinions)),
                "returned": len(opinions),
                "analyses": []
            }
            
            for opinion in opinions:
                # Get comprehensive opinion analysis
                analysis = await analyze_opinion_thoroughly(
                    opinion, courtlistener_ctx, include_full_text, include_citations, analyze_content
                )
                result["analyses"].append(analysis)
            
            return f"""COMPREHENSIVE OPINION ANALYSIS
Found {result['returned']} opinion(s) out of {result['total_found']} total matches:

{format_opinion_analyses(result['analyses'])}

💡 This analysis includes case context, legal holdings, and full text for LLM interpretation.
🔍 All codes have been converted to human-readable values."""
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Opinion not found. Please check the opinion ID or search criteria."
            elif e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error fetching opinion: {e}")
                return f"Error fetching opinion: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error fetching opinion: {e}", exc_info=True)
            return f"Error fetching opinion: {str(e)}\n\nDetails: {type(e).__name__}"


async def analyze_opinion_thoroughly(opinion: dict, courtlistener_ctx, include_full_text: bool, include_citations: bool, analyze_content: bool) -> dict:
    """Provide thorough analysis of a court opinion including content analysis."""
    
    # Get best available opinion text
    opinion_text, text_source = extract_best_opinion_text(opinion)
    
    # Basic opinion metadata with human-readable type conversion
    analysis = {
        "id": opinion.get('id'),
        "absolute_url": f"https://www.courtlistener.com{opinion.get('absolute_url', '')}",
        "type": opinion.get('type'),
        "type_display": get_opinion_type_display(opinion.get('type')),
        "authorship": {
            "author_name": opinion.get('author_str', 'Unknown'),
            "author_id": opinion.get('author_id'),
            "per_curiam": opinion.get('per_curiam', False),
            "joined_by": opinion.get('joined_by_str', '')
        },
        "technical_details": {
            "page_count": opinion.get('page_count'),
            "sha1": opinion.get('sha1', ''),
            "extracted_by_ocr": opinion.get('extracted_by_ocr', False),
            "text_source": text_source,
            "text_length": len(opinion_text) if opinion_text else 0,
            "ordering_key": opinion.get('ordering_key'),
            "download_url": opinion.get('download_url'),
            "local_path": opinion.get('local_path')
        }
    }
    
    # Fetch comprehensive cluster information for case context
    cluster_id = opinion.get('cluster_id')
    if cluster_id:
        try:
            cluster_response = await courtlistener_ctx.http_client.get(
                f"{courtlistener_ctx.base_url}/clusters/{cluster_id}/"
            )
            if cluster_response.status_code == 200:
                cluster_data = cluster_response.json()
                
                # Process citations safely
                citations = safe_extract_citations(cluster_data.get('citations', []))
                
                analysis["case_context"] = {
                    "case_name": cluster_data.get('case_name', ''),
                    "case_name_full": cluster_data.get('case_name_full', ''),
                    "date_filed": cluster_data.get('date_filed'),
                    "citations": citations,
                    "judges": cluster_data.get('judges', ''),
                    "precedential_status": cluster_data.get('precedential_status'),
                    "source": cluster_data.get('source'),
                    "syllabus": cluster_data.get('syllabus', ''),
                    "headnotes": cluster_data.get('headnotes', ''),
                    "summary": cluster_data.get('summary', '')
                }
                
                # Get docket information for additional context
                docket_url = cluster_data.get('docket')
                if docket_url:
                    try:
                        docket_id = docket_url.rstrip('/').split('/')[-1]
                        docket_response = await courtlistener_ctx.http_client.get(
                            f"{courtlistener_ctx.base_url}/dockets/{docket_id}/"
                        )
                        if docket_response.status_code == 200:
                            docket_data = docket_response.json()
                            analysis["case_context"]["docket_info"] = {
                                "docket_number": docket_data.get('docket_number'),
                                "nature_of_suit": docket_data.get('nature_of_suit'),
                                "court_id": docket_data.get('court_id'),
                                "assigned_judge": docket_data.get('assigned_to_str'),
                                "date_filed": docket_data.get('date_filed'),
                                "date_terminated": docket_data.get('date_terminated')
                            }
                    except Exception as e:
                        logger.warning(f"Failed to fetch docket for cluster {cluster_id}: {e}")
        except Exception as e:
            logger.warning(f"Failed to fetch cluster {cluster_id}: {e}")
    
    # Include full text for LLM analysis - ALWAYS include when available
    if include_full_text and opinion_text:
        # Always provide full text for LLM analysis, but with smart truncation if extremely long
        if len(opinion_text) > 100000:  # 100k characters - very long
            analysis["full_text_preview"] = opinion_text[:10000] + "\n\n[TRUNCATED - Full text continues...]"
            analysis["text_analysis"] = {
                "full_text_available": True,
                "text_length": len(opinion_text),
                "truncation_note": "Text truncated at 10,000 characters for readability. Full analysis available in content_analysis section."
            }
        else:
            # Include full text for LLM analysis
            analysis["full_text"] = opinion_text
    elif include_full_text and not opinion_text:
        analysis["text_analysis"] = {
            "full_text_available": False,
            "text_length": 0,
            "note": "No text content available for this opinion."
        }
    
    # Provide content analysis if requested
    if analyze_content and opinion_text:
        analysis["content_analysis"] = analyze_opinion_content(opinion_text, analysis.get("case_context", {}))
    
    # Include citations analysis if requested
    if include_citations:
        cited_opinions = opinion.get('opinions_cited', [])
        analysis["citations_analysis"] = {
            "total_citations": len(cited_opinions),
            "cited_opinions": cited_opinions[:10] if cited_opinions else []  # First 10
        }
    
    return analysis


def extract_best_opinion_text(opinion: dict) -> tuple[Optional[str], str]:
    """Extract the best available opinion text using priority order from API metadata."""
    text_fields = [
        ('html_with_citations', 'HTML with citations'),
        ('html_columbia', 'Columbia HTML'),
        ('html_lawbox', 'Lawbox HTML'),
        ('xml_harvard', 'Harvard XML'),
        ('html_anon_2020', 'Anonymous 2020 HTML'),
        ('html', 'Original HTML'),
        ('plain_text', 'Plain text')
    ]
    
    for field, source in text_fields:
        field_value = opinion.get(field)
        if field_value and field_value.strip():
            return field_value, source
    
    return None, "No text available"


def analyze_opinion_content(text: str, case_context: dict) -> dict:
    """Analyze opinion content to extract key legal information."""
    if not text:
        return {"error": "No text available for analysis"}
    
    # Clean and prepare text for analysis
    clean_text = text[:10000]  # First 10k characters for analysis
    
    # Basic content analysis
    analysis = {
        "word_count": len(text.split()),
        "character_count": len(text),
        "has_substantial_content": len(text.strip()) > 1000,
    }
    
    # Extract key sections (basic pattern matching)
    sections = {}
    
    # Look for common legal opinion sections
    import re
    
    # Look for holdings/conclusions
    holding_patterns = [
        r"(HELD|HOLDING|CONCLUSION|CONCLUDING)[\s:]+(.{0,500})",
        r"(We hold|We conclude|We find|We decide)[\s]+(.{0,300})",
        r"(Therefore|Accordingly|Thus),?\s+(.{0,300})"
    ]
    
    holdings = []
    for pattern in holding_patterns:
        matches = re.finditer(pattern, clean_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            holdings.append(match.group().strip())
    
    if holdings:
        sections["key_holdings"] = holdings[:3]  # First 3 holdings
    
    # Look for procedural information
    procedural_patterns = [
        r"(REVERSED|AFFIRMED|REMANDED|VACATED|DISMISSED)(?:\s+and\s+(REMANDED|VACATED))?",
        r"(The judgment|The decision|The order)[\s]+(?:of the|is)\s+(.{0,200})",
        r"(APPEAL FROM|PETITION FOR|APPLICATION FOR)[\s]+(.{0,200})"
    ]
    
    procedural_info = []
    for pattern in procedural_patterns:
        matches = re.finditer(pattern, clean_text, re.IGNORECASE)
        for match in matches:
            procedural_info.append(match.group().strip())
    
    if procedural_info:
        sections["procedural_disposition"] = procedural_info[:2]  # First 2
    
    # Extract factual background indicators
    fact_patterns = [
        r"(BACKGROUND|FACTS?|FACTUAL BACKGROUND)[\s\n]*(.{0,1000})",
        r"(The facts|This case|This appeal)[\s]+(.{0,500})"
    ]
    
    factual_background = []
    for pattern in fact_patterns:
        matches = re.finditer(pattern, clean_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            factual_background.append(match.group(2).strip())
    
    if factual_background:
        sections["factual_background"] = factual_background[0][:800]  # First match, limited
    
    analysis["extracted_sections"] = sections
    
    # Add case context summary
    if case_context:
        analysis["case_summary"] = {
            "case_name": case_context.get('case_name', 'Unknown'),
            "date_decided": case_context.get('date_filed', 'Unknown'),
            "precedential_status": case_context.get('precedential_status', 'Unknown'),
            "primary_citations": case_context.get('citations', [])[:2]  # First 2 citations
        }
    
    return analysis