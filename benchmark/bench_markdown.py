import time
import tracemalloc
from schemas.report import Report, ReportFormat
from schemas.finding import Finding
from reporting.markdown_renderer import generate_markdown
from uuid import uuid4

def benchmark_markdown(count):
    findings = tuple([Finding(title=f"Bug {i}", severity="low", confidence="certain", description="test", evidence="test") for i in range(count)])
    report = Report(report_id=uuid4(), report_path="test", report_format=ReportFormat.MARKDOWN, findings=findings, total_findings=count)
    
    tracemalloc.start()
    t0 = time.time()
    generated = generate_markdown(report)
    t1 = time.time()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Markdown {count}: {t1-t0:.4f}s, Peak RSS: {peak/1024/1024:.2f} MB, Size: {len(generated.content)/1024/1024:.2f} MB")

if __name__ == "__main__":
    benchmark_markdown(10)
    benchmark_markdown(100)
    benchmark_markdown(1000)
    benchmark_markdown(10000)
