"""UI Colors utility for professional CLI feedback."""

import sys

class UIColors:
    """ANSI color codes for terminal output."""
    
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Wrap text in ANSI color codes if terminal supports it."""
        # Simple check for terminal support (can be enhanced)
        if not sys.stdout.isatty():
            return text
        return f"{color}{text}{UIColors.ENDC}"

    @classmethod
    def success(cls, text: str) -> str:
        return cls.colorize(text, cls.GREEN)

    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colorize(text, cls.YELLOW)

    @classmethod
    def error(cls, text: str) -> str:
        return cls.colorize(text, cls.RED)

    @classmethod
    def info(cls, text: str) -> str:
        return cls.colorize(text, cls.CYAN)

    @classmethod
    def bold(cls, text: str) -> str:
        return cls.colorize(text, cls.BOLD)

    @classmethod
    def get_score_color(cls, score: float) -> str:
        """Return appropriate color based on score value."""
        if score >= 80:
            return cls.GREEN
        if score >= 50:
            return cls.YELLOW
        return cls.RED
