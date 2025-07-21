"""
CourtListener Output Formatting Utilities

Handles all output formatting for opinions, dockets, clusters, courts, and other legal content.
Ensures consistent, readable formatting across all tools.
"""


def format_opinion_analyses(analyses: list) -> str:
    """Format comprehensive opinion analyses for readable output."""
    if not analyses:
        return "No opinions found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        lines = [
            f"{'='*50}",
            f"OPINION {i}: {analysis.get('case_context', {}).get('case_name', 'Unknown Case')}",
            f"{'='*50}",
            f"📋 Opinion ID: {analysis['id']}",
            f"📝 Type: {analysis['type_display']}",
            f"👨‍⚖️ Author: {analysis['authorship']['author_name']}",
            f"🔗 URL: {analysis['absolute_url']}"
        ]
        
        # Case context
        if 'case_context' in analysis:
            context = analysis['case_context']
            lines.append(f"\n📚 CASE CONTEXT:")
            lines.append(f"  • Case: {context.get('case_name', 'Unknown')}")
            lines.append(f"  • Date Filed: {context.get('date_filed', 'Unknown')}")
            lines.append(f"  • Citations: {', '.join(context.get('citations', []))}")
            lines.append(f"  • Status: {context.get('precedential_status', 'Unknown')}")
            
            if context.get('docket_info'):
                docket = context['docket_info']
                lines.append(f"  • Docket: {docket.get('docket_number', 'Unknown')}")
                lines.append(f"  • Court: {docket.get('court_id', 'Unknown')}")
                lines.append(f"  • Judge: {docket.get('assigned_judge', 'Unknown')}")
        
        # Authorship details
        authorship = analysis['authorship']
        if authorship.get('per_curiam'):
            lines.append(f"\n✍️  AUTHORSHIP: Per Curiam (no single author)")
        else:
            lines.append(f"\n✍️  AUTHORSHIP: {authorship['author_name']}")
        if authorship.get('joined_by'):
            lines.append(f"  • Joined by: {authorship['joined_by']}")
        
        # Content analysis
        if 'content_analysis' in analysis:
            content = analysis['content_analysis']
            lines.append(f"\n📊 CONTENT ANALYSIS:")
            lines.append(f"  • Length: {content.get('word_count', 0):,} words ({content.get('character_count', 0):,} characters)")
            
            if 'case_summary' in content:
                summary = content['case_summary']
                lines.append(f"  • Decided: {summary.get('date_decided', 'Unknown')}")
                lines.append(f"  • Status: {summary.get('precedential_status', 'Unknown')}")
            
            # Extracted sections
            sections = content.get('extracted_sections', {})
            
            if 'key_holdings' in sections:
                lines.append(f"\n⚖️  KEY HOLDINGS:")
                for j, holding in enumerate(sections['key_holdings'], 1):
                    lines.append(f"  {j}. {holding[:200]}{'...' if len(holding) > 200 else ''}")
            
            if 'procedural_disposition' in sections:
                lines.append(f"\n📋 PROCEDURAL DISPOSITION:")
                for proc in sections['procedural_disposition']:
                    lines.append(f"  • {proc}")
            
            if 'factual_background' in sections:
                lines.append(f"\n📖 FACTUAL BACKGROUND:")
                background = sections['factual_background']
                lines.append(f"  {background[:400]}{'...' if len(background) > 400 else ''}")
        
        # Full text for LLM analysis
        if 'full_text' in analysis:
            lines.append(f"\n📄 FULL OPINION TEXT (for LLM analysis):")
            text = analysis['full_text']
            lines.append(f"  📊 Length: {len(text):,} characters")
            lines.append(f"  {text}")
        elif 'full_text_preview' in analysis:
            lines.append(f"\n📄 OPINION TEXT PREVIEW (for LLM analysis):")
            lines.append(f"  📊 Total Length: {analysis.get('text_analysis', {}).get('text_length', 0):,} characters")
            lines.append(f"  {analysis['full_text_preview']}")
        elif 'text_analysis' in analysis:
            text_info = analysis['text_analysis']
            lines.append(f"\n📄 TEXT INFORMATION:")
            lines.append(f"  Available: {'Yes' if text_info.get('full_text_available') else 'No'}")
            lines.append(f"  Length: {text_info.get('text_length', 0):,} characters")
            if text_info.get('note'):
                lines.append(f"  Note: {text_info['note']}")
            if text_info.get('text_preview'):
                lines.append(f"  Preview: {text_info['text_preview']}")
        
        # Citations
        if 'citations_analysis' in analysis:
            cites = analysis['citations_analysis']
            lines.append(f"\n📚 CITATIONS: {cites['total_citations']} opinions cited")
        
        # Technical details with human-readable conversions
        technical = analysis['technical_details']
        lines.append(f"\n🔧 TECHNICAL INFO:")
        lines.append(f"  • Source: {technical['text_source']}")
        if technical.get('page_count'):
            lines.append(f"  • Pages: {technical['page_count']}")
        if technical.get('extracted_by_ocr'):
            lines.append(f"  • OCR Extracted: Yes")
        lines.append(f"  • SHA1: {technical.get('sha1', 'Not available')}")
        
        # Note about code conversions
        lines.append(f"\n✅ All legal codes converted to human-readable values")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_docket_cases(cases: list) -> str:
    """Format docket cases with comprehensive human-readable values and enhanced analysis."""
    if not cases:
        return "No cases found."
    
    output_lines = []
    for i, case in enumerate(cases, 1):
        lines = [
            f"{'='*60}",
            f"CASE {i}: {case['case_details']['case_name']}",
            f"{'='*60}",
            f"📋 Docket ID: {case['id']}",
            f"📄 Docket Number: {case['case_details']['docket_number']}",
            f"🏛️  Court: {case['court_info']['court_name']}",
            f"🔗 URL: {case['absolute_url']}"
        ]
        
        # Enhanced timeline with better formatting
        timeline = case['timeline']
        lines.append("\n📅 CASE TIMELINE:")
        timeline_events = []
        if timeline.get('date_filed'):
            timeline_events.append(f"Filed: {timeline['date_filed']}")
        if timeline.get('date_argued'):
            timeline_events.append(f"Argued: {timeline['date_argued']}")
        if timeline.get('date_cert_granted'):
            timeline_events.append(f"Cert Granted: {timeline['date_cert_granted']}")
        if timeline.get('date_cert_denied'):
            timeline_events.append(f"Cert Denied: {timeline['date_cert_denied']}")
        if timeline.get('date_terminated'):
            timeline_events.append(f"Terminated: {timeline['date_terminated']}")
        if timeline.get('date_last_filing'):
            timeline_events.append(f"Last Filing: {timeline['date_last_filing']}")
        
        for event in timeline_events:
            lines.append(f"  • {event}")
        
        # Enhanced case classification with human-readable values
        classification = case['case_classification']
        if any(classification.values()):
            lines.append("\n⚖️  CASE CLASSIFICATION:")
            if classification.get('nature_of_suit'):
                lines.append(f"  • Nature of Suit: {classification['nature_of_suit']}")
            if classification.get('jurisdiction_type'):
                lines.append(f"  • Jurisdiction: {classification['jurisdiction_type']}")
            if classification.get('cause'):
                lines.append(f"  • Cause: {classification['cause']}")
            if classification.get('jury_demand'):
                lines.append(f"  • Jury Demand: {classification['jury_demand']}")
            if classification.get('appellate_case_type'):
                lines.append(f"  • Appellate Type: {classification['appellate_case_type']}")
            if classification.get('mdl_status'):
                lines.append(f"  • MDL Status: {classification['mdl_status']}")
        
        # Comprehensive Integrated Database analysis with all human-readable codes
        if 'integrated_database_info' in case:
            idb = case['integrated_database_info']
            lines.append("\n📊 INTEGRATED DATABASE ANALYSIS:")
            
            # Dataset and case origin
            if idb.get('dataset_source'):
                lines.append(f"  • Dataset Source: {idb['dataset_source']}")
            if idb.get('origin'):
                lines.append(f"  • Case Origin: {idb['origin']}")
            
            # Jurisdiction and case type
            if idb.get('jurisdiction'):
                lines.append(f"  • Jurisdiction: {idb['jurisdiction']}")
            if idb.get('nature_of_suit'):
                lines.append(f"  • Nature of Suit: {idb['nature_of_suit']}")
            
            # Case progression and outcome
            if idb.get('procedural_progress'):
                lines.append(f"  • Procedural Progress: {idb['procedural_progress']}")
            if idb.get('disposition'):
                lines.append(f"  • Disposition: {idb['disposition']}")
            if idb.get('judgment'):
                lines.append(f"  • Judgment: {idb['judgment']}")
            if idb.get('nature_of_judgement'):
                lines.append(f"  • Nature of Judgment: {idb['nature_of_judgement']}")
            
            # Financial information
            if idb.get('monetary_demand'):
                lines.append(f"  • Monetary Demand: ${idb['monetary_demand']:,}K" if idb['monetary_demand'] else "  • Monetary Demand: Not specified")
            if idb.get('amount_received'):
                lines.append(f"  • Amount Received: ${idb['amount_received']:,}K" if idb['amount_received'] else "  • Amount Received: Not specified")
            
            # Case characteristics
            if idb.get('class_action') is not None:
                lines.append(f"  • Class Action: {'Yes' if idb['class_action'] else 'No'}")
            if idb.get('pro_se'):
                lines.append(f"  • Pro Se Representation: {idb['pro_se']}")
            
            # Arbitration information
            if idb.get('arbitration_at_filing'):
                lines.append(f"  • Arbitration at Filing: {idb['arbitration_at_filing']}")
            if idb.get('arbitration_at_termination'):
                lines.append(f"  • Arbitration at Termination: {idb['arbitration_at_termination']}")
            
            # Class action status
            if idb.get('termination_class_action_status'):
                lines.append(f"  • Class Action Status: {idb['termination_class_action_status']}")
            
            # Parties
            if idb.get('plaintiff'):
                lines.append(f"  • Plaintiff: {idb['plaintiff']}")
            if idb.get('defendant'):
                lines.append(f"  • Defendant: {idb['defendant']}")
            
            # Additional case details
            if idb.get('office'):
                lines.append(f"  • Office Code: {idb['office']}")
            if idb.get('multidistrict_litigation_docket_number'):
                lines.append(f"  • MDL Docket: {idb['multidistrict_litigation_docket_number']}")
        
        # Judge information
        judges = case['judges_and_panel']
        if any(judges.values()):
            lines.append("\n👨‍⚖️ JUDICIAL ASSIGNMENT:")
            if judges.get('assigned_to'):
                lines.append(f"  • Assigned Judge: {judges['assigned_to']}")
            if judges.get('referred_to'):
                lines.append(f"  • Referred Judge: {judges['referred_to']}")
            if judges.get('panel'):
                lines.append(f"  • Panel: {judges['panel']}")
        
        # Federal case details
        federal = case['federal_details']
        if any(federal.values()):
            lines.append("\n🏛️  FEDERAL COURT DETAILS:")
            if federal.get('case_type'):
                lines.append(f"  • Case Type: {federal['case_type']}")
            if federal.get('office_code'):
                lines.append(f"  • Office Code: {federal['office_code']}")
            if federal.get('judge_initials_assigned'):
                lines.append(f"  • Judge Initials (Assigned): {federal['judge_initials_assigned']}")
            if federal.get('judge_initials_referred'):
                lines.append(f"  • Judge Initials (Referred): {federal['judge_initials_referred']}")
            if federal.get('defendant_number'):
                lines.append(f"  • Defendant Number: {federal['defendant_number']}")
        
        # PACER information
        pacer_id = case['case_details'].get('pacer_case_id')
        if pacer_id:
            lines.append(f"\n📊 PACER Case ID: {pacer_id}")
        
        # Core docket number for federal cases
        core_docket = case['case_details'].get('docket_number_core')
        if core_docket:
            lines.append(f"🔢 Core Docket Number: {core_docket}")
        
        # Opinion clusters summary with enhanced details
        if 'opinions_summary' in case:
            opinions = case['opinions_summary']
            lines.append(f"\n📜 RELATED OPINIONS: {opinions['cluster_count']} cluster(s)")
            for j, cluster in enumerate(opinions['clusters'][:3], 1):
                citations = ', '.join(cluster.get('citations', [])) if cluster.get('citations') else 'No citations'
                status = cluster.get('precedential_status', 'Unknown status')
                lines.append(f"  {j}. {cluster.get('date_filed', 'Unknown date')} - {citations}")
                lines.append(f"     Status: {status}, Opinions: {cluster.get('opinion_count', 0)}")
                if cluster.get('judges'):
                    lines.append(f"     Judges: {cluster['judges']}")
        
        # Archive links
        if 'archive_links' in case:
            lines.append("\n🏛️  INTERNET ARCHIVE:")
            archive = case['archive_links']
            if archive.get('ia_docket_xml'):
                lines.append(f"  • XML: {archive['ia_docket_xml']}")
            if archive.get('ia_docket_json'):
                lines.append(f"  • JSON: {archive['ia_docket_json']}")
        
        # Status and metadata with enhanced source display
        status = case['status_and_source']
        lines.append(f"\n📋 METADATA:")
        lines.append(f"  • Source: {status['source']}")
        if status.get('blocked'):
            lines.append(f"  • ⚠️  Blocked from search engines ({status.get('date_blocked', 'date unknown')})")
        lines.append(f"  • Created: {status.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {status.get('date_modified', 'Unknown')}")
        
        # Note about comprehensive code conversion
        lines.append(f"\n✅ All legal codes converted to human-readable values")
        lines.append(f"🔍 Enhanced IDB analysis with complete code translations")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_cluster_analyses(analyses: list) -> str:
    """Format comprehensive cluster analyses for readable output with enhanced code conversions."""
    if not analyses:
        return "No clusters found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        case_id = analysis['case_identification']
        lines = [
            f"{'='*70}",
            f"CLUSTER {i}: {case_id.get('case_name', 'Unknown Case')}",
            f"{'='*70}",
            f"📋 Cluster ID: {analysis['id']}",
            f"📝 Case Name: {case_id.get('case_name_full') or case_id.get('case_name', 'Unknown')}",
            f"🔗 URL: {analysis['absolute_url']}"
        ]
        
        # Filing and legal significance with enhanced status display
        filing = analysis['filing_info']
        significance = analysis['legal_significance']
        lines.append(f"\n📅 FILING INFORMATION:")
        lines.append(f"  • Date Filed: {filing.get('date_filed', 'Unknown')}")
        if filing.get('date_filed_is_approximate'):
            lines.append(f"  • ⚠️  Date is approximate")
        if filing.get('other_dates'):
            lines.append(f"  • Other Dates: {filing['other_dates']}")
        
        lines.append(f"\n⚖️  LEGAL SIGNIFICANCE:")
        lines.append(f"  • Precedential Status: {significance.get('precedential_status_display', 'Unknown')} ({significance.get('precedential_status', 'N/A')})")
        lines.append(f"  • Citation Count: {significance.get('citation_count', 0):,} times cited")
        if significance.get('blocked'):
            lines.append(f"  • ⚠️  Blocked from search engines ({significance.get('date_blocked', 'date unknown')})")
        
        # Enhanced citations information with type mapping
        if 'citations' in analysis:
            citations = analysis['citations']
            lines.append(f"\n📚 CITATIONS ({citations['count']}):")
            for citation in citations['detailed_citations'][:5]:  # Show first 5
                citation_str = citation.get('citation_string', 'Unknown')
                citation_type = citation.get('type_display', 'Unknown type')
                lines.append(f"  • {citation_str} ({citation_type})")
        
        # Enhanced Supreme Court Database information with vote display
        if 'supreme_court_database' in analysis:
            scdb = analysis['supreme_court_database']
            lines.append(f"\n🏛️  SUPREME COURT DATABASE:")
            lines.append(f"  • SCDB ID: {scdb.get('scdb_id')}")
            if scdb.get('decision_direction_display'):
                lines.append(f"  • Decision Direction: {scdb['decision_direction_display']} ({scdb.get('decision_direction', 'N/A')})")
            if scdb.get('vote_summary'):
                lines.append(f"  • Vote Count: {scdb['vote_summary']}")
        
        # Judicial panel
        panel = analysis['judicial_panel']
        if panel.get('judges'):
            lines.append(f"\n👨‍⚖️ JUDICIAL PANEL:")
            lines.append(f"  • Judges: {panel['judges']}")
            if panel.get('non_participating_judges'):
                lines.append(f"  • Non-participating: {len(panel['non_participating_judges'])} judge(s)")
        
        # Procedural information
        procedural = analysis['procedural_info']
        procedural_items = []
        if procedural.get('disposition'):
            procedural_items.append(f"Disposition: {procedural['disposition']}")
        if procedural.get('posture'):
            procedural_items.append(f"Posture: {procedural['posture']}")
        if procedural.get('nature_of_suit'):
            procedural_items.append(f"Nature of Suit: {procedural['nature_of_suit']}")
        
        if procedural_items:
            lines.append(f"\n📋 PROCEDURAL INFORMATION:")
            for item in procedural_items:
                lines.append(f"  • {item}")
        
        # Enhanced content summary
        content = analysis['content_summary']
        content_items = []
        if content.get('syllabus'):
            content_items.append(("Syllabus", content['syllabus']))
        if content.get('summary'):
            content_items.append(("Summary", content['summary']))
        if content.get('headnotes'):
            content_items.append(("Headnotes", content['headnotes']))
        if content.get('arguments'):
            content_items.append(("Arguments", content['arguments']))
        if content.get('headmatter'):
            content_items.append(("Headmatter", content['headmatter']))
        
        if content_items:
            lines.append(f"\n📖 CONTENT SUMMARY:")
            for title, text in content_items[:3]:  # Show first 3
                preview = text[:200] + "..." if len(text) > 200 else text
                lines.append(f"  • {title}: {preview}")
        
        # Cross-references and corrections
        if content.get('cross_reference'):
            lines.append(f"\n🔗 CROSS REFERENCE: {content['cross_reference'][:200]}{'...' if len(content['cross_reference']) > 200 else ''}")
        if content.get('correction'):
            lines.append(f"\n📝 CORRECTION: {content['correction'][:200]}{'...' if len(content['correction']) > 200 else ''}")
        
        # Related opinions with enhanced type display
        if 'opinions_summary' in analysis:
            opinions = analysis['opinions_summary']
            lines.append(f"\n📜 RELATED OPINIONS ({opinions['opinion_count']}):")
            for j, opinion in enumerate(opinions['opinions'][:5], 1):  # Show first 5
                opinion_type = opinion.get('type_display', opinion.get('type', 'Unknown'))
                author = opinion.get('author', 'Unknown')
                lines.append(f"  {j}. {opinion_type} by {author}")
                if opinion.get('joined_by'):
                    lines.append(f"     Joined by: {opinion['joined_by']}")
                if opinion.get('page_count'):
                    lines.append(f"     Pages: {opinion['page_count']}")
                lines.append(f"     Has text: {'Yes' if opinion.get('has_text') else 'No'}")
        
        # Docket information
        if 'docket_info' in analysis:
            docket = analysis['docket_info']
            lines.append(f"\n📄 DOCKET INFORMATION:")
            lines.append(f"  • Docket Number: {docket.get('docket_number', 'Unknown')}")
            lines.append(f"  • Court: {docket.get('court_name', docket.get('court_id', 'Unknown'))}")
            if docket.get('assigned_judge'):
                lines.append(f"  • Assigned Judge: {docket['assigned_judge']}")
            if docket.get('pacer_case_id'):
                lines.append(f"  • PACER Case ID: {docket['pacer_case_id']}")
        
        # Enhanced source and metadata with source mapping
        source = analysis['source_info']
        lines.append(f"\n📊 SOURCE & METADATA:")
        lines.append(f"  • Source: {source.get('source_display', 'Unknown')} ({source.get('source', 'N/A')})")
        lines.append(f"  • Created: {source.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {source.get('date_modified', 'Unknown')}")
        
        # External resources
        resources = analysis['external_resources']
        if resources.get('filepath_json_harvard') or resources.get('filepath_pdf_harvard'):
            lines.append(f"\n📚 EXTERNAL RESOURCES:")
            if resources.get('filepath_json_harvard'):
                lines.append(f"  • Harvard JSON: Available")
            if resources.get('filepath_pdf_harvard'):
                lines.append(f"  • Harvard PDF: Available")
        
        # SCDB ID for easy reference
        if case_id.get('scdb_id'):
            lines.append(f"\n🏛️  SCDB ID: {case_id['scdb_id']}")
        
        # Note about comprehensive code conversion
        lines.append(f"\n✅ All legal codes converted to human-readable values")
        lines.append(f"🔍 Enhanced with SCDB data, citation types, and source mapping")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_court_analyses(analyses: list) -> str:
    """Format comprehensive court analyses for readable output with enhanced jurisdiction display."""
    if not analyses:
        return "No courts found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        identification = analysis['identification']
        jurisdiction = analysis['jurisdiction_info']
        lines = [
            f"{'='*60}",
            f"COURT {i}: {identification.get('short_name', 'Unknown Court')}",
            f"{'='*60}",
            f"📋 Court ID: {analysis['id']}",
            f"🏛️  Full Name: {identification.get('full_name', 'Unknown')}",
            f"📖 Citation: {identification.get('citation_string', 'N/A')}",
            f"🌐 Website: {identification.get('url', 'N/A')}"
        ]
        
        # Jurisdiction and classification with human-readable values
        lines.append(f"\n⚖️  JURISDICTION & CLASSIFICATION:")
        lines.append(f"  • Jurisdiction: {jurisdiction.get('jurisdiction_display', 'Unknown')} ({jurisdiction.get('jurisdiction', 'N/A')})")
        lines.append(f"  • Hierarchical Position: {jurisdiction.get('position', 'N/A')}")
        
        if 'court_classification' in analysis:
            classification = analysis['court_classification']
            lines.append(f"  • Court System: {classification.get('court_system', 'Unknown')}")
            lines.append(f"  • Court Level: {classification.get('court_level', 'Unknown')}")
            lines.append(f"  • Court Type: {classification.get('court_type', 'Unknown')}")
        
        # Operational information
        operational = analysis['operational_dates']
        activity = analysis['activity_status']
        
        lines.append(f"\n📅 OPERATIONAL STATUS:")
        if operational.get('start_date'):
            lines.append(f"  • Established: {operational['start_date']}")
        if operational.get('end_date'):
            lines.append(f"  • Abolished: {operational['end_date']}")
        
        lines.append(f"  • In Use: {'Yes' if activity.get('in_use') else 'No'}")
        lines.append(f"  • Opinion Scraper: {'Yes' if activity.get('has_opinion_scraper') else 'No'}")
        lines.append(f"  • Oral Argument Scraper: {'Yes' if activity.get('has_oral_argument_scraper') else 'No'}")
        
        # Federal integration
        federal = analysis['federal_integration']
        federal_items = []
        if federal.get('pacer_court_id'):
            federal_items.append(f"PACER ID: {federal['pacer_court_id']}")
        if federal.get('pacer_has_rss_feed') is not None:
            federal_items.append(f"PACER RSS: {'Yes' if federal['pacer_has_rss_feed'] else 'No'}")
        if federal.get('fjc_court_id'):
            federal_items.append(f"FJC ID: {federal['fjc_court_id']}")
        if federal.get('date_last_pacer_contact'):
            federal_items.append(f"Last PACER Contact: {federal['date_last_pacer_contact']}")
        if federal.get('pacer_rss_entry_types'):
            federal_items.append(f"RSS Entry Types: {federal['pacer_rss_entry_types']}")
        
        if federal_items:
            lines.append(f"\n🏛️  FEDERAL INTEGRATION:")
            for item in federal_items:
                lines.append(f"  • {item}")
        
        # Court hierarchy with jurisdiction display
        if 'hierarchy' in analysis:
            hierarchy = analysis['hierarchy']
            
            if hierarchy.get('parent_courts'):
                lines.append(f"\n⬆️  PARENT COURTS:")
                for parent in hierarchy['parent_courts']:
                    lines.append(f"  • {parent.get('name', 'Unknown')} ({parent.get('jurisdiction_display', 'Unknown')})")
            
            if hierarchy.get('appeals_to'):
                lines.append(f"\n📈 APPEALS TO:")
                for appeal_court in hierarchy['appeals_to']:
                    lines.append(f"  • {appeal_court.get('name', 'Unknown')} ({appeal_court.get('jurisdiction_display', 'Unknown')})")
        
        # Activity statistics
        if 'activity_statistics' in analysis:
            stats = analysis['activity_statistics']
            lines.append(f"\n📊 ACTIVITY STATISTICS:")
            lines.append(f"  • Total Dockets: {stats.get('docket_count', 0):,}")
            lines.append(f"  • Opinion Clusters: {stats.get('opinion_cluster_count', 0):,}")
            lines.append(f"  • Recent Activity: {'Yes' if stats.get('recent_activity') else 'No'}")
        
        # Note about code conversions
        lines.append(f"\n✅ All jurisdiction codes converted to human-readable values")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_judge_analyses(analyses: list) -> str:
    """Format comprehensive judge analyses for readable output with all code conversions."""
    if not analyses:
        return "No judges found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        identification = analysis['identification']
        biographical = analysis['biographical_info']
        professional = analysis['professional_identifiers']
        
        lines = [
            f"{'='*70}",
            f"JUDGE {i}: {identification.get('full_name', 'Unknown Name')}",
            f"{'='*70}",
            f"📋 Person ID: {analysis['id']}",
            f"🔗 URL: {analysis['absolute_url']}",
            f"📝 Slug: {analysis.get('slug', 'N/A')}"
        ]
        
        # Name details with suffix
        lines.append(f"\n👤 IDENTIFICATION:")
        lines.append(f"  • First Name: {identification.get('name_first', 'Unknown')}")
        if identification.get('name_middle'):
            lines.append(f"  • Middle Name: {identification['name_middle']}")
        lines.append(f"  • Last Name: {identification.get('name_last', 'Unknown')}")
        if identification.get('name_suffix_display'):
            lines.append(f"  • Suffix: {identification['name_suffix_display']} ({identification.get('name_suffix', 'N/A')})")
        
        # Alias information
        if identification.get('is_alias'):
            lines.append(f"  • ⚠️  This is an alias record (refers to person ID: {identification.get('is_alias_of')})")
        
        # Biographical information with enhanced date handling
        lines.append(f"\n📅 BIOGRAPHICAL INFORMATION:")
        
        # Birth information
        birth_parts = []
        if biographical.get('date_dob'):
            birth_date = biographical['date_dob']
            granularity = biographical.get('date_granularity_dob_display', 'Unknown granularity')
            birth_parts.append(f"Born: {birth_date} ({granularity} precision)")
        
        birth_location_parts = []
        if biographical.get('birth_location', {}).get('city'):
            birth_location_parts.append(biographical['birth_location']['city'])
        if biographical.get('birth_location', {}).get('state_display'):
            birth_location_parts.append(biographical['birth_location']['state_display'])
        elif biographical.get('birth_location', {}).get('state'):
            birth_location_parts.append(biographical['birth_location']['state'])
        if biographical.get('birth_location', {}).get('country'):
            birth_location_parts.append(biographical['birth_location']['country'])
        
        if birth_location_parts:
            birth_parts.append(f"Birthplace: {', '.join(birth_location_parts)}")
        
        if birth_parts:
            lines.append(f"  • {' | '.join(birth_parts)}")
        
        # Death information
        if biographical.get('date_dod'):
            death_parts = []
            death_date = biographical['date_dod']
            granularity = biographical.get('date_granularity_dod_display', 'Unknown granularity')
            death_parts.append(f"Died: {death_date} ({granularity} precision)")
            
            death_location_parts = []
            if biographical.get('death_location', {}).get('city'):
                death_location_parts.append(biographical['death_location']['city'])
            if biographical.get('death_location', {}).get('state_display'):
                death_location_parts.append(biographical['death_location']['state_display'])
            elif biographical.get('death_location', {}).get('state'):
                death_location_parts.append(biographical['death_location']['state'])
            if biographical.get('death_location', {}).get('country'):
                death_location_parts.append(biographical['death_location']['country'])
            
            if death_location_parts:
                death_parts.append(f"Place: {', '.join(death_location_parts)}")
            
            lines.append(f"  • {' | '.join(death_parts)}")
        
        # Demographics with human-readable conversions
        demographics = []
        if biographical.get('gender_display'):
            demographics.append(f"Gender: {biographical['gender_display']} ({biographical.get('gender', 'N/A')})")
        if biographical.get('race_display'):
            demographics.append(f"Race: {biographical['race_display']} ({biographical.get('race', 'N/A')})")
        if biographical.get('religion_display'):
            demographics.append(f"Religion: {biographical['religion_display']} ({biographical.get('religion', 'N/A')})")
        
        if demographics:
            lines.append(f"  • {' | '.join(demographics)}")
        
        # Professional identifiers
        prof_ids = []
        if professional.get('fjc_id'):
            prof_ids.append(f"FJC ID: {professional['fjc_id']}")
        if professional.get('ftm_eid'):
            prof_ids.append(f"Follow The Money ID: {professional['ftm_eid']}")
        if professional.get('has_photo'):
            prof_ids.append("📸 Has photo available")
        if professional.get('ftm_total_received'):
            prof_ids.append(f"FTM Total Received: ${professional['ftm_total_received']:,.2f}")
        
        if prof_ids:
            lines.append(f"\n🏛️  PROFESSIONAL IDENTIFIERS:")
            for prof_id in prof_ids:
                lines.append(f"  • {prof_id}")
        
        # Political affiliations with enhanced display
        if 'political_affiliations' in analysis:
            affiliations = analysis['political_affiliations']
            lines.append(f"\n🗳️  POLITICAL AFFILIATIONS ({affiliations['count']}):")
            for affiliation in affiliations['affiliations'][:5]:  # Show first 5
                party_info = f"{affiliation.get('political_party_display', 'Unknown')} ({affiliation.get('political_party', 'N/A')})"
                source_info = f"Source: {affiliation.get('source_display', 'Unknown')}"
                
                date_range = []
                if affiliation.get('date_start'):
                    start_granularity = affiliation.get('date_granularity_start_display', '')
                    date_range.append(f"From: {affiliation['date_start']} ({start_granularity})")
                if affiliation.get('date_end'):
                    end_granularity = affiliation.get('date_granularity_end_display', '')
                    date_range.append(f"To: {affiliation['date_end']} ({end_granularity})")
                
                affiliation_line = f"  • {party_info} | {source_info}"
                if date_range:
                    affiliation_line += f" | {' '.join(date_range)}"
                lines.append(affiliation_line)
        
        # ABA ratings
        if 'aba_ratings' in analysis:
            ratings = analysis['aba_ratings']
            lines.append(f"\n⚖️  ABA RATINGS ({ratings['count']}):")
            for rating in ratings['ratings']:
                rating_info = f"{rating.get('rating_display', 'Unknown')} ({rating.get('rating', 'N/A')})"
                year_info = f"Year: {rating.get('year_rated', 'Unknown')}"
                lines.append(f"  • {rating_info} | {year_info}")
        
        # Educational history
        if 'educations' in analysis:
            educations = analysis['educations']
            lines.append(f"\n🎓 EDUCATION ({educations['count']}):")
            for education in educations['education_history']:
                school_name = education.get('school_name', 'Unknown School')
                degree_info = education.get('degree_level_display', 'Unknown degree')
                degree_detail = education.get('degree_detail', '')
                year = education.get('degree_year', 'Unknown year')
                
                education_line = f"  • {school_name} - {degree_info}"
                if degree_detail:
                    education_line += f" ({degree_detail})"
                education_line += f" - {year}"
                lines.append(education_line)
        
        # Positions held
        if 'positions' in analysis:
            positions = analysis['positions']
            lines.append(f"\n💼 POSITIONS HELD ({positions['count']}):")
            for position in positions['positions_held'][:10]:  # Show first 10
                position_parts = []
                
                if position.get('job_title'):
                    position_parts.append(f"Title: {position['job_title']}")
                if position.get('organization_name'):
                    position_parts.append(f"Organization: {position['organization_name']}")
                if position.get('court'):
                    position_parts.append(f"Court: {position['court']}")
                
                # Date information
                date_parts = []
                if position.get('date_start'):
                    date_parts.append(f"Started: {position['date_start']}")
                if position.get('date_termination'):
                    date_parts.append(f"Ended: {position['date_termination']}")
                elif position.get('date_retirement'):
                    date_parts.append(f"Retired: {position['date_retirement']}")
                
                # Selection and appointment info
                selection_parts = []
                if position.get('how_selected'):
                    selection_parts.append(f"Selected: {position['how_selected']}")
                if position.get('appointer'):
                    selection_parts.append(f"Appointed by: {position['appointer']}")
                if position.get('date_confirmation'):
                    selection_parts.append(f"Confirmed: {position['date_confirmation']}")
                
                position_line = f"  • {' | '.join(position_parts)}"
                if date_parts:
                    position_line += f"\n    📅 {' | '.join(date_parts)}"
                if selection_parts:
                    position_line += f"\n    🏛️  {' | '.join(selection_parts)}"
                
                lines.append(position_line)
        
        # Sources information
        if 'sources' in analysis:
            sources = analysis['sources']
            lines.append(f"\n📚 DATA SOURCES ({sources['count']}):")
            for source in sources['source_info']:
                source_parts = []
                if source.get('url'):
                    source_parts.append(f"URL: {source['url']}")
                if source.get('date_accessed'):
                    source_parts.append(f"Accessed: {source['date_accessed']}")
                if source.get('notes'):
                    notes = source['notes'][:100] + "..." if len(source['notes']) > 100 else source['notes']
                    source_parts.append(f"Notes: {notes}")
                
                if source_parts:
                    lines.append(f"  • {' | '.join(source_parts)}")
        
        # Metadata
        metadata = analysis['metadata']
        lines.append(f"\n📊 METADATA:")
        lines.append(f"  • Created: {metadata.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {metadata.get('date_modified', 'Unknown')}")
        if metadata.get('date_completed'):
            lines.append(f"  • Completed: {metadata['date_completed']}")
        
        # Note about comprehensive code conversion
        lines.append(f"\n✅ All legal and demographic codes converted to human-readable values")
        lines.append(f"🔍 Includes biographical data, career positions, education, and political affiliations")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_political_affiliations_analyses(analyses: list) -> str:
    """Format comprehensive political affiliation analyses for readable output with enhanced timeline display."""
    if not analyses:
        return "No political affiliations found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        affiliation_details = analysis['affiliation_details']
        timeline = analysis['timeline']
        
        lines = [
            f"{'='*70}",
            f"POLITICAL AFFILIATION {i}: {affiliation_details.get('political_party_display', 'Unknown Party')}",
            f"{'='*70}",
            f"📋 Affiliation ID: {analysis['id']}",
            f"🎗️  Political Party: {affiliation_details.get('political_party_display', 'Unknown')} ({affiliation_details.get('political_party', 'N/A')})",
            f"📊 Source: {affiliation_details.get('source_display', 'Unknown')} ({affiliation_details.get('source', 'N/A')})"
        ]
        
        # Person information
        if 'person_details' in analysis:
            person = analysis['person_details']
            lines.append(f"\n👤 PERSON INFORMATION:")
            lines.append(f"  • Name: {person.get('full_name', 'Unknown')}")
            lines.append(f"  • Person ID: {person.get('person_id', 'N/A')}")
            lines.append(f"  • Profile: {person.get('absolute_url', 'N/A')}")
            if person.get('fjc_id'):
                lines.append(f"  • FJC ID: {person['fjc_id']}")
            if person.get('gender'):
                lines.append(f"  • Gender: {person['gender']}")
            if person.get('date_dob'):
                lines.append(f"  • Date of Birth: {person['date_dob']}")
            lines.append(f"  • Has Photo: {'Yes' if person.get('has_photo') else 'No'}")
        elif analysis.get('person_id'):
            lines.append(f"\n👤 Person ID: {analysis['person_id']}")
        
        # Enhanced timeline information with granularity display
        lines.append(f"\n📅 AFFILIATION TIMELINE:")
        
        # Start date with granularity
        if timeline.get('date_start'):
            start_info = f"Started: {timeline['date_start']}"
            if timeline.get('date_granularity_start_display'):
                start_info += f" ({timeline['date_granularity_start_display']} precision)"
            lines.append(f"  • {start_info}")
        else:
            lines.append(f"  • Started: Unknown date")
        
        # End date with granularity
        if timeline.get('date_end'):
            end_info = f"Ended: {timeline['date_end']}"
            if timeline.get('date_granularity_end_display'):
                end_info += f" ({timeline['date_granularity_end_display']} precision)"
            lines.append(f"  • {end_info}")
        else:
            lines.append(f"  • Status: {'Current affiliation (no end date)' if timeline.get('is_current') else 'End date unknown'}")
        
        # Duration analysis
        if timeline.get('duration_analysis'):
            duration = timeline['duration_analysis']
            lines.append(f"  • Duration: {duration['total_days']} days (~{duration['approximate_years']} years)")
        elif timeline.get('is_current') and timeline.get('date_start'):
            lines.append(f"  • Duration: Ongoing since {timeline['date_start']}")
        
        # Current status indicator
        if timeline.get('is_current'):
            lines.append(f"  • ✅ Currently Active")
        else:
            lines.append(f"  • 📋 Historical Affiliation")
        
        # Metadata
        metadata = analysis['metadata']
        lines.append(f"\n📊 RECORD METADATA:")
        lines.append(f"  • Created: {metadata.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {metadata.get('date_modified', 'Unknown')}")
        
        # Resource URI for API access
        if analysis.get('resource_uri'):
            lines.append(f"  • API Resource: {analysis['resource_uri']}")
        
        # Note about comprehensive code conversion
        lines.append(f"\n✅ All political party and source codes converted to human-readable values")
        lines.append(f"🔍 Date granularity indicates precision of timeline information")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_aba_ratings_analyses(analyses: list) -> str:
    """Format comprehensive ABA rating analyses for readable output with enhanced evaluation context."""
    if not analyses:
        return "No ABA ratings found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        rating_details = analysis['rating_details']
        timeline = analysis['timeline']
        
        lines = [
            f"{'='*70}",
            f"ABA RATING {i}: {rating_details.get('rating_display', 'Unknown Rating')}",
            f"{'='*70}",
            f"📋 Rating ID: {analysis['id']}",
            f"⚖️  ABA Rating: {rating_details.get('rating_display', 'Unknown')} ({rating_details.get('rating', 'N/A')})",
            f"📅 Year Rated: {rating_details.get('year_rated', 'Unknown')}"
        ]
        
        # Timeline context
        if timeline.get('years_ago') is not None:
            lines.append(f"🕒 Time Since Rating: {timeline['years_ago']} years ago")
        
        # Person information
        if 'person_details' in analysis:
            person = analysis['person_details']
            lines.append(f"\n👤 PERSON INFORMATION:")
            lines.append(f"  • Name: {person.get('full_name', 'Unknown')}")
            lines.append(f"  • Person ID: {person.get('person_id', 'N/A')}")
            lines.append(f"  • Profile: {person.get('absolute_url', 'N/A')}")
            if person.get('fjc_id'):
                lines.append(f"  • FJC ID: {person['fjc_id']}")
            if person.get('gender'):
                lines.append(f"  • Gender: {person['gender']}")
            if person.get('date_dob'):
                lines.append(f"  • Date of Birth: {person['date_dob']}")
            lines.append(f"  • Has Photo: {'Yes' if person.get('has_photo') else 'No'}")
        elif analysis.get('person_id'):
            lines.append(f"\n👤 Person ID: {analysis['person_id']}")
        
        # Enhanced rating context and significance
        rating_context = rating_details.get('rating_context', {})
        if rating_context:
            lines.append(f"\n📊 RATING SIGNIFICANCE:")
            lines.append(f"  • Level: {rating_context.get('significance', 'Unknown')}")
            lines.append(f"  • Description: {rating_context.get('description', 'No description available')}")
            lines.append(f"  • Context: {rating_context.get('rarity', 'Unknown rarity')}")
        
        # Rating scale explanation for context
        lines.append(f"\n📚 ABA RATING SCALE REFERENCE:")
        lines.append(f"  • EWQ: Exceptionally Well Qualified (Highest)")
        lines.append(f"  • WQ: Well Qualified (Strong positive)")
        lines.append(f"  • Q: Qualified (Acceptable)")
        lines.append(f"  • NQ: Not Qualified (Negative)")
        lines.append(f"  • NQA: Not Qualified By Reason of Age (Historical)")
        
        # Current rating highlight
        current_rating = rating_details.get('rating', '').upper()
        if current_rating:
            lines.append(f"  • ➤ This person received: {current_rating} ({rating_details.get('rating_display', 'Unknown')})")
        
        # Metadata
        metadata = analysis['metadata']
        lines.append(f"\n📊 RECORD METADATA:")
        lines.append(f"  • Created: {metadata.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {metadata.get('date_modified', 'Unknown')}")
        
        # Resource URI for API access
        if analysis.get('resource_uri'):
            lines.append(f"  • API Resource: {analysis['resource_uri']}")
        
        # Note about ABA ratings importance
        lines.append(f"\n💡 ABOUT ABA RATINGS:")
        lines.append(f"  • ABA ratings are influential in federal judicial nominations")
        lines.append(f"  • Ratings assess legal competence, integrity, and temperament")
        lines.append(f"  • Historical context important for understanding judicial careers")
        
        # Note about comprehensive code conversion
        lines.append(f"\n✅ All rating codes converted to human-readable values with context")
        lines.append(f"🔍 Rating significance and rarity information provided for analysis")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_retention_events_analyses(analyses: list) -> str:
    """Format comprehensive retention event analyses for readable output."""
    if not analyses:
        return "No retention events found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        retention_details = analysis['retention_details']
        voting_data = analysis['voting_data']
        
        lines = [
            f"{'='*70}",
            f"RETENTION EVENT {i}: {retention_details.get('retention_type_display', 'Unknown Type')}",
            f"{'='*70}",
            f"📋 Event ID: {analysis['id']}",
            f"⚖️  Retention Type: {retention_details.get('retention_type_display', 'Unknown')} ({retention_details.get('retention_type', 'N/A')})",
            f"📅 Date: {retention_details.get('date_retention', 'Unknown')}",
            f"🏆 Result: {'Won' if retention_details.get('won') else 'Lost' if retention_details.get('won') is False else 'Unknown'}"
        ]
        
        # Position information
        if 'position_details' in analysis:
            position = analysis['position_details']
            lines.append(f"\n💼 POSITION INFORMATION:")
            lines.append(f"  • Title: {position.get('job_title', 'Unknown')}")
            lines.append(f"  • Court: {position.get('court', 'Unknown')}")
            lines.append(f"  • Person: {position.get('person', 'Unknown')}")
            lines.append(f"  • Position ID: {position.get('position_id', 'N/A')}")
            if position.get('date_start'):
                lines.append(f"  • Position Start: {position['date_start']}")
            if position.get('appointer'):
                lines.append(f"  • Appointer: {position['appointer']}")
            if position.get('how_selected'):
                lines.append(f"  • Selection Method: {position['how_selected']}")
        elif analysis.get('position_id'):
            lines.append(f"\n💼 Position ID: {analysis['position_id']}")
        
        # Voting data analysis
        lines.append(f"\n🗳️  VOTING ANALYSIS:")
        
        if retention_details.get('unopposed'):
            lines.append(f"  • Status: Unopposed retention")
        else:
            lines.append(f"  • Status: Contested retention")
        
        # Vote counts
        if voting_data.get('votes_yes') is not None and voting_data.get('votes_no') is not None:
            lines.append(f"  • Yes Votes: {voting_data['votes_yes']:,}")
            lines.append(f"  • No Votes: {voting_data['votes_no']:,}")
            lines.append(f"  • Total Votes: {voting_data['total_votes']:,}")
            lines.append(f"  • Margin: {voting_data['margin']:,} votes")
            if voting_data.get('percentage_won'):
                lines.append(f"  • Percentage Won: {voting_data['percentage_won']}%")
        elif voting_data.get('votes_yes_percent') is not None:
            lines.append(f"  • Yes Percentage: {voting_data['votes_yes_percent']}%")
            if voting_data.get('votes_no_percent') is not None:
                lines.append(f"  • No Percentage: {voting_data['votes_no_percent']}%")
        else:
            lines.append(f"  • Vote counts not available")
        
        # Retention type context
        retention_type = retention_details.get('retention_type', '')
        lines.append(f"\n📊 RETENTION TYPE CONTEXT:")
        if retention_type == 'reapp_gov':
            lines.append(f"  • Governor reappointment - executive branch selection")
        elif retention_type == 'reapp_leg':
            lines.append(f"  • Legislative reappointment - legislative branch selection")
        elif retention_type == 'elec_p':
            lines.append(f"  • Partisan election - party affiliation on ballot")
        elif retention_type == 'elec_n':
            lines.append(f"  • Nonpartisan election - no party affiliation on ballot")
        elif retention_type == 'elec_u':
            lines.append(f"  • Uncontested election - no opposition candidate")
        else:
            lines.append(f"  • Unknown retention method")
        
        # Metadata
        metadata = analysis['metadata']
        lines.append(f"\n📊 RECORD METADATA:")
        lines.append(f"  • Created: {metadata.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {metadata.get('date_modified', 'Unknown')}")
        
        # Resource URI for API access
        if analysis.get('resource_uri'):
            lines.append(f"  • API Resource: {analysis['resource_uri']}")
        
        # Note about code conversion
        lines.append(f"\n✅ All retention type codes converted to human-readable values")
        lines.append(f"🔍 Voting analysis includes margins, percentages, and context")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_sources_analyses(analyses: list) -> str:
    """Format comprehensive source analyses for readable output."""
    if not analyses:
        return "No sources found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        source_details = analysis['source_details']
        
        lines = [
            f"{'='*70}",
            f"DATA SOURCE {i}: {source_details.get('url_domain', 'Unknown Domain')}",
            f"{'='*70}",
            f"📋 Source ID: {analysis['id']}",
            f"🌐 URL: {source_details.get('url', 'No URL provided')[:100]}{'...' if len(source_details.get('url', '')) > 100 else ''}",
            f"📅 Date Accessed: {source_details.get('date_accessed', 'Unknown')}"
        ]
        
        # Person information
        if 'person_details' in analysis:
            person = analysis['person_details']
            lines.append(f"\n👤 PERSON INFORMATION:")
            lines.append(f"  • Name: {person.get('full_name', 'Unknown')}")
            lines.append(f"  • Person ID: {person.get('person_id', 'N/A')}")
            lines.append(f"  • Profile: {person.get('absolute_url', 'N/A')}")
            if person.get('fjc_id'):
                lines.append(f"  • FJC ID: {person['fjc_id']}")
            lines.append(f"  • Has Photo: {'Yes' if person.get('has_photo') else 'No'}")
        elif analysis.get('person_id'):
            lines.append(f"\n👤 Person ID: {analysis['person_id']}")
        
        # Source details
        lines.append(f"\n🔍 SOURCE DETAILS:")
        if source_details.get('url'):
            lines.append(f"  • Full URL: {source_details['url']}")
            if source_details.get('url_domain'):
                lines.append(f"  • Domain: {source_details['url_domain']}")
        else:
            lines.append(f"  • No URL provided")
        
        lines.append(f"  • Access Date: {source_details.get('date_accessed', 'Not specified')}")
        lines.append(f"  • Has Notes: {'Yes' if source_details.get('has_notes') else 'No'}")
        
        if source_details.get('has_notes'):
            lines.append(f"  • Notes Length: {source_details.get('notes_length', 0)} characters")
        
        # Notes content (if available and reasonable length)
        if source_details.get('notes') and len(source_details['notes']) <= 500:
            lines.append(f"\n📝 NOTES:")
            lines.append(f"  {source_details['notes']}")
        elif source_details.get('notes') and len(source_details['notes']) > 500:
            lines.append(f"\n📝 NOTES (PREVIEW):")
            lines.append(f"  {source_details['notes'][:400]}...")
            lines.append(f"  [Full notes: {source_details['notes_length']} characters]")
        
        # Source analysis
        lines.append(f"\n📊 SOURCE ANALYSIS:")
        domain = source_details.get('url_domain', '').lower()
        if 'gov' in domain:
            lines.append(f"  • Type: Government source")
        elif 'edu' in domain:
            lines.append(f"  • Type: Educational institution")
        elif 'org' in domain:
            lines.append(f"  • Type: Organization")
        elif 'wikipedia' in domain:
            lines.append(f"  • Type: Wikipedia/Wiki source")
        elif any(news_term in domain for news_term in ['news', 'times', 'post', 'herald', 'tribune']):
            lines.append(f"  • Type: News/Media source")
        else:
            lines.append(f"  • Type: General web source")
        
        # Metadata
        metadata = analysis['metadata']
        lines.append(f"\n📊 RECORD METADATA:")
        lines.append(f"  • Created: {metadata.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {metadata.get('date_modified', 'Unknown')}")
        
        # Resource URI for API access
        if analysis.get('resource_uri'):
            lines.append(f"  • API Resource: {analysis['resource_uri']}")
        
        # Note about data provenance
        lines.append(f"\n💡 ABOUT DATA SOURCES:")
        lines.append(f"  • Sources track where biographical data was gathered")
        lines.append(f"  • Essential for data quality and verification")
        lines.append(f"  • Helps researchers understand data provenance")
        
        # Note about analysis
        lines.append(f"\n✅ Source analysis includes domain classification and access tracking")
        lines.append(f"🔍 Notes provide additional context about data gathering")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_education_analyses(analyses: list) -> str:
    """Format comprehensive education analyses for readable output with enhanced degree and school information."""
    if not analyses:
        return "No education records found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        degree_details = analysis['degree_details']
        school_summary = analysis['school_summary']
        
        lines = [
            f"{'='*70}",
            f"EDUCATION {i}: {degree_details.get('degree_level_display', 'Unknown Degree')}",
            f"{'='*70}",
            f"📋 Education ID: {analysis['id']}",
            f"🎓 Degree: {degree_details.get('degree_level_display', 'Unknown')} ({degree_details.get('degree_level', 'N/A')})",
            f"🏫 School: {school_summary.get('school_name', 'Unknown School')}",
            f"📅 Year: {degree_details.get('degree_year', 'Unknown')}"
        ]
        
        # Person information
        if 'person_details' in analysis:
            person = analysis['person_details']
            lines.append(f"\n👤 PERSON INFORMATION:")
            lines.append(f"  • Name: {person.get('full_name', 'Unknown')}")
            lines.append(f"  • Person ID: {person.get('person_id', 'N/A')}")
            lines.append(f"  • Profile: {person.get('absolute_url', 'N/A')}")
            if person.get('fjc_id'):
                lines.append(f"  • FJC ID: {person['fjc_id']}")
            lines.append(f"  • Has Photo: {'Yes' if person.get('has_photo') else 'No'}")
        elif analysis.get('person_id'):
            lines.append(f"\n👤 Person ID: {analysis['person_id']}")
        
        # Enhanced degree information
        lines.append(f"\n🎓 DEGREE DETAILS:")
        if degree_details.get('degree_level_display'):
            lines.append(f"  • Type: {degree_details['degree_level_display']}")
        
        if degree_details.get('degree_detail'):
            lines.append(f"  • Detail: {degree_details['degree_detail']}")
        
        if degree_details.get('degree_year'):
            current_year = 2025  # Could be dynamic
            years_ago = current_year - degree_details['degree_year']
            lines.append(f"  • Year Earned: {degree_details['degree_year']} ({years_ago} years ago)")
        
        # Degree context and insights
        degree_context = degree_details.get('degree_context', {})
        if degree_context:
            lines.append(f"\n📊 DEGREE CONTEXT:")
            lines.append(f"  • Category: {degree_context.get('category', 'Unknown')}")
            lines.append(f"  • Typical Duration: {degree_context.get('typical_duration', 'Unknown')}")
            lines.append(f"  • Description: {degree_context.get('description', 'No description available')}")
        
        # School information
        lines.append(f"\n🏫 SCHOOL INFORMATION:")
        lines.append(f"  • Name: {school_summary.get('school_name', 'Unknown')}")
        if school_summary.get('school_id'):
            lines.append(f"  • School ID: {school_summary['school_id']}")
        if school_summary.get('school_ein'):
            lines.append(f"  • EIN: {school_summary['school_ein']}")
        if school_summary.get('is_alias'):
            lines.append(f"  • ⚠️  This is an alias school record")
            if school_summary.get('alias_of'):
                lines.append(f"  • Alias of: School ID {school_summary['alias_of']}")
        
        # Enhanced school analysis
        if 'enhanced_school_details' in analysis:
            school_analysis = analysis['enhanced_school_details']['school_analysis']
            if school_analysis.get('school_type_hints'):
                lines.append(f"  • School Type: {', '.join(school_analysis['school_type_hints'])}")
            lines.append(f"  • Has EIN: {'Yes' if school_analysis.get('has_ein') else 'No'}")
        
        # Educational progression analysis (if multiple degrees would be shown)
        lines.append(f"\n📚 EDUCATIONAL CONTEXT:")
        degree_level = degree_details.get('degree_level', '').lower()
        if degree_level in ['aa', 'ba']:
            lines.append(f"  • Level: Undergraduate education")
        elif degree_level in ['ma', 'mba', 'llm']:
            lines.append(f"  • Level: Graduate education (requires prior degree)")
        elif degree_level in ['jd', 'md']:
            lines.append(f"  • Level: Professional doctorate (requires prior degree)")
        elif degree_level in ['phd', 'jsd']:
            lines.append(f"  • Level: Academic doctorate (highest degree level)")
        elif degree_level in ['cfa', 'cert']:
            lines.append(f"  • Level: Professional certification/training")
        
        # Timeline context
        if degree_details.get('degree_year'):
            year = degree_details['degree_year']
            if year < 1970:
                lines.append(f"  • Era: Historical education (pre-1970)")
            elif year < 1990:
                lines.append(f"  • Era: Mid-career education (1970s-1980s)")
            elif year < 2010:
                lines.append(f"  • Era: Modern education (1990s-2000s)")
            else:
                lines.append(f"  • Era: Recent education (2010s+)")
        
        # Metadata
        metadata = analysis['metadata']
        lines.append(f"\n📊 RECORD METADATA:")
        lines.append(f"  • Created: {metadata.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {metadata.get('date_modified', 'Unknown')}")
        
        # Resource URI for API access
        if analysis.get('resource_uri'):
            lines.append(f"  • API Resource: {analysis['resource_uri']}")
        
        # Note about educational significance
        lines.append(f"\n💡 ABOUT EDUCATIONAL DATA:")
        lines.append(f"  • Educational history helps understand judicial qualifications")
        lines.append(f"  • Legal education (JD, LLB, LLM) particularly relevant for judges")
        lines.append(f"  • School prestige and specialization may influence career paths")
        
        # Note about comprehensive analysis
        lines.append(f"\n✅ All degree level codes converted to human-readable values")
        lines.append(f"🔍 Includes school analysis, degree context, and timeline information")
        lines.append(f"📊 Supports CharFilter, ChoiceFilter, and RelatedFilter queries")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)

