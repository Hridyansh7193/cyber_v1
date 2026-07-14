#!/usr/bin/env python3
import sys
import json
import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Swagger endpoint discovery tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL to scan")
    args = parser.parse_args()

    target = args.url
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    paths = ["/swagger.json", "/api/swagger.json", "/v1/swagger.json", "/v2/api-docs", "/v3/api-docs"]
    
    for path in paths:
        try:
            r = requests.get(target.rstrip("/") + path, timeout=5, verify=False)  # nosec B501 - intentional for bug bounty targets
            if r.status_code == 200 and ("swagger" in r.text.lower() or "openapi" in r.text.lower() or "paths" in r.text.lower()):
                print(json.dumps({"url": args.url, "endpoint": path, "schema": "2.0"}))
                sys.exit(0)
        except Exception:
            pass

    sys.exit(0)

if __name__ == "__main__":
    main()
