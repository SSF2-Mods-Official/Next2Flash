/**
 * Command Pattern - Encapsulates mutations as objects for undo/redo.
 *
 * Benefits over snapshot-based undo:
 *   - Memory efficient: stores only deltas, not full state copies
 *   - Fast: O(1) undo/redo vs O(n) deep-clone + restore
 *   - Composable: macro commands group multiple edits
 *   - Extensible: new commands add new undo-able operations
 *
 * Architecture:
 *   - Command (abstract): execute() + undo() interface
 *   - Concrete commands: UpdatePlaceCommand, AddLayerCommand, etc.
 *   - UndoManager: maintains history stack, invokes execute/undo
 *
 * @class
 * @memberOf global
 * @abstract
 */
class Command
{
    /**
     * @description Execute this command (apply changes).
     *
     * @return {void}
     * @method
     * @public
     * @abstract
     */
    execute ()
    {
        throw new Error("Command.execute() must be implemented by subclass");
    }

    /**
     * @description Undo this command (revert changes).
     *
     * @return {void}
     * @method
     * @public
     * @abstract
     */
    undo ()
    {
        throw new Error("Command.undo() must be implemented by subclass");
    }

    /**
     * @description Get human-readable description for UI.
     *
     * @return {string}
     * @method
     * @public
     */
    getDescription ()
    {
        return "Unknown Command";
    }
}


// ══════════════════════════════════════════════════════════════════════
//                        PLACE OBJECT COMMANDS
// ══════════════════════════════════════════════════════════════════════

/**
 * UpdatePlaceCommand - Updates a PlaceObject character's properties.
 *
 * Stores old/new values for properties like x, y, scaleX, rotation, etc.
 * Only modified properties are stored (shallow diff).
 *
 * @class
 * @extends Command
 */
class UpdatePlaceCommand extends Command
{
    /**
     * @param {object} target - PlaceObject instance to modify
     * @param {object} newProps - New property values {x: 100, y: 50, ...}
     *
     * @constructor
     * @public
     */
    constructor (target, newProps)
    {
        super();
        this._$target = target;
        this._$newProps = newProps;
        this._$oldProps = {};

        // Capture old values for undo
        for (const key in newProps) {
            if (Object.prototype.hasOwnProperty.call(newProps, key)) {
                this._$oldProps[key] = target[key];
            }
        }
    }

    execute ()
    {
        for (const key in this._$newProps) {
            if (Object.prototype.hasOwnProperty.call(this._$newProps, key)) {
                this._$target[key] = this._$newProps[key];
            }
        }
    }

    undo ()
    {
        for (const key in this._$oldProps) {
            if (Object.prototype.hasOwnProperty.call(this._$oldProps, key)) {
                this._$target[key] = this._$oldProps[key];
            }
        }
    }

    getDescription ()
    {
        const props = Object.keys(this._$newProps).join(", ");
        return `Update Place (${props})`;
    }
}


/**
 * UpdateRecodesCommand - Updates shape recodes (vector data).
 *
 * @class
 * @extends Command
 */
class UpdateRecodesCommand extends Command
{
    /**
     * @param {object} target - Shape instance
     * @param {Array} newRecodes - New recodes array
     *
     * @constructor
     * @public
     */
    constructor (target, newRecodes)
    {
        super();
        this._$target = target;
        this._$newRecodes = newRecodes;
        this._$oldRecodes = target.recodes ? target.recodes.slice(0) : [];
    }

    execute ()
    {
        this._$target.recodes = this._$newRecodes;
    }

    undo ()
    {
        this._$target.recodes = this._$oldRecodes;
    }

    getDescription ()
    {
        return "Update Shape Recodes";
    }
}


// ══════════════════════════════════════════════════════════════════════
//                          LAYER COMMANDS
// ══════════════════════════════════════════════════════════════════════

/**
 * AddLayerCommand - Adds a new layer to a container.
 *
 * @class
 * @extends Command
 */
class AddLayerCommand extends Command
{
    /**
     * @param {object} container - MovieClip or container instance
     * @param {object} layer - Layer to add
     * @param {number} [index] - Insertion index (default: append)
     *
     * @constructor
     * @public
     */
    constructor (container, layer, index)
    {
        super();
        this._$container = container;
        this._$layer = layer;
        this._$index = index !== undefined ? index : container.layers.length;
    }

    execute ()
    {
        if (!this._$container.layers) {
            this._$container.layers = [];
        }
        this._$container.layers.splice(this._$index, 0, this._$layer);
    }

    undo ()
    {
        this._$container.layers.splice(this._$index, 1);
    }

    getDescription ()
    {
        return `Add Layer (${this._$layer.name || "Unnamed"})`;
    }
}


/**
 * DeleteLayerCommand - Deletes a layer from a container.
 *
 * @class
 * @extends Command
 */
class DeleteLayerCommand extends Command
{
    /**
     * @param {object} container - MovieClip or container instance
     * @param {number} index - Layer index to delete
     *
     * @constructor
     * @public
     */
    constructor (container, index)
    {
        super();
        this._$container = container;
        this._$index = index;
        this._$deletedLayer = container.layers[index];
    }

    execute ()
    {
        this._$container.layers.splice(this._$index, 1);
    }

    undo ()
    {
        this._$container.layers.splice(this._$index, 0, this._$deletedLayer);
    }

