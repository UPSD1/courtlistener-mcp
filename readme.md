# CourtListener MCP Server

A comprehensive Model Context Protocol (MCP) server for accessing CourtListener's legal database. Provides Claude Desktop with powerful legal research capabilities including court opinions, case dockets, judge profiles, and comprehensive legal analysis.

## Features

- 🏛️ **Court Opinion Analysis** - Retrieve and analyze court decisions with full text interpretation
- 📋 **Case Docket Information** - Complete case timelines, parties, and procedural history  
- ⚖️ **Legal Content Analysis** - Extract holdings, dispositions, and factual backgrounds
- 👨‍⚖️ **Judge & People Profiles** - Comprehensive biographical, educational, and career data
- 🗳️ **Political & Career Analysis** - Political affiliations, ABA ratings, and retention events
- 💼 **Position & Appointment Tracking** - Judicial positions, appointment processes, and career timelines
- 🔍 **Advanced Search & Citations** - Search across all content types with citation network analysis
- 📊 **Human-Readable Codes** - Automatic translation of legal codes to plain English
- 🔗 **Citation & Precedent Analysis** - Track case citations and legal precedents

## Complete Tool Set

### **Court Opinions & Case Law**
- **`get_opinion`** - Individual court decisions with full text analysis
- **`get_cluster`** - Grouped opinions (cases with multiple decisions)
- **`get_docket`** - Case information, timelines, and procedural history
- **`search_legal_cases`** - Advanced search across all legal content
- **`advanced_legal_search`** - Complex filtering and multi-court searches

### **Judge & People Information**  
- **`get_judge`** - Comprehensive judge biographical and career data
- **`get_positions`** - Judicial and professional position history
- **`get_political_affiliations`** - Political party history and timeline
- **`get_aba_ratings`** - American Bar Association ratings analysis
- **`get_educations`** - Educational background and degree details
- **`get_retention_events`** - Judicial retention votes and reappointments
- **`get_sources`** - Data provenance and source tracking

### **Citation & Legal Analysis**
- **`verify_citations`** - Citation verification and lookup using Eyecite
- **`bulk_citation_verification`** - Batch citation processing
- **`find_authorities_cited`** - Legal precedents an opinion relies upon
- **`find_citing_opinions`** - Later cases that cite a specific decision
- **`analyze_citation_network`** - Comprehensive precedent network analysis

### **Courts & Infrastructure**
- **`get_court`** - Court information, jurisdiction, and hierarchy

## Project Structure

```
courtlistener-mcp/
├── courtlistener_server.py          # Main MCP server
├── server_factory.py                 # server factory
├── requirements.txt                  # Dependencies
├── .env.template                     # Environment template
├── README.md                        # Project documentation
├── core/
│   ├── __init__.py
│   └── lifespan.py                  # Lifecycle management
├── tools/                           # All 16 tool implementations
│   ├── __init__.py
│   ├── opinion_tools.py
│   ├── cluster_tools.py
│   ├── docket_tools.py
│   ├── court_tools.py
│   ├── search_tools.py
│   ├── people_tools.py
│   ├── position_tools.py
│   ├── political_affiliation_tools.py
│   ├── aba_ratings_tools.py
│   ├── retention_events_tools.py
│   ├── sources_tools.py
│   ├── education_tools.py
│   ├── citation_tools.py
│   └── opinions_cited_tools.py
├── utils/
│   ├── __init__.py
│   ├── mappings.py                  # Code mappings
│   └── formatters.py                # Output formatting
└── tests/                           # Test directory (NEW)
    ├── __init__.py                  # Make it a Python package
    ├── courtlistener_evals.py       # Comprehensive evaluation suite
    ├── mcp_test_runner.py           # Practical test runner
    ├── test_config.sh                 # Automated test script
    ├── pytest.ini                   # Pytest configuration
    └── .env.test                     # Test environment template
```

## Installation

### 1. Clone and Setup

```bash
# Install MCP framework
pip install mcp

# Install legal database clients
pip install courtlistener-api
pip install brave-search-api
```

