"""
CourtListener Legal Search Tools

Comprehensive search capabilities across case law, PACER documents, judges, and oral arguments.
Uses CourtListener's search engine API with advanced query operators and filtering.
"""

import logging
from typing import Optional, List
from urllib.parse import quote_plus

import httpx
from mcp.server.fastmcp import FastMCP

from utils.mappings import (
    get_cluster_source_display_enhanced, get_precedential_status_display_enhanced,
    get_opinion_type_display
)

logger = logging.getLogger(__name__)


def register_search_tools(mcp: FastMCP):
    """Register all search-related tools with the MCP server."""
    
    @mcp.tool()
    async def search_legal_cases(
        query: str,
        search_type: str = "o",
        court: Optional[str] = None,
        judge: Optional[str] = None,
        date_filed_after: Optional[str] = None,
        date_filed_before: Optional[str] = None,
        citation: Optional[str] = None,
        case_name: Optional[str] = None,
        docket_number: Optional[str] = None,
        status: Optional[str] = None,
        order_by: Optional[str] = None,
        enable_highlighting: bool = True,
        limit: int = 20
    ) -> str:
        """
        Search across CourtListener's comprehensive legal database using advanced search capabilities.
        
        Args:
            query: Main search query (supports advanced operators like AND, OR, quotes, field searches)
            search_type: Type of search ('o'=case law [default], 'r'=federal cases, 'rd'=PACER docs, 'd'=dockets, 'p'=judges, 'oa'=oral arguments)
            court: Court filter (e.g., 'scotus', 'ca9', 'dcd') 
            judge: Judge name filter
            date_filed_after: Show results filed after this date (YYYY-MM-DD)
            date_filed_before: Show results filed before this date (YYYY-MM-DD)
            citation: Citation filter (e.g., '576 U.S. 644')
            case_name: Case name filter
            docket_number: Docket number filter
            status: Precedential status filter ('Published', 'Unpublished', etc.)
            order_by: Sort order ('relevance', 'dateFiled desc', 'citeCount desc', etc.)
            enable_highlighting: Whether to highlight search terms in results
            limit: Maximum number of results (1-100)
        
        Returns:
            Comprehensive search results formatted for legal research with highlighting and relevance scoring
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build search parameters
            params = {
                'q': query,
                'type': search_type,
                'format': 'json'
            }
            
            # Add optional filters
            if court:
                params['court'] = court
            if judge:
                params['judge'] = judge
            if date_filed_after:
                params['filed_after'] = date_filed_after
            if date_filed_before:
                params['filed_before'] = date_filed_before
            if citation:
                params['citation'] = citation
            if case_name:
                params['case_name'] = case_name
            if docket_number:
                params['docket_number'] = docket_number
            if status:
                params['stat_Published'] = 'on' if status == 'Published' else ''
                params['stat_Unpublished'] = 'on' if status == 'Unpublished' else ''
            if order_by:
                params['order_by'] = order_by
            if enable_highlighting:
                params['highlight'] = 'on'
            
            # Set page size
            params['page_size'] = min(max(1, limit), 100)
            
            logger.info(f"Performing {get_search_type_name(search_type)} search with query: '{query}'")
            
            # Make search request
            url = f"{courtlistener_ctx.base_url}/search/"
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results based on search type
            results = data.get('results', [])
            total_count = data.get('count', 0)
            
            if not results:
                return f"No results found for query: '{query}' in {get_search_type_name(search_type)} search."
            
            # Format results based on search type
            formatted_results = await format_search_results(results, search_type, courtlistener_ctx)
            
            # Build response
            search_summary = f"""LEGAL SEARCH RESULTS
Search Type: {get_search_type_name(search_type)}
Query: "{query}"
Results: Showing {len(results)} of {total_count:,} total matches
Highlighting: {'Enabled' if enable_highlighting else 'Disabled'}

{formatted_results}

