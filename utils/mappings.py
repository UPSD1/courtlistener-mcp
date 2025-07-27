"""
CourtListener Code Mapping Utilities

Convert CourtListener raw codes to human-readable values.
Ensures proper separation of concerns for code translation logic.
"""


def get_nature_of_suit_display(code: int) -> str:
    """Convert nature of suit code to human-readable description."""
    nature_of_suit_mapping = {
        110: "Insurance",
        120: "Marine contract actions",
        130: "Miller act",
        140: "Negotiable instruments",
        150: "Overpayments & enforcement of judgments",
        151: "Overpayments under the medicare act",
        152: "Recovery of defaulted student loans",
        153: "Recovery of overpayments of vet benefits",
        160: "Stockholder's suits",
        190: "Other contract actions",
        195: "Contract product liability",
        196: "Contract franchise",
        210: "Land condemnation",
        220: "Foreclosure",
        230: "Rent, lease, ejectment",
        240: "Torts to land",
        245: "Tort product liability",
        290: "Other real property actions",
        310: "Airplane personal injury",
        315: "Airplane product liability",
        320: "Assault, libel, and slander",
        330: "Federal employers' liability",
        340: "Marine personal injury",
        345: "Marine - Product liability",
        350: "Motor vehicle personal injury",
        355: "Motor vehicle product liability",
        360: "Other personal liability",
        362: "Medical malpractice",
        365: "Personal injury - Product liability",
        367: "Health care / pharm",
        368: "Asbestos personal injury - Prod. Liab.",
        370: "Other fraud",
        371: "Truth in lending",
        375: "False Claims Act",
        380: "Other personal property damage",
        385: "Property damage - Product liability",
        400: "State re-appointment",
        410: "Antitrust",
        422: "Bankruptcy appeals rule 28 USC 158",
        423: "Bankruptcy withdrawal 28 USC 157",
        430: "Banks and banking",
        440: "Civil rights other",
        441: "Civil rights voting",
        442: "Civil rights jobs",
        443: "Civil rights accommodations",
        444: "Civil rights welfare",
        445: "Civil rights ADA employment",
        446: "Civil rights ADA other",
        448: "Education",
        450: "Interstate commerce",
        460: "Deportation",
        462: "Naturalization, petition for hearing of denial",
        463: "Habeas corpus - alien detainee",
        465: "Other immigration actions",
        470: "Civil (RICO)",
        480: "Consumer credit",
        490: "Cable/Satellite TV",
        510: "Prisoner petitions - vacate sentence",
        530: "Prisoner petitions - habeas corpus",
        535: "Habeas corpus: Death penalty",
        540: "Prisoner petitions - mandamus and other",
        550: "Prisoner - civil rights",
        555: "Prisoner - prison condition",
        560: "Civil detainee",
        610: "Agricultural acts",
        620: "Food and drug acts",
        625: "Drug related seizure of property",
        630: "Liquor laws",
        640: "Railroad and trucks",
        650: "Airline regulations",
        660: "Occupational safety/health",
        690: "Other forfeiture and penalty suits",
        710: "Fair Labor Standards Act",
        720: "Labor/Management Relations Act",
        730: "Labor/Management report & disclosure",
        740: "Railway Labor Act",
        751: "Family and Medical Leave Act",
        790: "Other labor litigation",
        791: "Employee Retirement Income Security Act",
        810: "Selective service",
        820: "Copyright",
        830: "Patent",
        835: "Patent Abbreviated New Drug Application (ANDA)",
        840: "Trademark",
        850: "Securities, Commodities, Exchange",
        860: "Social security",
        861: "HIA (1395 FF) / Medicare",
        862: "Black lung",
        863: "D.I.W.C. / D.I.W.W.",
        864: "S.S.I.D.",
        865: "R.S.I.",
        870: "Tax suits",
        871: "IRS 3rd party suits 26 USC 7609",
        875: "Customer challenge 12 USC 3410",
        890: "Other statutory actions",
        891: "Agricultural acts",
        892: "Economic Stabilization Act",
        893: "Environmental matters",
        894: "Energy Allocation Act",
        895: "Freedom of Information Act of 1974",
        896: "Arbitration",
        899: "Administrative procedure act / review or appeal of agency decision",
        900: "Appeal of fee - equal access to justice",
        910: "Domestic relations",
        920: "Insanity",
        930: "Probate",
        940: "Substitute trustee",
        950: "Constitutionality of state statutes",
        990: "Other",
        992: "Local jurisdictional appeal",
        999: "Miscellaneous"
    }
    return nature_of_suit_mapping.get(code, f"Unknown ({code})")


