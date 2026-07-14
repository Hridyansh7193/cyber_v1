from pathlib import Path
from typing import Dict, List, Optional

class WordlistManager:
    def __init__(self):
        self._wordlists: Dict[str, str] = {}
        self._search_paths = [
            Path.home() / "SecLists",
            Path.home() / ".local" / "share" / "seclists",
            Path("/usr/share/seclists"),
            Path("wordlists"),
            Path("project/wordlists")
        ]

    def detect(self) -> None:
        """Find common wordlists across search paths."""
        common_lists = {
            "common": str(Path.home() / "SecLists" / "Discovery" / "Web-Content" / "common.txt"),
            "raft-small-words": "Discovery/Web-Content/raft-small-words.txt",
            "raft-large-words": "Discovery/Web-Content/raft-large-words.txt",
            "api": "Discovery/Web-Content/api/api-endpoints.txt",
            "parameters": "Discovery/Web-Content/burp-parameter-names.txt"
        }

        for name, rel_path in common_lists.items():
            if Path(rel_path).is_absolute():
                self._wordlists[name] = rel_path
                continue

            for base_path in self._search_paths:
                full_path = base_path / rel_path
                if full_path.exists() and full_path.is_file():
                    self._wordlists[name] = str(full_path)
                    break

    def has(self, name: str) -> bool:
        return name in self._wordlists

    def get(self, name: str) -> Optional[str]:
        return self._wordlists.get(name)

    def available(self) -> List[str]:
        return list(self._wordlists.keys())
