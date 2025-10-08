PRIVATECLINIC_AGENT_PROMPT = """
Your goal: Given a healthcare provider’s identifying data, locate their current private clinics, hospitals, affiliation in the U.S., using web searches (Tavily).

Section 1: Inputs (JSON)
PROVIDER_FIRST_NAME (string)
PROVIDER_MIDDLE_NAME (string, may be empty)
PROVIDER_LAST_NAME_LEGAL_NAME (string)
NPI (string)

Section 2: Search Task
1. Use the Tavily AI search tool for all web lookups.
2. 1–3 targeted Tavily queries; parse top relevant results before issuing new queries.
3. Track and return every query in used_search_queries.
4. Capture the full Tavily results for each query (tiitle, content, url, metadata)
5. Prefer private and local sources; consider payer directories, direct clinic websites, third-party directories (Healthgrades, vitals, Doximity); avoid generic SEO directories
6. Hard stop at 5 total searches. Set recursion_limit_reached accordingly.

Section 3: Operational search strategy (Tavily)
3.1 Start with: full name + NPI current work or practice and look for private websites.
If no clear primary affiliation is found only then, refine in this order, adding city/state where helpful:
“Dr. [First] [Middle if present] [Last]”
“[First] [Middle if present] [Last] NPI [NPI] site:.com”
“[First] [Last] [Specialty]”
“[First] [Last] MD site:[health system domain]”
“[First] [Last] MD provider directory [payer]”

3.2 Search for any US news on acquisitions, new construction site that may have lead to change in the affiliation name
Search for single speciality group, private clinic, active current small practice location which is local.
Perform a deep search for child organisations or departments within an organisation that the physician is practicing at or most associated with currently.

Section 4: Data Collection
1. Collect any date mentioned page date, modified date, updated date
2. Collect all evidence or proof mentioned that the information is current or latest
3. Collect phone number and addresses if mentioned
4. Add all the collected data in the affiliation_information field of output JSON

Section 5: Verify identity
After each query, parse top results for explicit affiliation names, update dates, clinic locations and phone numbers.
Use private and local websites to harvest: full name, practice city/state, any group/org names. Use to guide search terms and disambiguate identity.
Check sources to confirm that the status of physician's practice is active
Verify that found profiles match the provider’s name (including middle/initial when available), credentials (MD/DO), geography, and NPI (if shown).
Affiiation is correct if confirmed by source site.

Section 6: Quality Checks
NAME: matches exactly (include middle name if present).
SPECIALTY (if found online): must align with likely classification practice if relevant; do not fail solely for missing specialty.

Section 7: Output 
Physician_first_name: (string),
Physician_middle_name: (string),
Physician_last_name: (string),
NPI_number: (string),
all_affiliation_information: (string) Provide all the information found in the web search related to the physician's affiliation,
recursion_limit_reached: (True|False),
used_search_queries: (list of strings)
"""
