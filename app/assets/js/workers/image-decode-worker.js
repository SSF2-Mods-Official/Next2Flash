/**
 * Image Decode Worker
 * Offloads CPU-intensive bitmap buffer decoding off the main thread.
 * Handles base64-encoded RGBA and latin-1 string-to-Uint8Array conversions.
 *
 * Messages IN:
 *   { type: 'decode-batch', items: Array<{ id: number, buffer: string|Array }> }
 *
 * Messages OUT:
 *   { type: 'batch-done', results: Array<{ id: number, buffer: Uint8Array }> }
 *   { type: 'error', message: string }
 */

self.onmessage = function (e) {
    var msg = e.data;

    if (msg.type === 'decode-batch') {
        var items = msg.items;
        var results = [];
        var transferables = [];

        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            var decoded = decodeBuffer(item.buffer);
            results.push({ id: item.id, buffer: decoded });
            if (decoded) {
                transferables.push(decoded.buffer);
            }
        }

        self.postMessage({ type: 'batch-done', results: results }, transferables);
    }
};

function decodeBuffer(binary) {
    if (!binary) return null;

    // Already a typed array or array — convert to Uint8Array
    if (typeof binary === 'object') {
        if (binary instanceof Uint8Array) return binary;
        if (Array.isArray(binary)) return new Uint8Array(binary);
        return null;
    }

    if (typeof binary !== 'string') return null;

    // Base64-encoded RGBA
    if (binary.indexOf('b64:') === 0) {
        var b64 = binary.slice(4);
        var raw = atob(b64);
        var len = raw.length;
        var arr = new Uint8Array(len);
        for (var i = 0; i < len; i++) {
            arr[i] = raw.charCodeAt(i);
        }
        return arr;
    }

    // Latin-1 string
    var length = binary.length;
    var arr2 = new Uint8Array(length);
    for (var j = 0; j < length; j++) {
        arr2[j] = binary.charCodeAt(j) & 0xff;
    }
    return arr2;
}
