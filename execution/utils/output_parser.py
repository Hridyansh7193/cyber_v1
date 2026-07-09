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
                if " " not in line and len(line) < 500:
                    results.append(line)
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
            
        return [line.strip() for line in raw_output.strip().split('\n') if line.strip()]
