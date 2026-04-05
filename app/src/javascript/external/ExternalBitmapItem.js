/**
 * @class
 * @memberOf external
 * @extends {ExternalItem}
 */
class ExternalBitmapItem extends ExternalItem
{
    /**
     * @param {Instance} instance
     * @param {ExternalDocument} external_document
     * @constructor
     * @public
     */
    constructor (instance, external_document)
    {
        super(instance, external_document);

        /**
         * @type {boolean}
         * @private
         */
        this._$smoothing = false;
    }

    /**
     * @member {boolean}
     * @public
     */
    get allowSmoothing ()
    {
        return this._$smoothing;
    }
    set allowSmoothing (smoothing)
    {
        this._$smoothing = !!smoothing;
    }

    _$load

    /**
     * @param  {File} file
     * @return {Promise}
     * @method
     * @public
     */
    addFile (file)
    {
        return new Promise((reslove) => 
        {
            if (Util.$loadingFile) {
                Util.$waitFiles.push({
                    "file": file,
                    "instance": this._$instance,
                    "callback": reslove
                });
            } else {
                Util.$loadingFile = true;
                Util.$loadFils(file, this._$instance, reslove);
            }
        });
    }

    /**
     * @param  {string} path
     * @return {void}
     * @method
     * @public
     */
    exportToFile (path)
    {
        let canvas  = Util.$getCanvas();
        let context = null;
        if (this._$instance.type === InstanceType.SHAPE) {

            const bitmapObject = this._$instance._$recodes[this._$instance._$recodes.length - 4];
            canvas.width  = bitmapObject.width;
            canvas.height = bitmapObject.height;
            context = canvas.getContext("2d");

            const { BitmapData } = window.next2d.display;
            for (let idx = 0; this._$instance._$recodes.length > idx; ++idx) {

                const value = this._$instance._$recodes[idx];

                if (typeof value !== "object") {
                    continue;
                }

                if (value.namespace !== BitmapData.namespace) {
                    continue;
                }

                // ── M1.1: Buffer validation (prevent crash on invalid bitmaps) ──
                const buffer = value._$buffer;
                if (!buffer || !Array.isArray(buffer) && !(buffer instanceof Uint8Array)) {
                    console.warn("[ExternalBitmapItem] Invalid buffer for bitmap, skipping");
                    continue;
                }

                const width = value.width || 0;
                const height = value.height || 0;
                if (width <= 0 || height <= 0 || width > 8192 || height > 8192) {
                    console.warn(`[ExternalBitmapItem] Invalid dimensions ${width}x${height}, skipping`);
                    continue;
                }

                const expectedSize = width * height * 4;
                if (buffer.length < expectedSize) {
                    console.warn(`[ExternalBitmapItem] Buffer too small (${buffer.length} < ${expectedSize}), skipping`);
                    continue;
                }

                try {
                    const bitmapCanvas  = Util.$getCanvas();
                    bitmapCanvas.width  = width;
                    bitmapCanvas.height = height;
                    const bitmapContext = bitmapCanvas.getContext("2d");

                    const bitmapData = context.createImageData(width, height);
                    for (let idx = 0; idx < buffer.length && idx < bitmapData.data.length; ++idx) {
                        bitmapData.data[idx] = buffer[idx];
                    }

                    bitmapContext.putImageData(bitmapData, 0, 0);
                    context.drawImage(bitmapCanvas, 0, 0);
                } catch (err) {
                    console.error("[ExternalBitmapItem] Failed to draw bitmap:", err);
                    // Continue with next bitmap instead of crashing
                }
            }
        } else {

            // ── M1.1: Buffer validation for non-shape bitmaps ──
            const buffer = this._$instance._$buffer;
            if (!buffer || !Array.isArray(buffer) && !(buffer instanceof Uint8Array)) {
                console.error("[ExternalBitmapItem] Invalid buffer for bitmap instance");
                Util.$poolCanvas(canvas);
                return;
            }

            const width = this._$instance.width || 0;
            const height = this._$instance.height || 0;
            if (width <= 0 || height <= 0 || width > 8192 || height > 8192) {
                console.error(`[ExternalBitmapItem] Invalid dimensions ${width}x${height}`);
                Util.$poolCanvas(canvas);
                return;
            }

            const expectedSize = width * height * 4;
            if (buffer.length < expectedSize) {
                console.error(`[ExternalBitmapItem] Buffer too small (${buffer.length} < ${expectedSize})`);
                Util.$poolCanvas(canvas);
                return;
            }

            try {
                canvas.width  = width;
                canvas.height = height;
                context = canvas.getContext("2d");

                const bitmapData = context.createImageData(canvas.width, canvas.height);
                for (let idx = 0; idx < buffer.length && idx < bitmapData.data.length; ++idx) {
                    bitmapData.data[idx] = buffer[idx];
                }

                context.putImageData(bitmapData, 0, 0);
            } catch (err) {
                console.error("[ExternalBitmapItem] Failed to export bitmap:", err);
                Util.$poolCanvas(canvas);
                return;
            }
        }

        const ext = path.split(".").pop().toLowerCase();
        window.FLfile.writeBase64(path, canvas.toDataURL(`image/${ext}`));

        Util.$poolCanvas(canvas);
    }
}