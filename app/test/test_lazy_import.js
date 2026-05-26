/**
 * Test lazy loading import flow with ssf2intro_beta.
 * Connects to running server on port 5000 (launched via Electron bat).
 *
 * Usage: node test/test_lazy_import.js
 */
const puppeteer = require('puppeteer');
const path = require('path');

const PORT = 5000;
// Set the SWF path via environment variable or edit this line for your local setup:
const SSF_PATH = process.env.N2F_TEST_SWF || String.raw`\path\to\your.swf`;
const TIMEOUT = 300_000; // 5 minutes

async function main() {
  console.log('=== Lazy Loading Import Test (ssf2intro_beta) ===');
  console.log(`Using server at port ${PORT}`);
  console.log(`SWF: ${SSF_PATH}\n`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-web-security',
      '--js-flags=--max-old-space-size=8192',
    ],
  });

  const page = await browser.newPage();

  // Collect console messages
  const consoleErrors = [];
  const consoleLogs = [];
  const uncaughtErrors = [];

  page.on('console', (msg) => {
    const text = msg.text();
    if (msg.type() === 'error') {
      consoleErrors.push(text);
      if (text.includes('[N2F]') || text.includes('[Lazy]')) {
        console.log(`  ERR: ${text.substring(0, 200)}`);
      }
    } else {
      consoleLogs.push(text);
      // Print key progress logs
      if (text.includes('[N2F]') || text.includes('[Lazy]') || text.includes('Hydrat')) {
        console.log(`  LOG: ${text.substring(0, 200)}`);
      }
    }
  });

  page.on('pageerror', (err) => {
    uncaughtErrors.push(err.message);
    console.log(`  PAGE_ERR: ${err.message.substring(0, 200)}`);
  });

  try {
    // Load tool
    console.log('[1/5] Loading tool...');
    await page.goto(`http://127.0.0.1:${PORT}/`, { waitUntil: 'networkidle2', timeout: 30000 });
    console.log('  Page loaded.\n');

    // Trigger lazy SWF import and feed to tool in one step
    console.log('[2/4] Starting lazy SWF import + feed to tool...');
    console.log('  (Conversion takes ~2 min for this file)');
    const t0 = Date.now();

    const loadResult = await page.evaluate(async (swfPath) => {
      // Step 1: Import via lazy path
      const resp = await fetch('/api/import-swf-path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ swfPath: swfPath, lazy: true }),
      });

      if (!resp.ok) {
        const errBody = await resp.text();
        return { error: `HTTP ${resp.status}: ${errBody.substring(0, 500)}` };
      }

      const name = resp.headers.get('X-N2D-Name') || 'ssf2intro_beta';
      const libs = resp.headers.get('X-N2D-Libraries') || '?';
      const projDir = resp.headers.get('X-Project-Dir') || '';
      const blob = await resp.blob();
      const blobSizeMB = (blob.size / 1048576).toFixed(1);

      // Step 2: Feed to tool
      return await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          // Gather state on timeout
          const Util = window.Util;
          let libCount = 0, lazyCount = 0;
          if (Util && Util.$workSpaces && Util.$workSpaces.length > 0) {
            const ws = Util.$workSpaces[Util.$workSpaces.length - 1];
            const repo = ws._$project && ws._$project.repository;
            if (repo) {
              for (const lib of repo.getAll()) {
                libCount++;
                if (lib._$lazy) lazyCount++;
              }
            }
          }
          resolve({
            status: 'timeout',
            name, libs, projDir, blobSizeMB,
            totalLibs: libCount, lazyLibs: lazyCount
          });
        }, 120000);

        try {
          const cacheStore = window.next2d && window.next2d.player && window.next2d.player.cacheStore;
          if (cacheStore) cacheStore.reset();

          const fileInput = document.getElementById('tools-load-file-input');
          if (!fileInput) {
            clearTimeout(timeout);
            resolve({ error: 'tools-load-file-input not found' });
            return;
          }

          const file = new File([blob], name + '.n2d', { type: 'application/octet-stream' });
          const dt = new DataTransfer();
          dt.items.add(file);
          fileInput.files = dt.files;
          fileInput.dispatchEvent(new Event('change', { bubbles: true }));

          // Listen for loading complete
          const origLog = console.log;
          console.log = function(...args) {
            origLog.apply(console, args);
            const msg = args.join(' ');
            if (msg.includes('Progressive loading complete') ||
                msg.includes('UI setup complete') ||
                msg.includes('Load all libraries')) {
              setTimeout(() => {
                clearTimeout(timeout);
                console.log = origLog;

                const Util = window.Util;
                let libCount = 0, lazyCount = 0;
                if (Util && Util.$workSpaces && Util.$workSpaces.length > 0) {
                  const ws = Util.$workSpaces[Util.$workSpaces.length - 1];
                  const repo = ws._$project && ws._$project.repository;
                  if (repo) {
                    for (const lib of repo.getAll()) {
                      libCount++;
                      if (lib._$lazy) lazyCount++;
                    }
                  }
                }

                resolve({
                  status: 'loaded',
                  name, libs, projDir, blobSizeMB,
                  totalLibs: libCount, lazyLibs: lazyCount
                });
              }, 2000);
            }
          };
        } catch (e) {
          clearTimeout(timeout);
          resolve({ error: e.message });
        }
      });
    }, SSF_PATH);

    const loadElapsed = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(`  Done in ${loadElapsed}s: ${JSON.stringify(loadResult)}\n`);

    if (loadResult.error) {
      console.error('ERROR: Load failed:', loadResult.error);
      await browser.close();
      process.exit(1);
    }

    // Check if bulk hydration happens
    console.log('[3/4] Triggering background hydration...');
    const hydrationResult = await page.evaluate(async () => {
      const Util = window.Util;
      if (!Util || !Util.$workSpaces || Util.$workSpaces.length === 0) {
        return { error: 'No workspace' };
      }

      const ws = Util.$workSpaces[Util.$workSpaces.length - 1];
      const repo = ws._$project && ws._$project.repository;
      if (!repo) return { error: 'No repository' };

      // Count lazy before
      let lazyBefore = 0;
      for (const lib of repo.getAll()) {
        if (lib._$lazy) lazyBefore++;
      }

      if (lazyBefore === 0) {
        return { status: 'no_lazy_libs', msg: 'All libraries already hydrated' };
      }

      // Manually trigger bulk hydration
      const hydrator = new BackgroundHydrator('/api/lazy');
      const t0 = performance.now();
      let lastProgress = '';

      try {
        const count = await hydrator.hydrate(repo, (hydrated, total) => {
          lastProgress = `${hydrated}/${total}`;
        });
        const elapsed = ((performance.now() - t0) / 1000).toFixed(1);

        // Count lazy after
        let lazyAfter = 0;
        for (const lib of repo.getAll()) {
          if (lib._$lazy) lazyAfter++;
        }

        return {
          status: 'ok',
          lazyBefore,
          hydrated: count,
          lazyAfter,
          elapsed: elapsed + 's',
          lastProgress
        };
      } catch (e) {
        return { error: e.message, stack: e.stack };
      }
    });

    console.log(`  Hydration result: ${JSON.stringify(hydrationResult)}\n`);

    // Trigger re-render after hydration
    console.log('[4/5] Triggering canvas re-render...');
    const rerenderResult = await page.evaluate(() => {
      const Util = window.Util;
      if (!Util || !Util.$workSpaces || !Util.$workSpaces.length) {
        return { error: 'No workspace for re-render' };
      }
      const ws = Util.$workSpaces[Util.$workSpaces.length - 1];
      const repo = ws._$project && ws._$project.repository;

      // Clear graphic buffer caches
      let cleared = 0;
      if (repo) {
        for (const lib of repo.getAll()) {
          if (lib._$graphicBuffer) {
            lib._$graphicBuffer = null;
            cleared++;
          }
        }
      }

      // Re-initialize scene
      let sceneOk = false;
      if (ws._$scene) {
        ws.initialize(ws._$scene);
        sceneOk = true;
      } else if (ws.scene) {
        ws.initialize(ws.scene);
        sceneOk = true;
      }

      // Check stage
      const stage = ws.stage;
      const stageInfo = stage ? {
        hasCanvas: !!stage._$canvas,
        canvasTag: stage._$canvas ? stage._$canvas.tagName : null,
      } : null;

      // Enumerate canvas elements
      const canvases = document.querySelectorAll('canvas');
      const canvasInfo = Array.from(canvases).map(c => ({
        id: c.id, className: c.className,
        w: c.width, h: c.height,
        parent: c.parentElement ? c.parentElement.className || c.parentElement.id : null,
      }));

      return { cleared, sceneOk, stageInfo, canvasCount: canvases.length, canvasInfo };
    });
    console.log(`  Re-render: ${JSON.stringify(rerenderResult)}\n`);

    // Wait for render
    await new Promise(r => setTimeout(r, 2000));

    // Check canvas state
    console.log('[5/5] Checking canvas state...');
    const canvasResult = await page.evaluate(() => {
      const canvases = document.querySelectorAll('canvas');
      const results = [];
      for (const canvas of canvases) {
        try {
          const ctx = canvas.getContext('2d');
          if (!ctx) {
            results.push({ id: canvas.id, w: canvas.width, h: canvas.height, type: 'webgl-or-no-2d' });
            continue;
          }
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const pixels = imageData.data;
          let nonTransparent = 0;
          for (let i = 3; i < pixels.length; i += 4) {
            if (pixels[i] > 0) nonTransparent++;
          }
          results.push({
            id: canvas.id, w: canvas.width, h: canvas.height,
            total: canvas.width * canvas.height,
            nonTransparent, hasContent: nonTransparent > 100,
          });
        } catch (e) {
          results.push({ id: canvas.id, error: e.message });
        }
      }
      return results;
    });
    const hasAnyContent = canvasResult.some(c => c.hasContent);

    console.log(`  Canvas: ${JSON.stringify(canvasResult)}\n`);

    // Summary
    console.log('========================================');
    console.log('  SUMMARY');
    console.log('========================================');
    console.log(`  Console errors: ${consoleErrors.length}`);
    console.log(`  Uncaught errors: ${uncaughtErrors.length}`);
    console.log(`  Canvas has content: ${hasAnyContent}`);

    if (consoleErrors.length > 0) {
      console.log('\n--- Console Errors (first 10 unique) ---');
      const unique = [...new Set(consoleErrors)];
      unique.slice(0, 10).forEach((e, i) => {
        const count = consoleErrors.filter(x => x === e).length;
        console.log(`  [${i + 1}] (×${count}) ${e.substring(0, 300)}`);
      });
    }

    if (uncaughtErrors.length > 0) {
      console.log('\n--- Uncaught Errors ---');
      const unique = [...new Set(uncaughtErrors)];
      unique.slice(0, 10).forEach((e, i) => {
        const count = uncaughtErrors.filter(x => x === e).length;
        console.log(`  [${i + 1}] (×${count}) ${e.substring(0, 300)}`);
      });
    }

    // Key N2F logs
    const n2fLogs = consoleLogs.filter(l => l.includes('[N2F]') || l.includes('[Lazy]'));
    if (n2fLogs.length > 0) {
      console.log('\n--- Key N2F Logs ---');
      n2fLogs.slice(0, 30).forEach(l => console.log(`  ${l.substring(0, 200)}`));
    }

    console.log('\n========================================');

  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('Test failed:', err);
  process.exit(1);
});