💡 Use advanced operators in your query: AND, OR, "exact phrases", field:value
🔍 Search types: o=case law, r=federal cases, rd=PACER docs, d=dockets, p=judges, oa=oral arguments"""

            return search_summary
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return f"Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error in search: {e}")
                return f"Search error: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error in legal search: {e}", exc_info=True)
            return f"Search error: {str(e)}\n\nDetails: {type(e).__name__}"

    
    @mcp.tool()
    async def advanced_legal_search(
        query: str,
        search_type: str = "o",
        courts: Optional[List[str]] = None,
        date_range: Optional[str] = None,
        advanced_filters: Optional[dict] = None,
        order_by: str = "relevance",
        enable_highlighting: bool = True,
        limit: int = 20
    ) -> str:
        """
        Perform advanced legal search with complex filtering and multiple courts.
        
        Args:
            query: Advanced search query with operators (AND, OR, "phrases", field:value)
            search_type: Search type ('o'=case law, 'r'=federal cases, 'rd'=PACER docs, 'd'=dockets, 'p'=judges, 'oa'=oral arguments)
            courts: List of court IDs to search (e.g., ['scotus', 'ca9', 'dcd'])
            date_range: Date range string (e.g., 'last_month', 'last_year', '2020-2025')
            advanced_filters: Dictionary of additional filters (status, cite_count, etc.)
            order_by: Sort order ('relevance', 'dateFiled desc', 'citeCount desc', 'random')
            enable_highlighting: Whether to highlight search terms
            limit: Maximum results (1-100)
        
        Returns:
            Advanced search results with comprehensive legal analysis and relevance scoring
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build advanced query
            enhanced_query = query
            
            # Add court filters to query if specified
            if courts:
                court_filter = " OR ".join([f"court:{court}" for court in courts])
                enhanced_query = f"({enhanced_query}) AND ({court_filter})"
            
            # Add date range to query if specified
            if date_range:
                if date_range == 'last_month':
                    enhanced_query = f"({enhanced_query}) AND dateFiled:[now-1M TO now]"
                elif date_range == 'last_year':
                    enhanced_query = f"({enhanced_query}) AND dateFiled:[now-1y TO now]"
                elif '-' in date_range and len(date_range.split('-')) == 2:
                    start_year, end_year = date_range.split('-')
                    enhanced_query = f"({enhanced_query}) AND dateFiled:[{start_year}-01-01 TO {end_year}-12-31]"
            
            # Apply advanced filters
            if advanced_filters:
                for field, value in advanced_filters.items():
                    if value:
                        enhanced_query = f"({enhanced_query}) AND {field}:{value}"
            
            # Use the basic search with enhanced query
            return await search_legal_cases(
                query=enhanced_query,
                search_type=search_type,
                order_by=order_by,
                enable_highlighting=enable_highlighting,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error in advanced legal search: {e}", exc_info=True)
            return f"Advanced search error: {str(e)}"


def get_search_type_name(search_type: str) -> str:
    """Convert search type code to human-readable name."""
    type_names = {
        'o': 'Case Law Opinion Clusters',
        'r': 'Federal Cases (with documents)',
        'rd': 'Federal Filing Documents',
        'd': 'Federal Dockets',
        'p': 'Judges', 
        'oa': 'Oral Arguments'
    }
    return type_names.get(search_type, f"Unknown type ({search_type})")


async def format_search_results(results: list, search_type: str, courtlistener_ctx) -> str:
    """Format search results based on search type."""
    if search_type == 'o':
        return format_case_law_results(results)
    elif search_type in ['r', 'd']:
        return format_federal_case_results(results)
    elif search_type == 'rd':
        return format_document_results(results)
    elif search_type == 'p':
        return format_judge_results(results)
    elif search_type == 'oa':
        return format_oral_argument_results(results)
    else:
        return format_generic_results(results)


def format_case_law_results(results: list) -> str:
    """Format case law search results with comprehensive legal information."""
    formatted_lines = []
    
    for i, result in enumerate(results, 1):
        lines = [
            f"{'='*60}",
            f"CASE {i}: {result.get('caseName', 'Unknown Case')}",
            f"{'='*60}",
            f"📋 Cluster ID: {result.get('cluster_id', 'N/A')}",
            f"🏛️  Court: {result.get('court', 'Unknown')} ({result.get('court_id', 'N/A')})",
            f"📅 Date Filed: {result.get('dateFiled', 'Unknown')}",
            f"📄 Docket: {result.get('docketNumber', 'N/A')}",
            f"🔗 URL: https://www.courtlistener.com{result.get('absolute_url', '')}"
        ]
        
        # Citations
        citations = result.get('citation', [])
        if citations:
            lines.append(f"📚 Citations: {', '.join(citations)}")
        
        # Legal significance
        cite_count = result.get('citeCount', 0)
        status = result.get('status', 'Unknown')
        status_display = get_precedential_status_display_enhanced(status)
        lines.append(f"⚖️  Status: {status_display}")
        lines.append(f"📊 Cited {cite_count:,} times")
        
        # Source with human-readable conversion
        source = result.get('source', '')
        source_display = get_cluster_source_display_enhanced(source)
        lines.append(f"📁 Source: {source_display}")
        
        # Judges
        judge = result.get('judge', '')
        if judge:
            lines.append(f"👨‍⚖️ Judges: {judge}")
        
        # Case content
        if result.get('syllabus'):
            syllabus = result['syllabus'][:300] + "..." if len(result['syllabus']) > 300 else result['syllabus']
            lines.append(f"\n📖 SYLLABUS: {syllabus}")
        
        if result.get('procedural_history'):
            history = result['procedural_history'][:300] + "..." if len(result['procedural_history']) > 300 else result['procedural_history']
            lines.append(f"\n📋 PROCEDURAL HISTORY: {history}")
        
        # Opinions
        opinions = result.get('opinions', [])
        if opinions:
            lines.append(f"\n📜 OPINIONS ({len(opinions)}):")
            for j, opinion in enumerate(opinions[:3], 1):  # Show first 3
                opinion_type = get_opinion_type_display(opinion.get('type', ''))
                lines.append(f"  {j}. {opinion_type}")
                if opinion.get('snippet'):
                    snippet = opinion['snippet'][:200] + "..." if len(opinion['snippet']) > 200 else opinion['snippet']
                    lines.append(f"     Preview: {snippet}")
        
        # Search relevance
        meta = result.get('meta', {})
        score = meta.get('score', {}).get('bm25', 0)
        lines.append(f"\n🎯 Relevance Score: {score:.4f}")
        
        formatted_lines.append('\n'.join(lines))
    
    return '\n\n'.join(formatted_lines)


def format_federal_case_results(results: list) -> str:
    """Format federal case/docket search results."""
    formatted_lines = []
    
    for i, result in enumerate(results, 1):
        lines = [
            f"{'='*60}",
            f"FEDERAL CASE {i}: {result.get('caseName', 'Unknown Case')}",
            f"{'='*60}",
            f"📋 Docket ID: {result.get('docket_id', 'N/A')}",
            f"📄 Docket Number: {result.get('docketNumber', 'N/A')}",
            f"🏛️  Court: {result.get('court', 'Unknown')}",
            f"📅 Date Filed: {result.get('dateFiled', 'Unknown')}"
        ]
        
        # Additional case details
        if result.get('suitNature'):
            lines.append(f"⚖️  Nature of Suit: {result['suitNature']}")
        if result.get('judge'):
            lines.append(f"👨‍⚖️ Judge: {result['judge']}")
        
        # Documents
        if 'more_docs' in result and result['more_docs']:
            lines.append(f"📎 Documents: 3+ available (more exist)")
        
        # Search relevance
        meta = result.get('meta', {})
        score = meta.get('score', {}).get('bm25', 0)
        lines.append(f"🎯 Relevance Score: {score:.4f}")
        
        formatted_lines.append('\n'.join(lines))
    
    return '\n\n'.join(formatted_lines)


def format_document_results(results: list) -> str:
    """Format PACER document search results.""" 
    formatted_lines = []
    
    for i, result in enumerate(results, 1):
        lines = [
            f"{'='*60}",
            f"DOCUMENT {i}: {result.get('short_description', 'Unknown Document')}",
            f"{'='*60}",
            f"📋 Document ID: {result.get('id', 'N/A')}",
            f"📄 Description: {result.get('description', 'N/A')}",
            f"📅 Date Filed: {result.get('date_filed', 'Unknown')}"
        ]
        
        if result.get('snippet'):
            snippet = result['snippet'][:300] + "..." if len(result['snippet']) > 300 else result['snippet']
            lines.append(f"\n📖 CONTENT PREVIEW: {snippet}")
        
        formatted_lines.append('\n'.join(lines))
    
    return '\n\n'.join(formatted_lines)


def format_judge_results(results: list) -> str:
    """Format judge search results."""
    formatted_lines = []
    
    for i, result in enumerate(results, 1):
        lines = [
            f"{'='*60}",
            f"JUDGE {i}: {result.get('name', 'Unknown Judge')}",
            f"{'='*60}",
            f"📋 Judge ID: {result.get('id', 'N/A')}",
            f"🏛️  Court: {result.get('court', 'Unknown')}"
        ]
        
        if result.get('date_start'):
            lines.append(f"📅 Service Start: {result['date_start']}")
        if result.get('date_termination'):
            lines.append(f"📅 Service End: {result['date_termination']}")
        
        formatted_lines.append('\n'.join(lines))
    
    return '\n\n'.join(formatted_lines)


def format_oral_argument_results(results: list) -> str:
    """Format oral argument search results."""
    formatted_lines = []
    
    for i, result in enumerate(results, 1):
        lines = [
            f"{'='*60}",
            f"ORAL ARGUMENT {i}: {result.get('case_name', 'Unknown Case')}",
            f"{'='*60}",
            f"📋 Audio ID: {result.get('id', 'N/A')}",
            f"🏛️  Court: {result.get('court', 'Unknown')}",
            f"📅 Date Argued: {result.get('date_argued', 'Unknown')}"
        ]
        
        if result.get('duration'):
            lines.append(f"⏱️ Duration: {result['duration']} seconds")
        
        formatted_lines.append('\n'.join(lines))
    
    return '\n\n'.join(formatted_lines)


def format_generic_results(results: list) -> str:
    """Generic result formatter for unknown search types."""
    formatted_lines = []
    
    for i, result in enumerate(results, 1):
        lines = [f"RESULT {i}:"]
        for key, value in result.items():
            if key != 'meta' and value:
                lines.append(f"  {key}: {value}")
        formatted_lines.append('\n'.join(lines))
    
    return '\n\n'.join(formatted_lines)