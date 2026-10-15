/**
 * autosave-worker.js
 * Offloads JSON.stringify + deflate compression from the main thread during autosave.
 *
 * Receives: { type: 'serialize', obj: <plain project object> }
 * Returns:  { type: 'done', buffer: ArrayBuffer }  (transferred)
 *        or { type: 'error', message: string }
 */
self.onmessage = function (e) {
    var msg = e.data;
    if (msg.type !== 'serialize') return;

    try {
        var jsonStr = JSON.stringify(msg.obj);
        var encoded = new TextEncoder().encode(jsonStr);

        var cs = new CompressionStream('deflate');
        var writer = cs.writable.getWriter();
        writer.write(encoded);
        writer.close();

        new Response(cs.readable).arrayBuffer().then(function (buf) {
            self.postMessage({ type: 'done', buffer: buf }, [buf]);
        }).catch(function (err) {
            self.postMessage({ type: 'error', message: err.message });
        });
    } catch (err) {
        self.postMessage({ type: 'error', message: err.message });
    }
};
