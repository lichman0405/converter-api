# The module is to provide logger
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track as rich_track
from rich.theme import Theme
from rich.traceback import Traceback

SUCCESS_LEVEL_NUM = 25

if logging.getLevelName(SUCCESS_LEVEL_NUM) == f"Level {SUCCESS_LEVEL_NUM}":
    logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success_log(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

if not hasattr(logging.Logger, 'success'):
    setattr(logging.Logger, 'success', success_log)


class ConsoleManager:
    """
    ConsoleManger is a singleton class that manages a Rich Console instance
    and provides a unified interface for logging and console output.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConsoleManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # initialize only once
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        custom_theme = Theme({
            "logging.level.success": "bold green"
        })
        self._console = Console(theme=custom_theme)
        self._logger = self._setup_logger()
        self._initialized = True

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("file-converter-api")
        
        # Always ensure the 'success' method is attached
        if not hasattr(logger, 'success'):
            setattr(logger, 'success', success_log.__get__(logger, logging.Logger))

        if logger.hasHandlers():
            return logger

        logger.setLevel(logging.INFO)
        handler = RichHandler(
            console=self._console,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            keywords=["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG", "CRITICAL"],
            show_path=False 
        )
        handler.setFormatter(logging.Formatter(fmt="%(message)s", datefmt="[%X]"))
        logger.addHandler(handler)
        return logger

    def info(self, message: str):
        self._logger.info(message)

    def success(self, message: str):
        success_method = getattr(self._logger, 'success', None)
        if callable(success_method):
            success_method(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def exception(self, message: str):
        self._logger.exception(message)

    def rule(self, title: str, style: str = "cyan"):
        self._console.rule(f"[bold {style}]{title}[/bold {style}]", style=style)

    def display_data_as_table(self, data: dict, title: str):
        table = Table(show_header=True, header_style="bold magenta", box=None, show_edge=False)
        table.add_column("Parameter", style="cyan", no_wrap=True, width=25)
        table.add_column("Value", style="white")

        for key, value in data.items():
            table.add_row(key, str(value))
        
        panel = Panel(table, title=f"[bold green]✓ {title}[/bold green]", border_style="green", expand=False)
        self._console.print(panel)

    def display_error_panel(self, title: str, error_message: str):
        panel = Panel(error_message, title=f"[bold red]✗ {title}[/bold red]", border_style="red", expand=False)
        self._console.print(panel)

    def display_traceback(self):
        self._console.print(Traceback(show_locals=True))

    def track(self, *args, **kwargs):
        return rich_track(*args, console=self._console, **kwargs)


logger = ConsoleManager()