"""
DIKSHA+ High-End Ultra-Modern Colorful Console Logger.
Supports ANSI 24-bit TrueColor in Windows CMD & Windows Terminal.
"""

import sys
import os
import re
import logging
import ctypes
from datetime import datetime, timezone, timedelta

# Indian Standard Time (IST = GMT +5:30)
IST = timezone(timedelta(hours=5, minutes=30))


# Enable Native ANSI Escape Sequences in Windows CMD
if sys.platform == "win32":
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

class ColoredFormatter(logging.Formatter):
    """
    Custom Logging Formatter providing a modern, vibrant color scheme
    for CMD and Terminal logs with Indian Standard Time (IST) timestamps.
    """
    # ANSI Color Tokens
    C_RESET = "\033[0m"
    C_BOLD = "\033[1m"
    C_DIM = "\033[2m"

    C_TIME = "\033[38;5;141m"     # Soft Purple
    C_NAME = "\033[38;5;220m"     # Golden Yellow
    C_INFO = "\033[38;5;45m"      # Electric Cyan
    C_WARN = "\033[38;5;214m"     # Amber Gold
    C_ERR = "\033[38;5;196m"      # Bright Red
    C_TEXT = "\033[38;5;231m"     # Crisp White
    C_GREEN = "\033[38;5;82m"     # Neon Green
    C_CYAN = "\033[38;5;51m"      # Bright Cyan
    C_MAGENTA = "\033[38;5;207m"  # Hot Pink

    LEVEL_COLORS = {
        logging.INFO: C_INFO,
        logging.WARNING: C_WARN,
        logging.ERROR: C_ERR,
        logging.CRITICAL: C_ERR,
    }

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=IST)
        return dt.strftime("%H:%M:%S")

    def format(self, record):
        time_str = self.formatTime(record)

        level_color = self.LEVEL_COLORS.get(record.levelno, self.C_INFO)
        level_name = f"{level_color}{self.C_BOLD}{record.levelname:<5}{self.C_RESET}"
        name_str = f"{self.C_NAME}{self.C_BOLD}[{record.name}]{self.C_RESET}"
        timestamp = f"{self.C_TIME}[{time_str}]{self.C_RESET}"

        raw_msg = record.getMessage()

        # Apply rich contextual highlights to message body
        colored_msg = raw_msg
        if "-->" in colored_msg:
            colored_msg = colored_msg.replace("-->", f"{self.C_GREEN}-->{self.C_RESET}")
        
        if "▶ SUBSECTION" in colored_msg:
            colored_msg = colored_msg.replace("▶", f"{self.C_MAGENTA}▶{self.C_RESET}")
            colored_msg = colored_msg.replace("SUBSECTION", f"{self.C_CYAN}{self.C_BOLD}SUBSECTION{self.C_RESET}")
            colored_msg = re.sub(r'(\[\d+/\d+\])', f'{self.C_NAME}{self.C_BOLD}\\1{self.C_RESET}', colored_msg)
            colored_msg = re.sub(r'(\(Type:\s*\'[^\']+\'\))', f'{self.C_GREEN}\\1{self.C_RESET}', colored_msg)
        elif "▶" in colored_msg:
            colored_msg = colored_msg.replace("▶", f"{self.C_CYAN}▶{self.C_RESET}")

        if "==========================================================" in colored_msg:
            colored_msg = f"{self.C_MAGENTA}{self.C_BOLD}{colored_msg}{self.C_RESET}"
        elif "📚 MODULE" in colored_msg:
            colored_msg = f"{self.C_CYAN}{self.C_BOLD}{colored_msg}{self.C_RESET}"

        # Colorize percentages: 100% (Neon Green), 0% (Amber Red-Orange), 1-99% (Vibrant Electric Cyan)
        def colorize_pct(m):
            val = int(m.group(1))
            if val == 100:
                return f"{self.C_GREEN}{self.C_BOLD}100%{self.C_RESET}"
            elif val == 0:
                return f"\033[38;5;208m{self.C_BOLD}0%{self.C_RESET}"
            else:
                return f"\033[38;5;51m{self.C_BOLD}{val}%{self.C_RESET}"

        colored_msg = re.sub(r"\b(\d{1,3})%\b", colorize_pct, colored_msg)

        if "✓" in colored_msg:
            colored_msg = colored_msg.replace("✓", f"{self.C_GREEN}{self.C_BOLD}✓{self.C_RESET}")
        if "⏳" in colored_msg:
            colored_msg = colored_msg.replace("⏳", f"\033[38;5;220m{self.C_BOLD}⏳{self.C_RESET}")
        if "||" in colored_msg:
            colored_msg = colored_msg.replace("||", f"\033[38;5;242m||\033[0m")
        if "CONFIRMED" in colored_msg:
            colored_msg = colored_msg.replace("CONFIRMED", f"{self.C_GREEN}{self.C_BOLD}CONFIRMED{self.C_RESET}")

        return f"{timestamp} {level_name} {name_str} {self.C_TEXT}{colored_msg}{self.C_RESET}"





def get_logger(name="DIKSHA"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = ColoredFormatter(datefmt="%H:%M:%S")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
