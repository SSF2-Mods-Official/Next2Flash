/**
 * Asset Loader Interface - Extensible pattern for loading assets.
 *
 * Problem: Asset loading logic scattered across multiple files with no
 * abstraction layer. Cannot easily swap storage backends (disk, HTTP, IndexedDB).
 *
 * Solution: Define AssetLoader interface with concrete implementations.
 *
 * Benefits:
 *   - Testability: Mock loaders for unit tests
 *   - Flexibility: Swap backends without changing business logic
 *   - Decorators: Add caching, logging, retry logic as wrappers
 *   - Composition: Chain loaders (try IndexedDB → fallback to HTTP)
 *
 * @module AssetLoader
 * @memberOf global
 */

/**
 * AssetLoader - Abstract base class for asset loading.
 *
 * @class
 * @abstract
 */
class AssetLoader
{
    /**
     * @description Load an asset by ID.
     *
     * @param  {number} assetId - Asset identifier
     * @return {Promise<Asset>} - Asset data
     * @method
     * @abstract
     */
    async load (assetId)
    {
        throw new Error("AssetLoader.load() must be implemented by subclass");
    }

    /**
     * @description Check if asset exists.
     *
     * @param  {number} assetId
     * @return {Promise<boolean>}
     * @method
     * @public
     */
    async exists (assetId)
    {
        try {
            await this.load(assetId);
            return true;
        } catch (e) {
            return false;
        }
    }
}


/**
 * HTTPAssetLoader - Load assets via HTTP API.
 *
 * @class
 * @extends AssetLoader
 */
class HTTPAssetLoader extends AssetLoader
{
    /**
     * @param {string} baseUrl - API base URL (e.g., "/api/lazy")
     *
     * @constructor
     * @public
     */
    constructor (baseUrl = "/api/lazy")
    {
        super();
        this._$baseUrl = baseUrl;
    }

    async load (assetId)
    {
        const url = `${this._$baseUrl}/library/${assetId}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Asset ${assetId} not found: ${response.status}`);
        }

        // Decode msgpack response
        const buffer = await response.arrayBuffer();
        return MessagePack.decode(new Uint8Array(buffer));
    }
}


/**
 * CachedAssetLoader - Decorator that adds caching to any loader.
 *
 * @class
 * @extends AssetLoader
 */
class CachedAssetLoader extends AssetLoader
{
    /**
     * @param {AssetLoader} innerLoader - Loader to wrap
     * @param {number} [maxSize=1000] - Maximum cache entries
     *
     * @constructor
     * @public
     */
    constructor (innerLoader, maxSize = 1000)
    {
        super();
        this._$inner = innerLoader;
        this._$cache = new Map();
        this._$maxSize = maxSize;
    }

    async load (assetId)
    {
        // Check cache first
        if (this._$cache.has(assetId)) {
            return this._$cache.get(assetId);
        }

        // Cache miss - load from inner loader
        const asset = await this._$inner.load(assetId);

        // Store in cache
        this._$cache.set(assetId, asset);

        // Evict oldest entry if cache full (FIFO)
        if (this._$cache.size > this._$maxSize) {
            const firstKey = this._$cache.keys().next().value;
            this._$cache.delete(firstKey);
        }

        return asset;
    }

    /**
     * @description Clear cache.
     *
     * @return {void}
     * @method
     * @public
     */
    clear ()
    {
        this._$cache.clear();
    }

    /**
     * @description Get cache size.
     *
     * @return {number}
     * @method
     * @public
     */
    getCacheSize ()
    {
        return this._$cache.size;
    }
}


/**
 * RetryAssetLoader - Decorator that adds retry logic with exponential backoff.
 *
 * @class
 * @extends AssetLoader
 */
class RetryAssetLoader extends AssetLoader
{
    /**
     * @param {AssetLoader} innerLoader - Loader to wrap
     * @param {number} [maxRetries=3] - Maximum retry attempts
     * @param {number} [baseDelay=100] - Base delay in ms
     *
     * @constructor
     * @public
     */
    constructor (innerLoader, maxRetries = 3, baseDelay = 100)
    {
        super();
        this._$inner = innerLoader;
        this._$maxRetries = maxRetries;
        this._$baseDelay = baseDelay;
    }

