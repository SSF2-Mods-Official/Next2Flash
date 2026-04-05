"""
Next2Flash Performance Profiler
================================
Instruments all major operations and logs timing, memory, and throughput data.

Usage:
    from profiler import Profiler

    # Start a profiling session
    Profiler.start_session("swf-import")

    with Profiler.timer("parse_swf"):
        result = parse_swf(data)

    Profiler.count("shapes", 150)
    Profiler.size("input_swf", len(data))

    report = Profiler.end_session()
    print(report)

    # Or use the decorator
    @Profiler.profile
    def my_function():
        ...
"""

import time
import threading
import functools
import json
import os
import tracemalloc
from contextlib import contextmanager
from collections import defaultdict

_lock = threading.Lock()


class _TimerEntry:
    __slots__ = ('name', 'start', 'end', 'elapsed', 'children', 'parent',
                 'mem_start', 'mem_end', 'count', 'extra')

    def __init__(self, name, parent=None):
        self.name = name
        self.start = time.perf_counter()
        self.end = 0.0
        self.elapsed = 0.0
        self.children = []
        self.parent = parent
        self.mem_start = 0
        self.mem_end = 0
        self.count = 1
        self.extra = {}

    def finish(self):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start

    def to_dict(self):
        d = {
            'name': self.name,
            'elapsed_ms': round(self.elapsed * 1000, 2),
            'count': self.count,
        }
        if self.mem_end > self.mem_start:
            d['mem_delta_kb'] = round((self.mem_end - self.mem_start) / 1024, 1)
        if self.extra:
            d.update(self.extra)
        if self.children:
            d['children'] = [c.to_dict() for c in self.children]
        return d


class _Session:
    def __init__(self, name):
        self.name = name
        self.start_time = time.perf_counter()
        self.end_time = 0.0
        self.timers = []            # top-level timers
        self.active_stack = []      # current nesting
        self.counters = defaultdict(int)
        self.sizes = {}
        self.notes = []
        self.track_memory = False

    def push_timer(self, name):
        parent = self.active_stack[-1] if self.active_stack else None
        entry = _TimerEntry(name, parent)
        if self.track_memory:
            entry.mem_start = tracemalloc.get_traced_memory()[0]
        if parent:
            parent.children.append(entry)
        else:
            self.timers.append(entry)
        self.active_stack.append(entry)
        return entry

    def pop_timer(self):
        if not self.active_stack:
            return None
        entry = self.active_stack.pop()
        entry.finish()
        if self.track_memory:
            entry.mem_end = tracemalloc.get_traced_memory()[0]
        return entry


