/**
 * Next2Dのフィルターと連動したColorMatrixFilterクラス
 * ColorMatrixFilter class in conjunction with Next2D filters
 *
 * @class
 * @extends {Filter}
 * @memberOf filter
 */
class ColorMatrixFilter extends Filter
{
    static get LUMA_R ()
    {
        return 0.3086;
    }

    static get LUMA_G ()
    {
        return 0.6094;
    }

    static get LUMA_B ()
    {
        return 0.0820;
    }

    /**
     * @param {object} [object=null]
     * @constructor
     * @public
     */
    constructor (object = null)
    {
        super(object);
        this.name = "ColorMatrixFilter";

        this._$matrix = [
            1, 0, 0, 0, 0,
            0, 1, 0, 0, 0,
            0, 0, 1, 0, 0,
            0, 0, 0, 1, 0
        ];

        this._$brightness = 0;
        this._$contrast = 0;
        this._$hue = 0;
        this._$saturation = 0;
        this._$isCustomMatrix = false;

        if (object) {
            if (Array.isArray(object.matrix)) {
                this.matrix = object.matrix;
            } else if (Array.isArray(object.params) && Array.isArray(object.params[1])) {
                this.matrix = object.params[1];
            } else {
                if (typeof object.brightness !== "undefined") {
                    this.brightness = object.brightness;
                }
                if (typeof object.contrast !== "undefined") {
                    this.contrast = object.contrast;
                }
                if (typeof object.hue !== "undefined") {
                    this.hue = object.hue;
                }
                if (typeof object.saturation !== "undefined") {
                    this.saturation = object.saturation;
                }
            }
        }
    }

    /**
     * @member {number}
     * @public
     */
    get brightness ()
    {
        return this._$brightness;
    }
    set brightness (brightness)
    {
        this._$brightness = Util.$clamp(+brightness, -100, 100);
        this.updateFromAdjustColor();
    }

    /**
     * @member {number}
     * @public
     */
    get contrast ()
    {
        return this._$contrast;
    }
    set contrast (contrast)
    {
        this._$contrast = Util.$clamp(+contrast, -100, 100);
        this.updateFromAdjustColor();
    }

    /**
     * @member {number}
     * @public
     */
    get hue ()
    {
        return this._$hue;
    }
    set hue (hue)
    {
        this._$hue = Util.$clamp(+hue, -180, 180);
        this.updateFromAdjustColor();
    }

    /**
     * @member {number}
     * @public
     */
    get saturation ()
    {
        return this._$saturation;
    }
    set saturation (saturation)
    {
        this._$saturation = Util.$clamp(+saturation, -100, 100);
        this.updateFromAdjustColor();
    }

    /**
     * @member {boolean}
     * @public
     */
    get isCustomMatrix ()
    {
        return this._$isCustomMatrix;
    }

    /**
     * @member {array}
     * @public
     */
    get matrix ()
    {
        return this._$matrix.slice();
    }
    set matrix (matrix)
    {
        if (!Array.isArray(matrix) || matrix.length !== 20) {
            return ;
        }

        const values = [];
        for (let idx = 0; idx < 20; ++idx) {
            values.push(+matrix[idx]);
        }

        this._$matrix = values;

        const detectedSaturation = ColorMatrixFilter.detectSaturation(values);
        if (detectedSaturation === null) {
            this._$brightness = 0;
            this._$contrast = 0;
            this._$hue = 0;
            this._$saturation = 0;
            this._$isCustomMatrix = true;
        } else {
            this._$isCustomMatrix = false;
            this._$brightness = 0;
            this._$contrast = 0;
            this._$hue = 0;
            this._$saturation = detectedSaturation;
        }
    }

    /**
     * @return {void}
     * @method
     * @public
     */
    updateFromAdjustColor ()
    {
        this._$isCustomMatrix = false;
        this._$matrix = ColorMatrixFilter.adjustColorToMatrix(
            this._$brightness,
            this._$contrast,
            this._$hue,
            this._$saturation
        );
    }

    /**
     * @param  {number} saturation
     * @return {array<number>}
     * @method
     * @public
     */
    static saturationToMatrix (saturation)
    {
        const sat = Util.$clamp(+saturation, -100, 100);
        const x = 1 + sat / 100;

        const inv = 1 - x;
        const ir = inv * ColorMatrixFilter.LUMA_R;
        const ig = inv * ColorMatrixFilter.LUMA_G;
        const ib = inv * ColorMatrixFilter.LUMA_B;

        return [
            ir + x, ig, ib, 0, 0,
            ir, ig + x, ib, 0, 0,
            ir, ig, ib + x, 0, 0,
            0, 0, 0, 1, 0
        ];
    }

    /**
     * @return {array<number>}
     * @method
     * @public
     */
    static identityMatrix ()
    {
        return [
            1, 0, 0, 0, 0,
            0, 1, 0, 0, 0,
            0, 0, 1, 0, 0,
            0, 0, 0, 1, 0
        ];
    }

    /**
     * @param  {array<number>} left
     * @param  {array<number>} right
     * @return {array<number>}
     * @method
     * @public
     */
    static multiplyMatrix (left, right)
    {
        const out = new Array(20);

        for (let row = 0; row < 4; ++row) {

            const base = row * 5;
            for (let col = 0; col < 5; ++col) {
                out[base + col] = col === 4
                    ? left[base    ] * right[4]
                        + left[base + 1] * right[9]
                        + left[base + 2] * right[14]
                        + left[base + 3] * right[19]
                        + left[base + 4]
                    : left[base    ] * right[col]
                        + left[base + 1] * right[5  + col]
                        + left[base + 2] * right[10 + col]
                        + left[base + 3] * right[15 + col];
            }
        }

        return out;
    }

