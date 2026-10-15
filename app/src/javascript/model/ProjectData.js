/**
 * ProjectData - Core project domain model (Phase 2.1 refactoring)
 * 
 * Extracted from WorkSpace God object to separate concerns.
 * Holds project data without UI or timeline state.
 * 
 * @class
 * @memberOf global
 */
class ProjectData
{
    /**
     * @param {object} [options={}]
     * @constructor
     * @public
     */
    constructor (options = {})
    {
        this._$name        = options.name || "";
        this._$repository  = options.repository || new LibraryRepository();
        this._$plugins     = options.plugins || new Map();
        this._$characterId = options.characterId || 0;
        this._$stage       = options.stage || new Stage();

        // Ensure root MovieClip exists (ID 0)
        if (!this._$repository.has(0)) {
            const root = new MovieClip({
                "id": 0,
                "type": InstanceType.MOVIE_CLIP,
                "name": "main",
                "symbol": ""
            });
            this._$repository.add(root);
        }
    }

    /**
     * @description Get project name
     * @return {string}
     * @public
     */
    get name ()
    {
        return this._$name;
    }

    /**
     * @description Set project name
     * @param {string} name
     * @public
     */
    set name (name)
    {
        this._$name = `${name}`;
    }

    /**
     * @description Get library repository
     * @return {LibraryRepository}
     * @public
     */
    get repository ()
    {
        return this._$repository;
    }

    /**
     * @description Get root MovieClip (ID 0)
     * @return {MovieClip}
     * @readonly
     * @public
     */
    get root ()
    {
        return this._$repository.get(0);
    }

    /**
     * @description Get Stage object
     * @return {Stage}
     * @public
     */
    get stage ()
    {
        return this._$stage;
    }

    /**
     * @description Get plugins Map
     * @return {Map}
     * @public
     */
    get plugins ()
    {
        return this._$plugins;
    }

    /**
     * @description Get current character ID counter
     * @return {number}
     * @public
     */
    get characterId ()
    {
        return this._$characterId;
    }

    /**
     * @description Set character ID counter
     * @param {number} id
     * @public
     */
    set characterId (id)
    {
        this._$characterId = id | 0;
    }

    /**
     * @description Generate next unique library ID
     * @return {number}
     * @readonly
     * @public
     */
    get nextLibraryId ()
    {
        const keys = this._$repository.getAllIds();
        keys.sort(function (a, b)
        {
            if (a > b) {
                return 1;
            }
            if (a < b) {
                return -1;
            }
            return 0;
        });

        const lastLibraryId = this._$repository.get(keys.pop() | 0).id | 0;
        return lastLibraryId + 1;
    }

    /**
     * @description Load project from object
     * @param {object} object
     * @return {void}
     * @public
     */
    loadFromObject (object)
    {
        // Preserve binary buffer data from existing instances before clearing.
        // Undo snapshots use light mode (no buffers) to save memory.
        const savedBuffers = new Map();
        if (this._$repository.count() > 0) {
            for (const lib of this._$repository.getAll()) {
                if (lib._$buffer) {
                    savedBuffers.set(lib.id, lib._$buffer);
                } else if (lib.buffer && typeof lib.buffer !== "string" || (typeof lib.buffer === "string" && lib.buffer.length > 0)) {
                    savedBuffers.set(lib.id, lib.buffer);
                }
            }
        }

        this._$characterId = object.characterId | 0;
        this._$name        = object.name;
        this._$stage       = new Stage(object.stage);

        // Load plugins
        if (this._$plugins.size) {
            this._$plugins.clear();
        }
        if (object.plugins) {
            for (let idx = 0; idx < object.plugins.length; ++idx) {
                const plugin = object.plugins[idx];
                this._$plugins.set(plugin.name, plugin);
            }
        }

        // Load libraries
        if (this._$repository.count() > 0) {
            this._$repository.clear();
        }
        const libraries = object.libraries;
        for (let idx = 0; idx < libraries.length; ++idx) {
            const libData = libraries[idx];
            const instance = this.addLibrary(libData);
            // Restore buffer if it was stripped from the light snapshot
            if (instance && !instance._$buffer && savedBuffers.has(instance.id)) {
                const buf = savedBuffers.get(instance.id);
                if (typeof instance.buffer !== "undefined") {
                    instance.buffer = buf;
                }
            }
        }
        savedBuffers.clear();
    }

    /**
     * @description Add library to repository
     * @param {object} data
     * @return {Instance}
     * @public
     */
    addLibrary (data)
    {
        // Validate required fields
        if (!data || typeof data !== 'object') {
            throw new Error(`ProjectData.addLibrary: invalid data (not an object)`);
        }

        if (typeof data.id === 'undefined' || data.id === null) {
            throw new Error(
                `ProjectData.addLibrary: library missing 'id' field. ` +
                `Type: ${data.type || 'unknown'}, Name: ${data.name || 'unknown'}`
            );
        }

        if (!data.type) {
            throw new Error(
                `ProjectData.addLibrary: library missing 'type' field. ` +
                `ID: ${data.id}, Name: ${data.name || 'unknown'}`
            );
        }

        let instance = null;

        switch (data.type) {
            case InstanceType.BITMAP:
                instance = new Bitmap(data);
                break;

            case InstanceType.BUTTON:
                instance = new Button(data);
                break;

            case InstanceType.FOLDER:
                instance = new Folder(data);
                break;

            case InstanceType.GRAPHIC:
                instance = new Graphic(data);
                break;

            case InstanceType.SHAPE:
                instance = new Shape(data);
                break;

            case InstanceType.SOUND:
                instance = new Sound(data);
                break;

            case InstanceType.SPRITE:
            case InstanceType.MOVIE_CLIP:
                instance = new MovieClip(data);
                break;

            case InstanceType.TEXT:
                instance = new TextField(data);
                break;

            case InstanceType.VIDEO:
                instance = new Video(data);
                break;

            default:
                throw new Error(`Unknown library type: ${data.type}`);
        }

        this._$repository.add(instance);
        return instance;
    }

    /**
     * @description Convert project to object
     * @return {object}
     * @public
     */
    toObject (light)
    {
        const libraries = [];
        for (const value of this._$repository.getAll()) {
            libraries.push(
                light && typeof value.toLightObject === "function"
                    ? value.toLightObject()
                    : value.toObject()
            );
        }

        return {
            "version": Util.VERSION,
            "name": this.name,
            "characterId": this._$characterId,
            "stage": this.stage.toObject(),
            "libraries": libraries,
            "plugins": Array.from(this._$plugins.values())
        };
    }
}
