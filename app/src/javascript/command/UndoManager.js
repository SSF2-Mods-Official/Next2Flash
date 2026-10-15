/**
 * UndoManager - Manages command history and undo/redo operations.
 *
 * Features:
 *   - Circular buffer history (max 100 commands by default)
 *   - O(1) undo/redo operations
 *   - Memory efficient: discards old history when limit reached
 *   - Event dispatching for UI updates
 *   - Transaction support (batch commands)
 *
 * Architecture:
 *   - history[]: array of executed commands (circular buffer)
 *   - currentIndex: pointer to current position in history
 *   - maxHistorySize: capacity limit (default 100)
 *
 * Memory usage:
 *   - Typical command: ~200 bytes (stores old/new property values)
 *   - 100 commands: ~20 KB << snapshot-based (~10-50 MB per snapshot)
 *
 * @class
 * @memberOf global
 */
class UndoManager
{
    /**
     * @param {number} [maxHistorySize=100] - Maximum history size
     *
     * @constructor
     * @public
     */
    constructor (maxHistorySize = 100)
    {
        this._$history = [];
        this._$currentIndex = -1;
        this._$maxHistorySize = maxHistorySize;
        this._$listeners = [];
        this._$transactionCommands = null;
    }

    /**
     * @description Execute a command and add it to history.
     *
     * Clears any forward history (commands after currentIndex) before
     * adding the new command, matching standard undo/redo behavior.
     *
     * @param  {Command} command - Command to execute
     * @return {void}
     * @method
     * @public
     */
    execute (command)
    {
        // If in transaction mode, accumulate commands
        if (this._$transactionCommands) {
            this._$transactionCommands.push(command);
            command.execute();
            return;
        }

        // Execute command
        command.execute();

        // Clear forward history (redo stack)
        if (this._$currentIndex < this._$history.length - 1) {
            this._$history.splice(this._$currentIndex + 1);
        }

        // Add to history
        this._$history.push(command);
        this._$currentIndex++;

        // Trim old history if exceeding limit
        if (this._$history.length > this._$maxHistorySize) {
            const overflow = this._$history.length - this._$maxHistorySize;
            this._$history.splice(0, overflow);
            this._$currentIndex -= overflow;
        }

        this._notifyListeners();
    }

    /**
     * @description Undo the last command.
     *
     * @return {boolean} - True if undo succeeded, false if nothing to undo
     * @method
     * @public
     */
    undo ()
    {
        if (!this.canUndo()) {
            return false;
        }

        const command = this._$history[this._$currentIndex];
        command.undo();
        this._$currentIndex--;

        this._notifyListeners();
        return true;
    }

    /**
     * @description Redo the next command.
     *
     * @return {boolean} - True if redo succeeded, false if nothing to redo
     * @method
     * @public
     */
    redo ()
    {
        if (!this.canRedo()) {
            return false;
        }

        this._$currentIndex++;
        const command = this._$history[this._$currentIndex];
        command.execute();

        this._notifyListeners();
        return true;
    }

    /**
     * @description Check if undo is available.
     *
     * @return {boolean}
     * @method
     * @public
     */
    canUndo ()
    {
        return this._$currentIndex >= 0;
    }

    /**
     * @description Check if redo is available.
     *
     * @return {boolean}
     * @method
     * @public
     */
    canRedo ()
    {
        return this._$currentIndex < this._$history.length - 1;
    }

    /**
     * @description Get description of command that would be undone.
     *
     * @return {string|null}
     * @method
     * @public
     */
    getUndoDescription ()
    {
        if (!this.canUndo()) {
            return null;
        }
        return this._$history[this._$currentIndex].getDescription();
    }

    /**
     * @description Get description of command that would be redone.
     *
     * @return {string|null}
     * @method
     * @public
     */
    getRedoDescription ()
    {
        if (!this.canRedo()) {
            return null;
        }
        return this._$history[this._$currentIndex + 1].getDescription();
    }

    /**
     * @description Clear all history.
     *
     * @return {void}
     * @method
     * @public
     */
    clear ()
    {
        this._$history = [];
        this._$currentIndex = -1;
        this._notifyListeners();
    }

