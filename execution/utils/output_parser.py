import json
from typing import Dict, Any, List, Tuple

class OutputParser:
    @staticmethod
    def parse_json(raw_output: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parses a string containing JSON or JSON Lines into a list of dicts.
        Returns a tuple of (parsed_results, parse_errors)
        """
        if not raw_output or not raw_output.strip():
            return [], []
            
        # Try to parse as a single JSON object first
        try:
            parsed = json.loads(raw_output)
            if isinstance(parsed, list):
                return parsed, []
            elif isinstance(parsed, dict):
                return [parsed], []
        except json.JSONDecodeError:
            try:
                start = raw_output.find('{')
                end = raw_output.rfind('}')
                if start != -1 and end != -1 and start < end:
                    parsed = json.loads(raw_output[start:end+1])
                    if isinstance(parsed, dict):
                        return [parsed], []
            except json.JSONDecodeError:
                pass
        results = []
        errors = []
        for line in raw_output.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                # If it's a valid string (no spaces, could be a domain/endpoint), keep it.
                sanitized = OutputParser.sanitize_target(line)
                if sanitized:
                    results.append(sanitized)
                else:
                    errors.append(f"JSONDecodeError: {str(e)} on line: {line[:50]}")
                
        return results, errors

    @staticmethod
    def parse_lines(raw_output: str) -> List[str]:
        """
        Parses a string into a list of non-empty lines.
        """
        if not raw_output or not raw_output.strip():
            return []
        parsed = []
        for line in raw_output.strip().split('\n'):
            sanitized = OutputParser.sanitize_target(line)
            if sanitized:
                parsed.append(sanitized)
        return parsed

    @staticmethod
    def sanitize_target(target: str) -> str:
        """
        Validates target quality. Drops malformed strings, headers, and html tags.
        Returns the sanitized string, or empty string if invalid.
        """
        target = target.strip()
        if not target:
            return ""
        if " " in target or "<" in target or ">" in target or '"' in target or "'" in target:
            return ""
        if len(target) > 2000:
            return ""
        if target.startswith("HTTP/") or target.startswith("Content-Type:"):
            return ""
        return target
