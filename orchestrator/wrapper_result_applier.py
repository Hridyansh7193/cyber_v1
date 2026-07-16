from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from schemas.tool_result import ToolResult
from schemas.telemetry import ExecutionTelemetry
from execution.constants import *
from typing import Tuple

def _append_trace(state: ExecutionState, stage: str, tool_res: ToolResult, stored_count: int):
    if state.runtime_context and hasattr(state.runtime_context, "trace"):
        from schemas.trace import TraceEvent
        from datetime import datetime, timezone
        import os
        
        workspace_file = ""
        if state.target.session_id:
            from utils.target_utils import sanitize_workspace_target
            workspace_file = os.path.join("workspaces", sanitize_workspace_target(state.target.domain), "sessions", state.target.session_id, "telemetry", tool_res.tool_name, "execution.json")
            
        trace = TraceEvent(
            stage=stage,
            plugin=tool_res.tool_name,
            received=getattr(tool_res, 'received_count', 1),
            stdout_lines=len(tool_res.stdout.splitlines()) if tool_res.stdout else 0,
            parsed=tool_res.parsed_findings,
            stored=stored_count,
            runtime=tool_res.execution_time,
            success=tool_res.success,
            exit_code=tool_res.exit_code,
            errors=list(tool_res.errors),
            warnings=[],
            workspace_file=workspace_file,
            timestamp=datetime.now(timezone.utc)
        )
        state.runtime_context.trace.trace.append(trace)

def _extract_telemetry(wrapper_out: Tuple[ToolResult, ...]) -> Tuple[ExecutionTelemetry, ...]:
    return tuple(
        ExecutionTelemetry(
            tool=t.tool_name,
            version=t.plugin_version,
            command=t.command,
            execution_time=t.execution_time,
            exit_code=t.exit_code,
            stdout_size=t.stdout_size,
            stderr_size=len(t.stderr),
            parsed_objects=t.parsed_findings,
            success=t.success,
            timeout=t.exit_code == -1,
            wrapper_errors=tuple([e for e in t.errors if "Parse error" not in e]),
            parser_errors=tuple([e for e in t.errors if "Parse error" in e]),
            binary_path=t.binary_path,
            working_directory=t.working_directory
        )
        for t in wrapper_out
    )

def apply_recon_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_subdomains = list(state.recon_state.subdomains)
    new_hosts = list(state.recon_state.alive_hosts)
    new_urls = list(state.recon_state.urls)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    merged_tech = dict(state.recon_state.tech_stack)
    merged_waf = dict(state.recon_state.waf_detected)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_subdomains.extend(output.get(NEW_SUBDOMAINS, []))
        new_hosts.extend(output.get(NEW_HOSTS, []))
        new_urls.extend(output.get(NEW_URLS, []))
        
        # Merge tech stack
        for k, v in output.get("tech_stack", {}).items():
            if k in merged_tech:
                merged_tech[k] = tuple(dict.fromkeys(list(merged_tech[k]) + list(v)))
            else:
                merged_tech[k] = v
                
        # Merge waf detected
        merged_waf.update(output.get("waf_detected", {}))
        
        stored_count = sum(len(v) for k, v in output.items() if isinstance(v, (list, tuple)) and k != "tech_stack" and k != "waf_detected")
        _append_trace(state, "recon", tool_res, stored_count)

    merged_subs = tuple(dict.fromkeys(new_subdomains))
    merged_hosts = tuple(dict.fromkeys(new_hosts))
    merged_urls = tuple(dict.fromkeys(new_urls))
    
    new_recon = ReconState(
        subdomains=merged_subs,
        alive_hosts=merged_hosts,
        urls=merged_urls,
        parameters=state.recon_state.parameters,
        tech_stack=merged_tech,
        waf_detected=merged_waf
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"recon_state": new_recon, "logs": tuple(new_logs)})

