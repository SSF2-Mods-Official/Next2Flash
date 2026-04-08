# Playback Gameplan — Crisp Desktop Animation

## Current Architecture (the problem)

```
TimelinePlayer.run()          ← rAF loop, fires every ~33ms (30fps)
  └─ reloadScreen()
       └─ scene.changeFrame(frame)
            └─ Promise.all(layerPromises)     ← ONE hang = ALL blocked
                 └─ layer.appendCharacter()
                      └─ Screen.appendCharacter()
                           └─ character.draw()
                                └─ instance.draw()
                                     └─ new Promise(resolve => {
                                          bitmapData.draw(container, ..., canvas, resolve)
                                        })
                                        ↑ player never calls resolve → Promise hangs forever
```

**Root cause**: The player's `BitmapData.draw()` has early-return paths that silently skip the `resolve` callback:
- `if(!width||!height) return;` — zero-dimension BitmapData
- `if(!context) return;` — canvas 2D context is null (Chrome hard limit ~300 live contexts)

Since the rendering worker is **explicitly disabled** (`Mr=null` hardcoded in `next2d.js`), all drawing is **synchronous on the main thread**. The resolve callback either fires during the `bitmapData.draw()` call or **never**.

`Promise.all()` in `changeFrame()` means one hanging promise blocks the entire frame. The `_$rendering` flag stays true, the 5s force-reset fires, animation crawls at ~1 frame per 5 seconds.

---

## Fix Strategy (ordered by impact)

### Fix 1 — Synchronous Resolve Safety Net ⚡ CRITICAL

**File**: `Instance.js` → `draw()`  
**Effort**: Small  
**Impact**: Eliminates ALL hanging promises instantly

Since `Mr=null` (worker disabled), `bitmapData.draw()` is fully synchronous. If resolve wasn't called during execution, it never will be. We detect this at zero cost:

```javascript
return new Promise((resolve) => {
    const { Matrix } = window.next2d.geom;
    let called = false;
    const safeResolve = (result) => {
        called = true;
        resolve(result);
    };
    try {
        bitmapData.draw(
            container,
            new Matrix(sacle, 0, 0, sacle, tx, ty),
            null, canvas, safeResolve
        );
    } catch (e) { /* swallow — resolve below */ }
    if (!called) {
        resolve(canvas); // blank canvas rather than hang forever
    }
});
```

**Why this works**: No timeout, no polling, no overhead. The check is a single boolean test after a synchronous call. Frames that previously hung forever now complete in microseconds.

---

### Fix 2 — Canvas Context Pool (reduces failed draws) ⚡ HIGH

**File**: `Character.js` → `draw()`, `Instance.js`  
**Effort**: Medium  
**Impact**: Prevents the `getContext("2d") → null` path that causes blank frames

Chrome limits live 2D canvas contexts to ~300. With 1531 library items and ~50+ characters per frame, the limit is hit quickly. Currently each `Instance.draw()` creates a fresh `BitmapData(w, h)` which internally uses a canvas context, and old ones aren't released until GC runs.

**Fix**: After `bitmapData.draw()` finishes, explicitly dispose the BitmapData to release the internal canvas/context. The result is already copied onto the output `canvas` — the BitmapData is not needed after draw.

```javascript
// After bitmapData.draw completes:
try { bitmapData.dispose(); } catch(e) {}
```

---

### Fix 3 — Frame Cache (avoid re-rendering) 🟡 MEDIUM

**File**: `Character.js` → `draw()`  
**Effort**: Small  
**Impact**: Eliminates redundant draws on 2nd+ playthrough

Already partially implemented: `if (this._$canvas) return Promise.resolve(this._$canvas)` — cached frames skip rendering entirely. But `character.dispose()` is called when `doUpdate` is false in some paths, wiping the cache unnecessarily.

**Fix**: During playback (`!Util.$timelinePlayer.stopFlag`), skip `character.dispose()` unless the character's place data actually changed. This makes frame 2+ of playback nearly free.

---

### Fix 4 — Chunked First-Play Warm-up 🟡 MEDIUM

**File**: `TimelinePlayer.js`  
**Effort**: Medium  
**Impact**: Eliminates the 3-10 second stall on first play

Profiler shows 10+ back-to-back long tasks of ~1000ms each when play is first pressed (every uncached character must render via WebGL). This starves the event loop.

**Options for desktop Electron**:

#### Option A — `requestIdleCallback` Pre-warming
After hydration completes, pre-render characters in small batches during idle time:
```javascript
function prewarmCharacters(characters, batchSize = 5) {
    let i = 0;
    function tick(deadline) {
        while (i < characters.length && deadline.timeRemaining() > 5) {
            characters[i].draw(Util.$getCanvas(), 1);
            i++;
        }
        if (i < characters.length) {
            requestIdleCallback(tick);
        }
    }
    requestIdleCallback(tick);
}
```

#### Option B — Worker Thread Pre-rendering (Electron-specific)
Use Electron's `worker_threads` or a hidden `BrowserWindow` to pre-render frames off the main thread. The main window stays responsive.

#### Option C — Delayed Frame Start
Don't start rAF playback until the first frame is fully rendered. Show a brief "preparing…" state. This avoids the jarring lag but doesn't reduce total time.

---

### Fix 5 — Electron-Specific GPU & Process Tuning 🟡 MEDIUM

**File**: `electron/main.js`  
**Effort**: Small  
**Impact**: Better GPU utilization, higher frame budget

Electron 33 (Chromium 130) has desktop-only options:

