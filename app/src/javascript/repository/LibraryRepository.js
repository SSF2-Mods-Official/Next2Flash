/**
 * LibraryRepository - Data access layer for library management.
 *
 * Implements the Repository pattern to decouple WorkSpace from direct
 * Map-based storage. Provides:
 *   - CRUD operations (create, read, update, delete)
 *   - Query methods (findByName, findByPath, findByType)
 *   - Index maintenance for fast lookups
 *   - Storage abstraction (Map-based, extensible to IndexedDB)
 *
 * Benefits:
 *   - Single Responsibility: data access logic in one place
 *   - Testability: mock repository for unit tests
 *   - Flexibility: swap storage backend without changing WorkSpace
 *   - Performance: indexed queries for name/path lookups
 *
 * @class
 * @memberOf global
 */
class LibraryRepository
{
    /**
     * @constructor
     * @public
     */
    constructor ()
    {
        // Primary storage: id → library instance
        this._$storage = new Map();

        // Indexes for fast lookup
        this._$nameIndex = new Map();  // name → id
        this._$pathIndex = new Map();  // path → id[]
        this._$typeIndex = new Map();  // type → id[]
    }

    /**
     * @description Add or update a library instance.
     *
     * @param  {object} library - Library instance (MovieClip, Bitmap, etc.)
     * @return {void}
     * @method
     * @public
     */
    add (library)
    {
        if (!library || typeof library.id === "undefined") {
            throw new Error("LibraryRepository.add: library must have an id");
        }

        const id = library.id | 0;

        // Remove old indexes if updating
        if (this._$storage.has(id)) {
            this._removeFromIndexes(id);
        }

        // Store library
        this._$storage.set(id, library);

        // Update indexes
        this._addToIndexes(library);
    }

    /**
     * @description Retrieve a library by ID.
     *
     * @param  {number} id - Library ID
     * @return {object|undefined} - Library instance or undefined
     * @method
     * @public
     */
    get (id)
    {
        return this._$storage.get(id | 0);
    }

    /**
     * @description Check if a library exists.
     *
     * @param  {number} id - Library ID
     * @return {boolean}
     * @method
     * @public
     */
    has (id)
    {
        return this._$storage.has(id | 0);
    }

    /**
     * @description Delete a library by ID.
     *
     * @param  {number} id - Library ID
     * @return {boolean} - True if deleted, false if not found
     * @method
     * @public
     */
    delete (id)
    {
        const normalizedId = id | 0;

        if (!this._$storage.has(normalizedId)) {
            return false;
        }

        this._removeFromIndexes(normalizedId);
        return this._$storage.delete(normalizedId);
    }

    /**
     * @description Get all libraries.
     *
     * @return {Array<object>} - Array of all library instances
     * @method
     * @public
     */
    getAll ()
    {
        return Array.from(this._$storage.values());
    }

    /**
     * @description Get all library IDs.
     *
     * @return {Array<number>}
     * @method
     * @public
     */
    getAllIds ()
    {
        return Array.from(this._$storage.keys());
    }

    /**
     * @description Find a library by name (exact match).
     *
     * @param  {string} name - Library name
     * @return {object|undefined} - Library instance or undefined
     * @method
     * @public
     */
    findByName (name)
    {
        const id = this._$nameIndex.get(name);
        return id !== undefined ? this._$storage.get(id) : undefined;
    }

    /**
     * @description Find libraries by path prefix.
     *
     * @param  {string} pathPrefix - Path prefix to match
     * @return {Array<object>} - Array of matching library instances
     * @method
     * @public
     */
    findByPath (pathPrefix)
    {
        const results = [];
        const normalizedPrefix = pathPrefix.toLowerCase();

        for (const [path, ids] of this._$pathIndex.entries()) {
            if (path.startsWith(normalizedPrefix)) {
                for (const id of ids) {
                    const lib = this._$storage.get(id);
                    if (lib) {
                        results.push(lib);
                    }
                }
            }
        }

        return results;
    }

    /**
     * @description Find all libraries of a specific type.
     *
     * @param  {string} type - Library type (e.g., "bitmap", "movieclip")
     * @return {Array<object>} - Array of matching library instances
     * @method
     * @public
     */
    findByType (type)
    {
        const ids = this._$typeIndex.get(type) || [];
        return ids
            .map(id => this._$storage.get(id))
            .filter(lib => lib !== undefined);
    }

    /**
     * @description Count total libraries.
     *
     * @return {number}
     * @method
     * @public
     */
    count ()
    {
        return this._$storage.size;
    }

