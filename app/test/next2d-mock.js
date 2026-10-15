/**
 * Minimal mock of window.next2d for testing purposes
 * Provides constructor functions for Next2D classes used in Bitmap.createInstance() and MovieClip.createInstance()
 */

(function() {
    "use strict";

    // Mock Shape class
    class Shape {
        constructor() {
            this._$loaderInfo = null;
            this._$characterId = 0;
            this._$graphics = new Graphics();
            this._$scaleX = 1;
            this._$scaleY = 1;
            this._$regX = 0;
            this._$regY = 0;
            this._$x = 0;
            this._$y = 0;
            this._$rotation = 0;
            this._$alpha = 1;
            this._$visible = true;
            this._$blendMode = "normal";
            this._$filters = [];
            this._$matrix = null;
            this._$colorTransform = null;
        }
        
        static get namespace() {
            return "next2d.display.Shape";
        }
        
        get graphics() {
            return this._$graphics;
        }
    }

    // Mock Graphics class
    class Graphics {
        constructor() {
            this._$commands = [];
        }
        
        static get namespace() {
            return "next2d.display.Graphics";
        }
        
        clear() {
            this._$commands = [];
            return this;
        }
        
        beginBitmapFill(bitmapData, matrix, repeat, smooth) {
            this._$commands.push(["beginBitmapFill", bitmapData, matrix, repeat, smooth]);
            return this;
        }
        
        drawRect(x, y, width, height) {
            this._$commands.push(["drawRect", x, y, width, height]);
            return this;
        }
        
        endFill() {
            this._$commands.push(["endFill"]);
            return this;
        }
    }

    // Mock BitmapData class
    class BitmapData {
        constructor(width, height, transparent, fillColor) {
            this._$width = width || 0;
            this._$height = height || 0;
            this._$transparent = transparent !== false;
            this._$fillColor = fillColor || 0xFFFFFFFF;
        }
        
        static get namespace() {
            return "next2d.display.BitmapData";
        }
        
        get width() {
            return this._$width;
        }
        
        get height() {
            return this._$height;
        }
    }

    // Mock MovieClip class
    class MovieClip {
        constructor() {
            this._$loaderInfo = null;
            this._$characterId = 0;
            this._$currentFrame = 1;
            this._$totalFrames = 1;
            this._$graphics = new Graphics();
            this._$scaleX = 1;
            this._$scaleY = 1;
            this._$regX = 0;
            this._$regY = 0;
            this._$x = 0;
            this._$y = 0;
            this._$rotation = 0;
            this._$alpha = 1;
            this._$visible = true;
            this._$blendMode = "normal";
            this._$filters = [];
            this._$matrix = null;
            this._$colorTransform = null;
            this._$labels = [];
            this._$children = [];
        }
        
        static get namespace() {
            return "next2d.display.MovieClip";
        }
        
        get currentFrame() {
            return this._$currentFrame;
        }
        
        get totalFrames() {
            return this._$totalFrames;
        }
        
        get graphics() {
            return this._$graphics;
        }
        
        gotoAndStop(frame) {
            if (typeof frame === "number") {
                this._$currentFrame = frame;
            }
        }
        
        gotoAndPlay(frame) {
            if (typeof frame === "number") {
                this._$currentFrame = frame;
            }
        }
        
        addChild(child) {
            if (!this._$children.includes(child)) {
                this._$children.push(child);
            }
            return child;
        }
        
        removeChild(child) {
            const index = this._$children.indexOf(child);
            if (index > -1) {
                this._$children.splice(index, 1);
            }
            return child;
        }
    }

    // Mock Sprite class
    class Sprite {
        constructor() {
            this._$loaderInfo = null;
            this._$characterId = 0;
            this._$graphics = new Graphics();
            this._$scaleX = 1;
            this._$scaleY = 1;
            this._$regX = 0;
            this._$regY = 0;
            this._$x = 0;
            this._$y = 0;
            this._$rotation = 0;
            this._$alpha = 1;
            this._$visible = true;
            this._$blendMode = "normal";
            this._$filters = [];
            this._$matrix = null;
            this._$colorTransform = null;
            this._$children = [];
        }
        
        static get namespace() {
            return "next2d.display.Sprite";
        }
        
        get graphics() {
            return this._$graphics;
        }
        
        addChild(child) {
            if (!this._$children.includes(child)) {
                this._$children.push(child);
            }
            return child;
        }
        
        removeChild(child) {
            const index = this._$children.indexOf(child);
            if (index > -1) {
                this._$children.splice(index, 1);
            }
            return child;
        }
    }

    // Mock Matrix class
    class Matrix {
        constructor(a, b, c, d, tx, ty) {
            this.a = a !== undefined ? a : 1;
            this.b = b || 0;
            this.c = c || 0;
            this.d = d !== undefined ? d : 1;
            this.tx = tx || 0;
            this.ty = ty || 0;
        }
        
        static get namespace() {
            return "next2d.geom.Matrix";
        }
        
        clone() {
            return new Matrix(this.a, this.b, this.c, this.d, this.tx, this.ty);
        }
        
        identity() {
            this.a = 1;
            this.b = 0;
            this.c = 0;
            this.d = 1;
            this.tx = 0;
            this.ty = 0;
        }
    }

    // Mock ColorTransform class  
    class ColorTransform {
        constructor(redMultiplier, greenMultiplier, blueMultiplier, alphaMultiplier,
                    redOffset, greenOffset, blueOffset, alphaOffset) {
            this.redMultiplier = redMultiplier !== undefined ? redMultiplier : 1;
            this.greenMultiplier = greenMultiplier !== undefined ? greenMultiplier : 1;
            this.blueMultiplier = blueMultiplier !== undefined ? blueMultiplier : 1;
            this.alphaMultiplier = alphaMultiplier !== undefined ? alphaMultiplier : 1;
            this.redOffset = redOffset || 0;
            this.greenOffset = greenOffset || 0;
            this.blueOffset = blueOffset || 0;
            this.alphaOffset = alphaOffset || 0;
        }
        
        static get namespace() {
            return "next2d.geom.ColorTransform";
        }
    }

    // Mock Rectangle class
    class Rectangle {
        constructor(x, y, width, height) {
            this.x = x || 0;
            this.y = y || 0;
            this.width = width || 0;
            this.height = height || 0;
        }
        
        static get namespace() {
            return "next2d.geom.Rectangle";
        }
        
        clone() {
            return new Rectangle(this.x, this.y, this.width, this.height);
        }
    }

    // Mock LoaderInfo class
    class LoaderInfo {
        constructor() {
            this._$data = {};
            this._$width = 0;
            this._$height = 0;
            this._$frameRate = 24;
        }
        
        static get namespace() {
            return "next2d.display.LoaderInfo";
        }
        
        get width() {
            return this._$width;
        }
        
        get height() {
            return this._$height;
        }
        
        get frameRate() {
            return this._$frameRate;
        }
    }

    // Mock Sound class
    class Sound {
        constructor() {
            this._$url = null;
        }
        
        static get namespace() {
            return "next2d.media.Sound";
        }
        
        load(url) {
            this._$url = url;
        }
        
        play() {
            // Mock play - no-op
        }
    }

    // Create window.next2d namespace if it doesn't exist
    if (!window.next2d) {
        window.next2d = {
            display: {
                Shape: Shape,
                Graphics: Graphics,
                BitmapData: BitmapData,
                MovieClip: MovieClip,
                Sprite: Sprite,
                LoaderInfo: LoaderInfo
            },
            geom: {
                Matrix: Matrix,
                ColorTransform: ColorTransform,
                Rectangle: Rectangle
            },
            media: {
                Sound: Sound
            },
            net: {},
            events: {},
            filters: {},
            text: {},
            ui: {}
        };
    }
})();