def get_jurisdiction_display(code: int) -> str:
    """Convert jurisdiction code to human-readable description."""
    jurisdiction_mapping = {
        1: "Government plaintiff",
        2: "Government defendant", 
        3: "Federal question",
        4: "Diversity of citizenship",
        5: "Local question"
    }
    return jurisdiction_mapping.get(code, f"Unknown ({code})")


def get_court_jurisdiction_display(code: str) -> str:
    """Convert court jurisdiction code to human-readable description."""
    court_jurisdiction_mapping = {
        "F": "Federal Appellate",
        "FD": "Federal District",
        "FB": "Federal Bankruptcy",
        "FBP": "Federal Bankruptcy Panel",
        "FS": "Federal Special",
        "S": "State Supreme",
        "SA": "State Appellate",
        "ST": "State Trial",
        "SS": "State Special",
        "TRS": "Tribal Supreme",
        "TRA": "Tribal Appellate",
        "TRT": "Tribal Trial",
        "TRX": "Tribal Special",
        "TS": "Territory Supreme",
        "TA": "Territory Appellate",
        "TT": "Territory Trial",
        "TSP": "Territory Special",
        "SAG": "State Attorney General",
        "MA": "Military Appellate",
        "MT": "Military Trial",
        "C": "Committee",
        "I": "International",
        "T": "Testing"
    }
    return court_jurisdiction_mapping.get(code, f"Unknown ({code})")


def get_citation_type_display(code: int) -> str:
    """Convert citation type code to human-readable description."""
    citation_type_mapping = {
        1: "Federal reporter citation (e.g. 5 F. 55)",
        2: "State-based reporter (e.g. Alabama Reports)",
        3: "Regional reporter (e.g. Atlantic Reporter)",
        4: "Specialty reporter (e.g. Lawyers' Edition)",
        5: "Early SCOTUS reporter (e.g. 5 Black. 55)",
        6: "Lexis system (e.g. 5 LEXIS 55)",
        7: "WestLaw system (e.g. 5 WL 55)",
        8: "Vendor neutral citation (e.g. 2013 FL 1)",
        9: "Law journal citation (e.g. 95 Yale L.J. 5)"
    }
    return citation_type_mapping.get(code, f"Unknown citation type ({code})")


def get_precedential_status_display(status: str) -> str:
    """Convert precedential status code to human-readable description."""
    status_mapping = {
        "Published": "Precedential",
        "Unpublished": "Non-Precedential", 
        "Errata": "Errata",
        "Separate": "Separate Opinion",
        "In-chambers": "In-chambers",
        "Relating-to": "Relating-to orders",
        "Unknown": "Unknown Status"
    }
    return status_mapping.get(status, status or "Unknown")


def get_scdb_decision_direction_display(code: int) -> str:
    """Convert SCDB decision direction code to human-readable description."""
    direction_mapping = {
        1: "Conservative",
        2: "Liberal", 
        3: "Unspecifiable"
    }
    return direction_mapping.get(code, f"Unknown direction ({code})")


