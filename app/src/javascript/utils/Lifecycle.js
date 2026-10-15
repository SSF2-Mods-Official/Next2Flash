/**
 * Lifecycle - Manage disposable resources and event listeners.
 *
 * Problem: Event listeners and resources not cleaned up, causing memory leaks.
 * Especially problematic for:
 *   - Long-lived editor sessions
 *   - Large projects with many MovieClips
 *   - Frequent timeline scrubbing
 *
 * Solution: IDisposable pattern with automatic cleanup tracking.
 *
 * Usage:
 *   class MovieClip extends Instance {
 *       constructor() {
 *           super();
 *           this._$lifecycle = new Lifecycle();
 *           
 *           // Track event listeners
 *           this._$lifecycle.addEventListener(canvas, 'click', this._onClick);
 *           
 *           // Track child resources
 *           const child = new MovieClip();
 *           this._$lifecycle.track(child);
 *       }
 *       
 *       dispose() {
 *           this._$lifecycle.dispose(); // Cleans up everything
 *           super.dispose();
 *       }
 *   }
 *
 * @class
 * @memberOf global
 */
class Lifecycle
{
    /**
     * @constructor
     * @public
     */
    constructor ()
    {
        this._$disposables = [];
        this._$eventListeners = [];
        this._$disposed = false;
    }

    /**
     * @description Check if disposed.
     *
     * @return {boolean}
     * @method
     * @public
     */
    isDisposed ()
    {
        return this._$disposed;
    }

    /**
     * @description Add event listener with automatic cleanup.
     *
     * @param  {EventTarget} target - Element or object
     * @param  {string} event - Event name
     * @param  {function} handler - Event handler
     * @param  {object} [options] - addEventListener options
     * @return {void}
     * @method
     * @public
     */
    addEventListener (target, event, handler, options)
    {
        if (this._$disposed) {
            console.warn("Cannot add listener to disposed lifecycle");
            return;
        }

        target.addEventListener(event, handler, options);

        this._$eventListeners.push({
            target,
            event,
            handler,
            options
        });
    }

    /**
     * @description Track a disposable resource.
     *
     * @param  {object} disposable - Object with dispose() method
     * @return {void}
     * @method
     * @public
     */
    track (disposable)
    {
        if (this._$disposed) {
            console.warn("Cannot track resource on disposed lifecycle");
            disposable.dispose?.();
            return;
        }

        if (!disposable || typeof disposable.dispose !== 'function') {
            console.warn("Attempted to track non-disposable resource");
            return;
        }

        this._$disposables.push(disposable);
    }

    /**
     * @description Register cleanup callback.
     *
     * @param  {function} callback - Cleanup function
     * @return {void}
     * @method
     * @public
     */
    onDispose (callback)
    {
        if (this._$disposed) {
            console.warn("Cannot register callback on disposed lifecycle");
            return;
        }

        this._$disposables.push({ dispose: callback });
    }

    /**
     * @description Dispose all tracked resources.
     *
     * @return {void}
     * @method
     * @public
     */
    dispose ()
    {
        if (this._$disposed) {
            return;
        }

        this._$disposed = true;

        // Remove all event listeners
        for (const listener of this._$eventListeners) {
            try {
                listener.target.removeEventListener(
                    listener.event,
                    listener.handler,
                    listener.options
                );
            } catch (error) {
                console.error("Error removing event listener:", error);
            }
        }
        this._$eventListeners = [];

        // Dispose all tracked resources
        for (const disposable of this._$disposables) {
            try {
                disposable.dispose();
            } catch (error) {
                console.error("Error disposing resource:", error);
            }
        }
        this._$disposables = [];
    }
}


/**
 * CanvasPool - Reusable canvas element pool with memory management.
 *
 * Problem: Creating/destroying canvas elements is expensive. Old canvases
 * retain pixel data in GPU memory even after JavaScript references released.
 *
 * Solution: Pool of reusable canvases with explicit cleanup.
 *
 * Usage:
 *   const pool = CanvasPool.getInstance();
 *   const canvas = pool.acquire(800, 600);
 *   // ... use canvas ...
 *   pool.release(canvas);
 *
 * @class
 * @memberOf global
 */
