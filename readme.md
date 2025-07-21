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
git clone <your-repo>
cd courtlistener-mcp
pip install -r requirements.txt
```

### 2. Get CourtListener API Token

1. Visit [CourtListener Token Page](https://www.courtlistener.com/profile/tokens/)
2. Sign up/login and create a new API token
3. Copy your token

### 3. Configure Environment

```bash
cp .env.template .env
# Edit .env and add your API token
```

### 4. Install in Claude Desktop

```bash
# Automatic installation
mcp install courtlistener_server.py --name "CourtListener Legal Research" -v COURTLISTENER_API_TOKEN=your_token

# Or test with MCP inspector
mcp dev courtlistener_server.py
```

## Usage Examples

### **Opinion & Case Analysis**

Ask Claude:
- *"Explain what happened in opinion 11063335"*
- *"Find recent Supreme Court decisions about privacy rights"*
- *"Get dissenting opinions from Justice Thomas in 2024"*
- *"Analyze the holding in Citizens United v. FEC"*
- *"Show me the case docket 65663213 timeline"*

### **Judge & People Research**

Ask Claude:
- *"Find information about Judge Smith from the 9th Circuit"*
- *"Show me Justice Ginsburg's career timeline and positions"*
- *"What are Elena Kagan's ABA ratings and educational background?"*
- *"Find judges appointed by Obama with Harvard law degrees"*
- *"Analyze retention events for state supreme court justices"*

### **Citation & Precedent Analysis**

Ask Claude:
- *"Verify this citation: 576 U.S. 644"*
- *"What cases does Obergefell v. Hodges cite?"*
- *"Find all cases that cite Brown v. Board of Education"*
- *"Check if this citation is valid: 999 U.S. 1"*
- *"Analyze the citation network for Roe v. Wade"*

## Key API Tools

### **`get_opinion`** - Comprehensive Opinion Analysis

```python
get_opinion(
    opinion_id=11063335,           # Specific opinion ID
    court="scotus",                # Court filter  
    opinion_type="040dissent",     # Dissenting opinions
    include_full_text=True,        # Include complete text
    analyze_content=True           # Extract holdings & facts
)
```

### **`get_judge`** - Complete Judge Profiles

```python
get_judge(
    name_last="Ginsburg",          # Judge name search
    court_name="Supreme Court",    # Court filter
    include_positions=True,        # Career positions
    include_educations=True,       # Educational history
    include_aba_ratings=True       # ABA ratings
)
```

### **`get_positions`** - Career & Appointment Analysis

```python
get_positions(
    person_id=8521,               # Specific person
    position_type="pres",         # President positions
    include_court_details=True,   # Court information
    include_retention_events=True # Retention history
)
```

### **`verify_citations`** - Citation Verification

```python
verify_citations(
    text="See Obergefell v. Hodges (576 U.S. 644)",  # Parse from text
    include_cluster_details=True,  # Full case details
    sort_by="status"              # Sort results
)
```

## Architecture

### **Separation of Concerns**

- **`core/`** - Application lifecycle and HTTP client management
- **`tools/`** - Complete MCP tool implementations for legal analysis  
- **`utils/`** - Shared utilities for code translation and formatting
- **Main server** - FastMCP setup and tool registration

### **Legal Code Translation**

Automatically converts CourtListener's codes to human-readable descriptions:

- **Nature of Suit**: `440` → `"Civil rights other"`
- **Position Types**: `"pres"` → `"President"`, `"jud"` → `"Judge"`
- **Selection Methods**: `"a_pres"` → `"Appointed by President"`
- **ABA Ratings**: `"ewq"` → `"Exceptionally Well Qualified"`
- **Political Parties**: `"d"` → `"Democratic"`, `"r"` → `"Republican"`
- **Opinion Types**: `"040dissent"` → `"Dissent"`

### **Content Analysis**

Advanced opinion text analysis extracts:

- **Key Holdings** - "We hold...", "We conclude..."
- **Procedural Disposition** - "AFFIRMED", "REVERSED", "REMANDED"  
- **Factual Background** - Case facts and procedural history
- **Citation Analysis** - Referenced cases and precedents

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COURTLISTENER_API_TOKEN` | **Required** - Your API token | None |
| `COURTLISTENER_BASE_URL` | API base URL | Production URL |
| `MCP_TRANSPORT` | Transport method | `stdio` |
| `MCP_HOST` | Server host (non-stdio) | `0.0.0.0` |
| `MCP_PORT` | Server port (non-stdio) | `8000` |
| `MCP_LOG_FILE` | Enable file logging | `false` |