    /**
     * @description Get current history size.
     *
     * @return {number}
     * @method
     * @public
     */
    getHistorySize ()
    {
        return this._$history.length;
    }

    /**
     * @description Get estimated memory usage (rough approximation).
     *
     * @return {number} - Estimated bytes (assumes ~200 bytes per command)
     * @method
     * @public
     */
    getEstimatedMemoryUsage ()
    {
        return this._$history.length * 200;
    }

    /**
     * @description Begin a transaction (batch multiple commands).
     *
     * All commands executed between beginTransaction() and commitTransaction()
     * are grouped into a single CompositeCommand for undo/redo.
     *
     * Example:
     *   undoMgr.beginTransaction("Paste");
     *   undoMgr.execute(new AddLibraryCommand(...));
     *   undoMgr.execute(new AddLayerCommand(...));
     *   undoMgr.commitTransaction();
     *   // Now undo/redo treats both as one operation
     *
     * @param  {string} [description] - Transaction description
     * @return {void}
     * @method
     * @public
     */
    beginTransaction (description)
    {
        if (this._$transactionCommands) {
            throw new Error("UndoManager: nested transactions not supported");
        }
        this._$transactionCommands = [];
        this._$transactionDescription = description || "Transaction";
    }

    /**
     * @description Commit the current transaction.
     *
     * @return {void}
     * @method
     * @public
     */
    commitTransaction ()
    {
        if (!this._$transactionCommands) {
            throw new Error("UndoManager: no transaction in progress");
        }

        if (this._$transactionCommands.length === 0) {
            // Empty transaction — discard
            this._$transactionCommands = null;
            return;
        }

        if (this._$transactionCommands.length === 1) {
            // Single command — add directly (no CompositeCommand wrapper)
            const command = this._$transactionCommands[0];
            this._$transactionCommands = null;

            // Clear forward history
            if (this._$currentIndex < this._$history.length - 1) {
                this._$history.splice(this._$currentIndex + 1);
            }

            this._$history.push(command);
            this._$currentIndex++;

            // Trim old history
            if (this._$history.length > this._$maxHistorySize) {
                const overflow = this._$history.length - this._$maxHistorySize;
                this._$history.splice(0, overflow);
                this._$currentIndex -= overflow;
            }

            this._notifyListeners();
            return;
        }

        // Multiple commands — wrap in CompositeCommand
        const composite = new CompositeCommand(
            this._$transactionCommands,
            this._$transactionDescription
        );

        this._$transactionCommands = null;

        // Clear forward history
        if (this._$currentIndex < this._$history.length - 1) {
            this._$history.splice(this._$currentIndex + 1);
        }

        this._$history.push(composite);
        this._$currentIndex++;

        // Trim old history
        if (this._$history.length > this._$maxHistorySize) {
            const overflow = this._$history.length - this._$maxHistorySize;
            this._$history.splice(0, overflow);
            this._$currentIndex -= overflow;
        }

        this._notifyListeners();
    }

    /**
     * @description Cancel the current transaction (discard accumulated commands).
     *
     * @return {void}
     * @method
     * @public
     */
    cancelTransaction ()
    {
        if (!this._$transactionCommands) {
            throw new Error("UndoManager: no transaction in progress");
        }

        // Undo all executed commands in reverse order
        for (let i = this._$transactionCommands.length - 1; i >= 0; i--) {
            this._$transactionCommands[i].undo();
        }

        this._$transactionCommands = null;
    }

    /**
     * @description Add a listener for history changes.
     *
     * Callback signature: function(undoManager) { ... }
     *
     * @param  {function} callback - Function called when history changes
     * @return {void}
     * @method
     * @public
     */
    addListener (callback)
    {
        this._$listeners.push(callback);
    }

    /**
     * @description Remove a listener.
     *
     * @param  {function} callback - Function to remove
     * @return {void}
     * @method
     * @public
     */
    removeListener (callback)
    {
        const index = this._$listeners.indexOf(callback);
        if (index !== -1) {
            this._$listeners.splice(index, 1);
        }
    }

    // ── Private Methods ──

    /**
     * @description Notify all listeners of history change.
     *
     * @return {void}
     * @private
     */
    _notifyListeners ()
    {
        for (const callback of this._$listeners) {
            callback(this);
        }
    }
}