class CanvasPool
{
    /**
     * @constructor
     * @private
     */
    constructor ()
    {
        this._$available = [];
        this._$inUse = new Set();
        this._$maxPoolSize = 50; // Prevent unbounded growth
    }

    /**
     * @description Get singleton instance.
     *
     * @return {CanvasPool}
     * @method
     * @static
     * @public
     */
    static getInstance ()
    {
        if (!CanvasPool._instance) {
            CanvasPool._instance = new CanvasPool();
        }
        return CanvasPool._instance;
    }

    /**
     * @description Acquire canvas from pool.
     *
     * @param  {number} width
     * @param  {number} height
     * @return {HTMLCanvasElement}
     * @method
     * @public
     */
    acquire (width, height)
    {
        let canvas = this._findMatchingCanvas(width, height);

        if (!canvas) {
            canvas = document.createElement("canvas");
        } else {
            // Clear canvas before reuse
            this._clearCanvas(canvas);
        }

        canvas.width = width;
        canvas.height = height;

        this._$inUse.add(canvas);
        return canvas;
    }

    /**
     * @description Return canvas to pool.
     *
     * @param  {HTMLCanvasElement} canvas
     * @return {void}
     * @method
     * @public
     */
    release (canvas)
    {
        if (!this._$inUse.has(canvas)) {
            console.warn("Attempted to release canvas not acquired from pool");
            return;
        }

        this._$inUse.delete(canvas);

        // Clear pixel data to free GPU memory
        this._clearCanvas(canvas);

        // Add to pool if not full
        if (this._$available.length < this._$maxPoolSize) {
            this._$available.push(canvas);
        } else {
            // Pool full - destroy canvas
            this._destroyCanvas(canvas);
        }
    }

    /**
     * @description Clear all pooled canvases.
     *
     * @return {void}
     * @method
     * @public
     */
    clear ()
    {
        for (const canvas of this._$available) {
            this._destroyCanvas(canvas);
        }
        this._$available = [];

        for (const canvas of this._$inUse) {
            console.warn("Canvas still in use during pool clear");
        }
    }

    /**
     * @description Get pool statistics.
     *
     * @return {object}
     * @method
     * @public
     */
    getStats ()
    {
        return {
            available: this._$available.length,
            inUse: this._$inUse.size,
            total: this._$available.length + this._$inUse.size
        };
    }

    /**
     * @description Find matching canvas in pool.
     *
     * @param  {number} width
     * @param  {number} height
     * @return {HTMLCanvasElement|null}
     * @private
     */
    _findMatchingCanvas (width, height)
    {
        for (let i = 0; i < this._$available.length; i++) {
            const canvas = this._$available[i];
            // Allow 10% size tolerance to improve reuse
            if (Math.abs(canvas.width - width) / width < 0.1 &&
                Math.abs(canvas.height - height) / height < 0.1) {
                this._$available.splice(i, 1);
                return canvas;
            }
        }
        return null;
    }

    /**
     * @description Clear canvas pixel data.
     *
     * @param  {HTMLCanvasElement} canvas
     * @return {void}
     * @private
     */
    _clearCanvas (canvas)
    {
        // Clear pixel data (frees GPU memory)
        const ctx = canvas.getContext("2d");
        if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        // Reset to minimal size to free memory
        canvas.width = 1;
        canvas.height = 1;
    }

    /**
     * @description Destroy canvas completely.
     *
     * @param  {HTMLCanvasElement} canvas
     * @return {void}
     * @private
     */
    _destroyCanvas (canvas)
    {
        this._clearCanvas(canvas);
        
        // Remove all references
        canvas.width = 0;
        canvas.height = 0;
        
        // Explicitly null out context (helps GC in some browsers)
        const ctx = canvas.getContext("2d");
        if (ctx) {
            ctx.canvas = null;
        }
    }
}

/**
 * @private
 */
CanvasPool._instance = null;
