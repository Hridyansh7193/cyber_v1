import re

plugin_paths = [
    r"execution\recon\subfinder_wrapper.py",
    r"execution\recon\httpx_wrapper.py",
    r"execution\recon\katana_wrapper.py",
    r"execution\recon\assetfinder_wrapper.py",
    r"execution\recon\gau_wrapper.py",
    r"execution\js\linkfinder_wrapper.py",
    r"execution\js\secretfinder_wrapper.py",
    r"execution\js\trufflehog_wrapper.py",
    r"execution\vuln\nuclei_wrapper.py",
    r"execution\vuln\dalfox_wrapper.py",
    r"execution\vuln\ffuf_wrapper.py",
    r"execution\vuln\subzy_wrapper.py",
    r"execution\api\swagger_wrapper.py",
    r"execution\api\graphql_wrapper.py",
]

caps_map = {
    "subfinder": ["Capability.RECON", "Capability.DNS"],
    "assetfinder": ["Capability.RECON", "Capability.DNS"],
    "httpx": ["Capability.RECON", "Capability.HTTP"],
    "katana": ["Capability.RECON", "Capability.HTTP"],
    "gau": ["Capability.RECON", "Capability.HTTP"],
    "linkfinder": ["Capability.JS"],
    "secretfinder": ["Capability.JS", "Capability.SECRETS"],
    "trufflehog": ["Capability.SECRETS"],
    "nuclei": ["Capability.VULN", "Capability.HTTP"],
    "dalfox": ["Capability.VULN", "Capability.FUZZING"],
    "ffuf": ["Capability.FUZZING", "Capability.HTTP"],
    "subzy": ["Capability.VULN", "Capability.DNS"],
    "swagger": ["Capability.API"],
    "graphql": ["Capability.API"]
}

for path in plugin_paths:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "from schemas.runtime import Capability" not in content:
        content = content.replace(
            "from execution.plugins.base import ExecutionPlugin, PluginMetadata",
            "from execution.plugins.base import ExecutionPlugin, PluginMetadata\nfrom schemas.runtime import Capability"
        )
    
    # regex to replace capabilities=("...",) with capabilities=(Capability.RECON, ...)
    name_match = re.search(r'name="([^"]+)"', content)
    if name_match:
        name = name_match.group(1).replace("_discovery", "").replace("_plugin", "")
        # map name to actual tool name
        if "swagger" in name: name = "swagger"
        if "graphql" in name: name = "graphql"
        
        caps = caps_map.get(name, ["Capability.RECON"])
        caps_str = ", ".join(caps)
        if len(caps) == 1:
            caps_str += ","
        
        content = re.sub(
            r'capabilities=\([^)]+\)',
            f'capabilities=({caps_str})',
            content
        )
        
        # Add minimum_version
        if "minimum_version=" not in content:
            content = content.replace(
                "supported_tools=",
                'minimum_version="0.0.1",\n            supported_tools='
            )
            
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
