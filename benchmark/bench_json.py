import time
import tracemalloc
from schemas.report import Report, ReportFormat
from schemas.finding import Finding
from schemas.generated_report import GeneratedReport
from reporting.json_renderer import generate_json
from uuid import uuid4

def benchmark_json(count):
    findings = tuple([Finding(title=f"Bug {i}", severity="low", confidence="certain", description="test", evidence="test") for i in range(count)])
    report = Report(report_id=uuid4(), report_path="test", report_format=ReportFormat.JSON, findings=findings, total_findings=count)
    
    tracemalloc.start()
    t0 = time.time()
    generated = generate_json(report)
    t1 = time.time()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"JSON {count}: {t1-t0:.4f}s, Peak RSS: {peak/1024/1024:.2f} MB, Size: {len(generated.content)/1024/1024:.2f} MB")

if __name__ == "__main__":
    benchmark_json(10)
    benchmark_json(100)
    benchmark_json(1000)
    benchmark_json(10000)