### Transport Options

- **`stdio`** - Default for Claude Desktop integration
- **`sse`** - Server-Sent Events for web applications
- **`streamable-http`** - Recommended for production deployments

## Complete Tool Reference

### **Court Opinions & Cases**
| Tool | Purpose | Key Features |
|------|---------|--------------|
| `get_opinion` | Individual court decisions | Full text analysis, content extraction |
| `get_cluster` | Grouped case opinions | Multiple decisions per case |
| `get_docket` | Case information & timeline | Procedural history, parties |
| `search_legal_cases` | Legal content search | Advanced filtering, relevance scoring |

### **Judge & People Data**
| Tool | Purpose | Key Features |
|------|---------|--------------|
| `get_judge` | Judge biographical data | Demographics, career overview |
| `get_positions` | Position & appointment history | Career timeline, confirmation votes |
| `get_political_affiliations` | Political party history | Timeline, source tracking |
| `get_aba_ratings` | ABA rating analysis | Rating context, evaluation timeline |
| `get_educations` | Educational background | Degrees, schools, years |
| `get_retention_events` | Retention votes & reappointments | Voting data, retention success |
| `get_sources` | Data source tracking | Provenance, access dates |

### **Citation & Analysis**
| Tool | Purpose | Key Features |
|------|---------|--------------|
| `verify_citations` | Citation verification | Powered by Eyecite, text parsing |
| `find_authorities_cited` | Backward citation analysis | What a decision cites |
| `find_citing_opinions` | Forward citation analysis | What cites a decision |
| `analyze_citation_network` | Complete precedent mapping | Full citation networks |

### **Infrastructure**
| Tool | Purpose | Key Features |
|------|---------|--------------|
| `get_court` | Court information | Hierarchy, jurisdiction, activity |

## Development

### Local Testing

```bash
# Test with MCP inspector
mcp dev courtlistener_server.py

# Test specific functionality
python -c "
from tools.position_tools import register_position_tools
print('Position tools loaded successfully')
"
```

### Adding New Tools

1. Create tool function in appropriate module (`tools/`)
2. Register with MCP server in the module's register function
3. Add any new code mappings to `utils/mappings.py`
4. Update formatters in `utils/formatters.py` if needed
5. Update this README with tool documentation

### Code Standards

- Type hints for all functions
- Comprehensive error handling
- Detailed logging for debugging
- Human-readable code translations
- Consistent output formatting

## Legal Data Sources

This server accesses data from:

- **CourtListener** - Millions of court opinions and case law
- **RECAP Archive** - Federal court documents from PACER
- **Harvard Caselaw Access Project** - Historical legal decisions
- **Federal Judicial Center** - Integrated Database (IDB)
- **Eyecite** - Citation parsing engine (18+ million citations)
- **Free Law Project** - Curated legal datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow existing code organization patterns
4. Add appropriate tests and documentation
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **CourtListener API**: [Documentation](https://www.courtlistener.com/help/api/rest/)
- **MCP Protocol**: [Specification](https://spec.modelcontextprotocol.io)
- **Issues**: Create GitHub issues for bugs or feature requests

---

*Built with ❤️ for the legal research community*  
*Powered by [Free Law Project](https://free.law) and [CourtListener](https://www.courtlistener.com)*

## Quick Reference

**14 Complete Tools Available:**
✅ Court Opinions & Cases (4 tools)  
✅ Judge & People Data (7 tools)  
✅ Citation & Analysis (4 tools)  
✅ Infrastructure (1 tool)

**Total: 16 specialized legal research tools ready for Claude Desktop integration**