"""
Multi-MCP Retriever Server for Search-R1
AI-driven tool selection with intelligent parameter conversion
"""

from fastapi import FastAPI
import uvicorn
import asyncio
import os
import logging
import json
import re
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel
from contextlib import AsyncExitStack, asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    queries: List[str]
    topk: Optional[int] = 3
    return_scores: bool = False

class MCPToolConverter:
    """Convert natural language to proper MCP tool parameters"""
    
    def __init__(self):
        self.default_limits = {
            'get_opinion': 5,
            'get_cluster': 5,
            'get_docket': 5,
            'search_legal_cases': 5,
            'advanced_legal_search': 5,
            'get_judge': 5,
            'get_political_affiliations': 5,
            'get_aba_ratings': 5,
            'get_retention_events': 5,
            'get_sources': 5,
            'get_educations': 5,
            'get_positions': 5,
            'verify_citations': 5,
            'find_authorities_cited': 5,
            'find_citing_opinions': 5,
            'analyze_citation_network': 5,
            'get_court': 5,
            'brave_web_search': 5
        }
    
    def parse_tool_request(self, tool_request: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse AI tool request in format 'toolname: query'
        Returns (tool_name, parameters)
        """
        
        if ':' not in tool_request:
            raise ValueError(f"Invalid format. Expected 'toolname: query', got: {tool_request}")
        
        tool_name, query = tool_request.split(':', 1)
        tool_name = tool_name.strip()
        query = query.strip()
        
        if tool_name not in self.default_limits:
            raise ValueError(f"Unknown tool: {tool_name}. Available tools: {list(self.default_limits.keys())}")
        
        # Convert query to parameters based on tool
        params = self._convert_to_params(tool_name, query)
        
        return tool_name, params
    
    def _convert_to_params(self, tool_name: str, query: str) -> Dict[str, Any]:
        """Convert query to proper MCP format"""
        
        # Try JSON first
        try:
            params = json.loads(query)
            return self._add_defaults(tool_name, params)
        except (json.JSONDecodeError, ValueError):
            return self._convert_natural_language(tool_name, query)
    
    def _add_defaults(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add default parameters"""
        if 'limit' not in params:
            params['limit'] = self.default_limits[tool_name]
        
        if tool_name == 'brave_web_search' and 'count' not in params:
            params['count'] = self.default_limits[tool_name]
        
        return params
    
    def _convert_natural_language(self, tool_name: str, query: str) -> Dict[str, Any]:
        """Convert natural language to tool parameters"""
        
        # Court Opinions & Cases
        if tool_name == 'get_opinion':
            return self._convert_get_opinion(query)
        elif tool_name == 'get_cluster':
            return self._convert_get_cluster(query)
        elif tool_name == 'get_docket':
            return self._convert_get_docket(query)
        elif tool_name in ['search_legal_cases', 'advanced_legal_search']:
            return self._convert_legal_search(query)
        
        # Judge & People Information
        elif tool_name == 'get_judge':
            return self._convert_get_judge(query)
        elif tool_name == 'get_political_affiliations':
            return self._convert_political_affiliations(query)
        elif tool_name == 'get_aba_ratings':
            return self._convert_aba_ratings(query)
        elif tool_name in ['get_retention_events', 'get_sources', 'get_educations', 'get_positions']:
            return self._convert_people_tools(tool_name, query)
        
        # Citation & Legal Analysis
        elif tool_name == 'verify_citations':
            return self._convert_verify_citations(query)
        elif tool_name in ['find_authorities_cited', 'find_citing_opinions', 'analyze_citation_network']:
            return self._convert_citation_analysis(tool_name, query)
        
        # Courts & Web Search
        elif tool_name == 'get_court':
            return self._convert_get_court(query)
        elif tool_name == 'brave_web_search':
            return self._convert_brave_search(query)
        
        else:
            return {"query": query, "limit": 10}
    
    def _convert_get_opinion(self, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits['get_opinion']}
        
        opinion_id = self._extract_id(query, 'opinion')
        if opinion_id:
            params['opinion_id'] = opinion_id
            return params
        
        case_name = self._extract_case_name(query)
        if case_name:
            params['case_name'] = case_name
        
        court = self._extract_court(query)
        if court:
            params['court'] = court
        
        return params
    
    def _convert_get_cluster(self, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits['get_cluster']}
        
        cluster_id = self._extract_id(query, 'cluster')
        if cluster_id:
            params['cluster_id'] = cluster_id
            return params
        
        case_name = self._extract_case_name(query)
        if case_name:
            params['case_name'] = case_name
        
        court = self._extract_court(query)
        if court:
            params['court'] = court
        
        return params
    
    def _convert_get_docket(self, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits['get_docket']}
        
        docket_id = self._extract_id(query, 'docket')
        if docket_id:
            params['docket_id'] = docket_id
            return params
        
        case_name = self._extract_case_name(query)
        if case_name:
            params['case_name'] = case_name
        
        return params
    
    def _convert_legal_search(self, query: str) -> Dict[str, Any]:
        params = {
            "query": query,
            "limit": self.default_limits['search_legal_cases']
        }
        
        court = self._extract_court(query)
        if court:
            params['court'] = court
        
        return params
    
    def _convert_get_judge(self, query: str) -> Dict[str, Any]:
        params = {
            "limit": self.default_limits['get_judge'],
            "include_positions": True,
            "include_educations": True,
            "include_political_affiliations": True,
            "include_aba_ratings": True
        }
        
        person_id = self._extract_id(query, 'person')
        if person_id:
            params['person_id'] = person_id
            return params
        
        names = self._extract_judge_name(query)
        if names['last']:
            params['name_last'] = names['last']
        if names['first']:
            params['name_first'] = names['first']
        
        return params
    
    def _convert_political_affiliations(self, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits['get_political_affiliations']}
        
        person_id = self._extract_id(query, 'person')
        if person_id:
            params['person_id'] = person_id
        
        party = self._extract_political_party(query)
        if party:
            params['political_party'] = party
        
        return params
    
    def _convert_aba_ratings(self, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits['get_aba_ratings']}
        
        person_id = self._extract_id(query, 'person')
        if person_id:
            params['person_id'] = person_id
        
        return params
    
    def _convert_people_tools(self, tool_name: str, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits[tool_name]}
        
        person_id = self._extract_id(query, 'person')
        if person_id:
            params['person_id'] = person_id
        
        return params
    
    def _convert_verify_citations(self, query: str) -> Dict[str, Any]:
        citation_match = re.search(r'(\d+)\s+([A-Za-z\.]+)\s+(\d+)', query)
        if citation_match:
            return {
                "volume": citation_match.group(1),
                "reporter": citation_match.group(2),
                "page": citation_match.group(3),
                "limit": self.default_limits['verify_citations']
            }
        
        return {
            "text": query,
            "limit": self.default_limits['verify_citations']
        }
    
    def _convert_citation_analysis(self, tool_name: str, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits[tool_name]}
        
        opinion_id = self._extract_id(query, 'opinion')
        if opinion_id:
            params['opinion_id'] = opinion_id
        
        if tool_name in ['find_authorities_cited', 'find_citing_opinions']:
            params['include_opinion_details'] = True
            params['order_by'] = '-depth'
        
        return params
    
    def _convert_get_court(self, query: str) -> Dict[str, Any]:
        params = {"limit": self.default_limits['get_court']}
        
        court = self._extract_court(query)
        if court:
            params['court_id'] = court
        
        if 'federal' in query.lower():
            params['jurisdiction'] = 'F'
        elif 'state' in query.lower():
            params['jurisdiction'] = 'S'
        
        return params
    
    def _convert_brave_search(self, query: str) -> Dict[str, Any]:
        params = {
            "query": query,
            "count": self.default_limits['brave_web_search']
        }
        
        if 'recent' in query.lower() or 'latest' in query.lower():
            params['freshness'] = 'pd'
        
        return params
    
    # Helper Methods
    def _extract_id(self, query: str, id_type: str) -> Optional[int]:
        patterns = [
            rf'{id_type}[_\s]*id[:\s]*(\d+)',
            rf'{id_type}[:\s]*(\d+)',
            rf'id[:\s]*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_case_name(self, query: str) -> Optional[str]:
        case_match = re.search(r'([A-Za-z\s]+)\s+v\.?\s+([A-Za-z\s]+)', query)
        if case_match:
            return f"{case_match.group(1).strip()} v. {case_match.group(2).strip()}"
        
        quoted_match = re.search(r'"([^"]+)"', query)
        if quoted_match:
            return quoted_match.group(1)
        
        return None
    
    def _extract_court(self, query: str) -> Optional[str]:
        courts = {
            'supreme court': 'scotus',
            'scotus': 'scotus',
            'ninth circuit': 'ca9',
            '9th circuit': 'ca9',
            'dc circuit': 'cadc',
            'd.c. circuit': 'cadc'
        }
        
        query_lower = query.lower()
        for court_name, court_id in courts.items():
            if court_name in query_lower:
                return court_id
        
        return None
    
    def _extract_judge_name(self, query: str) -> Dict[str, Optional[str]]:
        names = {"first": None, "last": None}
        
        clean_query = re.sub(r'\b(Justice|Judge|Chief|Associate)\b', '', query, flags=re.IGNORECASE).strip()
        
        name_match = re.search(r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b', clean_query)
        if name_match:
            names["first"] = name_match.group(1)
            names["last"] = name_match.group(2)
        else:
            last_match = re.search(r'\b([A-Z][a-z]+)\b', clean_query)
            if last_match:
                names["last"] = last_match.group(1)
        
        return names
    
    def _extract_political_party(self, query: str) -> Optional[str]:
        parties = {
            'democrat': 'd',
            'democratic': 'd', 
            'republican': 'r',
            'independent': 'i',
            'green': 'g',
            'libertarian': 'l'
        }
        
        query_lower = query.lower()
        for party_name, party_code in parties.items():
            if party_name in query_lower:
                return party_code
        
        return None

class MultiMCPClient:
    """Multi-MCP Client - AI tells us which tool to use"""
    
    def __init__(self):
        self.sessions = {}
        self.exit_stack = AsyncExitStack()
        self.is_connected = {"legal": False, "web": False}
        self.converter = MCPToolConverter()
        
        # Server configurations
        self.server_configs = {
            "legal": {
                "script": os.getenv("COURTLISTENER_MCP_PATH", "./courtlistener_server.py"),
                "env": {
                    "COURTLISTENER_API_TOKEN": os.getenv("COURTLISTENER_API_TOKEN"),
                    "MCP_TRANSPORT": "stdio"
                }
            },
            "web": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")
                }
            }
        }
    
    async def connect(self):
        """Connect to available MCP servers"""
        try:
            # Connect to legal server if token available
            if os.getenv("COURTLISTENER_API_TOKEN"):
                await self._connect_server("legal")
            
            # Connect to web server if key available
            if os.getenv("BRAVE_API_KEY"):
                await self._connect_server("web")
            
            connected_count = sum(self.is_connected.values())
            logger.info(f"✅ Connected to {connected_count}/2 MCP servers")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP servers: {e}")
            raise
    
    async def _connect_server(self, server_type: str):
        """Connect to a specific server"""
        try:
            config = self.server_configs[server_type]
            
            if server_type == "legal":
                server_params = StdioServerParameters(
                    command="python",
                    args=[config["script"]],
                    env=config["env"]
                )
            else:  # web
                server_params = StdioServerParameters(
                    command=config["command"],
                    args=config["args"],
                    env=config["env"]
                )
            
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            await session.initialize()
            self.sessions[server_type] = session
            self.is_connected[server_type] = True
            
            tools_response = await session.list_tools()
            tool_names = [tool.name for tool in tools_response.tools]
            logger.info(f"✅ Connected to {server_type} server with tools: {tool_names}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to {server_type} server: {e}")
            self.is_connected[server_type] = False
    
    async def execute_tool_request(self, tool_request: str) -> List[str]:
        """
        Execute AI tool request in format 'toolname: query'
        AI has already decided which tool to use
        """
        try:
            # Parse the AI's tool request
            tool_name, params = self.converter.parse_tool_request(tool_request)
            
            # Determine which server hosts this tool
            server_type = self._get_server_for_tool(tool_name)
            
            if not self.is_connected.get(server_type, False):
                return [f"{server_type} MCP server not available for tool: {tool_name}"]
            
            logger.info(f"🔍 Executing {tool_name} on {server_type} server with params: {params}")
            
            # Call the MCP tool
            session = self.sessions[server_type]
            result = await session.call_tool(tool_name, params)
            
            # Extract content
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return [content.text]
                else:
                    return [str(content)]
            else:
                return [f"No results found for tool: {tool_name}"]
                
        except Exception as e:
            logger.error(f"❌ Tool execution failed for '{tool_request}': {e}")
            return [f"Tool execution error: {str(e)}"]
    
    def _get_server_for_tool(self, tool_name: str) -> str:
        """Determine which server hosts the given tool"""
        legal_tools = [
            'get_opinion', 'get_cluster', 'get_docket', 'search_legal_cases', 'advanced_legal_search',
            'get_judge', 'get_political_affiliations', 'get_aba_ratings', 'get_retention_events',
            'get_sources', 'get_educations', 'get_positions', 'verify_citations',
            'find_authorities_cited', 'find_citing_opinions', 'analyze_citation_network', 'get_court'
        ]
        
        if tool_name in legal_tools:
            return "legal"
        elif tool_name == "brave_web_search":
            return "web"
        else:
            return "legal"  # Default
    
    async def close(self):
        """Clean up connections"""
        try:
            await self.exit_stack.aclose()
            self.sessions.clear()
            self.is_connected = {"legal": False, "web": False}
            logger.info("🔌 MCP connections closed")
        except Exception as e:
            logger.error(f"Error closing MCP connections: {e}")

# Global MCP client
mcp_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global mcp_client
    
    # Startup
    logger.info("🚀 Starting AI-Driven Multi-MCP Server")
    try:
        mcp_client = MultiMCPClient()
        await mcp_client.connect()
        logger.info("✅ AI-driven Multi-MCP client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Multi-MCP client: {e}")
        mcp_client = None
    
    yield  # Server is running
    
    # Shutdown
    logger.info("🔄 Shutting down AI-Driven Multi-MCP Server")
    if mcp_client:
        await mcp_client.close()
        logger.info("✅ Multi-MCP client closed")

app = FastAPI(title="AI-Driven Multi-MCP Server", version="2.0.0", lifespan=lifespan)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI-Driven Multi-MCP Server (CourtListener + Brave Search)",
        "status": "running",
        "approach": "AI selects tools, server executes",
        "servers": {
            "legal": mcp_client.is_connected["legal"] if mcp_client else False,
            "web": mcp_client.is_connected["web"] if mcp_client else False
        },
        "version": "2.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    if not mcp_client:
        return {"status": "error", "message": "Multi-MCP client not initialized"}
    
    connected_servers = sum(mcp_client.is_connected.values())
    
    return {
        "status": "healthy" if connected_servers > 0 else "degraded",
        "servers": {
            "legal": {
                "connected": mcp_client.is_connected["legal"],
                "name": "CourtListener MCP"
            },
            "web": {
                "connected": mcp_client.is_connected["web"],
                "name": "Brave Search MCP"
            }
        },
        "summary": f"{connected_servers}/2 servers connected"
    }

@app.post("/retrieve")
async def retrieve_endpoint(request: QueryRequest):
    """
    Main endpoint - AI has already decided which tools to use
    Input: tool requests in format 'toolname: query'
    """
    logger.info(f"📥 Received {len(request.queries)} AI tool requests, topk={request.topk}")
    
    if not mcp_client:
        logger.warning("⚠️  MCP client not available")
        error_results = [[{"document": {"contents": "MCP service unavailable"}}] 
                        for _ in request.queries]
        return {"result": error_results}
    
    try:
        results = []
        
        for i, tool_request in enumerate(request.queries):
            logger.info(f"🔍 Processing AI tool request {i+1}: '{tool_request[:50]}...'")
            
            # Execute the AI's tool request
            docs = await mcp_client.execute_tool_request(tool_request)
            
            query_results = []
            for j, doc_content in enumerate(docs):
                doc = {
                    "document": {
                        "contents": doc_content
                    }
                }
                
                if request.return_scores:
                    doc["score"] = round(0.95 - (j * 0.05), 3)
                
                query_results.append(doc)
                
                # Respect topk limit
                if len(query_results) >= request.topk:
                    break
            
            results.append(query_results)
            logger.info(f"✅ Tool request {i+1}: {len(query_results)} documents returned")
        
        logger.info(f"📤 Returning {len(results)} result sets")
        return {"result": results}
        
    except Exception as e:
        logger.error(f"❌ Retrieval error: {e}")
        error_results = [[{"document": {"contents": f"Retrieval error: {str(e)}"}}] 
                        for _ in request.queries]
        return {"result": error_results}

@app.get("/test")
async def test_endpoint():
    """Test AI tool requests"""
    if not mcp_client:
        return {"error": "MCP client not connected"}
    
    try:
        # Test AI tool requests (these would come from AI agent)
        test_requests = [
            "get_judge: Justice Ruth Bader Ginsburg",
            "search_legal_cases: privacy rights Supreme Court",
            "brave_web_search: latest AI technology news"
        ]
        
        test_results = []
        for tool_request in test_requests:
            results = await mcp_client.execute_tool_request(tool_request)
            test_results.append({
                "ai_request": tool_request,
                "results_count": len(results),
                "sample_result": results[0][:100] + "..." if results and results[0] else None
            })
        
        return {
            "test_ai_requests": test_results,
            "servers_connected": mcp_client.is_connected,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info("🤖⚖️ AI-Driven Multi-MCP Server")
    logger.info("=" * 50)
    logger.info(f"🌐 Server: http://{host}:{port}")
    logger.info(f"⚖️  CourtListener Token: {'✅ Set' if os.getenv('COURTLISTENER_API_TOKEN') else '❌ Missing'}")
    logger.info(f"🔍 Brave API Key: {'✅ Set' if os.getenv('BRAVE_API_KEY') else '❌ Missing'}")
    logger.info("")
    logger.info("🔗 Endpoints:")
    logger.info("   POST /retrieve - Execute AI tool requests")
    logger.info("   GET  /test     - Test AI tool execution")
    logger.info("")
    logger.info("🎯 AI-Driven Approach:")
    logger.info("   • AI decides which tool to use")
    logger.info("   • Server converts parameters intelligently")
    logger.info("   • No rule-based routing needed")
    logger.info("🚀 Starting server...")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info"
    )