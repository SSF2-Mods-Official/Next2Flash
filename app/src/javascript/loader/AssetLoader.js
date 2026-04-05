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
     *
     * @param {LibraryRepository} repository
     * @param {Function} [onProgress] - Called with (hydrated, total)
     * @return {Promise<number>} - Number of libraries hydrated
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
            return 0;
        }

        console.log(`[N2F] BackgroundHydrator: ${lazyIds.length} lazy libraries — fetching bulk data...`);
        console.time("[N2F] Background hydration");

        // Single bulk fetch for ALL library data
        const response = await fetch(`${this._$baseUrl}/bulk`);
        if (!response.ok) {
            throw new Error(`Bulk fetch failed: ${response.status}`);
        }

        const buffer = await response.arrayBuffer();
        console.log(`[N2F] BackgroundHydrator: received ${(buffer.byteLength / 1048576).toFixed(1)}MB bulk data`);

        if (this._$aborted) {
            console.log("[N2F] BackgroundHydrator aborted after fetch");
            return 0;
        }

        // Decode the bulk msgpack (dict of id -> lib data)
        const allLibs = MessagePack.decode(new Uint8Array(buffer));

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
                } catch (e) {
                    errors++;
                    console.warn(`[N2F] Failed to hydrate library ${id}:`, e.message);
                }
            }

            if (onProgress) {
                onProgress(hydrated, lazyIds.length);
            }

            // Yield to UI thread between chunks using requestIdleCallback when available
            await new Promise(resolve =>
            {
                if (typeof requestIdleCallback === "function") {
                    requestIdleCallback(resolve, { timeout: 100 });
                } else {
                    setTimeout(resolve, 16);
                }
            });
        }

        console.timeEnd("[N2F] Background hydration");
        console.log(`[N2F] BackgroundHydrator: ${hydrated} hydrated, ${errors} errors`);
        return hydrated;
    }
}

window.BackgroundHydrator = BackgroundHydrator;
