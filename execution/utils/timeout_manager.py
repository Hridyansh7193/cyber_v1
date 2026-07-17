class TimeoutManager:
    FAST_TIMEOUT = 120
    DEFAULT_TIMEOUT = 600
    HEAVY_TIMEOUT = 1200

    @classmethod
    def get_timeout(cls, tool_name: str) -> int:
        heavy_tools = {"nuclei", "katana", "ffuf", "dalfox", "wpscan"}
        fast_tools = {"linkfinder", "secretfinder", "trufflehog"}
        
        if tool_name in heavy_tools:
            return cls.HEAVY_TIMEOUT
        if tool_name in fast_tools:
            return cls.FAST_TIMEOUT
        return cls.DEFAULT_TIMEOUT
