/**
 * UIState - UI chrome state management (Phase 2.1 refactoring)
 * 
 * Extracted from WorkSpace God object to separate concerns.
 * Holds UI layout preferences (panel sizes, ruler, etc.)
 * 
 * @class
 * @memberOf global
 */
class UIState
{
    /**
     * @param {object} [options={}]
     * @constructor
     * @public
     */
    constructor (options = {})
    {
        this._$timelineHeight  = options.timelineHeight || TimelineAdjustment.TIMELINE_DEFAULT_SIZE;
        this._$controllerWidth = options.controllerWidth || ControllerAdjustment.DEFAULT_SIZE;
        this._$ruler           = options.ruler !== undefined ? options.ruler : false;
        this._$rulerX          = options.rulerX || [];
        this._$rulerY          = options.rulerY || [];
    }

    /**
     * @description Get timeline panel height
     * @return {number}
     * @public
     */
    get timelineHeight ()
    {
        return this._$timelineHeight;
    }

    /**
     * @description Set timeline panel height
     * @param {number} height
     * @public
     */
    set timelineHeight (height)
    {
        this._$timelineHeight = height | 0;
        this.updateCSSVariables();
    }

    /**
     * @description Get controller panel width
     * @return {number}
     * @public
     */
    get controllerWidth ()
    {
        return this._$controllerWidth;
    }

    /**
     * @description Set controller panel width
     * @param {number} width
     * @public
     */
    set controllerWidth (width)
    {
        this._$controllerWidth = width | 0;
        this.updateCSSVariables();
    }

    /**
     * @description Get ruler visibility
     * @return {boolean}
     * @public
     */
    get ruler ()
    {
        return this._$ruler;
    }

    /**
     * @description Set ruler visibility
     * @param {boolean} enabled
     * @public
     */
    set ruler (enabled)
    {
        this._$ruler = !!enabled;
    }

    /**
     * @description Get ruler X positions
     * @return {Array<number>}
     * @public
     */
    get rulerX ()
    {
        return this._$rulerX;
    }

    /**
     * @description Set ruler X positions
     * @param {Array<number>} positions
     * @public
     */
    set rulerX (positions)
    {
        this._$rulerX = positions || [];
    }

    /**
     * @description Get ruler Y positions
     * @return {Array<number>}
     * @public
     */
    get rulerY ()
    {
        return this._$rulerY;
    }

    /**
     * @description Set ruler Y positions
     * @param {Array<number>} positions
     * @public
     */
    set rulerY (positions)
    {
        this._$rulerY = positions || [];
    }

    /**
     * @description Load UI state from object
     * @param {object} setting
     * @return {void}
     * @public
     */
    loadFromObject (setting)
    {
        if (!setting) {
            return;
        }

        if (setting.timelineHeight !== undefined) {
            this._$timelineHeight = setting.timelineHeight;
        }
        if (setting.controllerWidth !== undefined) {
            this._$controllerWidth = setting.controllerWidth;
        }
        if (setting.ruler !== undefined) {
            this._$ruler = !!setting.ruler;
        }
        if (setting.rulerX) {
            this._$rulerX = setting.rulerX.slice(0);
        }
        if (setting.rulerY) {
            this._$rulerY = setting.rulerY.slice(0);
        }

        this.updateCSSVariables();
    }

    /**
     * @description Convert UI state to object
     * @return {object}
     * @public
     */
    toObject ()
    {
        return {
            "timelineHeight":  this._$timelineHeight,
            "controllerWidth": this._$controllerWidth,
            "ruler": this._$ruler,
            "rulerX": this._$rulerX.slice(0),
            "rulerY": this._$rulerY.slice(0)
        };
    }

    /**
     * @description Update CSS variables for panel sizes
     * @return {void}
     * @private
     */
    updateCSSVariables ()
    {
        document
            .documentElement
            .style
            .setProperty(
                "--timeline-height",
                `${this._$timelineHeight}px`
            );

        document
            .documentElement
            .style
            .setProperty(
                "--controller-width",
                `${this._$controllerWidth}px`
            );
    }
}
