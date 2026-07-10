import xml.etree.ElementTree as ET
from schemas.report import Report
from schemas.generated_report import GeneratedReport
from xml.dom import minidom

def generate_burpxml(report: Report) -> GeneratedReport:
    """Generates a Burp Suite XML report from a Report object."""
    issues = ET.Element("issues", burpVersion="2023.1")
    
    for finding in report.findings:
        issue = ET.SubElement(issues, "issue")
        
        serial = ET.SubElement(issue, "serialNumber")
        serial.text = str(finding.id)
        
        type_elem = ET.SubElement(issue, "type")
        type_elem.text = "8388608" # Generic extension issue type
        
        name = ET.SubElement(issue, "name")
        name.text = finding.title
        
        host = ET.SubElement(issue, "host", ip="")
        host.text = finding.source_tool
        
        path = ET.SubElement(issue, "path")
        path.text = finding.evidence[:100]
        
        severity = ET.SubElement(issue, "severity")
        severity_map = {"critical": "High", "high": "High", "medium": "Medium", "low": "Low", "info": "Information"}
        severity.text = severity_map.get(finding.severity.lower(), "Information")
        
        confidence = ET.SubElement(issue, "confidence")
        conf_map = {"certain": "Certain", "firm": "Firm", "tentative": "Tentative"}
        confidence.text = conf_map.get(finding.confidence.lower(), "Tentative")
        
        issue_bg = ET.SubElement(issue, "issueBackground")
        issue_bg.text = "<![CDATA[" + finding.title + "]]>"
        
        issue_detail = ET.SubElement(issue, "issueDetail")
        issue_detail.text = "<![CDATA[" + (finding.evidence or "") + "]]>"
        
    xml_str = ET.tostring(issues, encoding='utf-8')
    parsed_xml = minidom.parseString(xml_str)
    content = parsed_xml.toprettyxml(indent="  ")
    
    filename = "report.xml"
    if report.report_path:
        parts = report.report_path.replace("\\", "/").split("/")
        filename = parts[-1].replace(".json", ".xml").replace(".md", ".xml")

    return GeneratedReport(
        report_id=report.report_id,
        format="burpxml",
        filename=filename,
        mime_type="application/xml",
        content=content
    )