def format_citation_verification_simple(results: list, is_text_parsing: bool) -> str:
    """Format citation lookup results for simple, readable output."""
    
    # Build header
    lines = [
        "CITATION VERIFICATION RESULTS",
        "=" * 50,
        f"🔍 Method: {'Text parsing' if is_text_parsing else 'Direct lookup'}",
        f"📊 Citations found: {len(results)}",
        f"🗄️ Database: 18,219,417 citations",
        f"🤖 Parser: Eyecite",
        ""
    ]
    
    # Process each citation
    for i, result in enumerate(results, 1):
        citation = result.get('citation', 'Unknown')
        status = result.get('status')
        
        # Citation header
        lines.extend([
            f"{'=' * 40}",
            f"CITATION {i}: {citation}",
            f"{'=' * 40}"
        ])
        
        # Status with emoji - inline mapping
        status_map = {
            200: "✅ Found and verified",
            404: "❌ Not found in database",
            400: "⚠️ Invalid citation format", 
            300: "🔄 Multiple matches (ambiguous)",
            429: "⏳ Rate limited"
        }
        status_info = status_map.get(status, f"❓ Unknown status ({status})")
        lines.append(f"Status: {status_info}")
        
        # Error message if any
        if result.get('error_message'):
            lines.append(f"❌ Error: {result['error_message']}")
        
        # Normalized citations (corrections/alternatives)
        normalized = result.get('normalized_citations', [])
        if normalized and len(normalized) > 1:
            lines.append(f"📝 Alternatives: {', '.join(normalized)}")
        elif normalized and normalized[0] != citation:
            lines.append(f"📝 Corrected to: {normalized[0]}")
        
        # Position in text (for text parsing)
        if is_text_parsing and result.get('start_index') is not None:
            start = result['start_index']
            end = result['end_index']
            lines.append(f"📍 Found at: characters {start}-{end}")
        
        # Case information
        clusters = result.get('clusters', [])
        if clusters:
            lines.append(f"📚 Cases found: {len(clusters)}")
            lines.append("")
            
            for j, cluster in enumerate(clusters[:2], 1):  # Show max 2 cases
                case_name = cluster.get('case_name', 'Unknown Case')
                lines.append(f"  📋 CASE {j}: {case_name}")
                
                if cluster.get('date_filed'):
                    lines.append(f"      📅 Date: {cluster['date_filed']}")
                
                if cluster.get('judges'):
                    lines.append(f"      👨‍⚖️ Judges: {cluster['judges']}")
                
                cite_count = cluster.get('citation_count', 0)
                lines.append(f"      📊 Cited: {cite_count:,} times")
                
                if cluster.get('precedential_status'):
                    lines.append(f"      ⚖️ Status: {cluster['precedential_status']}")
                
                # Show parallel citations
                citations = cluster.get('citations', [])
                if citations:
                    cite_strings = []
                    for cite in citations[:3]:  # Show first 3
                        vol = cite.get('volume', '')
                        rep = cite.get('reporter', '')
                        pg = cite.get('page', '')
                        if vol and rep and pg:
                            cite_strings.append(f"{vol} {rep} {pg}")
                    if cite_strings:
                        lines.append(f"      📚 Citations: {', '.join(cite_strings)}")
                
                # URL
                if cluster.get('absolute_url'):
                    url = f"https://www.courtlistener.com{cluster['absolute_url']}"
                    lines.append(f"      🔗 URL: {url}")
                
                lines.append("")  # Space between cases
        
        lines.append("")  # Space between citations
    
    # Add summary statistics for multiple citations
    if len(results) > 1:
        found_count = sum(1 for r in results if r.get('status') == 200)
        not_found_count = sum(1 for r in results if r.get('status') == 404)
        
        lines.extend([
            "📈 SUMMARY:",
            f"✅ Found: {found_count}",
            f"❌ Not found: {not_found_count}",
            f"📊 Success rate: {(found_count/len(results)*100):.1f}%",
            ""
        ])
    
    # Add helpful notes
    lines.extend([
        "💡 STATUS CODES:",
        "✅ 200 = Citation found and verified",
        "❌ 404 = Citation not found in database",
        "⚠️ 400 = Invalid citation format",
        "🔄 300 = Multiple matches (ambiguous)",
        "⏳ 429 = Rate limited (60/minute)",
        "",
        "🔍 Limitations:",
        "• Does not verify statutes, law journals, or id/supra citations",
        "• Max 250 citations per request",
        "• Max 64,000 characters for text parsing"
    ])
    
    return '\n'.join(lines)