def apply_js_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_js_files = list(state.js_state.js_files)
    new_endpoints = list(state.js_state.endpoints)
    new_secrets = list(state.js_state.secrets)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_js_files.extend(output.get(NEW_JS_FILES, []))
        new_endpoints.extend(output.get(NEW_ENDPOINTS, []))
        
        # JS plugins like SecretFinder or Trufflehog might return secrets
        secrets = output.get(NEW_SECRETS, [])
        if secrets:
            new_secrets.extend(secrets)
            
        stored_count = sum(len(v) for k, v in output.items() if isinstance(v, (list, tuple)))
        _append_trace(state, "js", tool_res, stored_count)

    merged_files = tuple(dict.fromkeys(new_js_files))
    merged_endpoints = tuple(dict.fromkeys(new_endpoints))
    
    # Simple deduplication for secrets assuming they are dicts
    seen_secrets = set()
    merged_secrets = []
    for secret in new_secrets:
        # Create a hashable representation for deduplication
        # fallback to raw string representation if needed
        repr_str = str(sorted(secret.items())) if isinstance(secret, dict) else str(secret)
        if repr_str not in seen_secrets:
            seen_secrets.add(repr_str)
            merged_secrets.append(secret)
    
    new_js = JSState(
        js_files=merged_files,
        endpoints=merged_endpoints,
        secrets=tuple(merged_secrets)
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"js_state": new_js, "logs": tuple(new_logs)})

def apply_api_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_swagger = list(state.api_state.swagger_urls)
    new_graphql = list(state.api_state.graphql_urls)
    new_endpoints = list(state.api_state.endpoints)
    new_schemas = list(state.api_state.schemas)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_swagger.extend(output.get(NEW_SWAGGER, []))
        new_graphql.extend(output.get(NEW_GRAPHQL, []))
        new_endpoints.extend(output.get("new_api_endpoints", []))
        new_schemas.extend(output.get("new_schemas", []))
        
        stored_count = sum(len(v) for k, v in output.items() if isinstance(v, (list, tuple)))
        _append_trace(state, "api", tool_res, stored_count)

    merged_swagger = tuple(dict.fromkeys(new_swagger))
    merged_graphql = tuple(dict.fromkeys(new_graphql))
    
    # Deduplicate dicts
    seen_endpoints = set()
    merged_endpoints = []
    for ep in new_endpoints:
        repr_str = str(sorted(ep.items())) if isinstance(ep, dict) else str(ep)
        if repr_str not in seen_endpoints:
            seen_endpoints.add(repr_str)
            merged_endpoints.append(ep)
            
    seen_schemas = set()
    merged_schemas = []
    for schema in new_schemas:
        repr_str = str(sorted(schema.items())) if isinstance(schema, dict) else str(schema)
        if repr_str not in seen_schemas:
            seen_schemas.add(repr_str)
            merged_schemas.append(schema)
            
    new_api = APIState(
        swagger_urls=merged_swagger,
        graphql_urls=merged_graphql,
        endpoints=tuple(merged_endpoints),
        schemas=tuple(merged_schemas)
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"api_state": new_api, "logs": tuple(new_logs)})