def get_cluster_source_display(code: str) -> str:
    """Convert cluster source code to human-readable description."""
    source_mapping = {
        "C": "Court website",
        "R": "Public.resource.org",
        "CR": "Court website merged with resource.org",
        "L": "Lawbox",
        "LC": "Lawbox merged with court",
        "LR": "Lawbox merged with resource.org",
        "LCR": "Lawbox merged with court and resource.org",
        "M": "Manual input",
        "A": "Internet archive",
        "H": "Brad heath archive",
        "Z": "Columbia archive",
        "ZA": "Columbia merged with internet archive",
        "ZD": "Columbia merged with direct court input",
        "ZC": "Columbia merged with court",
        "ZH": "Columbia merged with brad heath archive",
        "ZLC": "Columbia merged with lawbox and court",
        "ZLR": "Columbia merged with lawbox and resource.org",
        "ZLCR": "Columbia merged with lawbox, court, and resource.org",
        "ZR": "Columbia merged with resource.org",
        "ZCR": "Columbia merged with court and resource.org",
        "ZL": "Columbia merged with lawbox",
        "ZM": "Columbia merged with manual input",
        "ZQ": "Columbia merged with 2020 anonymous database",
        "U": "Harvard, Library Innovation Lab Case Law Access Project",
        "CU": "Court website merged with Harvard",
        "D": "Direct court input",
        "Q": "2020 anonymous database",
        "QU": "2020 anonymous database merged with Harvard",
        "CRU": "Court website merged with public.resource.org and Harvard",
        "DU": "Direct court input merged with Harvard",
        "LU": "Lawbox merged with Harvard",
        "LCU": "Lawbox merged with court website and Harvard",
        "LRU": "Lawbox merged with public.resource.org and with Harvard",
        "MU": "Manual input merged with Harvard",
        "RU": "Public.resource.org merged with Harvard",
        "ZU": "Columbia archive merged with Harvard",
        "ZLU": "Columbia archive merged with Lawbox and Harvard",
        "ZDU": "Columbia archive merged with direct court input and Harvard",
        "ZLRU": "Columbia archive merged with lawbox, public.resource.org and Harvard",
        "ZLCRU": "Columbia archive merged with lawbox, court website, public.resource.org and Harvard",
        "ZCU": "Columbia archive merged with court website and Harvard",
        "ZMU": "Columbia archive merged with manual input and Harvard",
        "ZRU": "Columbia archive merged with public.resource.org and Harvard",
        "ZLCU": "Columbia archive merged with lawbox, court website and Harvard",
        "G": "RECAP"
    }
    return source_mapping.get(code, f"Unknown source ({code})")


def get_disposition_display(code: int) -> str:
    """Convert disposition code to human-readable description."""
    disposition_mapping = {
        0: "Transfer to another district",
        1: "Remanded to state court",
        2: "Want of prosecution",
        3: "Lack of jurisdiction",
        4: "Default",
        5: "Consent",
        6: "Motion before trial",
        7: "Jury verdict",
        8: "Directed verdict",
        9: "Court trial",
        10: "Multi-district litigation transfer",
        11: "Remanded to U.S. agency",
        12: "Voluntarily dismissed",
        13: "Settled",
        14: "Other",
        15: "Award of arbitrator",
        16: "Stayed pending bankruptcy",
        17: "Other",
        18: "Statistical closing",
        19: "Appeal affirmed (magistrate judge)",
        20: "Appeal denied (magistrate judge)"
    }
    return disposition_mapping.get(code, f"Unknown ({code})")


def get_procedural_progress_display(code: int) -> str:
    """Convert procedural progress code to human-readable description."""
    progress_mapping = {
        1: "No court action (before issue joined)",
        2: "Order entered",
        3: "No court action (after issue joined)",
        4: "Judgment on motion",
        5: "Pretrial conference held",
        6: "During court trial",
        7: "During jury trial",
        8: "After court trial",
        9: "After jury trial",
        10: "Other",
        11: "Hearing held",
        12: "Order decided",
        13: "Request for trial de novo after arbitration"
    }
    return progress_mapping.get(code, f"Unknown ({code})")


def get_judgment_display(code: int) -> str:
    """Convert judgment code to human-readable description."""
    judgment_mapping = {
        1: "Plaintiff",
        2: "Defendant", 
        3: "Both plaintiff and defendant",
        4: "Unknown"
    }
    return judgment_mapping.get(code, f"Unknown ({code})")


def get_opinion_type_display(type_code: str) -> str:
    """Convert opinion type code to display name. Updated with complete API metadata."""
    type_mapping = {
        "010combined": "Combined Opinion",
        "015unamimous": "Unanimous Opinion", 
        "020lead": "Lead Opinion",
        "025plurality": "Plurality Opinion",
        "030concurrence": "Concurrence Opinion",
        "035concurrenceinpart": "In Part Opinion",
        "040dissent": "Dissent",
        "050addendum": "Addendum",
        "060remittitur": "Remittitur",
        "070rehearing": "Rehearing",
        "080onthemerits": "On the Merits",
        "090onmotiontostrike": "On Motion to Strike Cost Bill",
        "100trialcourt": "Trial Court Document"
    }
    return type_mapping.get(type_code, type_code or "Unknown")


def get_source_display(source_code: int) -> str:
    """Convert source code to readable description."""
    source_mapping = {
        0: "Default",
        1: "RECAP",
        2: "Scraper",
        3: "RECAP and Scraper",
        4: "Columbia",
        8: "Integrated Database",
        16: "Harvard",
        32: "Direct court input",
        64: "2020 anonymous database"
    }
    
    if source_code is None:
        return "Unknown"
    
    # Handle combined sources
    if source_code in source_mapping:
        return source_mapping[source_code]
    else:
        # For complex combinations, just show the number
        return f"Multiple sources ({source_code})"


