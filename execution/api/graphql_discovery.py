#!/usr/bin/env python3
import sys
import json
import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="GraphQL endpoint discovery tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL to scan")
    args = parser.parse_args()

    target = args.url
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    paths = ["/graphql", "/api/graphql", "/v1/graphql"]
    query = {"query": "{ __schema { queryType { name } } }"}
    
    for path in paths:
        try:
            r = requests.post(target.rstrip("/") + path, json=query, timeout=5, verify=False)
            if r.status_code == 200 and "data" in r.text.lower() and "__schema" in r.text.lower():
                print(json.dumps({"url": args.url, "endpoint": path, "introspection": True}))
                sys.exit(0)
            
            # Sometimes GET is allowed
            r_get = requests.get(target.rstrip("/") + path + "?query={__schema{queryType{name}}}", timeout=5, verify=False)
            if r_get.status_code == 200 and "data" in r_get.text.lower() and "__schema" in r_get.text.lower():
                print(json.dumps({"url": args.url, "endpoint": path, "introspection": True}))
                sys.exit(0)
        except Exception:
            pass

    sys.exit(0)

if __name__ == "__main__":
    main()
