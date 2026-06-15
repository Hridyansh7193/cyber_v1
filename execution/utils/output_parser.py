import json
from typing import Dict, Any, List

class OutputParser:
    @staticmethod
    def parse_json(raw_output: str) -> List[Dict[str, Any]]:
        """
        Parses a string containing JSON or JSON Lines into a list of dicts.
        """
        if not raw_output or not raw_output.strip():
            return []
            
        results = []
        for line in raw_output.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
                
        return results

    @staticmethod
    def parse_lines(raw_output: str) -> List[str]:
        """
        Parses a string into a list of non-empty lines.
        """
        if not raw_output or not raw_output.strip():
            return []
            
        return [line.strip() for line in raw_output.strip().split('\n') if line.strip()]