    async load (assetId)
    {
        let lastError;

        for (let attempt = 0; attempt <= this._$maxRetries; attempt++) {
            try {
                return await this._$inner.load(assetId);
            } catch (error) {
                lastError = error;

                if (attempt < this._$maxRetries) {
                    // Exponential backoff: 100ms, 200ms, 400ms, ...
                    const delay = this._$baseDelay * Math.pow(2, attempt);
                    await this._sleep(delay);
                }
            }
        }

        throw new Error(`Failed to load asset ${assetId} after ${this._$maxRetries} retries: ${lastError.message}`);
    }

    _sleep (ms)
    {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}


/**
 * FallbackAssetLoader - Try primary loader, fallback to secondary on failure.
 *
 * @class
 * @extends AssetLoader
 */
class FallbackAssetLoader extends AssetLoader
{
    /**
     * @param {AssetLoader} primaryLoader - Try this first
     * @param {AssetLoader} fallbackLoader - Use this if primary fails
     *
     * @constructor
     * @public
     */
    constructor (primaryLoader, fallbackLoader)
    {
        super();
        this._$primary = primaryLoader;
        this._$fallback = fallbackLoader;
    }

    async load (assetId)
    {
        try {
            return await this._$primary.load(assetId);
        } catch (primaryError) {
            console.warn(`Primary loader failed for asset ${assetId}, trying fallback:`, primaryError);
            return await this._$fallback.load(assetId);
        }
    }
}


/**
 * IndexedDBAssetLoader - Load assets from IndexedDB (browser-side storage).
 *
 * Use for large projects to reduce network overhead.
 *
 * @class
 * @extends AssetLoader
 */
class IndexedDBAssetLoader extends AssetLoader
{
    /**
     * @param {string} [dbName="Next2FlashAssets"] - Database name
     * @param {string} [storeName="assets"] - Object store name
     *
     * @constructor
     * @public
     */
    constructor (dbName = "Next2FlashAssets", storeName = "assets")
    {
        super();
        this._$dbName = dbName;
        this._$storeName = storeName;
        this._$db = null;
    }

