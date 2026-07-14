#!/usr/bin/env python3
"""
Diagnostic script to analyze orchestration state and find stalls.

Usage:
    python diagnose_stall.py <job_id> [--verbose]

This script:
1. Checks the checkpoint for the job
2. Shows what data passive_recon discovered
3. Profiles the scope enforcement filtering
4. Identifies bottlenecks
"""

import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

def diagnose_job(job_id: str, domain: str = "testphp.vulnweb.com", verbose: bool = False):
    """Analyze a failed/stalled job."""
    
    print(f"\n📋 Diagnosing Job: {job_id}")
    print(f"   Domain: {domain}")
    print("=" * 80)
    
    # Try to load checkpoint
    from utils.target_utils import sanitize_workspace_target
    session_dir = Path("workspaces") / sanitize_workspace_target(domain) / "sessions" / job_id
    checkpoint_path = session_dir / "checkpoint.json"
    
    if not checkpoint_path.exists():
        print(f"❌ No checkpoint found at {checkpoint_path}")
        print("   Job may not have progressed beyond init_node")
        return
    
    with open(checkpoint_path) as f:
        state = json.load(f)
    
    print("✅ Checkpoint loaded")
    
    # Check execution state
    exec_state = state.get("execution_state", {})
    recon = exec_state.get("recon_state", {})
    
    print("\n📊 Recon Discovery Results:")
    print(f"   Subdomains: {len(recon.get('subdomains', []))} discovered")
    print(f"   Alive hosts: {len(recon.get('alive_hosts', []))} discovered")
    print(f"   URLs: {len(recon.get('urls', []))} discovered")
    print(f"   Endpoints: {len(recon.get('endpoints', []))} discovered")
    print(f"   JS objects: {len(recon.get('js_objects', []))} discovered")
    print(f"   API endpoints: {len(recon.get('api_endpoints', []))} discovered")
    
    urls = recon.get("urls", [])
    if not urls:
        print("\n⚠️  No URLs discovered - passive_recon may have failed")
        return
    
    # Analyze URLs
    print(f"\n🔗 URL Analysis ({len(urls)} total):")
    
    netlocs = {}
    schemes = {}
    for url in urls[:10000]:  # Sample first 10k to avoid processing huge lists
        if "://" in url:
            try:
                parsed = urlparse(url)
                scheme = parsed.scheme
                netloc = parsed.netloc.split(":")[0]
                schemes[scheme] = schemes.get(scheme, 0) + 1
                netlocs[netloc] = netlocs.get(netloc, 0) + 1
            except:
                pass
    
    print(f"   Schemes: {schemes}")
    print(f"   Top 10 netlocs: {sorted(netlocs.items(), key=lambda x: -x[1])[:10]}")
    
    # Profile scope filtering (sample)
    print("\n⏱️  Scope Filtering Profile (sample of first 1000 URLs):")
    
    target_scope = exec_state.get("target", {}).get("scope", [domain, f"*.{domain}"])
    print(f"   In-scope rules: {target_scope}")
    
    sample_urls = urls[:1000]
    t0 = time.monotonic()
    
    # Simulate ScopeManager behavior
    from services.scope_manager import ScopeManager
    manager = ScopeManager(in_scope=target_scope)
    
    in_scope_count = 0
    for url in sample_urls:
        if "://" in url:
            try:
                netloc = urlparse(url).netloc.split(":")[0]
                if manager.is_in_scope(netloc):
                    in_scope_count += 1
            except:
                pass
    
    elapsed = time.monotonic() - t0
    rate = len(sample_urls) / elapsed if elapsed > 0 else 0
    
    print(f"   Sample: {sample_urls.__len__()} URLs in {elapsed:.3f}s")
    print(f"   Rate: {rate:.0f} URLs/second")
    print(f"   In-scope: {in_scope_count}/{len(sample_urls)} ({100*in_scope_count/len(sample_urls):.1f}%)")
    
    # Estimate total time
    if len(urls) > 5000:
        total_estimated = (len(urls) / rate) if rate > 0 else 0
        print(f"\n⚠️  Estimated time for ALL {len(urls)} URLs: {total_estimated:.0f}s ({total_estimated/60:.1f} minutes)")
        
        if total_estimated > 300:
            print(f"   ⚠️  RISK: Filtering will take >{5} minutes!")
            print("      Consider reducing URL discovery or optimizing filtering")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_stall.py <job_id> [domain]")
        print("Example: python diagnose_stall.py 5ea0fd43-f513-402a-9030-fc769b543b45")
        sys.exit(1)
    
    job_id = sys.argv[1]
    domain = sys.argv[2] if len(sys.argv) > 2 else "testphp.vulnweb.com"
    verbose = "--verbose" in sys.argv
    
    try:
        diagnose_job(job_id, domain, verbose)
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