def format_citation_network_results(analysis: dict) -> str:
    """Format citation network analysis results for readable output."""
    
    if not analysis.get('citations'):
        return "No citation network data to format."
    
    citations = analysis['citations']
    citation_type = analysis.get('type', 'unknown')
    total_found = analysis.get('total_found', 0)
    
    # Build header based on citation direction
    if citation_type == 'authorities':
        header = "LEGAL AUTHORITIES CITED"
        description = "Cases and precedents this opinion relies upon"
        emoji = "📚"
    elif citation_type == 'cited_by':
        header = "LATER CASES CITING THIS OPINION"
        description = "Subsequent decisions that reference this opinion"
        emoji = "🔗"
    else:
        header = "CITATION NETWORK ANALYSIS"
        description = "Citation relationships between legal opinions"
        emoji = "🕸️"
    
    lines = [
        f"{header}",
        "=" * 60,
        f"{emoji} {description}",
        f"📊 Total citations found: {total_found:,}",
        f"📋 Showing: {len(citations)}",
        ""
    ]
    
    # Add source opinion info if available
    if analysis.get('source_opinion'):
        source = analysis['source_opinion']
        lines.extend([
            f"🎯 SOURCE OPINION:",
            f"  • ID: {source.get('id', 'Unknown')}",
            f"  • Case: {source.get('case_name', 'Unknown Case')}",
            f"  • Court: {source.get('court', 'Unknown')}",
            f"  • Date: {source.get('date_filed', 'Unknown')}",
            ""
        ])
    
    # Process each citation relationship
    for i, citation in enumerate(citations, 1):
        citation_lines = [
            f"{'=' * 50}",
            f"CITATION {i}",
            f"{'=' * 50}",
            f"🔗 Citation ID: {citation.get('id', 'Unknown')}"
        ]
        
        # Citation depth (importance indicator)
        depth = citation.get('depth', 0)
        if depth > 0:
            importance = ""
            if depth == 1:
                importance = "(mentioned once)"
            elif depth <= 3:
                importance = "(cited multiple times)"
            elif depth <= 5:
                importance = "(frequently cited)"
            else:
                importance = "(heavily relied upon)"
            
            citation_lines.append(f"📊 Citation Depth: {depth} times {importance}")
        
        # Opinion details
        opinion_info = citation.get('opinion_details', {})
        if opinion_info:
            citation_lines.extend([
                "",
                f"📋 CASE DETAILS:",
                f"  • Opinion ID: {opinion_info.get('id', 'Unknown')}",
                f"  • Case Name: {opinion_info.get('case_name', 'Unknown Case')}",
                f"  • Court: {opinion_info.get('court', 'Unknown')}",
                f"  • Date Filed: {opinion_info.get('date_filed', 'Unknown')}",
                f"  • Judges: {opinion_info.get('judges', 'Unknown')}"
            ])
            
            # Citation count (how influential this case is)
            if opinion_info.get('citation_count') is not None:
                cite_count = opinion_info['citation_count']
                citation_lines.append(f"  • Times Cited: {cite_count:,}")
            
            # Precedential status
            if opinion_info.get('precedential_status'):
                citation_lines.append(f"  • Status: {opinion_info['precedential_status']}")
            
            # URL
            if opinion_info.get('absolute_url'):
                url = f"https://www.courtlistener.com{opinion_info['absolute_url']}"
                citation_lines.append(f"  • URL: {url}")
        
        # Cluster details if available
        cluster_info = citation.get('cluster_details', {})
        if cluster_info:
            citation_lines.extend([
                "",
                f"📚 CLUSTER INFO:",
                f"  • Cluster ID: {cluster_info.get('id', 'Unknown')}",
                f"  • Citations: {', '.join(cluster_info.get('citations', [])[:3])}"
            ])
            if len(cluster_info.get('citations', [])) > 3:
                citation_lines.append(f"    (+{len(cluster_info['citations'])-3} more citations)")
        
        lines.extend(citation_lines)
        lines.append("")  # Spacing between citations
    
    # Add summary statistics
    if len(citations) > 1:
        lines.extend([
            "📈 CITATION ANALYSIS:",
            ""
        ])
        
        # Depth analysis
        depths = [c.get('depth', 0) for c in citations if c.get('depth')]
        if depths:
            avg_depth = sum(depths) / len(depths)
            max_depth = max(depths)
            lines.extend([
                f"📊 Citation Depth Statistics:",
                f"  • Average citations per case: {avg_depth:.1f}",
                f"  • Maximum citations to one case: {max_depth}",
                f"  • Cases cited once: {sum(1 for d in depths if d == 1)}",
                f"  • Cases cited multiple times: {sum(1 for d in depths if d > 1)}",
                ""
            ])
        
        # Time analysis if dates available
        dates = [c.get('opinion_details', {}).get('date_filed') for c in citations]
        dates = [d for d in dates if d]
        if dates:
            lines.extend([
                f"📅 Temporal Analysis:",
                f"  • Date range: {min(dates)} to {max(dates)}",
                f"  • Cases with dates: {len(dates)} of {len(citations)}",
                ""
            ])
    
    # Add helpful notes
    lines.extend([
        "💡 CITATION NETWORK NOTES:",
        "• Depth = number of times one opinion cites another",
        "• Higher depth suggests greater reliance/importance",
        "• Citation networks show legal precedent flow",
        "• Powered by Eyecite citation parsing engine",
        "",
        "🔍 Limitations:",
        "• Not all parallel citations are captured",
        "• Some historical citations may be missing",
        "• Backfilled citations may not be fully linked"
    ])
    
    return '\n'.join(lines)

