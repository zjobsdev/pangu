# -*- coding: utf-8 -*-
# @Author: wqshen
# @Date: 2020/8/14 15:37
# @Last Modified by: wqshen


import time
from dataclasses import dataclass, field
from typing import Callable, ClassVar, Dict, Optional
from contextlib import ContextDecorator


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


@dataclass
class Timer(ContextDecorator):
    """
    A Timer class to calculate your python code lapse time in three ways

    1. the first way, as a class

        >>>t = Timer(name="class")
        >>>t.start()
        >>># Do something
        >>>t.stop()

    2. the second way, as a context manager

        >>>with Timer(name="context manager"):
        >>># Do something

    3. the third way, as a decorator

        >>>@Timer(name="decorator")
        >>>def stuff():
        >>>    # Do something

    Notes
    -----
    This class is totally fetched from https://realpython.com/python-timer/
    See the details on the website, it is a step-to-step toturial.
    """
    timers: ClassVar[Dict[str, float]] = dict()
    name: Optional[str] = None
    text: str = "{name}: elapsed time: {t:0.4f} seconds"
    logger: Optional[Callable[[str], None]] = print
    _start_time: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Add timer to dict of timers after initialization"""
        if self.name is not None:
            self.timers.setdefault(self.name, 0)

    def start(self) -> None:
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Report elapsed time
        if self.logger:
            self.logger(self.text.format(name=self.name, t=elapsed_time))
        if self.name:
            self.timers[self.name] += elapsed_time

        return elapsed_time

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()
