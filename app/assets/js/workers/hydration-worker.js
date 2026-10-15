/**
 * Hydration Worker
 * Offloads bulk fetch from the main thread.
 * Fetch happens off main thread, returns raw ArrayBuffer via zero-copy transfer.
 * MessagePack decode stays on main thread (decoded objects too large to clone).
 *
 * Messages IN:
 *   { type: 'hydrate', url: string }
 *
 * Messages OUT:
 *   { type: 'fetched', buffer: ArrayBuffer }    — raw bulk data (transferred)
 *   { type: 'error', message: string }
 */

self.onmessage = function (e) {
    var msg = e.data;

    if (msg.type === 'hydrate') {
        var url = msg.url || '/api/lazy/bulk';

        fetch(url).then(function (response) {
            if (!response.ok) {
                throw new Error('Bulk fetch failed: ' + response.status);
            }
            return response.arrayBuffer();
        }).then(function (buffer) {
            // Transfer raw buffer (zero-copy) — no cloning overhead
            self.postMessage({ type: 'fetched', buffer: buffer }, [buffer]);
        }).catch(function (err) {
            self.postMessage({ type: 'error', message: err.message });
        });
    }
};
