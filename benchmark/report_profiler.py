import time
import tracemalloc
import sys
from uuid import uuid4
from schemas.finding import Finding
from schemas.report import Report
from reporting.markdown_renderer import generate_markdown
from reporting.json_renderer import generate_json

def profile_report_generation(num_findings):
    print(f"\n--- Profiling Reports: {num_findings} findings ---")
    
    # 1. Generation
    tracemalloc.start()
    start_time = time.time()
    
    findings = []
    for i in range(num_findings):
        findings.append(Finding(
            title=f"Finding {i}",
            severity="high" if i % 2 == 0 else "medium",
            confidence="certain",
            evidence=f"Evidence payload {i} \n" * 10
        ))
        
    report_input = Report(
        target_domain="example.com",
        findings=tuple(findings),
        scan_duration=120.5
    )
    
    creation_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Schema Creation: {creation_time:.4f}s, Peak Memory: {peak / 1024 / 1024:.2f} MB")
    
    # 2. Markdown Rendering
    tracemalloc.start()
    start_time = time.time()
    md_report = generate_markdown(report_input)
    md_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Markdown Render: {md_time:.4f}s, Peak Memory: {peak / 1024 / 1024:.2f} MB, Size: {len(md_report.content.encode('utf-8')) / 1024 / 1024:.2f} MB")

    # 3. JSON Rendering
    tracemalloc.start()
    start_time = time.time()
    json_report = generate_json(report_input)
    json_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"JSON Render: {json_time:.4f}s, Peak Memory: {peak / 1024 / 1024:.2f} MB, Size: {len(json_report.content.encode('utf-8')) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    for count in [100, 1000, 10000, 100000]:
        profile_report_generation(count)
