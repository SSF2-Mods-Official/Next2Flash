/**
 * Canvas Validation Utilities
 * Helper functions to validate canvas and bitmap data before using in drawImage
 * 
 * These utilities prevent the error:
 * "TypeError: Failed to execute 'drawImage' on 'CanvasRenderingContext2D': 
 *  The provided value is not of type '(CSSImageValue or HTMLCanvasElement or ...)'"
 */

(function(window) {
    'use strict';

    const CanvasValidator = {
        /**
         * Check if a canvas element is valid and drawable
         * @param {*} canvas - The canvas to validate
         * @returns {boolean} True if canvas is valid for drawImage
         */
        isCanvasDrawable: function(canvas) {
            if (!canvas) {
                return false;
            }
            
            if (!(canvas instanceof HTMLCanvasElement)) {
                return false;
            }
            
            if (canvas.width <= 0 || canvas.height <= 0) {
                return false;
            }
            
            // Verify we can get a context (canvas might be invalid/corrupted)
            try {
                const ctx = canvas.getContext('2d');
                if (!ctx) {
                    return false;
                }
            } catch (e) {
                return false;
            }
            
            return true;
        },

        /**
         * Check if an image element is valid and drawable
         * @param {*} image - The image to validate
         * @returns {boolean} True if image is valid for drawImage
         */
        isImageDrawable: function(image) {
            if (!image) {
                return false;
            }
            
            // Check valid image types
            const validTypes = [
                HTMLImageElement,
                HTMLCanvasElement,
                HTMLVideoElement,
                ImageBitmap
            ];
            
            // Check if OffscreenCanvas exists (not in all browsers)
            if (typeof OffscreenCanvas !== 'undefined') {
                validTypes.push(OffscreenCanvas);
            }
            
            const isValidType = validTypes.some(type => image instanceof type);
            if (!isValidType) {
                return false;
            }
            
            // For images, check if loaded
            if (image instanceof HTMLImageElement) {
                if (!image.complete || !image.naturalWidth) {
                    return false;
                }
            }
            
            // Check dimensions
            const width = image.width || image.videoWidth || 0;
            const height = image.height || image.videoHeight || 0;
            
            if (width <= 0 || height <= 0) {
                return false;
            }
            
            return true;
        },

        /**
         * Validate BitmapData object from Next2D
         * @param {*} bitmapData - Next2D BitmapData instance
         * @returns {Object} Validation result with status and drawable source
         */
        validateBitmapData: function(bitmapData) {
            const result = {
                valid: false,
                source: null,
                reason: null
            };
            
            if (!bitmapData) {
                result.reason = 'bitmapData is null/undefined';
                return result;
            }
            
            // Check for Next2D BitmapData namespace
            const { BitmapData } = window.next2d && window.next2d.display || {};
            if (BitmapData && bitmapData.namespace !== BitmapData.namespace) {
                result.reason = 'not a BitmapData instance';
                return result;
            }
            
            // Try _$canvas first (internal property)
            if (bitmapData._$canvas && this.isCanvasDrawable(bitmapData._$canvas)) {
                result.valid = true;
                result.source = bitmapData._$canvas;
                return result;
            }
            
            // Try public canvas property
            if (bitmapData.canvas && this.isCanvasDrawable(bitmapData.canvas)) {
                result.valid = true;
                result.source = bitmapData.canvas;
                return result;
            }
            
            // Try _$image property
            if (bitmapData._$image && this.isImageDrawable(bitmapData._$image)) {
                result.valid = true;
                result.source = bitmapData._$image;
                return result;
            }
            
            // Check if has buffer but no canvas
            if (bitmapData._$buffer && bitmapData._$buffer.length > 0) {
                result.reason = 'has buffer but no valid canvas';
                return result;
            }
            
            result.reason = 'no valid drawable source found';
            return result;
        },

        /**
         * Safe wrapper for drawImage that validates source first
         * @param {CanvasRenderingContext2D} ctx - Canvas context
         * @param {*} source - Image source to draw
         * @param {...number} args - drawImage arguments (sx, sy, sw, sh, dx, dy, dw, dh)
         * @returns {boolean} True if draw succeeded, false if skipped
         */
        safeDrawImage: function(ctx, source, ...args) {
            if (!ctx || !ctx.drawImage) {
                console.warn('[CanvasValidator] Invalid context provided to safeDrawImage');
                return false;
            }
            
            // Handle BitmapData objects
            const { BitmapData } = window.next2d && window.next2d.display || {};
            if (BitmapData && source && source.namespace === BitmapData.namespace) {
                const validation = this.validateBitmapData(source);
                if (!validation.valid) {
                    console.warn('[CanvasValidator] BitmapData validation failed:', validation.reason);
                    return false;
                }
                source = validation.source;
            }
            
            // Validate source is drawable
            if (!this.isImageDrawable(source)) {
                console.warn('[CanvasValidator] Source is not drawable:', source);
                return false;
            }
            
            // Try to draw
            try {
                ctx.drawImage(source, ...args);
                return true;
            } catch (e) {
                console.error('[CanvasValidator] drawImage failed:', e.message);
                return false;
            }
        },

        /**
         * Create a placeholder canvas for invalid/loading bitmaps
         * @param {number} width - Canvas width
         * @param {number} height - Canvas height
         * @param {string} [color='#808080'] - Placeholder color
         * @returns {HTMLCanvasElement} Placeholder canvas
         */
        createPlaceholder: function(width, height, color = '#808080') {
            const canvas = document.createElement('canvas');
            canvas.width = Math.max(1, width || 1);
            canvas.height = Math.max(1, height || 1);
            
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillStyle = color;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw diagonal lines to indicate placeholder
                ctx.strokeStyle = '#404040';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(canvas.width, canvas.height);
                ctx.moveTo(canvas.width, 0);
                ctx.lineTo(0, canvas.height);
                ctx.stroke();
            }
            
            return canvas;
        },

        /**
         * Validate buffer data matches expected dimensions
         * @param {Uint8Array} buffer - RGBA buffer
         * @param {number} width - Expected width
         * @param {number} height - Expected height
         * @returns {boolean} True if buffer size matches dimensions
         */
        validateBufferSize: function(buffer, width, height) {
            if (!buffer || !(buffer instanceof Uint8Array)) {
                return false;
            }
            
            const expectedSize = width * height * 4; // RGBA
            return buffer.length === expectedSize;
        },

        /**
         * Create canvas from RGBA buffer
         * @param {Uint8Array} buffer - RGBA buffer
         * @param {number} width - Canvas width
         * @param {number} height - Canvas height
         * @returns {HTMLCanvasElement|null} Canvas or null if failed
         */
        createCanvasFromBuffer: function(buffer, width, height) {
            if (!this.validateBufferSize(buffer, width, height)) {
                console.warn('[CanvasValidator] Invalid buffer size for dimensions');
                return null;
            }
            
            if (width <= 0 || height <= 0) {
                console.warn('[CanvasValidator] Invalid dimensions:', width, height);
                return null;
            }
            
            try {
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                if (!ctx) {
                    return null;
                }
                
                const imageData = ctx.createImageData(width, height);
                imageData.data.set(buffer);
                ctx.putImageData(imageData, 0, 0);
                
                return canvas;
            } catch (e) {
                console.error('[CanvasValidator] Failed to create canvas from buffer:', e);
                return null;
            }
        }
    };

    // Export to window
    window.CanvasValidator = CanvasValidator;

    // Also expose via Next2D namespace if available
    if (window.next2d && window.next2d.utils) {
        window.next2d.utils.CanvasValidator = CanvasValidator;
    }

})(typeof window !== 'undefined' ? window : {});