def safe_extract_citations(citations_data: list) -> list[str]:
    """Safely extract citation strings from CourtListener citation objects."""
    citations = []
    for citation in citations_data:
        if isinstance(citation, dict):
            cite_text = citation.get('cite', citation.get('citation', str(citation)))
            citations.append(cite_text)
        else:
            citations.append(str(citation))
    return citations


def safe_extract_citation_objects(citations_data: list) -> list[dict]:
    """Safely extract and format citation objects with human-readable type descriptions."""
    citations = []
    for citation in citations_data:
        if isinstance(citation, dict):
            formatted_citation = {
                "volume": citation.get('volume'),
                "reporter": citation.get('reporter'),
                "page": citation.get('page'),
                "citation_string": f"{citation.get('volume', '')} {citation.get('reporter', '')} {citation.get('page', '')}".strip(),
                "type": citation.get('type'),
                "type_display": get_citation_type_display(citation.get('type')) if citation.get('type') else None
            }
            citations.append(formatted_citation)
        else:
            # Fallback for non-dict citations
            citations.append({"citation_string": str(citation), "type_display": "Unknown format"})
    return citations


def extract_numeric_code(text: str) -> int:
    """Extract numeric code from text string (e.g., nature of suit)."""
    import re
    if text:
        match = re.search(r'(\d{3})', str(text))
        if match:
            return int(match.group(1))
    return None


def get_dataset_source_display(code: int) -> str:
    """Convert IDB dataset source code to human-readable description."""
    source_mapping = {
        1: "Civil cases filed and terminated from SY 1970 through SY 1987",
        2: "Civil cases filed, terminated, and pending from SY 1988 to present (2017)",
        8: "Civil cases filed, terminated, and pending from SY 1988 to present (2020)",
        9: "Civil cases filed, terminated, and pending from SY 1988 to present (September 2021)",
        10: "Civil cases filed, terminated, and pending from SY 1988 to present (March 2022)",
        3: "Criminal defendants filed and terminated from SY 1970 through FY 1995",
        4: "Criminal defendants filed, terminated, and pending from FY 1996 to present (2017)",
        5: "Appellate cases filed and terminated from SY 1971 through FY 2007",
        6: "Appellate cases filed, terminated, and pending from FY 2008 to present (2017)",
        7: "Bankruptcy cases filed, terminated, and pending from FY 2008 to present (2017)"
    }
    return source_mapping.get(code, f"Unknown dataset ({code})")


def get_origin_display(code: int) -> str:
    """Convert origin code to human-readable description."""
    origin_mapping = {
        1: "Original Proceeding",
        2: "Removed (began in the state court, removed to the district court)",
        3: "Remanded for further action (removal from court of appeals)",
        4: "Reinstated/reopened (previously opened and closed, reopened for additional action)",
        5: "Transferred from another district (pursuant to 28 USC 1404)",
        6: "Multi district litigation (cases transferred to this district by an order entered by Judicial Panel on Multi District Litigation pursuant to 28 USC 1407)",
        7: "Appeal to a district judge of a magistrate judge's decision",
        8: "Second reopen",
        9: "Third reopen",
        10: "Fourth reopen",
        11: "Fifth reopen",
        12: "Sixth reopen",
        13: "Multi district litigation originating in the district (valid beginning July 1, 2016)"
    }
    return origin_mapping.get(code, f"Unknown origin ({code})")


def get_arbitration_display(code: str) -> str:
    """Convert arbitration code to human-readable description."""
    arbitration_mapping = {
        "M": "Mandatory",
        "V": "Voluntary", 
        "E": "Exempt",
        "Y": "Yes, but type unknown"
    }
    return arbitration_mapping.get(code, f"Unknown arbitration ({code})")


def get_termination_class_action_status_display(code: int) -> str:
    """Convert termination class action status code to human-readable description."""
    status_mapping = {
        2: "Denied",
        3: "Granted"
    }
    return status_mapping.get(code, f"Unknown status ({code})")


