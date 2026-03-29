/**
 * SWF / N2D Importer for Next2D Animation Tool
 *
 * Two import paths:
 *
 *   .swf → fed to the built-in library-menu-file-input which triggers the
 *          app's internal SWF parser (class V). Extracts shapes, bitmaps,
 *          sprites, sounds into the Library panel.
 *
 *   .n2d → fed to the built-in tools-load-file-input which opens a full
 *          project (with main timeline frames, layers, library, stage
 *          settings) as a new workspace tab.
 *
 * For full main-timeline reconstruction from a SWF, first convert it to
 * .n2d with the Python pipeline (main.py --xfl), then import the .n2d.
 */

(function () {
    'use strict';
    var _log = window.__N2F_DEBUG ? window.__N2F_DEBUG.logger('Import') : { trace:function(){},debug:function(){},info:function(){},warn:function(){},error:function(){},time:function(){},timeEnd:function(){},group:function(){},groupEnd:function(){} };

    function init() {
        _log.debug('SWF Timeline Importer initialized');
        var btn   = document.getElementById('library-menu-import-swf-timeline');
        var input = document.getElementById('library-menu-import-swf-timeline-input');

        if (!btn || !input) {
            _log.warn('UI not found, retrying…');
            return setTimeout(init, 1000);
        }

        _log.info('Ready');

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            input.click();
        });

        input.addEventListener('change', function (e) {
            if (e.target.files.length) route(e.target.files[0]);
            this.value = '';
        });
    }

    /* ------------------------------------------------------------------ */
    /*  Route by extension                                                 */
    /* ------------------------------------------------------------------ */
    function route(file) {
        _log.info('Routing file:', file.name, file.size, 'bytes');
        var ext = file.name.split('.').pop().toLowerCase();
        _log.debug('File extension:', ext);

        if (ext === 'n2d')  return loadN2D(file);
        if (ext === 'swf')  return loadSWF(file);

        toast('❌ Unsupported file type: .' + ext, true);
    }

    /* ------------------------------------------------------------------ */
    /*  .n2d  →  open as new workspace tab (full timeline + library)       */
    /* ------------------------------------------------------------------ */
    function loadN2D(file) {
        _log.info('Loading N2D file:', file.name);
        var target = document.getElementById('tools-load-file-input');
        if (!target) {
            toast('❌ Could not find .n2d loader input', true);
            return;
        }

        toast('⏳ Loading project: ' + file.name + '…');

        var dt = new DataTransfer();
        // Ensure the file has the .n2d extension the handler checks for
        var n2dFile = new File([file], file.name.replace(/\.[^.]+$/, '.n2d'), {
            type: file.type || 'application/octet-stream'
        });
        dt.items.add(n2dFile);
        target.files = dt.files;
        target.dispatchEvent(new Event('change', { bubbles: true }));

        _log.info('Dispatched .n2d load via tools-load-file-input');

        setTimeout(function () {
            toast('✅ Project loaded! Timeline and library should be populated.');
        }, 2500);
    }

    /* ------------------------------------------------------------------ */
    /*  .swf  →  import assets into Library via built-in SWF parser        */
    /* ------------------------------------------------------------------ */
    function loadSWF(file) {
        _log.info('Loading SWF file:', file.name);
        // Quick signature check
        var reader = new FileReader();
        reader.onload = function (e) {
            var v = new DataView(e.target.result);
            var s = String.fromCharCode(v.getUint8(0), v.getUint8(1), v.getUint8(2));
            if (s !== 'FWS' && s !== 'CWS' && s !== 'ZWS') {
                toast('❌ Invalid SWF (signature: ' + s + ')', true);
                return;
            }
            feedSWFToLibrary(file);
        };
        reader.onerror = function () { toast('❌ Could not read file', true); };
        reader.readAsArrayBuffer(file);
    }

    function feedSWFToLibrary(file) {
        _log.debug('Feeding SWF data to library');
        var target = document.getElementById('library-menu-file-input');
        if (!target) {
            toast('❌ Library file-input not found', true);
            return;
        }

        toast('⏳ Importing SWF assets: ' + file.name + '…');

        var dt = new DataTransfer();
        dt.items.add(file);
        target.files = dt.files;
        target.dispatchEvent(new Event('change', { bubbles: true }));

        _log.info('Dispatched SWF to library-menu-file-input');

        setTimeout(function () {
            toast(
                '✅ SWF assets imported to Library! ' +
                'For full timeline, convert to .n2d first (main.py --xfl) then import the .n2d.'
            );
        }, 2500);
    }

    /* ------------------------------------------------------------------ */
    /*  Toast notification                                                 */
    /* ------------------------------------------------------------------ */
    function toast(msg, isErr) {
        var old = document.getElementById('swf-import-toast');
        if (old) old.remove();

        var el = document.createElement('div');
        el.id = 'swf-import-toast';
        el.style.cssText =
            'position:fixed;top:20px;right:20px;z-index:100000;max-width:420px;' +
            'padding:12px 20px;border-radius:6px;font:13px/1.5 Arial,sans-serif;' +
            'color:#fff;box-shadow:0 4px 12px rgba(0,0,0,.3);transition:opacity .3s;' +
            'background:' + (isErr ? '#e74c3c' : '#2ecc71') + ';';
        el.textContent = msg;
        document.body.appendChild(el);

        var dur = isErr ? 6000 : 4000;
        setTimeout(function () {
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 300);
        }, dur);

        _log.info(msg);
    }

    // Boot
    if (document.readyState === 'loading')
        document.addEventListener('DOMContentLoaded', init);
    else
        init();
})();
