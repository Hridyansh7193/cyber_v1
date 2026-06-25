from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.prioritized_asset import PrioritizedAsset

def prioritize(state: ExecutionState, config: BugHunterConfig) -> tuple[PrioritizedAsset, ...]:
    assets = []
    
    # Priority scoring logic
    for url in state.recon_state.urls:
        score = 10.0
        reasoning = []
        if "admin" in url or "login" in url:
            score += 20.0
            reasoning.append("Authentication required")
        if "api" in url:
            score += 15.0
            reasoning.append("API endpoint")
            
        if not reasoning:
            reasoning.append("Discovered URL")
            
        assets.append(PrioritizedAsset(
            asset=url,
            asset_type="URL",
            score=score,
            reasoning=" ".join(reasoning)
        ))
        
    for url in state.api_state.swagger_urls:
        assets.append(PrioritizedAsset(
            asset=url,
            asset_type="SWAGGER",
            score=50.0,
            reasoning="Swagger documentation exposed"
        ))
        
    for url in state.api_state.graphql_urls:
        assets.append(PrioritizedAsset(
            asset=url,
            asset_type="GRAPHQL",
            score=50.0,
            reasoning="GraphQL endpoint exposed"
        ))
        
    # Sort by score descending
    assets.sort(key=lambda x: x.score, reverse=True)
    return tuple(assets)