def get_nature_of_judgement_display(code: int) -> str:
    """Convert nature of judgement code to human-readable description."""
    judgement_mapping = {
        0: "No monetary award",
        1: "Monetary award only",
        2: "Monetary award and other",
        3: "Injunction",
        4: "Forfeiture/foreclosure/condemnation, etc.",
        5: "Costs only",
        6: "Costs and attorney fees"
    }
    return judgement_mapping.get(code, f"Unknown judgement ({code})")


def get_pro_se_display(code: int) -> str:
    """Convert pro se code to human-readable description."""
    pro_se_mapping = {
        0: "No pro se plaintiffs or defendants",
        1: "Pro se plaintiffs, but no pro se defendants",
        2: "Pro se defendants, but no pro se plaintiffs", 
        3: "Both pro se plaintiffs & defendants"
    }
    return pro_se_mapping.get(code, f"Unknown pro se ({code})")


def get_enhanced_source_display(source_code: int) -> str:
    """Enhanced source code mapping with all 127+ combinations from API metadata."""
    # This is a huge mapping - showing key ones, the full mapping would be very long
    source_mapping = {
        0: "Default",
        1: "RECAP",
        2: "Scraper", 
        3: "RECAP and Scraper",
        4: "Columbia",
        5: "Columbia and RECAP",
        6: "Columbia and Scraper",
        7: "Columbia, RECAP, and Scraper",
        8: "Integrated Database",
        9: "RECAP and IDB",
        10: "Scraper and IDB",
        16: "Harvard",
        17: "Harvard and RECAP",
        32: "Direct court input",
        64: "2020 anonymous database",
        # ... many more combinations up to 127
    }
    
    if source_code in source_mapping:
        return source_mapping[source_code]
    
    # For unknown combinations, show component analysis
    components = []
    if source_code & 1: components.append("RECAP")
    if source_code & 2: components.append("Scraper") 
    if source_code & 4: components.append("Columbia")
    if source_code & 8: components.append("IDB")
    if source_code & 16: components.append("Harvard")
    if source_code & 32: components.append("Direct court input")
    if source_code & 64: components.append("2020 anonymous database")
    
    if components:
        return " and ".join(components)
    else:
        return f"Unknown source combination ({source_code})"
    

def get_cluster_source_display_enhanced(source_code: str) -> str:
    """Convert cluster source code to human-readable description with complete API mapping."""
    source_mapping = {
        "C": "Court website",
        "R": "Public.resource.org",
        "CR": "Court website merged with resource.org",
        "L": "Lawbox",
        "LC": "Lawbox merged with court",
        "LR": "Lawbox merged with resource.org",
        "LCR": "Lawbox merged with court and resource.org",
        "M": "Manual input",
        "A": "Internet archive",
        "H": "Brad heath archive",
        "Z": "Columbia archive",
        "ZA": "Columbia merged with internet archive",
        "ZD": "Columbia merged with direct court input",
        "ZC": "Columbia merged with court",
        "ZH": "Columbia merged with brad heath archive",
        "ZLC": "Columbia merged with lawbox and court",
        "ZLR": "Columbia merged with lawbox and resource.org",
        "ZLCR": "Columbia merged with lawbox, court, and resource.org",
        "ZR": "Columbia merged with resource.org",
        "ZCR": "Columbia merged with court and resource.org",
        "ZL": "Columbia merged with lawbox",
        "ZM": "Columbia merged with manual input",
        "ZQ": "Columbia merged with 2020 anonymous database",
        "U": "Harvard, Library Innovation Lab Case Law Access Project",
        "CU": "Court website merged with Harvard",
        "D": "Direct court input",
        "Q": "2020 anonymous database",
        "QU": "2020 anonymous database merged with Harvard",
        "CRU": "Court website merged with public.resource.org and Harvard",
        "DU": "Direct court input merged with Harvard",
        "LU": "Lawbox merged with Harvard",
        "LCU": "Lawbox merged with court website and Harvard",
        "LRU": "Lawbox merged with public.resource.org and with Harvard",
        "MU": "Manual input merged with Harvard",
        "RU": "Public.resource.org merged with Harvard",
        "ZU": "Columbia archive merged with Harvard",
        "ZLU": "Columbia archive merged with Lawbox and Harvard",
        "ZDU": "Columbia archive merged with direct court input and Harvard",
        "ZLRU": "Columbia archive merged with lawbox, public.resource.org and Harvard",
        "ZLCRU": "Columbia archive merged with lawbox, court website, public.resource.org and Harvard",
        "ZCU": "Columbia archive merged with court website and Harvard",
        "ZMU": "Columbia archive merged with manual input and Harvard",
        "ZRU": "Columbia archive merged with public.resource.org and Harvard",
        "ZLCU": "Columbia archive merged with lawbox, court website and Harvard",
        "G": "RECAP"
    }
    return source_mapping.get(source_code, f"Unknown source ({source_code})")