### 2. API Configuration

**CourtListener Setup:**
```bash
# Register for CourtListener API access at: https://www.courtlistener.com/api/
export COURTLISTENER_API_KEY="your_api_key_here"
```

**Brave Search Setup:**
```bash
# Register for Brave Search API at: https://api.search.brave.com/
export BRAVE_SEARCH_API_KEY="your_api_key_here"
```

### 3. Start MCP Servers

```bash
# Start CourtListener MCP Server
python mcp_servers/courtlistener_server.py --port 8000

# Start Brave Search MCP Server  
python mcp_servers/brave_server.py --port 8001
```

### 4. Run Training with MCP

```bash
python train_with_mcp.py \
    --config config/mcp_training.yaml \
    --mcp-servers courtlistener,brave \
    --output models/mcp_legal_agent_v1/
```

---

## Learning Patterns During Training

### Tool Usage Evolution

**Early Training (Episodes 1-100):**
- Random tool selection
- Poor query formulation
- No strategic sequencing

**Mid Training (Episodes 500-1000):**
- Begins preferring CourtListener for legal precedents
- Learns basic jurisdiction targeting
- Develops simple search refinement

**Advanced Training (Episodes 2000+):**
- Strategic tool sequencing (CourtListener → Brave for context)
- Jurisdiction-aware tool selection
- Complex query optimization

**Expert Level (Episodes 5000+):**
- Sophisticated search strategies
- Tool coordination patterns
- Professional-grade research workflows

### Optimal Search Strategy Patterns

**Precedent Research:**
1. Search CourtListener for case topic
2. Search CourtListener for jurisdiction-specific cases
3. Search Brave for recent developments

**Statutory Analysis:**
1. Search Brave for statute text
2. Search CourtListener for statute interpretation
3. Search Brave for recent applications

**General Consultation:**
1. Search Brave for topic overview
2. Search CourtListener for relevant cases
3. Search Brave for practical guidance

---

## Monitoring and Troubleshooting

### Health Checks

```bash
# Test MCP server connectivity
curl http://localhost:8000/health  # CourtListener
curl http://localhost:8001/health  # Brave
```

### Common Issues

**Connection Problems:**
- Check API keys are properly set
- Verify servers are running on correct ports
- Test network connectivity

**Rate Limiting:**
- Monitor API usage quotas
- Adjust request frequency if needed
- Scale servers for higher throughput

**Performance Issues:**
- Check server response times
- Monitor memory usage
- Verify database connectivity

### Scaling Considerations

**High-Traffic Scenarios:**
- Run multiple MCP server instances
- Use load balancers for distribution
- Implement connection pooling
- Cache frequent queries

---

## Key Benefits of Our MCP Approach

### 1. Strategic Learning During Training
- Agents develop optimal tool sequencing patterns naturally
- 9-call constraint forces efficient resource utilization
- Legal-specific search strategies emerge through reinforcement learning

### 2. Professional Legal Research Replication  
- Dual database approach mirrors real legal practice (specialized + general search)
- Jurisdiction-aware tool selection develops automatically
- Citation network navigation skills learned during training

### 3. Research Innovation
- First implementation of MCP integration during RL training episodes
- Reproducible methodology using standardized MCP protocols
- Novel training approach for legal AI development

### 4. Practical Advantages
- Cost-effective training through search constraints
- Quality-focused rewards for search relevance
- Scalable architecture supporting concurrent training

---

## Future MCP Enhancements

### Additional Legal Database Integration
- Westlaw and Lexis MCP servers
- Patent database access
- Regulatory database integration

### Advanced Search Capabilities  
- Multi-modal document analysis
- Real-time legal news integration
- Specialized practice area databases

### Performance Optimizations
- Intelligent query caching
- Predictive search suggestions
- Dynamic rate limit management

---

*This MCP integration enables our legal AI agents to develop professional-grade research skills by learning with tools during training, representing a fundamental advancement in legal AI training methodology.*