    /**
     * @description Initialize database connection.
     *
     * @return {Promise<void>}
     * @method
     * @public
     */
    async init ()
    {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this._$dbName, 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this._$db = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this._$storeName)) {
                    db.createObjectStore(this._$storeName, { keyPath: "id" });
                }
            };
        });
    }

    async load (assetId)
    {
        if (!this._$db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this._$db.transaction([this._$storeName], "readonly");
            const store = transaction.objectStore(this._$storeName);
            const request = store.get(assetId);

            request.onsuccess = () => {
                if (request.result) {
                    resolve(request.result);
                } else {
                    reject(new Error(`Asset ${assetId} not found in IndexedDB`));
                }
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * @description Store asset in IndexedDB.
     *
     * @param  {number} assetId
     * @param  {object} asset
     * @return {Promise<void>}
     * @method
     * @public
     */
    async store (assetId, asset)
    {
        if (!this._$db) {
            await this.init();
        }

        return new Promise((resolve, reject) => {
            const transaction = this._$db.transaction([this._$storeName], "readwrite");
            const store = transaction.objectStore(this._$storeName);
            const request = store.put({ id: assetId, ...asset });

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
}


// ══════════════════════════════════════════════════════════════════════
//                            FACTORY
// ══════════════════════════════════════════════════════════════════════

/**
 * Create default asset loader with caching + retry.
 *
 * @param {string} [baseUrl="/api/lazy"]
 * @return {AssetLoader}
 * @function
 * @public
 */
function createDefaultAssetLoader (baseUrl = "/api/lazy")
{
    const httpLoader = new HTTPAssetLoader(baseUrl);
    const retryLoader = new RetryAssetLoader(httpLoader, 3, 100);
    const cachedLoader = new CachedAssetLoader(retryLoader, 1000);
    return cachedLoader;
}


/**
 * Create asset loader with IndexedDB fallback.
 *
 * @param {string} [baseUrl="/api/lazy"]
 * @return {AssetLoader}
 * @function
 * @public
 */
function createIndexedDBAssetLoader (baseUrl = "/api/lazy")
{
    const indexedDBLoader = new IndexedDBAssetLoader();
    const httpLoader = new HTTPAssetLoader(baseUrl);
    const fallbackLoader = new FallbackAssetLoader(indexedDBLoader, httpLoader);
    const cachedLoader = new CachedAssetLoader(fallbackLoader, 1000);
    return cachedLoader;
}


/**
 * BackgroundHydrator - Hydrates lazy library instances via a single bulk fetch.
 *
 * After a skeleton project is loaded, call hydrate() to fetch ALL library
 * data from the server in one request, then apply it to the lazy stubs.
 *
 * @class
 */
class BackgroundHydrator
{
    /**
     * @param {string} [baseUrl="/api/lazy"] - API base URL
     *
     * @constructor
     * @public
     */
    constructor (baseUrl = "/api/lazy")
    {
        this._$baseUrl = baseUrl;
        this._$aborted = false;
    }

    /**
     * @description Abort background hydration.
     * @return {void}
     * @method
     * @public
     */
    abort ()
    {
        this._$aborted = true;
    }

    /**
     * @description Hydrate all lazy libraries in a repository via bulk fetch.
     * Uses a Web Worker for the heavy fetch + MessagePack decode when available.
     *
     * @param {LibraryRepository} repository
     * @param {Function} [onProgress] - Called with (hydrated, total)
    * @return {Promise<object>} - Hydration result summary
     * @method
     * @public
     */
    async hydrate (repository, onProgress)
    {
        const lazyIds = [];
        for (const lib of repository.getAll()) {
            if (lib._$lazy) {
                lazyIds.push(lib.id);
            }
        }

        if (lazyIds.length === 0) {
            return {
                "hydrated": 0,
                "errors": 0,
                "unresolved": 0,
                "fallbackHydrated": 0,
                "typeCounts": {}
            };
        }

        console.log(`[N2F] BackgroundHydrator: ${lazyIds.length} lazy libraries — fetching bulk data...`);
        const timerLabel = `[N2F] Background hydration #${Date.now()}`;
        console.time(timerLabel);

        // Try Worker-based fetch+decode (off main thread)
        let allLibs;
        try {
            allLibs = await this._$fetchAndDecodeWithWorker(lazyIds);
        } catch (workerErr) {
            console.warn("[N2F] Worker decode failed, falling back to main thread:", workerErr.message);
            allLibs = await this._$fetchAndDecodeFallback();
        }

        if (this._$aborted) {
            console.log("[N2F] BackgroundHydrator aborted after fetch");
            return 0;
        }

        // Offload bitmap buffer decoding (base64/latin-1 → Uint8Array) to worker
        try {
            await this._$decodeBitmapBuffersWithWorker(allLibs, repository);
        } catch (decodeErr) {
            console.warn("[N2F] Image decode worker failed (non-fatal):", decodeErr.message);
        }

        let hydrated = 0;
        let errors = 0;

        // Apply data to lazy stubs in chunks to avoid blocking UI
        const CHUNK = 200;
        for (let i = 0; i < lazyIds.length; i += CHUNK) {
            if (this._$aborted) {
                console.log("[N2F] BackgroundHydrator aborted during apply");
                break;
            }

            const end = Math.min(i + CHUNK, lazyIds.length);
            for (let j = i; j < end; j++) {
                const id = lazyIds[j];
                try {
                    const data = allLibs[id];
                    if (!data) {
                        errors++;
                        continue;
                    }
                    const lib = repository.get(id);
                    if (lib && lib._$lazy) {
                        lib._applyHydratedData(data);
                        lib._$lazy = false;
                        hydrated++;
                    }
                    // Release this entry so GC can reclaim the bulk data incrementally
                    allLibs[id] = null;
                } catch (e) {
                    errors++;
                    console.warn(`[N2F] Failed to hydrate library ${id}:`, e.message);
                }
            }

            if (onProgress) {
                onProgress(hydrated, lazyIds.length);
            }

            // Yield to UI thread between chunks
            await new Promise(resolve =>
            {
                if (typeof requestIdleCallback === "function") {
                    requestIdleCallback(resolve, { timeout: 100 });
                } else {
                    setTimeout(resolve, 16);
                }
            });
        }

        // Release the full decoded bulk payload to free ~1GB+ of heap
        allLibs = null;

        const unresolvedIds = [];
        const unresolvedTypeCounts = {};
        for (let i = 0; i < lazyIds.length; i++) {
            const id = lazyIds[i];
            const lib = repository.get(id);
            if (lib && lib._$lazy) {
                unresolvedIds.push(id);
                const key = String(lib.type != null ? lib.type : "unknown");
                unresolvedTypeCounts[key] = (unresolvedTypeCounts[key] || 0) + 1;
            }
        }

        let fallbackHydrated = 0;
        if (unresolvedIds.length) {
            console.warn(`[N2F] BackgroundHydrator: ${unresolvedIds.length} unresolved lazy libraries after bulk apply. Starting per-library fallback...`);
            const fallback = await this._$hydrateMissingLibraries(unresolvedIds, repository);
            fallbackHydrated = fallback.hydrated;
            errors += fallback.errors;
        }

        const finalUnresolved = [];
        for (let i = 0; i < lazyIds.length; i++) {
            const id = lazyIds[i];
            const lib = repository.get(id);
            if (lib && lib._$lazy) {
                finalUnresolved.push(id);
            }
        }

        console.timeEnd(timerLabel);
        console.log(`[N2F] BackgroundHydrator: hydrated=${hydrated} fallbackHydrated=${fallbackHydrated} unresolved=${finalUnresolved.length} errors=${errors}`);
        return {
            "hydrated": hydrated + fallbackHydrated,
            "errors": errors,
            "unresolved": finalUnresolved.length,
            "fallbackHydrated": fallbackHydrated,
            "typeCounts": unresolvedTypeCounts
        };
    }

    /**
     * @description Fallback hydrate unresolved lazy libraries individually.
     * @param {number[]} unresolvedIds
     * @param {LibraryRepository} repository
     * @return {Promise<object>}
     * @private
     */
    async _$hydrateMissingLibraries (unresolvedIds, repository)
    {
        let hydrated = 0;
        let errors = 0;

        // Keep concurrency conservative to avoid request spikes on large files.
        const MAX_PARALLEL = 6;
        let cursor = 0;

        const worker = async () =>
        {
            while (cursor < unresolvedIds.length) {
                const index = cursor++;
                const id = unresolvedIds[index];

                try {
                    const response = await fetch(`${this._$baseUrl}/library/${id}`);
                    if (!response.ok) {
                        errors++;
                        continue;
                    }

                    const buffer = await response.arrayBuffer();
                    const data = MessagePack.decode(new Uint8Array(buffer));
                    const lib = repository.get(id);
                    if (!lib || !lib._$lazy) {
                        continue;
                    }

                    lib._applyHydratedData(data);
                    lib._$lazy = false;
                    hydrated++;
                } catch (e) {
                    errors++;
                }
            }
        };

        const tasks = [];
        const count = Math.min(MAX_PARALLEL, unresolvedIds.length);
        for (let i = 0; i < count; i++) {
            tasks.push(worker());
        }
        await Promise.all(tasks);

        return { "hydrated": hydrated, "errors": errors };
    }

    /**
     * @description Fetch + decode via Web Worker (off main thread).
     * @param {number[]} lazyIds
     * @return {Promise<Object>}
     * @private
     */
    _$fetchAndDecodeWithWorker (lazyIds)
    {
        return new Promise((resolve, reject) =>
        {
            let worker;
            try {
                worker = new Worker("./assets/js/workers/hydration-worker.js");
            } catch (e) {
                return reject(new Error("Worker creation failed: " + e.message));
            }

            worker.onmessage = (e) =>
            {
                const msg = e.data;
                if (msg.type === "fetched") {
                    worker.terminate();
                    console.log(`[N2F] Hydration Worker: fetched ${(msg.buffer.byteLength / 1048576).toFixed(1)}MB (off main thread)`);
                    // Decode on main thread (structured clone can't handle 700MB+ decoded objects)
                    const allLibs = MessagePack.decode(new Uint8Array(msg.buffer));
                    resolve(allLibs);
                } else if (msg.type === "error") {
                    worker.terminate();
                    reject(new Error(msg.message));
                }
            };

            worker.onerror = (e) =>
            {
                worker.terminate();
                reject(new Error("Worker error: " + (e.message || "unknown")));
            };

            worker.postMessage({
                type: "hydrate",
                url: `${this._$baseUrl}/bulk`
            });
        });
    }

    /**
     * @description Fallback: fetch + decode on main thread.
     * @return {Promise<Object>}
     * @private
     */
    async _$fetchAndDecodeFallback ()
    {
        const response = await fetch(`${this._$baseUrl}/bulk`);
        if (!response.ok) {
            throw new Error(`Bulk fetch failed: ${response.status}`);
        }
        const buffer = await response.arrayBuffer();
        console.log(`[N2F] BackgroundHydrator (fallback): received ${(buffer.byteLength / 1048576).toFixed(1)}MB`);
        return MessagePack.decode(new Uint8Array(buffer));
    }

    /**
     * @description Decode bitmap string buffers (base64/latin-1) to Uint8Array
     * in a Web Worker. Mutates allLibs[id].buffer in-place with decoded Uint8Arrays.
     *
     * @param {Object} allLibs - Dict of {id: libData}
     * @param {LibraryRepository} repository
     * @return {Promise<void>}
     * @private
     */
    _$decodeBitmapBuffersWithWorker (allLibs, repository)
    {
        // Collect bitmap-like items with string buffers that need decoding.
        // Constructor names are unreliable in bundled builds, so use data shape.
        const bitmapItems = [];
        for (const id in allLibs) {
            const data = allLibs[id];
            if (data && data.buffer && typeof data.buffer === "string") {
                const lib = repository.get(parseInt(id));
                const isBitmapLike = data.imageType
                    || (typeof data.width === "number" && typeof data.height === "number" && data.type === 4)
                    || (lib && lib.imageType);
                if (isBitmapLike) {
                    bitmapItems.push({ id: id, buffer: data.buffer });
                }
            }
        }

        if (bitmapItems.length === 0) {
            return Promise.resolve();
        }

        console.log(`[N2F] Image Decode Worker: ${bitmapItems.length} bitmap buffers to decode`);

        return new Promise((resolve, reject) =>
        {
            let worker;
            try {
                worker = new Worker("./assets/js/workers/image-decode-worker.js");
            } catch (e) {
                return reject(new Error("Image worker creation failed: " + e.message));
            }

            worker.onmessage = (e) =>
            {
                const msg = e.data;
                if (msg.type === "batch-done") {
                    worker.terminate();
                    for (const result of msg.results) {
                        if (result.buffer && allLibs[result.id]) {
                            allLibs[result.id].buffer = result.buffer;
                        }
                    }
                    console.log(`[N2F] Image Decode Worker: ${msg.results.length} buffers decoded`);
                    resolve();
                } else if (msg.type === "error") {
                    worker.terminate();
                    reject(new Error(msg.message));
                }
            };

            worker.onerror = (e) =>
            {
                worker.terminate();
                reject(new Error("Image worker error: " + (e.message || "unknown")));
            };

            worker.postMessage({ type: "decode-batch", items: bitmapItems });
        });
    }
}

window.BackgroundHydrator = BackgroundHydrator;