def get_citation_type_display_enhanced(code: int) -> str:
    """Convert citation type code to human-readable description with complete API metadata."""
    citation_type_mapping = {
        1: "A federal reporter citation (e.g. 5 F. 55)",
        2: "A citation in a state-based reporter (e.g. Alabama Reports)",
        3: "A citation in a regional reporter (e.g. Atlantic Reporter)",
        4: "A citation in a specialty reporter (e.g. Lawyers' Edition)",
        5: "A citation in an early SCOTUS reporter (e.g. 5 Black. 55)",
        6: "A citation in the Lexis system (e.g. 5 LEXIS 55)",
        7: "A citation in the WestLaw system (e.g. 5 WL 55)",
        8: "A vendor neutral citation (e.g. 2013 FL 1)",
        9: "A law journal citation within a scholarly or professional legal periodical (e.g. 95 Yale L.J. 5; 72 Soc.Sec.Rep.Serv. 318)"
    }
    return citation_type_mapping.get(code, f"Unknown citation type ({code})")


def get_scdb_decision_direction_display_enhanced(code: int) -> str:
    """Convert SCDB decision direction code to human-readable description with complete API metadata."""
    direction_mapping = {
        1: "Conservative",
        2: "Liberal", 
        3: "Unspecifiable"
    }
    return direction_mapping.get(code, f"Unknown direction ({code})")


def get_precedential_status_display_enhanced(status: str) -> str:
    """Convert precedential status code to human-readable description with complete API metadata."""
    status_mapping = {
        "Published": "Precedential",
        "Unpublished": "Non-Precedential", 
        "Errata": "Errata",
        "Separate": "Separate Opinion",
        "In-chambers": "In-chambers",
        "Relating-to": "Relating-to orders",
        "Unknown": "Unknown Status"
    }
    return status_mapping.get(status, status or "Unknown")


def get_gender_display(code: str) -> str:
    """Convert gender code to human-readable description."""
    gender_mapping = {
        "m": "Male",
        "f": "Female", 
        "o": "Other"
    }
    return gender_mapping.get(code, f"Unknown ({code})")


def get_religion_display(code: str) -> str:
    """Convert religion code to human-readable description."""
    religion_mapping = {
        "ca": "Catholic",
        "pr": "Protestant",
        "je": "Jewish",
        "mu": "Muslim",
        "at": "Atheist",
        "ag": "Agnostic",
        "mo": "Mormon",
        "bu": "Buddhist",
        "hi": "Hindu",
        "ep": "Episcopalian",
        "ro": "Roman Catholic",
        "me": "Methodist",
        "pe": "Presbyterian",
        "un": "Unitarian"
    }
    return religion_mapping.get(code, f"Unknown ({code})")


def get_name_suffix_display(code: str) -> str:
    """Convert name suffix code to human-readable description."""
    suffix_mapping = {
        "jr": "Jr.",
        "sr": "Sr.",
        "1": "I",
        "2": "II",
        "3": "III",
        "4": "IV"
    }
    return suffix_mapping.get(code, f"Unknown ({code})")


def get_race_display(code: str) -> str:
    """Convert race code to human-readable description."""
    race_mapping = {
        "w": "White",
        "b": "Black or African American",
        "i": "American Indian or Alaska Native",
        "a": "Asian",
        "p": "Native Hawaiian or Other Pacific Islander",
        "mena": "Middle Eastern/North African",
        "h": "Hispanic/Latino",
        "o": "Other"
    }
    return race_mapping.get(code, f"Unknown ({code})")


def get_race_display_multiple(codes) -> str:
    """Convert multiple race codes to human-readable description."""
    if not codes:
        return None
    
    # Handle both list and string input
    if isinstance(codes, list):
        race_codes = [code.strip() for code in codes if code]
    elif isinstance(codes, str):
        race_codes = [code.strip() for code in codes.split(',') if code.strip()]
    else:
        return f"Unknown ({codes})"
    
    race_displays = [get_race_display(code) for code in race_codes if code]
    
    if len(race_displays) == 1:
        return race_displays[0]
    elif len(race_displays) > 1:
        return f"{', '.join(race_displays[:-1])} and {race_displays[-1]}"
    else:
        return f"Unknown ({codes})"