def format_position_analyses(analyses: list) -> str:
    """Format comprehensive position analyses for readable output with career timeline and appointment details."""
    if not analyses:
        return "No positions found."
    
    output_lines = []
    for i, analysis in enumerate(analyses, 1):
        position_details = analysis['position_details']
        timeline = analysis['timeline']
        appointment = analysis['appointment_process']
        confirmation = analysis['confirmation_details']
        
        lines = [
            f"{'='*70}",
            f"POSITION {i}: {position_details.get('position_type_display', 'Unknown Position')}",
            f"{'='*70}",
            f"📋 Position ID: {analysis['id']}",
            f"💼 Type: {position_details.get('position_type_display', 'Unknown')} ({position_details.get('position_type', 'N/A')})",
            f"🏢 Organization: {position_details.get('organization_name', 'Unknown') if position_details.get('organization_name') else 'Not specified'}",
            f"📍 Location: {analysis['location'].get('city', '')}, {analysis['location'].get('state', '')}"
        ]
        
        # Person information
        if 'person_details' in analysis:
            person = analysis['person_details']
            lines.append(f"\n👤 PERSON INFORMATION:")
            lines.append(f"  • Name: {person.get('full_name', 'Unknown')}")
            lines.append(f"  • Person ID: {person.get('person_id', 'N/A')}")
            if person.get('fjc_id'):
                lines.append(f"  • FJC ID: {person['fjc_id']}")
            if person.get('date_dob'):
                lines.append(f"  • Date of Birth: {person['date_dob']}")
            if person.get('gender'):
                lines.append(f"  • Gender: {person['gender']}")
            if person.get('race'):
                race_list = person['race'] if isinstance(person['race'], list) else [person['race']]
                lines.append(f"  • Race: {', '.join(race_list)}")
            lines.append(f"  • Has Photo: {'Yes' if person.get('has_photo') else 'No'}")
        elif analysis.get('person_id'):
            lines.append(f"\n👤 Person ID: {analysis['person_id']}")
        
        # Position details
        lines.append(f"\n💼 POSITION DETAILS:")
        if position_details.get('job_title'):
            lines.append(f"  • Job Title: {position_details['job_title']}")
        if position_details.get('sector'):
            lines.append(f"  • Sector: {position_details['sector']}")
        
        # Court information
        if 'court_details' in analysis:
            court = analysis['court_details']
            lines.append(f"  • Court: {court.get('full_name', court.get('short_name', 'Unknown'))}")
            lines.append(f"  • Court ID: {court.get('court_id', 'N/A')}")
            lines.append(f"  • Jurisdiction: {court.get('jurisdiction', 'Unknown')}")
            lines.append(f"  • Active: {'Yes' if court.get('in_use') else 'No'}")
        elif position_details.get('court'):
            lines.append(f"  • Court: {position_details['court']}")
        
        # Appointment process
        lines.append(f"\n🏛️  APPOINTMENT PROCESS:")
        if appointment.get('how_selected_display'):
            lines.append(f"  • Selection Method: {appointment['how_selected_display']} ({appointment.get('how_selected', 'N/A')})")
        
        if 'appointer_details' in analysis:
            appointer = analysis['appointer_details']
            lines.append(f"  • Appointer: {appointer.get('full_name', 'Unknown')}")
        elif appointment.get('appointer'):
            lines.append(f"  • Appointer: {appointment['appointer']}")
        
        if appointment.get('nomination_process_display'):
            lines.append(f"  • Process: {appointment['nomination_process_display']}")
        
        if appointment.get('predecessor'):
            lines.append(f"  • Predecessor: {appointment['predecessor']}")
        if appointment.get('supervisor'):
            lines.append(f"  • Supervisor: {appointment['supervisor']}")
        
        # Comprehensive timeline
        lines.append(f"\n📅 CAREER TIMELINE:")
        
        # Nomination and confirmation process
        timeline_events = []
        if timeline.get('date_nominated'):
            timeline_events.append(f"Nominated: {timeline['date_nominated']}")
        if timeline.get('date_referred_to_judicial_committee'):
            timeline_events.append(f"Referred to Committee: {timeline['date_referred_to_judicial_committee']}")
        if timeline.get('date_judicial_committee_action'):
            action = timeline.get('judicial_committee_action', 'action taken')
            timeline_events.append(f"Committee Action: {timeline['date_judicial_committee_action']} ({action})")
        if timeline.get('date_hearing'):
            timeline_events.append(f"Hearing: {timeline['date_hearing']}")
        if timeline.get('date_confirmation'):
            timeline_events.append(f"Confirmed: {timeline['date_confirmation']}")
        if timeline.get('date_elected'):
            timeline_events.append(f"Elected: {timeline['date_elected']}")
        if timeline.get('date_recess_appointment'):
            timeline_events.append(f"Recess Appointment: {timeline['date_recess_appointment']}")
        
        # Service dates
        if timeline.get('date_start'):
            start_granularity = timeline.get('date_granularity_start_display', '')
            service_start = f"Service Started: {timeline['date_start']}"
            if start_granularity:
                service_start += f" ({start_granularity} precision)"
            timeline_events.append(service_start)
        
        if timeline.get('date_termination'):
            end_granularity = timeline.get('date_granularity_termination_display', '')
            service_end = f"Service Ended: {timeline['date_termination']}"
            if end_granularity:
                service_end += f" ({end_granularity} precision)"
            timeline_events.append(service_end)
            
            # Add termination reason
            if timeline.get('termination_reason_display'):
                timeline_events.append(f"Termination Reason: {timeline['termination_reason_display']}")
        elif timeline.get('date_retirement'):
            timeline_events.append(f"Retired: {timeline['date_retirement']}")
        elif timeline.get('is_current'):
            timeline_events.append(f"Status: Currently serving")
        
        for event in timeline_events:
            lines.append(f"  • {event}")
        
        # Service duration analysis
        if 'service_duration' in timeline:
            duration = timeline['service_duration']
            lines.append(f"  • Total Service: {duration['years']} years ({duration['days']} days)")
        elif 'current_service_duration' in timeline:
            duration = timeline['current_service_duration']
            lines.append(f"  • Current Service: {duration['years']} years ({duration['days']} days)")
        
        # Confirmation details
        if any(confirmation.values()):
            lines.append(f"\n🗳️  CONFIRMATION DETAILS:")
            
            if confirmation.get('vote_type_display'):
                lines.append(f"  • Vote Type: {confirmation['vote_type_display']} ({confirmation.get('vote_type', 'N/A')})")
            
            if confirmation.get('voice_vote') is not None:
                lines.append(f"  • Voice Vote: {'Yes' if confirmation['voice_vote'] else 'No'}")
            
            # Vote counts and analysis
            if confirmation.get('votes_yes') is not None and confirmation.get('votes_no') is not None:
                lines.append(f"  • Yes Votes: {confirmation['votes_yes']:,}")
                lines.append(f"  • No Votes: {confirmation['votes_no']:,}")
                
                if confirmation.get('votes_yes_percent') is not None:
                    lines.append(f"  • Yes Percentage: {confirmation['votes_yes_percent']}%")
                if confirmation.get('votes_no_percent') is not None:
                    lines.append(f"  • No Percentage: {confirmation['votes_no_percent']}%")
            
            # Vote analysis
            vote_analysis = confirmation.get('vote_analysis')
            if vote_analysis:
                lines.append(f"  • Total Votes Cast: {vote_analysis['total_votes']:,}")
                lines.append(f"  • Margin: {vote_analysis['margin']:,} votes")
                lines.append(f"  • Approval Rate: {vote_analysis['percentage_approved']}%")
                
                if vote_analysis.get('was_unanimous'):
                    lines.append(f"  • Result: Unanimous approval")
                elif vote_analysis.get('was_close'):
                    lines.append(f"  • Result: Close vote (margin ≤ 5)")
                else:
                    lines.append(f"  • Result: Clear majority")
        
        # Retention events
        if 'retention_events' in analysis:
            retention = analysis['retention_events']
            lines.append(f"\n🔄 RETENTION EVENTS ({retention['event_count']}):")
            for j, event in enumerate(retention['events'], 1):
                # Display basic retention event info
                lines.append(f"  {j}. Event ID: {event.get('id', 'Unknown')}")
                # Additional event details would be formatted here based on retention event structure
        
        # Metadata and data quality
        metadata = analysis['metadata']
        lines.append(f"\n📊 METADATA:")
        lines.append(f"  • Created: {metadata.get('date_created', 'Unknown')}")
        lines.append(f"  • Modified: {metadata.get('date_modified', 'Unknown')}")
        if metadata.get('has_inferred_values'):
            lines.append(f"  • ⚠️  Contains inferred values (some data estimated)")
        
        # Resource URI for API access
        if analysis.get('resource_uri'):
            lines.append(f"  • API Resource: {analysis['resource_uri']}")
        
        # Note about comprehensive analysis
        lines.append(f"\n✅ All position codes converted to human-readable values")
        lines.append(f"🔍 Includes appointment process, timeline, and confirmation analysis")
        lines.append(f"⚖️ Timeline shows complete career progression from nomination to service")
        
        output_lines.append('\n'.join(lines))
    
    return '\n\n'.join(output_lines)