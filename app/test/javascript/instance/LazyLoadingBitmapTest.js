/**
 * Unit tests for lazy loading bitmap scenarios.
 * Tests the bitmap loading system to prevent drawImage errors like:
 *   TypeError: Failed to execute 'drawImage' on 'CanvasRenderingContext2D':
 *   The provided value is not of type '(CSSImageValue or HTMLCanvasElement ...)'
 */

describe("LazyLoadingBitmap", function () {

    let workSpace;

    // Minimal BitmapData mock used by Shape.recodes setter
    class MockBitmapData {
        constructor (w, h) {
            this.width  = w;
            this.height = h;
            this._$buffer = null;
            this._$canvas = null;
            this.namespace = "next2d.display.BitmapData";
        }
        set canvas (c)  { this._$canvas = c; }
        get canvas ()   { return this._$canvas; }
        set buffer (b)  { this._$buffer = b; }
        get buffer ()   { return this._$buffer; }
    }
    MockBitmapData.namespace = "next2d.display.BitmapData";

    beforeEach(function () {
        // Provide the mock that Shape.recodes & Bitmap.defaultSymbol need
        window.next2d = {
            "display": {
                "Shape": { "namespace": "next2d.display.Shape" },
                "BitmapData": MockBitmapData
            }
        };

        // Setup workspace (same pattern as BitmapTest / ShapeTest)
        workSpace = new WorkSpace();
        Util.$activeWorkSpaceId = Util.$workSpaces.length;
        Util.$workSpaces.push(workSpace);

        // Reset lazy loading state
        Instance._$lazyStats   = { fetched: 0, applied: 0, errors: 0, redraws: 0 };
        Instance._$lazyQueue   = [];
        Instance._$lazyInFlight = {};
        Instance._$lazyActive  = 0;
        Instance._$lazyBaseUrl = null;
        Instance._$lazySweptAll = false;
        if (Instance._$lazyRedrawTimer) {
            clearTimeout(Instance._$lazyRedrawTimer);
            Instance._$lazyRedrawTimer = null;
        }
    });

    afterEach(function () {
        Util.$workSpaces.length = 0;
        workSpace = null;
        delete window.next2d;
    });

    // ---------------------------------------------------------------
    //  Bitmap Instance Validation
    // ---------------------------------------------------------------
    describe("Bitmap Instance Validation", function () {

        it("should create a valid canvas when buffer is provided", function () {
            const width  = 10;
            const height = 10;
            const buffer = new Uint8Array(width * height * 4);
            for (let i = 0; i < buffer.length; i += 4) {
                buffer[i] = 255; buffer[i + 1] = 0;
                buffer[i + 2] = 0; buffer[i + 3] = 255;
            }

            const bitmap = new Bitmap({
                "id": 1, "name": "test_bitmap",
                "type": InstanceType.BITMAP,
                "width": width, "height": height
            });
            bitmap._$buffer = buffer;

            const canvas = document.createElement("canvas");
            canvas.width  = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            expect(ctx).not.toBeNull();

            const imageData = ctx.createImageData(width, height);
            imageData.data.set(buffer);
            ctx.putImageData(imageData, 0, 0);
            bitmap._$canvas = canvas;

            expect(bitmap._$canvas).toBeInstanceOf(HTMLCanvasElement);
            expect(bitmap._$canvas.width).toBe(width);
            expect(bitmap._$canvas.height).toBe(height);
        });

        it("should handle null buffer gracefully", function () {
            const bitmap = new Bitmap({
                "id": 2, "name": "empty_bitmap",
                "type": InstanceType.BITMAP,
                "width": 10, "height": 10
            });
            bitmap._$buffer = null;

            expect(function () {
                const c = document.createElement("canvas");
                c.width  = bitmap.width;
                c.height = bitmap.height;
            }).not.toThrow();
        });

        it("should validate canvas before using in drawImage", function () {
            const bitmap = new Bitmap({
                "id": 3, "name": "drawable_bitmap",
                "type": InstanceType.BITMAP,
                "width": 20, "height": 20
            });

            const buffer = new Uint8Array(20 * 20 * 4);
            const canvas = document.createElement("canvas");
            canvas.width  = 20;
            canvas.height = 20;
            const ctx = canvas.getContext("2d");
            const img = ctx.createImageData(20, 20);
            img.data.set(buffer);
            ctx.putImageData(img, 0, 0);
            bitmap._$canvas = canvas;

            const testCanvas = document.createElement("canvas");
            testCanvas.width  = 20;
            testCanvas.height = 20;
            const testCtx = testCanvas.getContext("2d");

            expect(function () {
                testCtx.drawImage(bitmap._$canvas, 0, 0);
            }).not.toThrow();
        });

        it("should detect invalid canvas state", function () {
            const bitmap = new Bitmap({
                "id": 4, "name": "invalid_bitmap",
                "type": InstanceType.BITMAP,
                "width": 10, "height": 10
            });

            // Set a plain object – NOT an HTMLCanvasElement
            bitmap._$canvas = { width: 10, height: 10 };

            expect(bitmap._$canvas instanceof HTMLCanvasElement).toBe(false);

            const testCanvas = document.createElement("canvas");
            const testCtx = testCanvas.getContext("2d");
            expect(function () {
                testCtx.drawImage(bitmap._$canvas, 0, 0);
            }).toThrow();
        });
    });

    // ---------------------------------------------------------------
    //  Lazy Loading Application  (_$lazyApply)
    // ---------------------------------------------------------------
    describe("Lazy Loading Application", function () {

        /**
         * Helper: create a small base-64 RGBA buffer for tests.
         */
        function makeBase64Buffer (w, h) {
            const arr = new Uint8Array(w * h * 4);
            return btoa(String.fromCharCode.apply(null, arr));
        }

        it("should apply lazy bitmap data and create canvas", function () {
            const bitmap = workSpace.addLibrary({
                "id": 10, "name": "lazy_bitmap",
                "type": InstanceType.BITMAP,
                "width": 1, "height": 1
            });
            bitmap._$lazy = true;

            Instance._$lazyApply(bitmap, {
                type: "bitmap",
                buffer: makeBase64Buffer(15, 15),
                width: 15, height: 15
            });

            expect(bitmap._$lazy).toBe(false);
            expect(bitmap._$width).toBe(15);
            expect(bitmap._$height).toBe(15);
            expect(bitmap._$buffer).toBeInstanceOf(Uint8Array);
            expect(bitmap._$buffer.length).toBe(15 * 15 * 4);
            expect(bitmap._$canvas).toBeInstanceOf(HTMLCanvasElement);
            expect(bitmap._$canvas.width).toBe(15);
            expect(bitmap._$canvas.height).toBe(15);
        });

        it("should skip canvas creation if valid canvas already exists", function () {
            const bitmap = workSpace.addLibrary({
                "id": 11, "name": "preloaded_bitmap",
                "type": InstanceType.BITMAP,
                "width": 10, "height": 10
            });
            bitmap._$lazy = true;

            const existingCanvas = document.createElement("canvas");
            existingCanvas.width  = 10;
            existingCanvas.height = 10;
            bitmap._$canvas = existingCanvas;

            Instance._$lazyApply(bitmap, {
                type: "bitmap",
                buffer: makeBase64Buffer(10, 10),
                width: 10, height: 10
            });

            expect(bitmap._$canvas).toBe(existingCanvas);
        });

        it("should handle missing buffer in lazy data", function () {
            const bitmap = workSpace.addLibrary({
                "id": 12, "name": "no_buffer",
                "type": InstanceType.BITMAP,
                "width": 10, "height": 10
            });
            bitmap._$lazy = true;

            expect(function () {
                Instance._$lazyApply(bitmap, {
                    type: "bitmap", width: 10, height: 10
                });
            }).not.toThrow();

            expect(bitmap._$lazy).toBe(false);
        });

        it("should handle corrupt base64 buffer", function () {
            const bitmap = workSpace.addLibrary({
                "id": 13, "name": "corrupt_bitmap",
                "type": InstanceType.BITMAP,
                "width": 10, "height": 10
            });
            bitmap._$lazy = true;

            expect(function () {
                Instance._$lazyApply(bitmap, {
                    type: "bitmap",
                    buffer: "!!!invalid-base64!!!",
                    width: 10, height: 10
                });
            }).toThrow();
        });

        it("should handle null data gracefully", function () {
            const bitmap = workSpace.addLibrary({
                "id": 14, "name": "null_data",
                "type": InstanceType.BITMAP,
                "width": 5, "height": 5
            });
            bitmap._$lazy = true;

            expect(function () {
                Instance._$lazyApply(bitmap, null);
            }).not.toThrow();

            // _$lazy is NOT cleared when data is null (no-op path)
            expect(bitmap._$lazy).toBe(true);
        });
    });

    // ---------------------------------------------------------------
    //  Shape with Bitmap Fills
    // ---------------------------------------------------------------
    describe("Shape with Bitmap Fills", function () {

        it("should convert recodes buffer objects to BitmapData", function () {
            const shape = new Shape({
                "id": 20, "name": "shape_bmp",
                "type": InstanceType.SHAPE,
                "bounds": { "xMin": 0, "xMax": 10, "yMin": 0, "yMax": 10 }
            });

            const width  = 4;
            const height = 4;
            const buffer = new Array(width * height * 4).fill(0);

            shape._$inBitmap = true;
            shape.recodes = [
                0,
                { "buffer": buffer, "width": width, "height": height }
            ];

            // The setter should have converted the plain object to a MockBitmapData
            expect(shape._$recodes[0]).toBe(0);
            expect(shape._$recodes[1].namespace).toBe(MockBitmapData.namespace);
            expect(shape._$recodes[1]._$canvas).toBeInstanceOf(HTMLCanvasElement);
            expect(shape._$recodes[1]._$canvas.width).toBe(width);
            expect(shape._$recodes[1]._$canvas.height).toBe(height);
        });

        it("should skip non-object entries in recodes", function () {
            const shape = new Shape({
                "id": 21, "name": "shape_plain",
                "type": InstanceType.SHAPE,
                "bounds": { "xMin": 0, "xMax": 10, "yMin": 0, "yMax": 10 }
            });

            shape._$inBitmap = true;
            shape.recodes = [0, 1, 2, 3];

            expect(shape._$recodes).toEqual([0, 1, 2, 3]);
        });

        it("should apply lazy shape recodes", function () {
            const shape = workSpace.addLibrary({
                "id": 22, "name": "lazy_shape",
                "type": InstanceType.SHAPE,
                "bounds": { "xMin": 0, "xMax": 50, "yMin": 0, "yMax": 50 }
            });
            shape._$lazy = true;

            Instance._$lazyApply(shape, {
                type: "shape",
                recodes: [0, 1, 2],
                bounds: { "xMin": 0, "xMax": 100, "yMin": 0, "yMax": 100 },
                inBitmap: false
            });

            expect(shape._$lazy).toBe(false);
            expect(shape._$recodes).toEqual([0, 1, 2]);
            expect(shape._$bounds.xMax).toBe(100);
            expect(shape._$inBitmap).toBe(false);
        });

        it("should invalidate graphicBuffer when bitmap dependency loads", function () {
            const bitmap = workSpace.addLibrary({
                "id": 30, "name": "dep_bitmap",
                "type": InstanceType.BITMAP,
                "width": 10, "height": 10
            });
            bitmap._$lazy = true;

            const shape = workSpace.addLibrary({
                "id": 31, "name": "dep_shape",
                "type": InstanceType.SHAPE,
                "bounds": { "xMin": 0, "xMax": 10, "yMin": 0, "yMax": 10 }
            });
            shape._$bitmapId = 30;
            shape._$graphicBuffer = "cached";

            Instance._$lazyApply(bitmap, {
                type: "bitmap",
                buffer: btoa(String.fromCharCode.apply(null, new Uint8Array(10 * 10 * 4))),
                width: 10, height: 10
            });

            expect(shape._$graphicBuffer).toBeNull();
        });
    });

    // ---------------------------------------------------------------
    //  Error Recovery and Edge Cases
    // ---------------------------------------------------------------
    describe("Error Recovery and Edge Cases", function () {

        it("should handle zero-dimension bitmap in lazy apply", function () {
            const bitmap = workSpace.addLibrary({
                "id": 40, "name": "zero_dim",
                "type": InstanceType.BITMAP,
                "width": 0, "height": 0
            });
            bitmap._$lazy = true;

            // Buffer is empty (0*0*4 = 0 bytes), canvas should NOT be created
            Instance._$lazyApply(bitmap, {
                type: "bitmap",
                buffer: btoa(""),
                width: 0, height: 0
            });

            expect(bitmap._$lazy).toBe(false);
            // _$canvas should remain falsy — zero dimensions trigger no canvas creation
            expect(!!bitmap._$canvas && bitmap._$canvas.width > 0).toBe(false);
        });

        it("should detect buffer / dimension mismatch", function () {
            const bitmap = new Bitmap({
                "id": 41, "name": "mismatch",
                "type": InstanceType.BITMAP,
                "width": 10, "height": 10
            });
            bitmap._$buffer = new Uint8Array(5 * 5 * 4); // wrong size

            const expected = bitmap.width * bitmap.height * 4;
            expect(bitmap._$buffer.length).not.toBe(expected);
        });

        it("should re-use in-flight promise for same charId", function () {
            const bitmap = workSpace.addLibrary({
                "id": 42, "name": "concurrent",
                "type": InstanceType.BITMAP,
                "width": 5, "height": 5
            });
            bitmap._$lazy      = true;
            bitmap._$swfCharId = 400;
            bitmap.swfCharId   = 400;

            Instance._$lazyBaseUrl = "http://test";

            const p1 = Instance._$lazyFetch(bitmap);
            const p2 = Instance._$lazyFetch(bitmap);

            expect(p1).toBe(p2);

            // Cleanup
            Instance._$lazyBaseUrl  = null;
            Instance._$lazyInFlight = {};
            Instance._$lazyQueue    = [];
        });

        it("should track statistics on apply", function () {
            const bitmap = new Bitmap({
                "id": 43, "name": "stats",
                "type": InstanceType.BITMAP,
                "width": 5, "height": 5
            });
            bitmap._$lazy = true;

            const before = Instance._$lazyStats.applied;

            Instance._$lazyApply(bitmap, {
                type: "bitmap",
                buffer: btoa(String.fromCharCode.apply(null, new Uint8Array(5 * 5 * 4))),
                width: 5, height: 5
            });

            expect(Instance._$lazyStats.applied).toBe(before + 1);
        });

        it("should handle large bitmap buffer", function () {
            const w = 100, h = 100;
            const arr = new Uint8Array(w * h * 4);
            // btoa may choke on large buffers; build string in chunks
            let bin = "";
            for (let i = 0; i < arr.length; i++) {
                bin += String.fromCharCode(arr[i]);
            }
            const b64 = btoa(bin);

            const bitmap = workSpace.addLibrary({
                "id": 44, "name": "large_bitmap",
                "type": InstanceType.BITMAP,
                "width": 1, "height": 1
            });
            bitmap._$lazy = true;

            Instance._$lazyApply(bitmap, {
                type: "bitmap", buffer: b64, width: w, height: h
            });

            expect(bitmap._$canvas).toBeInstanceOf(HTMLCanvasElement);
            expect(bitmap._$canvas.width).toBe(w);
            expect(bitmap._$canvas.height).toBe(h);
        });
    });

    // ---------------------------------------------------------------
    //  Canvas Drawable Validation (pure-logic helper)
    // ---------------------------------------------------------------
    describe("Canvas Drawable Validation", function () {

        function isCanvasDrawable (canvas) {
            return canvas instanceof HTMLCanvasElement
                && canvas.width > 0
                && canvas.height > 0
                && canvas.getContext("2d") !== null;
        }

        it("should accept a valid canvas", function () {
            const c = document.createElement("canvas");
            c.width  = 10;
            c.height = 10;
            expect(isCanvasDrawable(c)).toBe(true);
        });

        it("should reject null", function () {
            expect(isCanvasDrawable(null)).toBe(false);
        });

        it("should reject undefined", function () {
            expect(isCanvasDrawable(undefined)).toBe(false);
        });

        it("should reject a plain object", function () {
            expect(isCanvasDrawable({ width: 10, height: 10 })).toBe(false);
        });

        it("should reject zero-width canvas", function () {
            const c = document.createElement("canvas");
            c.width  = 0;
            c.height = 10;
            expect(isCanvasDrawable(c)).toBe(false);
        });

        it("should reject zero-height canvas", function () {
            const c = document.createElement("canvas");
            c.width  = 10;
            c.height = 0;
            expect(isCanvasDrawable(c)).toBe(false);
        });

        it("should drawImage safely with a validated canvas", function () {
            const src = document.createElement("canvas");
            src.width  = 8;
            src.height = 8;
            const srcCtx = src.getContext("2d");
            srcCtx.fillStyle = "red";
            srcCtx.fillRect(0, 0, 8, 8);

            const dst = document.createElement("canvas");
            dst.width  = 8;
            dst.height = 8;
            const dstCtx = dst.getContext("2d");

            expect(isCanvasDrawable(src)).toBe(true);
            expect(function () {
                dstCtx.drawImage(src, 0, 0);
            }).not.toThrow();
        });
    });
});