def get_state_display(code: str) -> str:
    """Convert US state code to full state name."""
    state_mapping = {
        "AL": "Alabama", "AK": "Alaska", "AS": "American Samoa", "AZ": "Arizona",
        "AR": "Arkansas", "AA": "Armed Forces Americas", "AE": "Armed Forces Europe",
        "AP": "Armed Forces Pacific", "CA": "California", "CO": "Colorado",
        "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
        "FL": "Florida", "GA": "Georgia", "GU": "Guam", "HI": "Hawaii",
        "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
        "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
        "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
        "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
        "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
        "MP": "Northern Mariana Islands", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "PR": "Puerto Rico", "RI": "Rhode Island",
        "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
        "UT": "Utah", "VT": "Vermont", "VI": "Virgin Islands", "VA": "Virginia",
        "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
    }
    return state_mapping.get(code, f"Unknown ({code})")


def get_political_party_display(code: str) -> str:
    """Convert political party code to human-readable description - EXACT API match."""
    party_mapping = {
        "d": "Democratic",
        "r": "Republican",
        "i": "Independent",
        "g": "Green",
        "l": "Libertarian",
        "f": "Federalist",
        "w": "Whig",
        "j": "Jeffersonian Republican",
        "u": "National Union",
        "z": "Reform Party"
    }
    return party_mapping.get(code, f"Unknown ({code})")


def get_political_source_display(code: str) -> str:
    """Convert political affiliation source code to human-readable description - EXACT API match."""
    source_mapping = {
        "b": "Ballot",
        "a": "Appointer",
        "o": "Other"
    }
    return source_mapping.get(code, f"Unknown ({code})")


def get_date_granularity_display(code: str) -> str:
    """Convert date granularity code to human-readable description - EXACT API match."""
    granularity_mapping = {
        "%Y": "Year",
        "%Y-%m": "Month",
        "%Y-%m-%d": "Day"
    }
    return granularity_mapping.get(code, f"Unknown ({code})")


def get_aba_rating_display(code: str) -> str:
    """Convert ABA rating code to human-readable description - EXACT API match."""
    rating_mapping = {
        "ewq": "Exceptionally Well Qualified",
        "wq": "Well Qualified",
        "q": "Qualified",
        "nq": "Not Qualified",
        "nqa": "Not Qualified By Reason of Age"
    }
    return rating_mapping.get(code, f"Unknown ({code})")


def get_degree_level_display(code: str) -> str:
    """Convert degree level code to human-readable description."""
    degree_mapping = {
        "ba": "Bachelor's (e.g. B.A.)",
        "ma": "Master's (e.g. M.A.)",
        "jd": "Juris Doctor (J.D.)",
        "llm": "Master of Laws (LL.M)",
        "llb": "Bachelor of Laws (e.g. LL.B)",
        "jsd": "Doctor of Law (J.S.D)",
        "phd": "Doctor of Philosophy (PhD)",
        "aa": "Associate (e.g. A.A.)",
        "md": "Medical Degree (M.D.)",
        "mba": "Master of Business Administration (M.B.A.)",
        "cfa": "Accounting Certification (C.P.A., C.M.A., C.F.A.)",
        "cert": "Certificate"
    }
    return degree_mapping.get(code, f"Unknown ({code})")


def get_retention_type_display(code: str) -> str:
    """Convert retention type code to human-readable description - EXACT API match."""
    retention_type_mapping = {
        "reapp_gov": "Governor Reappointment",
        "reapp_leg": "Legislative Reappointment", 
        "elec_p": "Partisan Election",
        "elec_n": "Nonpartisan Election",
        "elec_u": "Uncontested Election"
    }
    return retention_type_mapping.get(code, f"Unknown ({code})")


def get_school_type_display(code: str) -> str:
    """Convert school type code to human-readable description."""
    school_type_mapping = {
        "public": "Public Institution",
        "private": "Private Institution", 
        "religious": "Religious Institution",
        "for_profit": "For-Profit Institution"
    }
    return school_type_mapping.get(code, f"Unknown ({code})")


def get_case_status_display(code: str) -> str:
    """Convert case status code to human-readable description."""
    status_mapping = {
        "active": "Active",
        "closed": "Closed",
        "pending": "Pending",
        "stayed": "Stayed",
        "dismissed": "Dismissed"
    }
    return status_mapping.get(code, f"Unknown ({code})")