```javascript
// In main.js, BEFORE app.ready:
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');           // GPU texture sharing
app.commandLine.appendSwitch('enable-native-gpu-memory-buffers');
app.commandLine.appendSwitch('canvas-oop-rasterization');   // offload canvas to GPU process
app.commandLine.appendSwitch('disable-renderer-backgrounding'); // no throttling when window loses focus
app.commandLine.appendSwitch('disable-background-timer-throttling');
app.commandLine.appendSwitch('js-flags', '--max-old-space-size=4096'); // 4GB heap
```

Also in BrowserWindow:
```javascript
webPreferences: {
    backgroundThrottling: false,  // keep rAF firing when unfocused
}
```

These are free performance — no code changes to the rendering pipeline.

---

### Fix 6 — Break Promise.all Bottleneck 🟢 NICE-TO-HAVE

**File**: `MovieClip.js` → `changeFrame()`  
**Effort**: Medium  
**Impact**: Partial frame display instead of all-or-nothing

Currently `Promise.all(promises)` waits for EVERY layer/character before displaying anything. With Fix 1, hanging promises are eliminated, but rendering is still serial-feeling because nothing appears until all characters finish.

**Option A — Progressive Rendering**: Append each character's canvas to the DOM as it resolves, rather than waiting for all. The frame "fills in" over a few ms instead of popping in all at once.

**Option B — Promise.allSettled**: Replace `Promise.all` with `Promise.allSettled` so failed/slow characters don't block the rest.

---

## Desktop-Only Options Beyond WebGL

Since this is an Electron app, we're not limited to what a browser can do:

### 1. OffscreenCanvas + Web Workers (Best bang-for-buck)
The player already HAS a WebGL worker rendering path — it's just force-disabled (`Mr=null`). Re-enabling it would move all heavy `bitmapData.draw()` calls off the main thread. The worker uses OffscreenCanvas + WebGL2, posts back ImageBitmaps.

**Blocker**: `Mr=null` is hardcoded in the minified `next2d.js`. Options:
- Patch the minified file (fragile)
- Request an upstream config option
- Intercept and override `kr()` before it runs

### 2. Electron `nativeImage` / Sharp
Use Node.js-side image processing (Sharp, node-canvas) for CPU-bound bitmap operations. Render complex characters in the Node process, send the pixels back via IPC as `nativeImage` buffers.

**Pros**: Offloads work completely off the renderer process  
**Cons**: Significant architecture change, IPC overhead for large bitmaps

### 3. WebGPU (Electron 33+ = Chromium 130)
WebGPU is GA in Chromium 130. Could replace the WebGL2 rendering for the heavy `_$draw()` calls. Compute shaders could batch-process multiple characters simultaneously.

**Pros**: Modern, massively parallel, better memory management  
**Cons**: `next2d.js` player is WebGL2-native — would need player rewrite or custom rendering layer

### 4. Skia via `@aspect-build/aspect-engine` or `skia-canvas`
Node-native Skia bindings for hardware-accelerated 2D rendering. Could pre-render all frames to bitmap sheets on the Node side during import.

**Pros**: Desktop GPU-accelerated, no canvas context limits  
**Cons**: Additional native dependency, architecture change

### 5. Frame-Ahead Buffer (Video-style Pipeline)
Pre-render N frames ahead into an ImageBitmap ring buffer. Playback just blits pre-rendered frames — zero per-frame rendering cost.

```
[Render Thread]  → frame N+5 → frame N+6 → frame N+7
[Display Thread] → frame N   → frame N+1 → frame N+2  (just blits)
```

**Pros**: Perfectly smooth playback regardless of render time  
**Cons**: Memory cost (~5-10 frames × stage size), initial buffering delay

### 6. `VideoFrame` + `VideoEncoder` (Chromium 94+)
Electron supports the WebCodecs API. Could encode rendered frames into a video stream and play it back via `<video>`:

```javascript
const encoder = new VideoEncoder({ ... });
for (let f = 1; f <= 180; f++) {
    const frame = new VideoFrame(renderedCanvas, { timestamp: f * 33333 });
    encoder.encode(frame);
}
```

**Pros**: Hardware-decoded playback is buttery smooth  
**Cons**: Precompute time, not suitable for interactive editing playback

### 7. Hidden BrowserWindow Renderer Farm
Spawn 2-4 hidden `BrowserWindow` instances, each with their own WebGL context. Distribute character rendering across them via IPC:

```javascript
// Main process:
const workers = [createHiddenWindow(), createHiddenWindow()];
// Distribute: worker[0] renders characters 0-25, worker[1] renders 26-50
```

**Pros**: True multi-process parallelism, no shared context limits  
**Cons**: IPC overhead, complex orchestration, high memory

---

## Recommended Execution Order

| Phase | Fix | Impact | Effort | Dependency |
|-------|-----|--------|--------|------------|
| **1** | Fix 1: Resolve safety net | Eliminates hangs | 10 min | None |
| **1** | Fix 5: Electron GPU flags | Free perf boost | 5 min | None |
| **2** | Fix 3: Preserve frame cache during playback | Faster 2nd+ play | 30 min | Fix 1 |
| **2** | Fix 2: Canvas context disposal | Fewer blank frames | 30 min | Fix 1 |
| **3** | Fix 4: Pre-warm or chunked first play | Smooth first play | 1-2 hrs | Fixes 1-3 |
| **4** | Fix 6: Progressive rendering | Visual polish | 1-2 hrs | Fixes 1-3 |
| **5** | OffscreenCanvas worker re-enablement | Off-thread rendering | Research | Player cooperation |
| **5** | Frame-ahead buffer | Cinematic smoothness | 2-4 hrs | Fixes 1-4 |

**Phase 1 alone (Fix 1 + Fix 5) should make playback functional** — frames won't hang, GPU will be properly utilized. Phases 2-3 make it fast. Phases 4-5 make it cinema-quality.
