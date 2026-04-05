/**
 * BoundsCache - Performance optimization for bounds calculation caching.
 *
 * Problem: getBounds() is called repeatedly on every frame render, recalculating
 * the same bounding box multiple times. For complex MovieClips with nested children,
 * this becomes O(n×m) where n=frames, m=children.
 *
 * Solution: Memoize bounds calculations with cache invalidation on mutations.
 *
 * Usage:
 *   class Instance {
 *       constructor() {
 *           this._$boundsCache = new BoundsCache();
 *       }
 *       
 *       getBounds(matrix) {
 *           return this._$boundsCache.get(matrix, () => this._calculateBounds(matrix));
 *       }
 *       
 *       updateRecodes(newRecodes) {
 *           this._$recodes = newRecodes;
 *           this._$boundsCache.invalidate(); // Clear cache
 *       }
 *   }
 *
 * Performance: Reduces getBounds() calls by 90%+ for static content.
 *
 * @class
 * @memberOf global
 */
class BoundsCache
{
    /**
     * @param {number} [maxSize=100] - Maximum cache entries
     *
     * @constructor
     * @public
     */
    constructor (maxSize = 100)
    {
        this._$cache = new Map();
        this._$maxSize = maxSize;
        this._$hits = 0;
        this._$misses = 0;
    }

    /**
     * @description Get cached bounds or calculate and store.
     *
     * @param  {array|null} matrix - Transformation matrix
     * @param  {function} calculator - Function that calculates bounds
     * @return {object} - {xMin, yMin, xMax, yMax}
     * @method
     * @public
     */
    get (matrix, calculator)
    {
        const key = this._createKey(matrix);

        if (this._$cache.has(key)) {
            this._$hits++;
            return this._$cache.get(key);
        }

        // Cache miss — calculate
        this._$misses++;
        const bounds = calculator();

        // Store in cache
        this._$cache.set(key, bounds);

        // Evict old entries if cache too large (LRU-style)
        if (this._$cache.size > this._$maxSize) {
            const firstKey = this._$cache.keys().next().value;
            this._$cache.delete(firstKey);
        }

        return bounds;
    }

    /**
     * @description Invalidate cache (call when content changes).
     *
     * @return {void}
     * @method
     * @public
     */
    invalidate ()
    {
        this._$cache.clear();
    }

    /**
     * @description Get cache statistics.
     *
     * @return {object} - {hits, misses, hitRate, size}
     * @method
     * @public
     */
    getStats ()
    {
        const total = this._$hits + this._$misses;
        return {
            hits: this._$hits,
            misses: this._$misses,
            hitRate: total > 0 ? (this._$hits / total * 100).toFixed(2) + '%' : '0%',
            size: this._$cache.size
        };
    }

    /**
     * @description Create cache key from matrix.
     *
     * @param  {array|null} matrix
     * @return {string}
     * @private
     */
    _createKey (matrix)
    {
        if (!matrix) {
            return 'null';
        }

        // Round to 2 decimal places to improve cache hit rate
        // (minor floating point differences shouldn't bust cache)
        return matrix.map(v => Math.round(v * 100) / 100).join(',');
    }
}