class Profiler:
    """Global performance profiler for Next2Flash."""

    _sessions = {}          # name -> _Session
    _current = None         # active session (thread-local would be better but this is simpler)
    _log_dir = None
    _enabled = True

    @classmethod
    def enable(cls):
        cls._enabled = True

    @classmethod
    def disable(cls):
        cls._enabled = False

    @classmethod
    def start_session(cls, name, track_memory=False):
        """Begin a new profiling session."""
        if not cls._enabled:
            return
        with _lock:
            session = _Session(name)
            session.track_memory = track_memory
            if track_memory:
                try:
                    tracemalloc.start()
                except RuntimeError:
                    pass
            cls._sessions[name] = session
            cls._current = session
        return session

    @classmethod
    def end_session(cls, name=None):
        """End a session and return its report dict."""
        with _lock:
            session = cls._sessions.get(name) if name else cls._current
            if not session:
                return {}
            session.end_time = time.perf_counter()

            # Close any unclosed timers
            while session.active_stack:
                session.pop_timer()

            report = cls._build_report(session)

            if session.track_memory:
                try:
                    tracemalloc.stop()
                except RuntimeError:
                    pass

            # Auto-save
            cls._auto_save(report)

            if cls._current is session:
                cls._current = None
            return report

    @classmethod
    @contextmanager
    def timer(cls, name, session=None):
        """Context manager to time a block."""
        s = session or cls._current
        if not cls._enabled or not s:
            yield
            return
        with _lock:
            entry = s.push_timer(name)
        try:
            yield entry
        finally:
            with _lock:
                s.pop_timer()

    @classmethod
    def start_timer(cls, name, session=None):
        """Start a named timer (non-context-manager). Returns entry."""
        s = session or cls._current
        if not cls._enabled or not s:
            return None
        with _lock:
            return s.push_timer(name)

    @classmethod
    def stop_timer(cls, session=None):
        """Stop the most recent timer."""
        s = session or cls._current
        if not cls._enabled or not s:
            return
        with _lock:
            s.pop_timer()

    @classmethod
    def count(cls, name, n=1, session=None):
        """Increment a counter."""
        s = session or cls._current
        if not cls._enabled or not s:
            return
        s.counters[name] += n

    @classmethod
    def size(cls, name, nbytes, session=None):
        """Record a size measurement (bytes)."""
        s = session or cls._current
        if not cls._enabled or not s:
            return
        s.sizes[name] = nbytes

    @classmethod
    def note(cls, msg, session=None):
        """Add a freeform note."""
        s = session or cls._current
        if not cls._enabled or not s:
            return
        s.notes.append(msg)

    @classmethod
    def profile(cls, func=None, *, name=None):
        """Decorator to profile a function call."""
        def decorator(fn):
            label = name or f"{fn.__module__}.{fn.__qualname__}"
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                if not cls._enabled or not cls._current:
                    return fn(*args, **kwargs)
                with cls.timer(label):
                    return fn(*args, **kwargs)
            return wrapper
        if func is not None:
            return decorator(func)
        return decorator

    @classmethod
    def _build_report(cls, session):
        total = session.end_time - session.start_time
        report = {
            'session': session.name,
            'total_ms': round(total * 1000, 2),
            'total_s': round(total, 3),
            'timers': [t.to_dict() for t in session.timers],
            'counters': dict(session.counters),
            'sizes': {},
            'notes': session.notes,
        }
        # Human-readable sizes
        for k, v in session.sizes.items():
            if v >= 1024 * 1024:
                report['sizes'][k] = f"{v / (1024*1024):.2f} MB"
            elif v >= 1024:
                report['sizes'][k] = f"{v / 1024:.1f} KB"
            else:
                report['sizes'][k] = f"{v} B"
            report['sizes'][f"{k}_bytes"] = v

        return report

    @classmethod
    def _auto_save(cls, report):
        """Save report to app/converted/_profiles/."""
        try:
            base = os.path.join(os.path.dirname(__file__), 'converted', '_profiles')
            os.makedirs(base, exist_ok=True)
            ts = time.strftime('%Y%m%d_%H%M%S')
            name = report.get('session', 'unknown').replace(' ', '_')
            path = os.path.join(base, f"{name}_{ts}.json")
            with open(path, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception:
            pass  # Never crash on profiling failure

    @classmethod
    def format_report(cls, report):
        """Pretty-print a report to a string."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"  PROFILE: {report['session']}")
        lines.append(f"  Total: {report['total_ms']:.0f} ms ({report['total_s']:.2f}s)")
        lines.append(f"{'='*60}")

        # Sizes
        if report.get('sizes'):
            lines.append("\n  Sizes:")
            for k, v in report['sizes'].items():
                if not k.endswith('_bytes'):
                    lines.append(f"    {k}: {v}")

        # Counters
        if report.get('counters'):
            lines.append("\n  Counts:")
            for k, v in sorted(report['counters'].items()):
                lines.append(f"    {k}: {v:,}")

        # Timer tree
        if report.get('timers'):
            lines.append("\n  Timings:")
            cls._format_timers(report['timers'], lines, indent=4)

        # Notes
        if report.get('notes'):
            lines.append("\n  Notes:")
            for n in report['notes']:
                lines.append(f"    - {n}")

        lines.append(f"{'='*60}\n")
        return '\n'.join(lines)

    @classmethod
    def _format_timers(cls, timers, lines, indent=4):
        prefix = ' ' * indent
        for t in timers:
            elapsed = t['elapsed_ms']
            count = t.get('count', 1)

            # Determine color indicator
            if elapsed > 5000:
                indicator = '[!!!]'
            elif elapsed > 1000:
                indicator = '[!! ]'
            elif elapsed > 100:
                indicator = '[!  ]'
            else:
                indicator = '[   ]'

            extra = ''
            if count > 1:
                extra = f" (x{count})"
            mem = t.get('mem_delta_kb')
            if mem and mem > 0:
                extra += f" +{mem:.0f}KB"

            if elapsed >= 1000:
                lines.append(f"{prefix}{indicator} {t['name']}: {elapsed/1000:.2f}s{extra}")
            else:
                lines.append(f"{prefix}{indicator} {t['name']}: {elapsed:.1f}ms{extra}")

            if t.get('children'):
                cls._format_timers(t['children'], lines, indent + 4)