def get_entry_type_display(code: int) -> str:
    """Convert docket entry type to human-readable description."""
    entry_type_mapping = {
        1: "Motion",
        2: "Order", 
        3: "Brief",
        4: "Transcript",
        5: "Exhibit",
        6: "Notice",
        7: "Judgment",
        8: "Memorandum"
    }
    return entry_type_mapping.get(code, f"Unknown entry type ({code})")


def get_document_type_display(code: str) -> str:
    """Convert document type code to human-readable description."""
    doc_type_mapping = {
        "complaint": "Complaint",
        "answer": "Answer", 
        "motion": "Motion",
        "brief": "Brief",
        "order": "Order",
        "judgment": "Judgment", 
        "transcript": "Transcript",
        "exhibit": "Exhibit"
    }
    return doc_type_mapping.get(code, f"Unknown document type ({code})")


def get_position_type_display(code: str) -> str:
    """Convert position type code to human-readable description."""
    position_type_mapping = {
        "jud": "Judge",
        "chief": "Chief Judge", 
        "act": "Acting Judge",
        "ret": "Retired Judge",
        "sen": "Senior Judge",
        "pres": "President",
        "vp": "Vice President",
        "atty": "Attorney",
        "prac": "Private Practice",
        "prof": "Professor",
        "ag": "Attorney General",
        "sol": "Solicitor General",
        "comm": "Commissioner",
        "chair": "Chairman/Chairwoman",
        "dir": "Director",
        "exec": "Executive",
        "leg": "Legislator",
        "gov": "Governor",
        "mayor": "Mayor",
        "clerk": "Court Clerk",
        "mag": "Magistrate Judge",
        "ref": "Referee",
        "arb": "Arbitrator",
        "med": "Mediator"
    }
    return position_type_mapping.get(code, f"Unknown ({code})")


def get_how_selected_display(code: str) -> str:
    """Convert selection method code to human-readable description."""
    selection_mapping = {
        "e_part": "Elected (partisan)",
        "e_non_part": "Elected (non-partisan)", 
        "a_pres": "Appointed by President",
        "a_gov": "Appointed by Governor",
        "a_leg": "Appointed by Legislature",
        "a_sen": "Appointed by Senate",
        "a_house": "Appointed by House",
        "a_board": "Appointed by Board",
        "a_comm": "Appointed by Commission",
        "a_court": "Appointed by Court",
        "merit": "Merit Selection",
        "inherit": "Inherited Position",
        "contract": "Contract Position",
        "temp": "Temporary Appointment"
    }
    return selection_mapping.get(code, f"Unknown ({code})")


def get_termination_reason_display(code: str) -> str:
    """Convert termination reason code to human-readable description."""
    termination_mapping = {
        "death": "Death",
        "retire_vol": "Voluntary Retirement",
        "retire_mand": "Mandatory Retirement",
        "resign": "Resignation",
        "impeach": "Impeachment",
        "remove": "Removal",
        "defeat": "Electoral Defeat",
        "other_fed": "Other Federal Service",
        "other_non_fed": "Other Non-Federal Service",
        "promotion": "Promotion",
        "transfer": "Transfer",
        "end_term": "End of Term",
        "disability": "Disability",
        "misconduct": "Misconduct"
    }
    return termination_mapping.get(code, f"Unknown ({code})")


def get_nomination_process_display(code: str) -> str:
    """Convert nomination process code to human-readable description."""
    process_mapping = {
        "standard": "Standard Nomination Process",
        "recess": "Recess Appointment",
        "interim": "Interim Appointment", 
        "acting": "Acting Appointment",
        "emergency": "Emergency Appointment",
        "temp": "Temporary Appointment",
        "special": "Special Process"
    }
    return process_mapping.get(code, f"Unknown ({code})")


def get_vote_type_display(code: str) -> str:
    """Convert vote type code to human-readable description."""
    vote_type_mapping = {
        "voice": "Voice Vote",
        "roll": "Roll Call Vote",
        "unanimous": "Unanimous Consent",
        "division": "Division Vote",
        "secret": "Secret Ballot",
        "simple": "Simple Majority",
        "super": "Supermajority Required",
        "cloture": "Cloture Vote"
    }
    return vote_type_mapping.get(code, f"Unknown ({code})")