    /**
     * @description Clear all libraries (use with caution).
     *
     * @return {void}
     * @method
     * @public
     */
    clear ()
    {
        this._$storage.clear();
        this._$nameIndex.clear();
        this._$pathIndex.clear();
        this._$typeIndex.clear();
    }

    /**
     * @description Execute a query function on all libraries.
     *
     * @param  {function} predicate - Function (library) => boolean
     * @return {Array<object>} - Array of matching libraries
     * @method
     * @public
     */
    query (predicate)
    {
        const results = [];
        for (const library of this._$storage.values()) {
            if (predicate(library)) {
                results.push(library);
            }
        }
        return results;
    }

    // ── Private Index Management ──

    /**
     * @description Add library to indexes.
     *
     * @param  {object} library
     * @return {void}
     * @private
     */
    _addToIndexes (library)
    {
        const id = library.id | 0;

        // Name index
        if (library.name) {
            this._$nameIndex.set(library.name, id);
        }

        // Path index (folder path)
        if (library.path) {
            const normalizedPath = library.path.toLowerCase();
            if (!this._$pathIndex.has(normalizedPath)) {
                this._$pathIndex.set(normalizedPath, []);
            }
            this._$pathIndex.get(normalizedPath).push(id);
        }

        // Type index
        if (library.type) {
            const normalizedType = library.type.toLowerCase();
            if (!this._$typeIndex.has(normalizedType)) {
                this._$typeIndex.set(normalizedType, []);
            }
            this._$typeIndex.get(normalizedType).push(id);
        }
    }

    /**
     * @description Remove library from indexes.
     *
     * @param  {number} id
     * @return {void}
     * @private
     */
    _removeFromIndexes (id)
    {
        const library = this._$storage.get(id);
        if (!library) {
            return;
        }

        // Name index
        if (library.name && this._$nameIndex.get(library.name) === id) {
            this._$nameIndex.delete(library.name);
        }

        // Path index
        if (library.path) {
            const normalizedPath = library.path.toLowerCase();
            const ids = this._$pathIndex.get(normalizedPath);
            if (ids) {
                const index = ids.indexOf(id);
                if (index !== -1) {
                    ids.splice(index, 1);
                }
                if (ids.length === 0) {
                    this._$pathIndex.delete(normalizedPath);
                }
            }
        }

        // Type index
        if (library.type) {
            const normalizedType = library.type.toLowerCase();
            const ids = this._$typeIndex.get(normalizedType);
            if (ids) {
                const index = ids.indexOf(id);
                if (index !== -1) {
                    ids.splice(index, 1);
                }
                if (ids.length === 0) {
                    this._$typeIndex.delete(normalizedType);
                }
            }
        }
    }

    /**
     * @description Backward compatibility: Make LibraryRepository iterable (like Map)
     * @return {Iterator<[number, object]>}
     * @public
     */
    [Symbol.iterator] ()
    {
        return this._$storage[Symbol.iterator]();
    }

    /**
     * @description Backward compatibility: Map.entries() interface
     * @return {Iterator<[number, object]>}
     * @public
     */
    entries ()
    {
        return this._$storage.entries();
    }

    /**
     * @description Backward compatibility: Map.values() interface
     * @return {Iterator<object>}
     * @deprecated Use getAll() instead
     * @public
     */
    values ()
    {
        return this._$storage.values();
    }

    /**
     * @description Backward compatibility: Map.keys() interface
     * @return {Iterator<number>}
     * @deprecated Use getAllIds() instead
     * @public
     */
    keys ()
    {
        return this._$storage.keys();
    }

    /**
     * @description Backward compatibility: Map.set() interface
     * @param {number} id - Library ID
     * @param {object} library - Library instance
     * @return {LibraryRepository}
     * @deprecated Use add(library) instead
     * @public
     */
    set (id, library)
    {
        this.add(library);
        return this;
    }

    /**
     * @description Clear all libraries from repository
     * @return {void}
     * @public
     */
    clear ()
    {
        this._$storage.clear();
        this._$nameIndex.clear();
        this._$pathIndex.clear();
        this._$typeIndex.clear();
    }

    /**
     * @description Get repository size (number of libraries)
     * @return {number}
     * @public
     */
    get size ()
    {
        return this._$storage.size;
    }

    /**
     * @description Get repository size (alias for size)
     * @return {number}
     * @deprecated Use size property instead
     * @public
     */
    count ()
    {
        return this._$storage.size;
    }
}
