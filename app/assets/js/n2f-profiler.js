/**
 * Next2Flash Client-Side Performance Profiler
 * =============================================
 * Instruments browser-side operations: loading, rendering, import/export.
 *
 * Usage:
 *   N2FProfiler.startSession("swf-import");
 *   N2FProfiler.startTimer("parse");
 *   ... work ...
 *   N2FProfiler.stopTimer("parse");
 *   N2FProfiler.endSession();   // logs report + sends to /api/profile
 *
 * Auto-instrumented operations (call N2FProfiler.install() once):
 *   - addLibrary calls (count + total time)
 *   - Progressive loading chunks
 *   - Export (onExportSWF)
 *   - Scene changes
 *   - Fetch requests to server API
 */
(function() {
    "use strict";

    const _sessions = {};
    let _current = null;

    class TimerEntry {
        constructor(name) {
            this.name = name;
            this.start = performance.now();
            this.end = 0;
            this.elapsed = 0;
            this.children = [];
            this.count = 1;
            this.extra = {};
        }
        finish() {
            this.end = performance.now();
            this.elapsed = this.end - this.start;
        }
        toJSON() {
            const d = {
                name: this.name,
                elapsed_ms: Math.round(this.elapsed * 100) / 100,
                count: this.count,
            };
            if (Object.keys(this.extra).length) {
                Object.assign(d, this.extra);
            }
            if (this.children.length) {
                d.children = this.children.map(c => c.toJSON());
            }
            return d;
        }
    }

    class Session {
        constructor(name) {
            this.name = name;
            this.startTime = performance.now();
            this.endTime = 0;
            this.timers = [];
            this.activeStack = [];
            this.counters = {};
            this.sizes = {};
            this.notes = [];
        }
        pushTimer(name) {
            const parent = this.activeStack.length
                ? this.activeStack[this.activeStack.length - 1]
                : null;
            const entry = new TimerEntry(name);
            if (parent) {
                parent.children.push(entry);
            } else {
                this.timers.push(entry);
            }
            this.activeStack.push(entry);
            return entry;
        }
        popTimer() {
            if (!this.activeStack.length) return null;
            const entry = this.activeStack.pop();
            entry.finish();
            return entry;
        }
    }

    // =================================================================
    //  PUBLIC API
    // =================================================================

    const N2FProfiler = {
        enabled: true,

        startSession(name) {
            if (!this.enabled) return;
            const s = new Session(name);
            _sessions[name] = s;
            _current = s;
            console.log(`%c[N2F-PROFILE] Session started: ${name}`, "color:#4fc3f7;font-weight:bold");
            return s;
        },

        endSession(name) {
            const s = name ? _sessions[name] : _current;
            if (!s) return {};
            s.endTime = performance.now();

            // Close unclosed timers
            while (s.activeStack.length) s.popTimer();

            const report = this._buildReport(s);
            this._printReport(report);
            this._sendToServer(report);

            if (_current === s) _current = null;
            return report;
        },

        startTimer(name) {
            const s = _current;
            if (!this.enabled || !s) return null;
            return s.pushTimer(name);
        },

        stopTimer() {
            const s = _current;
            if (!this.enabled || !s) return;
            s.popTimer();
        },

        count(name, n) {
            const s = _current;
            if (!this.enabled || !s) return;
            s.counters[name] = (s.counters[name] || 0) + (n === undefined ? 1 : n);
        },

        size(name, bytes) {
            const s = _current;
            if (!this.enabled || !s) return;
            s.sizes[name] = bytes;
        },

        note(msg) {
            const s = _current;
            if (!this.enabled || !s) return;
            s.notes.push(msg);
        },

        /** Time an async function. Returns its result. */
        async timeAsync(name, fn) {
            this.startTimer(name);
            try {
                return await fn();
            } finally {
                this.stopTimer();
            }
        },

        /** Time a sync function. Returns its result. */
        timeSync(name, fn) {
            this.startTimer(name);
            try {
                return fn();
            } finally {
                this.stopTimer();
            }
        },

        // =============================================================
        //  AUTO-INSTRUMENTATION
        // =============================================================

        /** Install hooks on key operations. Call once after page load. */
        install() {
            this._instrumentFetch();
            this._instrumentAddLibrary();
            console.log("%c[N2F-PROFILE] Instrumentation installed", "color:#4fc3f7");
        },

        _instrumentFetch() {
            const origFetch = window.fetch;
            const self = this;
            window.fetch = function(url, opts) {
                const urlStr = typeof url === "string" ? url : url.url || "";
                const isApi = urlStr.includes("/api/");
                if (!isApi || !self.enabled) {
                    return origFetch.apply(this, arguments);
                }
                const method = (opts && opts.method) || "GET";
                const label = `fetch:${method} ${urlStr.split("/api/")[1] || urlStr}`;
                const t0 = performance.now();
                return origFetch.apply(this, arguments).then(resp => {
                    const elapsed = performance.now() - t0;
                    const sizeHeader = resp.headers.get("content-length");
                    const size = sizeHeader ? parseInt(sizeHeader, 10) : 0;
                    console.log(
                        `%c[N2F-PROFILE] ${label}: ${elapsed.toFixed(0)}ms` +
                        (size ? ` (${(size/1024).toFixed(1)} KB)` : ""),
                        "color:#81c784"
                    );
                    // Always emit to profiler window
                    _emitToProfiler({ type: 'fetch', label, ms: elapsed, size });
                    // Record in active session
                    if (_current) {
                        const entry = new TimerEntry(label);
                        entry.elapsed = elapsed;
                        if (size) entry.extra.response_bytes = size;
                        entry.extra.status = resp.status;
                        _current.timers.push(entry);
                    }
                    return resp;
                }).catch(err => {
                    const elapsed = performance.now() - t0;
                    _emitToProfiler({ type: 'error', label: `${label} FAILED`, ms: elapsed });
                    console.warn(`[N2F-PROFILE] ${label}: FAILED after ${elapsed.toFixed(0)}ms`, err);
                    throw err;
                });
            };
        },

        _instrumentAddLibrary() {
            // Defer until WorkSpace class is available
            const check = () => {
                try {
                    const ws = window.Util && window.Util.$workSpaces && window.Util.$workSpaces[0];
                    if (ws && ws.addLibrary && !ws._n2fProfiled) {
                        const orig = ws.addLibrary.bind(ws);
                        let totalTime = 0;
                        let totalCount = 0;
                        ws.addLibrary = function(data) {
                            const t0 = performance.now();
                            const result = orig(data);
                            totalTime += performance.now() - t0;
                            totalCount++;
                            if (totalCount % 200 === 0) {
                                console.log(
                                    `%c[N2F-PROFILE] addLibrary: ${totalCount} items, ` +
                                    `avg ${(totalTime / totalCount).toFixed(2)}ms each, ` +
                                    `total ${totalTime.toFixed(0)}ms`,
                                    "color:#ffb74d"
                                );
                            }
                            return result;
                        };
                        ws._n2fProfiled = true;
                    }
                } catch (e) { /* not ready yet */ }
            };
            // Try immediately and also after a delay
            check();
            setTimeout(check, 2000);
            setTimeout(check, 5000);
        },

        // =============================================================
        //  REPORTING
        // =============================================================

        _buildReport(session) {
            const total = session.endTime - session.startTime;
            const report = {
                session: session.name,
                total_ms: Math.round(total * 100) / 100,
                total_s: Math.round(total / 10) / 100,
                timers: session.timers.map(t => t.toJSON()),
                counters: session.counters,
                sizes: {},
                notes: session.notes,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent.substring(0, 80),
            };
            for (const [k, v] of Object.entries(session.sizes)) {
                if (v >= 1024 * 1024) {
                    report.sizes[k] = `${(v / (1024*1024)).toFixed(2)} MB`;
                } else if (v >= 1024) {
                    report.sizes[k] = `${(v / 1024).toFixed(1)} KB`;
                } else {
                    report.sizes[k] = `${v} B`;
                }
                report.sizes[k + "_bytes"] = v;
            }
            return report;
        },

        _printReport(report) {
            const sep = "=".repeat(55);
            const lines = [
                `\n${sep}`,
                `  PROFILE: ${report.session}`,
                `  Total: ${report.total_ms.toFixed(0)} ms (${report.total_s}s)`,
                sep,
            ];

            if (Object.keys(report.sizes).length) {
                lines.push("\n  Sizes:");
                for (const [k, v] of Object.entries(report.sizes)) {
                    if (!k.endsWith("_bytes")) lines.push(`    ${k}: ${v}`);
                }
            }
            if (Object.keys(report.counters).length) {
                lines.push("\n  Counts:");
                for (const [k, v] of Object.entries(report.counters).sort()) {
                    lines.push(`    ${k}: ${v.toLocaleString()}`);
                }
            }
            if (report.timers.length) {
                lines.push("\n  Timings:");
                this._formatTimers(report.timers, lines, 4);
            }
            if (report.notes.length) {
                lines.push("\n  Notes:");
                report.notes.forEach(n => lines.push(`    - ${n}`));
            }
            lines.push(sep + "\n");

            console.log(
                `%c${lines.join("\n")}`,
                "color:#4fc3f7;font-family:monospace"
            );
        },

        _formatTimers(timers, lines, indent) {
            const prefix = " ".repeat(indent);
            for (const t of timers) {
                const ms = t.elapsed_ms;
                let indicator;
                if (ms > 5000) indicator = "[!!!]";
                else if (ms > 1000) indicator = "[!! ]";
                else if (ms > 100) indicator = "[!  ]";
                else indicator = "[   ]";

                let extra = "";
                if (t.count > 1) extra += ` (x${t.count})`;
                if (t.response_bytes) extra += ` ${(t.response_bytes/1024).toFixed(1)}KB`;

                const time = ms >= 1000 ? `${(ms/1000).toFixed(2)}s` : `${ms.toFixed(1)}ms`;
                lines.push(`${prefix}${indicator} ${t.name}: ${time}${extra}`);

                if (t.children) {
                    this._formatTimers(t.children, lines, indent + 4);
                }
            }
        },

        _sendToServer(report) {
            try {
                fetch("/api/profile", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(report),
                }).catch(() => {}); // silent fail
            } catch (e) { /* ignore */ }
        },

        /** Get all stored session reports */
        getReports() {
            return Object.keys(_sessions).map(k => {
                const s = _sessions[k];
                return s.endTime ? this._buildReport(s) : { session: k, status: "in-progress" };
            });
        },
    };

    // Expose globally
    window.N2FProfiler = N2FProfiler;

    // ── Electron profiler bridge ──
    // Forward events to the profiler window via IPC (always-on)
    function _emitToProfiler(event) {
        try {
            if (window.n2fElectron && window.n2fElectron.sendProfilerEvent) {
                window.n2fElectron.sendProfilerEvent(event);
            }
        } catch (e) { /* not in Electron */ }
    }

    // Make _emitToProfiler available to fetch instrumentation
    // (it's called before patches below, from _instrumentFetch)

    // Patch key methods to emit events
    const _origStartSession = N2FProfiler.startSession.bind(N2FProfiler);
    N2FProfiler.startSession = function(name) {
        _emitToProfiler({ type: 'session', label: `Session started: ${name}` });
        return _origStartSession(name);
    };

    const _origEndSession = N2FProfiler.endSession.bind(N2FProfiler);
    N2FProfiler.endSession = function(name) {
        const report = _origEndSession(name);
        _emitToProfiler({ type: 'session', label: `Session ended: ${report.session}`, ms: report.total_ms });
        return report;
    };

    const _origStopTimer = N2FProfiler.stopTimer.bind(N2FProfiler);
    N2FProfiler.stopTimer = function() {
        const s = _current;
        if (s && s.activeStack.length) {
            const entry = s.activeStack[s.activeStack.length - 1];
            const name = entry.name;
            _origStopTimer();
            const elapsed = entry.elapsed;
            const type = name.startsWith('fetch:') ? 'fetch' : 'timer';
            _emitToProfiler({ type, label: name, ms: elapsed });
        } else {
            _origStopTimer();
        }
    };

    const _origNote = N2FProfiler.note.bind(N2FProfiler);
    N2FProfiler.note = function(msg) {
        _emitToProfiler({ type: 'metric', label: msg });
        return _origNote(msg);
    };

    const _origCount = N2FProfiler.count.bind(N2FProfiler);
    N2FProfiler.count = function(name, n) {
        _emitToProfiler({ type: 'metric', label: `${name}: ${n === undefined ? 1 : n}` });
        return _origCount(name, n);
    };

    // ── Always-on monitoring (no session required) ──

    // 1. Periodic performance heartbeat — gives the "constant graph"
    let _heartbeatId = null;
    function _startHeartbeat() {
        const INTERVAL = 1000; // 1s
        let lastFrames = 0;
        let frameCount = 0;
        let rafId = null;

        // Count frames via rAF
        function countFrame() {
            frameCount++;
            rafId = requestAnimationFrame(countFrame);
        }
        rafId = requestAnimationFrame(countFrame);

        _heartbeatId = setInterval(() => {
            const fps = frameCount - lastFrames;
            lastFrames = frameCount;

            // JS heap (Chromium only)
            let heapMB = 0;
            if (performance.memory) {
                heapMB = Math.round(performance.memory.usedJSHeapSize / (1024 * 1024));
            }

            // DOM node count
            const domNodes = document.querySelectorAll('*').length;

            _emitToProfiler({
                type: 'heartbeat',
                fps,
                heapMB,
                domNodes,
                ms: fps > 0 ? Math.round(1000 / fps) : 0, // avg frame time for the graph
            });
        }, INTERVAL);
    }

    // 2. Track all click events to see what the user does
    function _instrumentClicks() {
        document.addEventListener('click', (e) => {
            const el = e.target;
            const tag = el.tagName.toLowerCase();
            const id = el.id ? `#${el.id}` : '';
            const cls = el.className && typeof el.className === 'string'
                ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.')
                : '';
            const text = (el.textContent || '').trim().substring(0, 30);
            const label = `click: ${tag}${id}${cls}` + (text ? ` "${text}"` : '');
            _emitToProfiler({ type: 'timer', label, ms: 0 });
        }, true);
    }

    // 3. Track long tasks (>50ms) via PerformanceObserver
    function _instrumentLongTasks() {
        if (typeof PerformanceObserver === 'undefined') return;
        try {
            const obs = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    _emitToProfiler({
                        type: 'warn',
                        label: `Long task (${entry.name || 'script'})`,
                        ms: entry.duration,
                    });
                }
            });
            obs.observe({ type: 'longtask', buffered: true });
        } catch (e) { /* longtask not supported */ }
    }

    // 4. Track resource loads (scripts, images, xhr)
    function _instrumentResources() {
        if (typeof PerformanceObserver === 'undefined') return;
        try {
            const obs = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    // Only emit notable ones (>100ms or api calls)
                    if (entry.duration > 100 || entry.name.includes('/api/')) {
                        const url = entry.name.split('/').slice(-2).join('/');
                        _emitToProfiler({
                            type: 'fetch',
                            label: `resource: ${entry.initiatorType} ${url}`,
                            ms: entry.duration,
                        });
                    }
                }
            });
            obs.observe({ type: 'resource', buffered: false });
        } catch (e) { /* resource observer not supported */ }
    }

    // 5. Emit startup event with page load timing
    function _emitStartup() {
        const nav = performance.getEntriesByType('navigation')[0];
        if (nav) {
            _emitToProfiler({ type: 'session', label: 'Page load: DOM interactive', ms: nav.domInteractive });
            _emitToProfiler({ type: 'session', label: 'Page load: DOM complete', ms: nav.domComplete });
            _emitToProfiler({ type: 'session', label: 'Page load: Load event', ms: nav.loadEventEnd || nav.loadEventStart });
        }
        _emitToProfiler({ type: 'metric', label: `DOM nodes at startup: ${document.querySelectorAll('*').length}` });
        if (performance.memory) {
            _emitToProfiler({ type: 'metric', label: `Heap at startup: ${Math.round(performance.memory.usedJSHeapSize / (1024*1024))}MB` });
        }
    }

    // ── Boot everything ──
    function _bootProfiler() {
        N2FProfiler.install();
        _instrumentClicks();
        _instrumentLongTasks();
        _instrumentResources();
        _startHeartbeat();
        // Emit startup metrics after load event so navigation timing is fully populated
        if (document.readyState === 'complete') {
            setTimeout(_emitStartup, 50);
        } else {
            window.addEventListener('load', function() { setTimeout(_emitStartup, 50); });
        }
        _emitToProfiler({ type: 'session', label: 'Profiler initialized' });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", _bootProfiler);
    } else {
        _bootProfiler();
    }

})();
