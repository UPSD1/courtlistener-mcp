"""
CourtListener Opinions Cited Analysis Tools

Citation network analysis for understanding legal precedent and influence.
Powered by Eyecite - tracks millions of citations between legal decisions.
"""

import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

from utils.formatters import format_citation_network_results

logger = logging.getLogger(__name__)


def register_opinions_cited_tools(mcp: FastMCP):
    """Register citation network analysis tools with the MCP server."""
    
    @mcp.tool()
    async def find_authorities_cited(
        opinion_id: int,
        include_opinion_details: bool = True,
        order_by: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """
        Find legal authorities and precedents that a specific opinion cites.
        
        Analyzes backward citations to understand what precedents and authorities
        the opinion relies upon in its legal reasoning.
        
        Args:
            opinion_id: CourtListener opinion ID to analyze
            include_opinion_details: Whether to fetch full details for cited opinions
            order_by: Sort order ('id', 'depth', or with '-' prefix for descending)
            limit: Maximum number of authorities to retrieve (1-200)
        
        Returns:
            Analysis of legal authorities cited by the opinion
        
        Examples:
            # Find what Obergefell v. Hodges cites
            find_authorities_cited(opinion_id=2812209)
            
            # Focus on most heavily cited authorities
            find_authorities_cited(opinion_id=2812209, order_by="-depth", limit=20)
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters
            params = {
                'citing_opinion': opinion_id,
                'page_size': min(max(1, limit), 200)
            }
            
            if order_by:
                # Validate ordering field
                valid_orders = ['id', 'depth']
                order_field = order_by.lstrip('-')
                if order_field in valid_orders:
                    params['ordering'] = order_by
                else:
                    logger.warning(f"Invalid order_by field: {order_by}. Using default.")
                    params['ordering'] = '-depth'  # Most cited first
            else:
                params['ordering'] = '-depth'
            
            logger.info(f"Finding authorities cited by opinion {opinion_id}")
            
            # Make API request
            url = f"{courtlistener_ctx.base_url}/opinions-cited/"
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            citations = data.get('results', [])
            total_count = data.get('count', 0)
            
            if not citations:
                return f"❌ No authorities found for opinion {opinion_id}.\n\n💡 This opinion may not cite other cases, or citation data may not be available."
            
            # Fetch source opinion details
            source_opinion = await fetch_opinion_details(opinion_id, courtlistener_ctx)
            
            # Build analysis with opinion details if requested
            analysis = {
                'type': 'authorities',
                'source_opinion': source_opinion,
                'total_found': total_count,
                'citations': []
            }
            
            for citation in citations:
                citation_analysis = await analyze_citation_relationship(
                    citation, 'cited', courtlistener_ctx, include_opinion_details
                )
                analysis['citations'].append(citation_analysis)
            
            return format_citation_network_results(analysis)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"❌ Opinion {opinion_id} not found."
            elif e.response.status_code == 401:
                return "🔐 Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error in authorities analysis: {e}")
                return f"❌ Error analyzing authorities: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error in authorities analysis: {e}", exc_info=True)
            return f"❌ Error analyzing authorities: {str(e)}"

    
    @mcp.tool()
    async def find_citing_opinions(
        opinion_id: int,
        include_opinion_details: bool = True,
        order_by: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """
        Find later opinions that cite a specific opinion.
        
        Analyzes forward citations to understand the influence and impact
        of a legal decision on subsequent cases.
        
        Args:
            opinion_id: CourtListener opinion ID to analyze
            include_opinion_details: Whether to fetch full details for citing opinions
            order_by: Sort order ('id', 'depth', or with '-' prefix for descending) 
            limit: Maximum number of citing opinions to retrieve (1-200)
        
        Returns:
            Analysis of opinions that cite this decision
        
        Examples:
            # Find what cites Obergefell v. Hodges
            find_citing_opinions(opinion_id=2812209)
            
            # Focus on cases that cite it most heavily
            find_citing_opinions(opinion_id=2812209, order_by="-depth", limit=25)
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Build query parameters
            params = {
                'cited_opinion': opinion_id,
                'page_size': min(max(1, limit), 200)
            }
            
            if order_by:
                # Validate ordering field
                valid_orders = ['id', 'depth']
                order_field = order_by.lstrip('-')
                if order_field in valid_orders:
                    params['ordering'] = order_by
                else:
                    logger.warning(f"Invalid order_by field: {order_by}. Using default.")
                    params['ordering'] = '-depth'  # Most cited first
            else:
                params['ordering'] = '-depth'
            
            logger.info(f"Finding opinions citing opinion {opinion_id}")
            
            # Make API request
            url = f"{courtlistener_ctx.base_url}/opinions-cited/"
            response = await courtlistener_ctx.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            citations = data.get('results', [])
            total_count = data.get('count', 0)
            
            if not citations:
                return f"❌ No citing opinions found for opinion {opinion_id}.\n\n💡 This may be a very recent opinion, or it may not have been cited by other cases yet."
            
            # Fetch source opinion details
            source_opinion = await fetch_opinion_details(opinion_id, courtlistener_ctx)
            
            # Build analysis with opinion details if requested
            analysis = {
                'type': 'cited_by',
                'source_opinion': source_opinion,
                'total_found': total_count,
                'citations': []
            }
            
            for citation in citations:
                citation_analysis = await analyze_citation_relationship(
                    citation, 'citing', courtlistener_ctx, include_opinion_details
                )
                analysis['citations'].append(citation_analysis)
            
            return format_citation_network_results(analysis)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"❌ Opinion {opinion_id} not found."
            elif e.response.status_code == 401:
                return "🔐 Authentication failed. Please check your CourtListener API token."
            else:
                logger.error(f"HTTP error in citing analysis: {e}")
                return f"❌ Error analyzing citing opinions: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Error in citing analysis: {e}", exc_info=True)
            return f"❌ Error analyzing citing opinions: {str(e)}"

    
    @mcp.tool()
    async def analyze_citation_network(
        opinion_id: int,
        include_authorities: bool = True,
        include_citing: bool = True,
        authority_limit: int = 20,
        citing_limit: int = 20
    ) -> str:
        """
        Comprehensive citation network analysis for an opinion.
        
        Analyzes both backward citations (authorities) and forward citations
        (citing cases) to understand the opinion's place in legal precedent.
        
        Args:
            opinion_id: CourtListener opinion ID to analyze
            include_authorities: Whether to include authorities this opinion cites
            include_citing: Whether to include opinions that cite this one
            authority_limit: Maximum authorities to analyze (1-100)
            citing_limit: Maximum citing opinions to analyze (1-100)
        
        Returns:
            Comprehensive citation network analysis
        
        Examples:
            # Full network analysis
            analyze_citation_network(opinion_id=2812209)
            
            # Focus on influence (citing cases only)
            analyze_citation_network(opinion_id=2812209, include_authorities=False, citing_limit=50)
        """
        ctx = mcp.get_context()
        courtlistener_ctx = ctx.request_context.lifespan_context
        
        try:
            # Fetch source opinion details
            source_opinion = await fetch_opinion_details(opinion_id, courtlistener_ctx)
            if not source_opinion:
                return f"❌ Opinion {opinion_id} not found."
            
            analysis_parts = [
                "COMPREHENSIVE CITATION NETWORK ANALYSIS",
                "=" * 60,
                f"🎯 ANALYZING OPINION: {source_opinion.get('case_name', 'Unknown Case')}",
                f"📋 Opinion ID: {opinion_id}",
                f"🏛️ Court: {source_opinion.get('court', 'Unknown')}",
                f"📅 Date: {source_opinion.get('date_filed', 'Unknown')}",
                ""
            ]
            
            # Analyze authorities if requested
            if include_authorities:
                try:
                    authorities_result = await find_authorities_cited(
                        opinion_id=opinion_id,
                        include_opinion_details=True,
                        order_by="-depth",
                        limit=authority_limit
                    )
                    analysis_parts.extend([
                        "📚 PART I: LEGAL AUTHORITIES CITED",
                        "-" * 40,
                        authorities_result,
                        ""
                    ])
                except Exception as e:
                    analysis_parts.extend([
                        "📚 PART I: LEGAL AUTHORITIES CITED",
                        "-" * 40,
                        f"❌ Error analyzing authorities: {str(e)}",
                        ""
                    ])
            
            # Analyze citing opinions if requested
            if include_citing:
                try:
                    citing_result = await find_citing_opinions(
                        opinion_id=opinion_id,
                        include_opinion_details=True,
                        order_by="-depth",
                        limit=citing_limit
                    )
                    analysis_parts.extend([
                        "🔗 PART II: OPINIONS CITING THIS DECISION",
                        "-" * 40,
                        citing_result,
                        ""
                    ])
                except Exception as e:
                    analysis_parts.extend([
                        "🔗 PART II: OPINIONS CITING THIS DECISION",
                        "-" * 40,
                        f"❌ Error analyzing citing opinions: {str(e)}",
                        ""
                    ])
            
            # Add network summary
            analysis_parts.extend([
                "🕸️ CITATION NETWORK SUMMARY:",
                "• Use find_authorities_cited() for deeper authority analysis",
                "• Use find_citing_opinions() for deeper influence analysis", 
                "• Citation depth indicates frequency of reference",
                "• Higher depth suggests greater legal importance",
                "",
                "💡 Powered by Eyecite citation analysis engine"
            ])
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            logger.error(f"Error in network analysis: {e}", exc_info=True)
            return f"❌ Error in citation network analysis: {str(e)}"


