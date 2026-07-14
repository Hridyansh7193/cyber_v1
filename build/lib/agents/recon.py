from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from agents.deltas import ReconDelta

def analyze_recon(state: ExecutionState, config: BugHunterConfig) -> ReconDelta:
    # Deduplicate existing state deterministically
    subs = tuple(dict.fromkeys(state.recon_state.subdomains))
    hosts = tuple(dict.fromkeys(state.recon_state.alive_hosts))
    urls = tuple(dict.fromkeys(state.recon_state.urls))
    
    return ReconDelta(
        subdomains=subs,
        alive_hosts=hosts,
        urls=urls
    )