    getDescription ()
    {
        return `Delete Layer (${this._$deletedLayer.name || "Unnamed"})`;
    }
}


/**
 * RenameLayerCommand - Renames a layer.
 *
 * @class
 * @extends Command
 */
class RenameLayerCommand extends Command
{
    /**
     * @param {object} layer - Layer to rename
     * @param {string} newName - New layer name
     *
     * @constructor
     * @public
     */
    constructor (layer, newName)
    {
        super();
        this._$layer = layer;
        this._$oldName = layer.name;
        this._$newName = newName;
    }

    execute ()
    {
        this._$layer.name = this._$newName;
    }

    undo ()
    {
        this._$layer.name = this._$oldName;
    }

    getDescription ()
    {
        return `Rename Layer "${this._$oldName}" → "${this._$newName}"`;
    }
}


// ══════════════════════════════════════════════════════════════════════
//                        KEYFRAME COMMANDS
// ══════════════════════════════════════════════════════════════════════

/**
 * AddKeyframeCommand - Adds a new keyframe to a layer.
 *
 * @class
 * @extends Command
 */
class AddKeyframeCommand extends Command
{
    /**
     * @param {object} layer - Layer to modify
     * @param {number} frame - Frame number
     * @param {object} keyframe - Keyframe data
     *
     * @constructor
     * @public
     */
    constructor (layer, frame, keyframe)
    {
        super();
        this._$layer = layer;
        this._$frame = frame;
        this._$keyframe = keyframe;
    }

    execute ()
    {
        if (!this._$layer.characters) {
            this._$layer.characters = [];
        }
        this._$layer.characters.push(this._$keyframe);
    }

    undo ()
    {
        const index = this._$layer.characters.indexOf(this._$keyframe);
        if (index !== -1) {
            this._$layer.characters.splice(index, 1);
        }
    }

    getDescription ()
    {
        return `Add Keyframe (Frame ${this._$frame})`;
    }
}


/**
 * DeleteKeyframeCommand - Deletes a keyframe from a layer.
 *
 * @class
 * @extends Command
 */
class DeleteKeyframeCommand extends Command
{
    /**
     * @param {object} layer - Layer to modify
     * @param {number} index - Character index to delete
     *
     * @constructor
     * @public
     */
    constructor (layer, index)
    {
        super();
        this._$layer = layer;
        this._$index = index;
        this._$deletedKeyframe = layer.characters[index];
    }

    execute ()
    {
        this._$layer.characters.splice(this._$index, 1);
    }

    undo ()
    {
        this._$layer.characters.splice(this._$index, 0, this._$deletedKeyframe);
    }

    getDescription ()
    {
        return `Delete Keyframe`;
    }
}


// ══════════════════════════════════════════════════════════════════════
//                         LIBRARY COMMANDS
// ══════════════════════════════════════════════════════════════════════

/**
 * AddLibraryCommand - Adds a library item to the workspace.
 *
 * @class
 * @extends Command
 */
class AddLibraryCommand extends Command
{
    /**
     * @param {object} workspace - WorkSpace instance
     * @param {object} library - Library item to add
     *
     * @constructor
     * @public
     */
    constructor (workspace, library)
    {
        super();
        this._$workspace = workspace;
        this._$library = library;
    }

    execute ()
    {
        this._$workspace.addLibrary(this._$library);
    }

    undo ()
    {
        this._$workspace.removeLibrary(this._$library.id);
    }

    getDescription ()
    {
        return `Add Library (${this._$library.name || "Unnamed"})`;
    }
}


/**
 * DeleteLibraryCommand - Deletes a library item from the workspace.
 *
 * @class
 * @extends Command
 */
class DeleteLibraryCommand extends Command
{
    /**
     * @param {object} workspace - WorkSpace instance
     * @param {number} id - Library ID to delete
     *
     * @constructor
     * @public
     */
    constructor (workspace, id)
    {
        super();
        this._$workspace = workspace;
        this._$id = id;
        this._$deletedLibrary = workspace.getLibrary(id);
    }

    execute ()
    {
        this._$workspace.removeLibrary(this._$id);
    }

    undo ()
    {
        this._$workspace.addLibrary(this._$deletedLibrary);
    }

    getDescription ()
    {
        return `Delete Library (${this._$deletedLibrary.name || "Unnamed"})`;
    }
}


// ══════════════════════════════════════════════════════════════════════
//                       COMPOSITE COMMAND
// ══════════════════════════════════════════════════════════════════════

/**
 * CompositeCommand - Groups multiple commands into a single undo/redo unit.
 *
 * Use for macro operations like:
 *   - "Paste" (add library + add layer + add place object)
 *   - "Duplicate Layer" (add layer + copy all keyframes)
 *   - "Group Selection" (add folder + move items)
 *
 * @class
 * @extends Command
 */
class CompositeCommand extends Command
{
    /**
     * @param {Array<Command>} commands - Array of commands to execute as a group
     * @param {string} [description] - Human-readable description
     *
     * @constructor
     * @public
     */
    constructor (commands, description)
    {
        super();
        this._$commands = commands;
        this._$description = description || "Composite Command";
    }

    execute ()
    {
        for (const cmd of this._$commands) {
            cmd.execute();
        }
    }

    undo ()
    {
        // Undo in reverse order
        for (let i = this._$commands.length - 1; i >= 0; i--) {
            this._$commands[i].undo();
        }
    }

    getDescription ()
    {
        return this._$description;
    }
}
