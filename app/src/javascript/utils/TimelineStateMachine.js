/**
 * TimelineStateMachine - Formal state management for timeline playback.
 *
 * Problem: Timeline control uses scattered boolean flags (_isPlaying, _isPaused)
 * without validation or clear state transitions. This creates bugs like:
 *   - Playing while paused
 *   - Resuming when already playing
 *   - Invalid state combinations
 *
 * Solution: Finite State Machine with valid state transitions.
 *
 * States:
 *   - STOPPED: Initial state, no playback
 *   - PLAYING: Active playback
 *   - PAUSED: Suspended playback, resumable
 *
 * Transitions:
 *   STOPPED → PLAYING (play)
 *   PLAYING → PAUSED (pause)
 *   PAUSED → PLAYING (resume)
 *   * → STOPPED (stop)
 *
 * Usage:
 *   class MovieClip {
 *       constructor() {
 *           this._$stateMachine = new TimelineStateMachine();
 *       }
 *       
 *       play() {
 *           if (this._$stateMachine.canTransition('play')) {
 *               this._$stateMachine.transition('play');
 *               // ... playback logic
 *           }
 *       }
 *   }
 *
 * @class
 * @memberOf global
 */
class TimelineStateMachine
{
    /**
     * @constructor
     * @public
     */
    constructor ()
    {
        this._$state = TimelineStateMachine.STATE_STOPPED;
        this._$frameWhenPaused = null;
        this._$listeners = [];
    }

    /**
     * @description Get current state.
     *
     * @return {string}
     * @method
     * @public
     */
    getState ()
    {
        return this._$state;
    }

    /**
     * @description Check if in PLAYING state.
     *
     * @return {boolean}
     * @method
     * @public
     */
    isPlaying ()
    {
        return this._$state === TimelineStateMachine.STATE_PLAYING;
    }

    /**
     * @description Check if in PAUSED state.
     *
     * @return {boolean}
     * @method
     * @public
     */
    isPaused ()
    {
        return this._$state === TimelineStateMachine.STATE_PAUSED;
    }

    /**
     * @description Check if in STOPPED state.
     *
     * @return {boolean}
     * @method
     * @public
     */
    isStopped ()
    {
        return this._$state === TimelineStateMachine.STATE_STOPPED;
    }

    /**
     * @description Attempt state transition.
     *
     * @param  {string} action - 'play', 'pause', 'resume', 'stop'
     * @return {boolean} - True if transition succeeded
     * @throws {Error} - If invalid transition
     * @method
     * @public
     */
    transition (action)
    {
        const oldState = this._$state;
        const newState = this._getNextState(action);

        if (!newState) {
            throw new Error(
                `Invalid transition: Cannot '${action}' from state '${oldState}'`
            );
        }

        this._$state = newState;
        this._notifyListeners(oldState, newState, action);

        return true;
    }

    /**
     * @description Check if transition is valid without executing.
     *
     * @param  {string} action
     * @return {boolean}
     * @method
     * @public
     */
    canTransition (action)
    {
        return this._getNextState(action) !== null;
    }

    /**
     * @description Register state change listener.
     *
     * @param  {function} callback - (oldState, newState, action) => void
     * @return {void}
     * @method
     * @public
     */
    addListener (callback)
    {
        this._$listeners.push(callback);
    }

    /**
     * @description Remove state change listener.
     *
     * @param  {function} callback
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

    /**
     * @description Store frame number when paused.
     *
     * @param  {number} frame
     * @return {void}
     * @method
     * @public
     */
    setFrameWhenPaused (frame)
    {
        this._$frameWhenPaused = frame;
    }

    /**
     * @description Get frame number when paused.
     *
     * @return {number|null}
     * @method
     * @public
     */
    getFrameWhenPaused ()
    {
        return this._$frameWhenPaused;
    }

    /**
     * @description Get next state for action.
     *
     * @param  {string} action
     * @return {string|null} - Next state or null if invalid
     * @private
     */
    _getNextState (action)
    {
        const transitions = TimelineStateMachine.STATE_TRANSITIONS;
        const validTransitions = transitions[this._$state];

        if (!validTransitions || !validTransitions[action]) {
            return null;
        }

        return validTransitions[action];
    }

    /**
     * @description Notify all listeners of state change.
     *
     * @param  {string} oldState
     * @param  {string} newState
     * @param  {string} action
     * @return {void}
     * @private
     */
    _notifyListeners (oldState, newState, action)
    {
        for (const listener of this._$listeners) {
            try {
                listener(oldState, newState, action);
            } catch (error) {
                console.error("Error in state machine listener:", error);
            }
        }
    }
}


// ══════════════════════════════════════════════════════════════════════
//                            CONSTANTS
// ══════════════════════════════════════════════════════════════════════

/**
 * @constant {string}
 * @public
 */
TimelineStateMachine.STATE_STOPPED = "STOPPED";

/**
 * @constant {string}
 * @public
 */
TimelineStateMachine.STATE_PLAYING = "PLAYING";

/**
 * @constant {string}
 * @public
 */
TimelineStateMachine.STATE_PAUSED = "PAUSED";

/**
 * Valid state transitions.
 *
 * @constant {object}
 * @public
 */
TimelineStateMachine.STATE_TRANSITIONS = {
    STOPPED: {
        play: TimelineStateMachine.STATE_PLAYING
    },
    PLAYING: {
        pause: TimelineStateMachine.STATE_PAUSED,
        stop: TimelineStateMachine.STATE_STOPPED
    },
    PAUSED: {
        resume: TimelineStateMachine.STATE_PLAYING,
        play: TimelineStateMachine.STATE_PLAYING, // Allow 'play' as alias for 'resume'
        stop: TimelineStateMachine.STATE_STOPPED
    }
};
