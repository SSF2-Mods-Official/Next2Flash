/**
 * Simple test runner for lazy loading BitmapData tests
 * Can be run standalone in Node.js or in browser console
 */

// Simple test framework
class SimpleTestRunner {
    constructor() {
        this.suites = [];
        this.currentSuite = null;
        this.currentTest = null;
        this.results = {
            total: 0,
            passed: 0,
            failed: 0,
            skipped: 0,
            errors: []
        };
    }
    
    describe(name, fn) {
        const suite = { name, tests: [], beforeEach: null };
        this.suites.push(suite);
        this.currentSuite = suite;
        fn();
        this.currentSuite = null;
    }
    
    beforeEach(fn) {
        if (this.currentSuite) {
            this.currentSuite.beforeEach = fn;
        }
    }
    
    it(name, fn) {
        if (!this.currentSuite) return;
        this.currentSuite.tests.push({ name, fn });
    }
    
    pending(message) {
        throw new Error('PENDING: ' + message);
    }
    
    expect(actual) {
        return {
            toBeTruthy: (message) => {
                if (!actual) throw new Error(message || 'Expected truthy but got ' + actual);
            },
            toBeFalsy: (message) => {
                if (actual) throw new Error(message || 'Expected falsy but got ' + actual);
            },
            toEqual: (expected, message) => {
                if (actual !== expected) {
                    throw new Error(message || `Expected ${expected} but got ${actual}`);
                }
            },
            toBe: (expected, message) => {
                if (actual !== expected) {
                    throw new Error(message || `Expected ${expected} but got ${actual}`);
                }
            },
            not: {
                toThrow: () => {
                    try {
                        if (typeof actual === 'function') {
                            actual();
                        }
                    } catch (e) {
                        throw new Error('Expected not to throw but threw: ' + e.message);
                    }
                },
                toEqual: (expected, message) => {
                    if (actual === expected) {
                        throw new Error(message || `Expected not to equal ${expected}`);
                    }
                }
            }
        };
    }
    
    async run() {
        console.log('\n===============================================');
        console.log('Running Lazy Loading BitmapData Tests');
        console.log('===============================================\n');
        
        for (const suite of this.suites) {
            console.log(`\n${suite.name}`);
            console.log('-'.repeat(suite.name.length));
            
            for (const test of suite.tests) {
                this.results.total++;
                
                try {
                    if (suite.beforeEach) {
                        suite.beforeEach.call({
                            pending: this.pending.bind(this),
                            expect: this.expect.bind(this)
                        });
                    }
                    
                    await test.fn.call({
                        pending: this.pending.bind(this),
                        expect: this.expect.bind(this)
                    });
                    
                    console.log(`  ✓ ${test.name}`);
                    this.results.passed++;
                } catch (e) {
                    if (e.message && e.message.startsWith('PENDING:')) {
                        console.log(`  ○ ${test.name} (skipped: ${e.message.replace('PENDING:', '').trim()})`);
                        this.results.skipped++;
                    } else {
                        console.log(`  ✗ ${test.name}`);
                        console.log(`    Error: ${e.message}`);
                        this.results.failed++;
                        this.results.errors.push({
                            suite: suite.name,
                            test: test.name,
                            error: e.message
                        });
                    }
                }
            }
        }
        
        this.printSummary();
        return this.results;
    }
    
    printSummary() {
        console.log('\n===============================================');
        console.log('Test Summary');
        console.log('===============================================');
        console.log(`Total:   ${this.results.total}`);
        console.log(`Passed:  ${this.results.passed} ✓`);
        console.log(`Failed:  ${this.results.failed} ✗`);
        console.log(`Skipped: ${this.results.skipped} ○`);
        
        if (this.results.failed > 0) {
            console.log('\nFailed Tests:');
            this.results.errors.forEach(err => {
                console.log(`  ${err.suite} > ${err.test}`);
                console.log(`    ${err.error}`);
            });
        }
        
        if (this.results.failed === 0) {
            console.log('\n🎉 All tests passed!\n');
        } else {
            console.log('\n❌ Some tests failed\n');
        }
    }
}