async def fetch_opinion_details(opinion_id: int, courtlistener_ctx) -> dict:
    """Fetch detailed information about an opinion."""
    try:
        response = await courtlistener_ctx.http_client.get(
            f"{courtlistener_ctx.base_url}/opinions/{opinion_id}/"
        )
        if response.status_code == 200:
            opinion_data = response.json()
            
            # Also fetch cluster info for case name
            cluster_id = opinion_data.get('cluster_id')
            cluster_info = {}
            if cluster_id:
                try:
                    cluster_response = await courtlistener_ctx.http_client.get(
                        f"{courtlistener_ctx.base_url}/clusters/{cluster_id}/"
                    )
                    if cluster_response.status_code == 200:
                        cluster_info = cluster_response.json()
                except Exception:
                    pass
            
            return {
                'id': opinion_id,
                'case_name': cluster_info.get('case_name', 'Unknown Case'),
                'court': cluster_info.get('docket_id', 'Unknown'),  # Would need docket lookup for court name
                'date_filed': cluster_info.get('date_filed', 'Unknown'),
                'judges': cluster_info.get('judges', 'Unknown'),
                'citation_count': cluster_info.get('citation_count', 0),
                'precedential_status': cluster_info.get('precedential_status', 'Unknown'),
                'absolute_url': cluster_info.get('absolute_url', '')
            }
    except Exception as e:
        logger.warning(f"Failed to fetch opinion {opinion_id} details: {e}")
    
    return {'id': opinion_id, 'case_name': 'Unknown Case'}


async def analyze_citation_relationship(citation: dict, direction: str, courtlistener_ctx, include_details: bool) -> dict:
    """Analyze a single citation relationship with optional opinion details."""
    
    analysis = {
        'id': citation.get('id'),
        'depth': citation.get('depth', 0)
    }
    
    # Determine which opinion to fetch details for based on direction
    if direction == 'citing':
        # We want details about the opinion that's doing the citing
        opinion_url = citation.get('citing_opinion', '')
    else:  # direction == 'cited' 
        # We want details about the opinion being cited
        opinion_url = citation.get('cited_opinion', '')
    
    if include_details and opinion_url:
        try:
            # Extract opinion ID from URL
            opinion_id = opinion_url.rstrip('/').split('/')[-1]
            if opinion_id.isdigit():
                opinion_details = await fetch_opinion_details(int(opinion_id), courtlistener_ctx)
                analysis['opinion_details'] = opinion_details
        except Exception as e:
            logger.warning(f"Failed to fetch opinion details for {opinion_url}: {e}")
    
    return analysis
