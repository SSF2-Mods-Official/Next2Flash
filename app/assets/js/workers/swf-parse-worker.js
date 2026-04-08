/**
 * SWF Parse Worker
 * Offloads ZIP extraction + MessagePack decode of the .n2d project blob
 * from the main thread.
 *
 * Messages IN:
 *   { type: 'parse', buffer: ArrayBuffer }
 *
 * Messages OUT:
 *   { type: 'parsed', data: Object, format: string }   — decoded project object
 *   { type: 'raw-blob', buffer: ArrayBuffer }           — fallback: can't parse, return raw
 *   { type: 'error', message: string }
 */

importScripts('../jszip.min.js', '../msgpack.min.js');

self.onmessage = function (e) {
    var msg = e.data;

    if (msg.type === 'parse') {
        parseN2DBlob(msg.buffer);
    }
};

function parseN2DBlob(buffer) {
    var bytes = new Uint8Array(buffer);

    // Detect ZIP (PK magic bytes)
    if (bytes.length >= 4 && bytes[0] === 0x50 && bytes[1] === 0x4B) {
        JSZip.loadAsync(buffer).then(function (zip) {
            // Try MessagePack first
            if (zip.file('project.msgpack')) {
                return zip.file('project.msgpack').async('uint8array').then(function (msgpackData) {
                    var decoded = MessagePack.decode(msgpackData);
                    self.postMessage({ type: 'parsed', data: decoded, format: 'msgpack' });
                });
            }
            // Fall back to JSON
            if (zip.file('project.json')) {
                return zip.file('project.json').async('string').then(function (jsonStr) {
                    var decoded = JSON.parse(jsonStr);
                    self.postMessage({ type: 'parsed', data: decoded, format: 'json' });
                });
            }
            throw new Error('No project.msgpack or project.json in ZIP');
        }).catch(function (err) {
            self.postMessage({ type: 'error', message: err.message });
        });
    } else {
        // Legacy zlib-compressed format — can't easily handle in worker, send back raw
        self.postMessage({ type: 'raw-blob', buffer: buffer }, [buffer]);
    }
}