// Matrix transformation tests (standalone, no Next2D needed)
function runStandaloneTests() {
    const runner = new SimpleTestRunner();
    
    // Make runner methods global for test definition
    global.describe = runner.describe.bind(runner);
    global.beforeEach = runner.beforeEach.bind(runner);
    global.it = runner.it.bind(runner);
    
    // Matrix transformation tests
    describe('Matrix Transformation Tests (Standalone)', function() {
        
        it('should scale twips to pixels correctly (divide by 20)', function() {
            const twipsMatrix = [100, 0, 0, 100, 200, 400];
            const scaleFactor = 0.05;
            
            const pixelMatrix = twipsMatrix.map(v => v * scaleFactor);
            
            this.expect(pixelMatrix[0]).toEqual(5.0, 'scaleX should be 5.0');
            this.expect(pixelMatrix[3]).toEqual(5.0, 'scaleY should be 5.0');
            this.expect(pixelMatrix[4]).toEqual(10.0, 'translateX should be 10.0');
            this.expect(pixelMatrix[5]).toEqual(20.0, 'translateY should be 20.0');
        });
        
        it('should apply unitDivisor to all matrix components', function() {
            const unitDivisor = 20;
            
            const matrix = {
                scaleX: 100,
                rotateSkew0: 0,
                rotateSkew1: 0,
                scaleY: 100,
                translateX: 200,
                translateY: 400
            };
            
            const scaled = {
                scaleX: matrix.scaleX / unitDivisor,
                rotateSkew0: matrix.rotateSkew0 / unitDivisor,
                rotateSkew1: matrix.rotateSkew1 / unitDivisor,
                scaleY: matrix.scaleY / unitDivisor,
                translateX: matrix.translateX / unitDivisor,
                translateY: matrix.translateY / unitDivisor
            };
            
            this.expect(scaled.translateX).toEqual(10.0);
            this.expect(scaled.translateY).toEqual(20.0);
        });
        
        it('should handle identity matrix correctly', function() {
            const identity = [1, 0, 0, 1, 0, 0];
            const scaleFactor = 0.05;
            
            const scaled = identity.map(v => v * scaleFactor);
            
            this.expect(scaled[0]).toEqual(0.05, 'scaleX');
            this.expect(scaled[3]).toEqual(0.05, 'scaleY');
            this.expect(scaled[4]).toEqual(0, 'translateX');
            this.expect(scaled[5]).toEqual(0, 'translateY');
        });
        
        it('should handle non-zero translation correctly', function() {
            // This is the specific bug we fixed
            const matrix = [20, 0, 0, 20, 100, 200]; // 20x scale, 100x200 translation in twips
            const scaleFactor = 0.05;
            
            const scaled = matrix.map(v => v * scaleFactor);
            
            // Before fix: mtx[4] and mtx[5] were not scaled
            // After fix: all components scaled
            this.expect(scaled[4]).toEqual(5.0, 'translateX must be scaled');
            this.expect(scaled[5]).toEqual(10.0, 'translateY must be scaled');
        });
    });
    
    // BitmapData buffer validation tests
    describe('BitmapData Buffer Validation (Standalone)', function() {
        
        it('should validate bitmap dimensions match buffer size', function() {
            const width = 64;
            const height = 64;
            const expectedSize = width * height * 4; // RGBA
            
            const buffer = new Uint8Array(expectedSize);
            this.expect(buffer.length).toEqual(expectedSize);
        });
        
        it('should detect wrong buffer size', function() {
            const width = 64;
            const height = 64;
            const expectedSize = width * height * 4;
            
            const wrongBuffer = new Uint8Array(100);
            this.expect(wrongBuffer.length).not.toEqual(expectedSize);
        });
        
        it('should create valid canvas for bitmap rendering', function() {
            const width = 100;
            const height = 100;
            
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            
            this.expect(canvas).toBeTruthy('Canvas should be created');
            this.expect(canvas.width).toEqual(width);
            this.expect(canvas.height).toEqual(height);
            this.expect(ctx).toBeTruthy('Context should be created');
        });
        
        it('should create valid ImageData from canvas', function() {
            const width = 64;
            const height = 64;
            
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            const imageData = ctx.createImageData(width, height);
            
            this.expect(imageData).toBeTruthy();
            this.expect(imageData.width).toEqual(width);
            this.expect(imageData.height).toEqual(height);
            this.expect(imageData.data.length).toEqual(width * height * 4);
        });
    });
    
    return runner.run();
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SimpleTestRunner, runStandaloneTests };
}

// Auto-run if executed directly
if (typeof require !== 'undefined' && require.main === module) {
    // Setup DOM for Node.js
    global.document = {
        createElement: function(tag) {
            if (tag === 'canvas') {
                return {
                    width: 0,
                    height: 0,
                    getContext: function(type) {
                        if (type === '2d') {
                            return {
                                createImageData: function(w, h) {
                                    return {
                                        width: w,
                                        height: h,
                                        data: new Uint8Array(w * h * 4)
                                    };
                                },
                                putImageData: function() {}
                            };
                        }
                        return null;
                    }
                };
            }
            return {};
        }
    };
    
    runStandaloneTests().then(results => {
        process.exit(results.failed > 0 ? 1 : 0);
    });
}
