from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.attack_graph import AttackGraph, AttackGraphNode, AttackGraphEdge

def generate_graph(state: ExecutionState, config: BugHunterConfig) -> AttackGraph:
    nodes = {}
    edges = set()
    entry_points = set()
    attack_paths = set()
    
    def add_node(id_val, type_val, label_val):
        if id_val not in nodes:
            nodes[id_val] = AttackGraphNode(id=id_val, type=type_val, label=label_val)
            
    def add_edge(source, target, rel):
        edges.add((source, target, rel))
        
    # Target
    target_id = "target_root"
    add_node(target_id, "TARGET", "Root Target")
    entry_points.add(target_id)
    
    # Subdomains
    for sub in state.recon_state.subdomains:
        sub_id = f"sub_{sub}"
        add_node(sub_id, "SUBDOMAIN", sub)
        add_edge(target_id, sub_id, "has_subdomain")
        
        # We can map hosts, URLs, findings
    
    for url in state.recon_state.urls:
        url_id = f"url_{url}"
        add_node(url_id, "URL", url)
        # Attempt to link to subdomain
        for sub in state.recon_state.subdomains:
            if sub in url:
                add_edge(f"sub_{sub}", url_id, "hosts_url")
                break
        else:
            add_edge(target_id, url_id, "hosts_url")
            
    for finding in state.findings:
        finding_id = f"finding_{finding.title}"
        add_node(finding_id, "FINDING", finding.title)
        
        endpoint = finding.title.split(" in ")[1] if " in " in finding.title else finding.title
        if endpoint:
            add_edge(f"url_{endpoint}", finding_id, "has_vulnerability")
            attack_paths.add(f"{target_id} -> url_{endpoint} -> {finding_id}")
        else:
            add_edge(target_id, finding_id, "has_vulnerability")
            
    final_edges = tuple(
        AttackGraphEdge(source=s, target=t, relationship=r) 
        for s, t, r in sorted(edges)
    )
    
    return AttackGraph(
        nodes=tuple(nodes.values()),
        edges=final_edges,
        entry_points=tuple(sorted(entry_points)),
        attack_paths=tuple(sorted(attack_paths)),
        confidence=1.0
    )