    /**
     * @param  {number} brightness
     * @param  {number} contrast
     * @param  {number} hue
     * @param  {number} saturation
     * @return {array<number>}
     * @method
     * @public
     */
    static adjustColorToMatrix (brightness, contrast, hue, saturation)
    {
        brightness = Util.$clamp(+brightness, -100, 100);
        contrast   = Util.$clamp(+contrast, -100, 100);
        hue        = Util.$clamp(+hue, -180, 180);
        saturation = Util.$clamp(+saturation, -100, 100);

        let matrix = ColorMatrixFilter.identityMatrix();

        const satMatrix = ColorMatrixFilter.saturationToMatrix(saturation);
        matrix = ColorMatrixFilter.multiplyMatrix(satMatrix, matrix);

        const contrastScale = 1 + contrast / 100;
        const contrastOffset = 128 * (1 - contrastScale);
        const contrastMatrix = [
            contrastScale, 0, 0, 0, contrastOffset,
            0, contrastScale, 0, 0, contrastOffset,
            0, 0, contrastScale, 0, contrastOffset,
            0, 0, 0, 1, 0
        ];
        matrix = ColorMatrixFilter.multiplyMatrix(contrastMatrix, matrix);

        const brightnessOffset = (brightness / 100) * 255;
        const brightnessMatrix = [
            1, 0, 0, 0, brightnessOffset,
            0, 1, 0, 0, brightnessOffset,
            0, 0, 1, 0, brightnessOffset,
            0, 0, 0, 1, 0
        ];
        matrix = ColorMatrixFilter.multiplyMatrix(brightnessMatrix, matrix);

        const rad = hue * Math.PI / 180;
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        const lR = ColorMatrixFilter.LUMA_R;
        const lG = ColorMatrixFilter.LUMA_G;
        const lB = ColorMatrixFilter.LUMA_B;

        const hueMatrix = [
            lR + cos * (1 - lR) + sin * (-lR), lG + cos * (-lG) + sin * (-lG), lB + cos * (-lB) + sin * (1 - lB), 0, 0,
            lR + cos * (-lR) + sin * (0.143), lG + cos * (1 - lG) + sin * (0.14), lB + cos * (-lB) + sin * (-0.283), 0, 0,
            lR + cos * (-lR) + sin * (-(1 - lR)), lG + cos * (-lG) + sin * (lG), lB + cos * (1 - lB) + sin * (lB), 0, 0,
            0, 0, 0, 1, 0
        ];
        matrix = ColorMatrixFilter.multiplyMatrix(hueMatrix, matrix);

        return matrix;
    }

    /**
     * @param  {array<number>} matrix
     * @return {number|null}
     * @method
     * @public
     */
    static detectSaturation (matrix)
    {
        if (!Array.isArray(matrix) || matrix.length !== 20) {
            return null;
        }

        const epsilon = 1e-4;

        if (Math.abs(matrix[3]) > epsilon
            || Math.abs(matrix[8]) > epsilon
            || Math.abs(matrix[13]) > epsilon
            || Math.abs(matrix[15]) > epsilon
            || Math.abs(matrix[16]) > epsilon
            || Math.abs(matrix[17]) > epsilon
            || Math.abs(matrix[18] - 1) > epsilon
            || Math.abs(matrix[4]) > epsilon
            || Math.abs(matrix[9]) > epsilon
            || Math.abs(matrix[14]) > epsilon
            || Math.abs(matrix[19]) > epsilon
        ) {
            return null;
        }

        const x0 = matrix[0] - matrix[5];
        const x1 = matrix[6] - matrix[11];
        const x2 = matrix[12] - matrix[2];
        const x = (x0 + x1 + x2) / 3;

        const saturation = (x - 1) * 100;
        if (!Number.isFinite(saturation)) {
            return null;
        }

        const normalized = Util.$clamp(saturation, -100, 100);
        const expected = ColorMatrixFilter.saturationToMatrix(normalized);

        for (let idx = 0; idx < 20; ++idx) {
            if (Math.abs(expected[idx] - matrix[idx]) > 0.02) {
                return null;
            }
        }

        return normalized;
    }

    /**
     * @param  {ColorMatrixFilter} filter
     * @return {boolean}
     * @method
     * @public
     */
    isSame (filter)
    {
        if (!filter || !Array.isArray(filter._$matrix)) {
            return false;
        }

        for (let idx = 0; idx < 20; ++idx) {
            if (this._$matrix[idx] !== filter._$matrix[idx]) {
                return false;
            }
        }

        return true;
    }

    /**
     * @return {window.next2d.filters.ColorMatrixFilter}
     * @method
     * @public
     */
    createInstance ()
    {
        return new window.next2d.filters.ColorMatrixFilter(this.matrix);
    }

    /**
     * @return {array}
     * @method
     * @public
     */
    toParamArray ()
    {
        return [null, this.matrix];
    }

    /**
     * @return {object}
     * @method
     * @public
     */
    toObject ()
    {
        return {
            "name": this.name,
            "state": this.state,
            "matrix": this.matrix,
            "brightness": this.brightness,
            "contrast": this.contrast,
            "hue": this.hue,
            "saturation": this.saturation
        };
    }
}
