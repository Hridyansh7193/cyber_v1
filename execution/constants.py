from typing import TypedDict, List, Dict, Any

METADATA_SCHEMA_VERSION = 1

NEW_SUBDOMAINS = "new_subdomains"
NEW_HOSTS = "new_hosts"
NEW_URLS = "new_urls"
NEW_JS_FILES = "new_js_files"
NEW_ENDPOINTS = "new_endpoints"
NEW_SWAGGER = "new_swagger"
NEW_GRAPHQL = "new_graphql"
NEW_NUCLEI = "new_nuclei"
NEW_DALFOX = "new_dalfox"
NEW_TAKEOVERS = "new_takeovers"
NEW_FUZZ_RESULTS = "new_fuzz_results"
NEW_SECRETS = "new_secrets"

class ToolMetadata(TypedDict, total=False):
    new_subdomains: List[str]
    new_hosts: List[str]
    new_urls: List[str]
    new_js_files: List[str]
    new_endpoints: List[str]
    new_secrets: List[Dict[str, Any]]
    new_swagger: List[Dict[str, Any]]
    new_graphql: List[Dict[str, Any]]
    new_nuclei: List[Dict[str, Any]]
    new_dalfox: List[Dict[str, Any]]
    new_takeovers: List[Dict[str, Any]]
    new_fuzz_results: List[Dict[str, Any]]
