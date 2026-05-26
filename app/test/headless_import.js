/**
 * Headless browser test: starts the Python server, loads the tool,
 * imports fox.ssf via the API, and captures all console errors.
 *
 * Usage:  node test/headless_import.js
 */
const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');

const PORT = 5111; // Use a non-default port to avoid conflicts
// Set SWF_PATH via environment variable or edit this line for your local setup:
const SWF_PATH = process.env.N2F_TEST_SWF || String.raw`\path\to\your.swf`;
const SERVER_DIR = path.resolve(__dirname, '..');
const TIMEOUT = 120_000; // 2 minutes max

async function waitForServer(port, timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      await new Promise((resolve, reject) => {
        const req = http.get(`http://127.0.0.1:${port}/api/health`, (res) => {
          let data = '';
          res.on('data', (chunk) => data += chunk);
          res.on('end', () => resolve(data));
        });
        req.on('error', reject);
        req.setTimeout(2000, () => { req.destroy(); reject(new Error('timeout')); });
      });
      return true;
    } catch {
      await new Promise(r => setTimeout(r, 500));
    }
  }
  throw new Error(`Server did not start on port ${port} within ${timeoutMs}ms`);
}

async function main() {
  console.log('=== Headless Import Test ===');
  console.log(`SWF: ${SWF_PATH}`);
  console.log(`Port: ${PORT}`);

  // Verify SWF exists
  if (!fs.existsSync(SWF_PATH)) {
    console.error(`ERROR: SWF file not found: ${SWF_PATH}`);
    process.exit(1);
  }

  // Start server
  console.log('\n[1/4] Starting Python server...');
  const server = spawn('python', ['server.py', '--port', String(PORT), '--no-browser'], {
    cwd: SERVER_DIR,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  let serverOutput = '';
  server.stdout.on('data', (d) => { serverOutput += d.toString(); });
  server.stderr.on('data', (d) => { serverOutput += d.toString(); });

  server.on('error', (err) => {
    console.error('Failed to start server:', err);
    process.exit(1);
  });

  try {
    await waitForServer(PORT);
    console.log('  Server is up.');

    // Launch browser
    console.log('\n[2/4] Launching headless browser...');
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security'],
    });

    const page = await browser.newPage();

    // Collect console messages
    const consoleErrors = [];
    const consoleWarnings = [];
    const consoleLogs = [];
    const uncaughtErrors = [];

    page.on('console', (msg) => {
      const type = msg.type();
      const text = msg.text();
      if (type === 'error') {
        consoleErrors.push(text);
      } else if (type === 'warning') {
        consoleWarnings.push(text);
      } else {
        consoleLogs.push(text);
      }
    });

    page.on('pageerror', (err) => {
      uncaughtErrors.push(err.message);
    });

    // Navigate to tool
    console.log('\n[3/4] Loading the tool...');
    await page.goto(`http://127.0.0.1:${PORT}/`, { waitUntil: 'networkidle2', timeout: 30000 });
    console.log('  Page loaded.');

    // Monkey-patch drawImage to catch null/undefined arguments with full details
    await page.evaluate(() => {
      const origDrawImage = CanvasRenderingContext2D.prototype.drawImage;
      CanvasRenderingContext2D.prototype.drawImage = function(...args) {
        if (args[0] == null) {
          const stack = new Error().stack;
          // Walk up the stack to find the caller's local variables
          // Try to inspect the recodes being processed
          console.error(`[DRAWIMAGE-DEBUG] drawImage called with: ${String(args[0])} (type: ${typeof args[0]})`);
          console.error(`[DRAWIMAGE-DEBUG] Stack:\n${stack}`);
        }
        return origDrawImage.apply(this, args);
      };

      // Also monkey-patch _$getRecodes to catch errors with full context
      const origGetRecodes = window.next2d.display.Graphics.prototype._$getRecodes;
      if (origGetRecodes) {
        window.next2d.display.Graphics.prototype._$getRecodes = function(...args) {
          try {
            return origGetRecodes.apply(this, args);
          } catch (err) {
            // Log the recode around BITMAP_FILL (13) commands
            const BITMAP_FILL = 13;
            const BitmapData = window.next2d.display.BitmapData;
            const recode = this._$recode;
            if (recode) {
              for (let i = 0; i < recode.length; i++) {
                if (recode[i] === BITMAP_FILL) {
                  const bd = recode[i + 1];
                  const isBD = bd instanceof BitmapData;
                  // Show surrounding context
                  const ctx = [];
                  for (let j = Math.max(0, i - 3); j < Math.min(recode.length, i + 6); j++) {
                    const v = recode[j];
                    const desc = v instanceof BitmapData ? `BitmapData(w=${v.width},h=${v.height},buf=${v._$buffer ? 'yes' : 'no'},img=${v._$image},cvs=${v._$canvas})`
                      : v === null ? 'null'
                      : v === undefined ? 'undefined'
                      : typeof v === 'object' ? `${v.constructor?.name || 'Object'}(${JSON.stringify(v)?.substring(0, 80)})`
                      : `${typeof v}:${v}`;
                    ctx.push(`[${j}]=${desc}`);
                  }
                  console.error(`[BITMAP-FILL-CTX] pos=${i} isBD=${isBD} context: ${ctx.join(' | ')}`);
                }
              }
              console.error(`[BITMAP-FILL-CTX] recode.length=${recode.length}`);
            }
            throw err; // re-throw
          }
        };
      } else {
        console.error('[RECODE-DEBUG] Could not find Graphics._$getRecodes to patch');
      }
    });

    // Import the SWF via the API (POST multipart form with the SWF file)
    console.log('\n[4/4] Importing fox.ssf...');
    const swfBuffer = fs.readFileSync(SWF_PATH);

    // Upload via page context to trigger full client-side flow
    const importResult = await page.evaluate(async (swfArrayBuffer, port) => {
      const uint8 = new Uint8Array(swfArrayBuffer);
      const blob = new Blob([uint8], { type: 'application/octet-stream' });
      const form = new FormData();
      form.append('file', blob, 'fox.ssf');

      const resp = await fetch(`http://127.0.0.1:${port}/api/swf-to-project`, {
        method: 'POST',
        body: form,
      });

      if (!resp.ok) {
        const errText = await resp.text();
        return { error: `HTTP ${resp.status}: ${errText}` };
      }

      const name = resp.headers.get('X-N2D-Name') || 'fox';
      const libs = resp.headers.get('X-N2D-Libraries') || '?';
      const n2dBlob = await resp.blob();

      // Now feed into the tool (this is what next2flash-integration.js does)
      return await new Promise((resolve) => {
        // Give 60s for the loading to complete or for errors to appear
        const timeout = setTimeout(() => {
          resolve({ status: 'timeout', name, libs, blobSize: n2dBlob.size });
        }, 60000);

        try {
          // Reset cache
          const cacheStore = window.next2d && window.next2d.fw && window.next2d.fw.cache
            ? window.next2d.fw.cache
            : null;
          if (cacheStore && typeof cacheStore.reset === 'function') {
            cacheStore.reset();
          }

          // Create a File object and dispatch onto the tools input
          const fileInput = document.getElementById('tools-load-file-input');
          if (!fileInput) {
            clearTimeout(timeout);
            resolve({ error: 'tools-load-file-input not found' });
            return;
          }

          const file = new File([n2dBlob], name + '.n2d', { type: 'application/octet-stream' });
          const dt = new DataTransfer();
          dt.items.add(file);
          fileInput.files = dt.files;
          fileInput.dispatchEvent(new Event('change', { bubbles: true }));

          // Poll for completion
          let checks = 0;
          const interval = setInterval(() => {
            checks++;
            // Check if progressive loading logged completion
            if (checks > 120) { // 60 seconds
              clearInterval(interval);
              clearTimeout(timeout);
              resolve({ status: 'timeout-polling', name, libs, blobSize: n2dBlob.size });
            }
          }, 500);

          // Listen for the loading complete log
          const origLog = console.log;
          const origError = console.error;
          console.log = function(...args) {
            origLog.apply(console, args);
            const msg = args.join(' ');
            if (msg.includes('Progressive loading complete') || msg.includes('Load all libraries')) {
              // Wait a bit for rendering to attempt
              setTimeout(() => {
                clearInterval(interval);
                clearTimeout(timeout);
                console.log = origLog;
                console.error = origError;
                resolve({ status: 'loaded', name, libs, blobSize: n2dBlob.size });
              }, 3000);
            }
          };
        } catch (e) {
          clearTimeout(timeout);
          resolve({ error: e.message });
        }
      });
    }, Array.from(swfBuffer), PORT);

    console.log('\n  Import result:', JSON.stringify(importResult, null, 2));

    // Wait a bit more for any async errors
    await new Promise(r => setTimeout(r, 5000));

    // Print results
    console.log('\n========================================');
    console.log('  RESULTS');
    console.log('========================================');

    if (consoleErrors.length === 0 && uncaughtErrors.length === 0) {
      console.log('\n  ✓ NO ERRORS DETECTED');
    } else {
      console.log(`\n  ✗ ${consoleErrors.length} console errors, ${uncaughtErrors.length} uncaught errors`);
    }

    if (consoleErrors.length > 0) {
      console.log('\n--- Console Errors ---');
      // Show debug errors in full, deduplicate others
      const debugErrors = consoleErrors.filter(e => e.includes('[DRAWIMAGE-DEBUG]'));
      const otherErrors = consoleErrors.filter(e => !e.includes('[DRAWIMAGE-DEBUG]'));
      
      if (debugErrors.length > 0) {
        console.log('\n  -- DrawImage Debug Info --');
        debugErrors.forEach((e, i) => {
          console.log(`  [DEBUG ${i + 1}] ${e.substring(0, 1000)}`);
        });
      }
      
      const unique = [...new Set(otherErrors)];
      unique.forEach((e, i) => {
        const count = otherErrors.filter(x => x === e).length;
        console.log(`  [${i + 1}] (×${count}) ${e.substring(0, 300)}`);
      });
    }

    if (uncaughtErrors.length > 0) {
      console.log('\n--- Uncaught Errors ---');
      const unique = [...new Set(uncaughtErrors)];
      unique.forEach((e, i) => {
        const count = uncaughtErrors.filter(x => x === e).length;
        console.log(`  [${i + 1}] (×${count}) ${e.substring(0, 300)}`);
      });
    }

    // Show key logs
    const keyLogs = consoleLogs.filter(l =>
      l.includes('[N2F]') || l.includes('libraries') || l.includes('error') || l.includes('Error')
    );
    if (keyLogs.length > 0) {
      console.log('\n--- Key Logs ---');
      keyLogs.slice(0, 30).forEach(l => console.log(`  ${l.substring(0, 200)}`));
    }

    console.log('\n========================================');

    await browser.close();

  } finally {
    // Kill server
    server.kill('SIGTERM');
    try { process.kill(server.pid); } catch {}
  }
}

main().catch((err) => {
  console.error('Test failed:', err);
  process.exit(1);
});