def apply_vuln_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_nuclei = list(state.vuln_state.nuclei_results)
    new_dalfox = list(state.vuln_state.dalfox_results)
    new_takeovers = list(state.vuln_state.takeovers)
    new_fuzz_results = list(state.vuln_state.fuzz_results)
    new_findings = list(state.findings)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    from schemas.finding import Finding, Severity, Confidence
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        
        # Parse nuclei
        nuclei_out = [n for n in output.get(NEW_NUCLEI, []) if isinstance(n, dict)]
        new_nuclei.extend(nuclei_out)
        for vuln in nuclei_out:
            if isinstance(vuln, dict):
                sev_str = vuln.get("info", {}).get("severity", "info").lower()
                severity = Severity.INFO
                if sev_str in ["low", "medium", "high", "critical"]:
                    severity = Severity(sev_str)
                    
                template_id = vuln.get("template-id", "unknown")
                if template_id == "unknown":
                    category = "Reason: Parser couldn't identify template"
                else:
                    category = "nuclei_template"
                    
                target_url = vuln.get("matched-at", "unknown")
                target_host = vuln.get("host", "unknown")
                
                extracted = vuln.get("extracted-results", [])
                evidence_text = extracted[0] if extracted else target_url
                
                # Semantic Enrichment: Missing Security Headers
                if template_id == "missing-security-headers" or "headers" in template_id:
                    if not extracted:
                        # NOT_MEASURED: No reliable HTTP response/header evidence exists.
                        continue
                        
                    # HSTS is not applicable for plain HTTP contexts
                    if target_url.startswith("http://"):
                        extracted = [h for h in extracted if h.lower() != "strict-transport-security"]
                        
                    if not extracted:
                        continue
                        
                    evidence_text = f"Missing headers: {', '.join(extracted)}"
                    vuln["extracted-results"] = extracted
                    
                from utils.recommendations import get_recommendation
                recommendation = get_recommendation(template_id, category, vuln) or ""
                
                info_dict = vuln.get("info", {})
                description = info_dict.get("description", "")
                
                classification = info_dict.get("classification", {})
                cwe_ids = tuple(classification.get("cwe-id", [])) if isinstance(classification.get("cwe-id"), list) else ()
                cve_ids = tuple(classification.get("cve-id", [])) if isinstance(classification.get("cve-id"), list) else ()
                cvss_metrics = classification.get("cvss-metrics", "")
                cvss_score = classification.get("cvss-score", 0.0)
                    
                finding = Finding(
                    title=info_dict.get("name", "Nuclei Finding"),
                    description=description,
                    severity=severity,
                    confidence=Confidence.HIGH,
                    evidence=evidence_text,
                    poc=vuln.get("curl-command", ""),
                    source_tool="nuclei",
                    plugin="nuclei",
                    tool_version=tool_res.plugin_version,
                    target=target_host,
                    url=target_url,
                    template_id=template_id,
                    category=category,
                    recommendation=recommendation,
                    timestamp=vuln.get("timestamp", ""),
                    command=tool_res.command or "",
                    parser="nuclei_json_parser",
                    metadata=vuln,
                    references=tuple(info_dict.get("reference", [])) if isinstance(info_dict.get("reference"), list) else (),
                    cwe_ids=cwe_ids,
                    cve_ids=cve_ids,
                    cvss_score=float(cvss_score),
                    cvss_vector=cvss_metrics
                )
                new_findings.append(finding)
                
        # Parse dalfox
        dalfox_out = [d for d in output.get(NEW_DALFOX, []) if isinstance(d, dict)]
        new_dalfox.extend(dalfox_out)
        for vuln in dalfox_out:
            if isinstance(vuln, dict):
                sev_str = vuln.get("severity", "low").lower()
                severity = Severity.LOW
                if sev_str in ["low", "medium", "high", "critical"]:
                    severity = Severity(sev_str)
                    
                from utils.recommendations import get_recommendation
                recommendation = get_recommendation("dalfox_payload", "xss", vuln) or ""
                finding = Finding(
                    title=f"Dalfox XSS: {vuln.get('type', 'Unknown')}",
                    severity=severity,
                    confidence=Confidence.HIGH,
                    evidence=vuln.get("poc", ""),
                    poc=vuln.get("message", ""),
                    source_tool="dalfox",
                    plugin="dalfox",
                    tool_version=tool_res.plugin_version,
                    target=vuln.get("target", "unknown"),
                    url=vuln.get("url", "unknown"),
                    template_id="dalfox_payload",
                    category="xss",
                    recommendation=recommendation,
                    timestamp=vuln.get("timestamp", ""),
                    command=tool_res.command or "",
                    parser="dalfox_json_parser",
                    metadata=vuln
                )
                new_findings.append(finding)
                
        # Parse takeovers and fuzz results
        takeovers_out = [t for t in output.get(NEW_TAKEOVERS, []) if isinstance(t, dict)]
        new_takeovers.extend(takeovers_out)
        fuzz_out = [f for f in output.get(NEW_FUZZ_RESULTS, []) if isinstance(f, dict)]
        new_fuzz_results.extend(fuzz_out)
        
        stored_count = sum(len(v) for k, v in output.items() if isinstance(v, (list, tuple)))
        _append_trace(state, "vuln", tool_res, stored_count)
    
    new_vuln = VulnerabilityState(
        nuclei_results=tuple(new_nuclei),
        dalfox_results=tuple(new_dalfox),
        takeovers=tuple(new_takeovers),
        fuzz_results=tuple(new_fuzz_results)
    )
    
    # Deduplicate findings by id
    seen_ids = set()
    deduped_findings = []
    for f in new_findings:
        if f.id not in seen_ids:
            seen_ids.add(f.id)
            deduped_findings.append(f)
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"vuln_state": new_vuln, "findings": tuple(deduped_findings), "logs": tuple(new_logs)})

def apply_parameter_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    new_params = list(state.recon_state.parameters)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_params.extend(output.get(NEW_PARAMETERS, []))
        stored_count = sum(len(v) for k, v in output.items() if isinstance(v, (list, tuple)))
        _append_trace(state, "parameter", tool_res, stored_count)

    merged_params = tuple(dict.fromkeys(new_params))
    
    new_recon = ReconState(
        subdomains=state.recon_state.subdomains,
        alive_hosts=state.recon_state.alive_hosts,
        urls=state.recon_state.urls,
        parameters=merged_params,
        tech_stack=state.recon_state.tech_stack,
        waf_detected=state.recon_state.waf_detected
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"recon_state": new_recon, "logs": tuple(new_logs)})
