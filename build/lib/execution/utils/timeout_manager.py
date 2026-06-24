class TimeoutManager:
    DEFAULT_TIMEOUT = 300
    HEAVY_TIMEOUT = 600

    @classmethod
    def get_timeout(cls, tool_name: str) -> int:
        heavy_tools = {"nuclei", "katana", "ffuf"}
        if tool_name in heavy_tools:
            return cls.HEAVY_TIMEOUT
        return cls.DEFAULT_TIMEOUT
