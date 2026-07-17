from typing import Optional
from services.persistence_service import PersistenceService
from schemas.enums import SearchEntityType
from schemas.cli_responses import SearchResponse

class SearchService:
    def __init__(self, persistence_service: PersistenceService):
        self.persistence = persistence_service
        
    def search(
        self,
        query: str,
        entity_type: Optional[SearchEntityType] = None,
        limit: int = 50,
        offset: int = 0,
        session_id: Optional[str] = None,
        sort: str = "relevance"
    ) -> SearchResponse:
        
        results = []
        types_to_search = [entity_type] if entity_type else list(SearchEntityType)
        
        for t in types_to_search:
            items = []
            if t == SearchEntityType.FINDINGS:
                items = self.persistence.get_findings_for_session(session_id) if session_id else self.persistence.get_all_findings()
            elif t == SearchEntityType.REPORTS:
                items = self.persistence.get_reports_for_session(session_id) if session_id else self.persistence.get_all_reports()
            elif t == SearchEntityType.SESSIONS:
                if session_id:
                    sess = self.persistence.get_session(session_id)
                    items = [sess] if sess else []
                else:
                    items = self.persistence.get_all_sessions()
            elif t == SearchEntityType.URLS:
                items = self.persistence.get_all_urls()
            elif t == SearchEntityType.SUBDOMAINS:
                items = self.persistence.get_all_subdomains()
            elif t == SearchEntityType.SECRETS:
                items = self.persistence.get_all_secrets()
                
            for item in items:
                # Basic case-insensitive text search across the stringified model
                if query.lower() in str(item).lower():
                    # For a real implementation, we would extract relevant fields
                    res_dict = item.__dict__.copy() if hasattr(item, "__dict__") else dict(item)
                    res_dict.pop('_sa_instance_state', None)
                    res_dict["_entity_type"] = t.value
                    results.append(res_dict)
                    
        # Sort logic
        if sort == "newest":
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort == "oldest":
            results.sort(key=lambda x: x.get("created_at", ""))
            
        total = len(results)
        
        # Paginate
        paginated_results = results[offset:offset+limit]
        
        return SearchResponse(
            query=query,
            entity_type=entity_type.value if entity_type else "all",
            total_matches=total,
            results=paginated_results
        )
