/**
 * MessagePack binary parser for N2D files
 * Uses @msgpack/msgpack library
 */

// This will be loaded from the CDN or bundled library
const msgpack = typeof window !== 'undefined' && window.MessagePack 
    ? window.MessagePack 
    : (typeof require !== 'undefined' ? require('@msgpack/msgpack') : null);

/**
 * Load and parse N2D file from ZIP (supports both MessagePack and JSON formats)
 * @param {Uint8Array} data - The ZIP file data
 * @returns {Promise<object>} Parsed N2D project object
 */
async function loadN2DFromZip(data) {
    if (typeof JSZip === 'undefined') {
        throw new Error('JSZip library not loaded');
    }

    const zip = await JSZip.loadAsync(data.buffer || data);
    
    // Try MessagePack format first (preferred)
    if (zip.file('project.msgpack')) {
        console.log('[N2F] Loading MessagePack format (binary)');
        const msgpackData = await zip.file('project.msgpack').async('uint8array');
        
        if (!msgpack || !msgpack.decode) {
            console.error('[N2F] MessagePack library not available, cannot load .msgpack format');
            throw new Error('MessagePack library required but not loaded');
        }
        
        try {
            const decoded = msgpack.decode(msgpackData);
            console.log('[N2F] MessagePack decoded successfully');
            return decoded;
        } catch (e) {
            console.error('[N2F] MessagePack decode failed:', e);
            throw new Error('MessagePack decode failed: ' + e.message);
        }
    }
    
    // Fall back to JSON format (legacy)
    if (zip.file('project.json')) {
        console.log('[N2F] Loading JSON format (legacy)');
        const jsonText = await zip.file('project.json').async('string');
        try {
            return JSON.parse(jsonText);
        } catch (e) {
            console.error('[N2F] JSON parse failed:', e);
            throw new Error('JSON parse failed: ' + e.message);
        }
    }
    
    throw new Error('N2D file contains neither project.msgpack nor project.json');
}

/**
 * Check if MessagePack library is available
 * @returns {boolean}
 */
function isMsgpackAvailable() {
    return msgpack && typeof msgpack.decode === 'function';
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadN2DFromZip,
        isMsgpackAvailable
    };
}
