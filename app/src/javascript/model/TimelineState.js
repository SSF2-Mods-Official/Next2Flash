/**
 * TimelineState - Timeline state management (Phase 2.1 refactoring)
 * 
 * Extracted from WorkSpace God object to separate concerns.
 * Holds current timeline position and playback state.
 * 
 * @class
 * @memberOf global
 */
class TimelineState
{
    /**
     * @param {object} [options={}]
     * @constructor
     * @public
     */
    constructor (options = {})
    {
        this._$currentFrame = options.currentFrame || 0;
        this._$position     = options.position || 0;
        this._$leftFrame    = options.leftFrame || 0;
        this._$scene        = options.scene || null;
    }

    /**
     * @description Get current frame number
     * @return {number}
     * @public
     */
    get currentFrame ()
    {
        return this._$currentFrame;
    }

    /**
     * @description Set current frame number
     * @param {number} frame
     * @public
     */
    set currentFrame (frame)
    {
        this._$currentFrame = frame | 0;
    }

    /**
     * @description Get undo/redo position
     * @return {number}
     * @public
     */
    get position ()
    {
        return this._$position;
    }

    /**
     * @description Set undo/redo position
     * @param {number} position
     * @public
     */
    set position (position)
    {
        this._$position = position | 0;
    }

    /**
     * @description Get left frame (scroll position)
     * @return {number}
     * @public
     */
    get leftFrame ()
    {
        return this._$leftFrame;
    }

    /**
     * @description Set left frame (scroll position)
     * @param {number} frame
     * @public
     */
    set leftFrame (frame)
    {
        this._$leftFrame = frame | 0;
    }

    /**
     * @description Get current scene (MovieClip)
     * @return {MovieClip}
     * @public
     */
    get scene ()
    {
        return this._$scene;
    }

    /**
     * @description Set current scene (MovieClip)
     * @param {MovieClip} scene
     * @public
     */
    set scene (scene)
    {
        if (this._$scene) {
            this._$scene.stop();
        }
        this._$scene = scene;
        if (scene) {
            scene.initialize();
        }
    }

    /**
     * @description Reset timeline state
     * @return {void}
     * @public
     */
    reset ()
    {
        this._$currentFrame = 0;
        this._$position     = 0;
        this._$leftFrame    = 0;
        if (this._$scene) {
            this._$scene.stop();
            this._$scene = null;
        }
    }
}
