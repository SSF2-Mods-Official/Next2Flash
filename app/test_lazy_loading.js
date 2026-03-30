/**
 * Test script to verify lazy loading works without getTexture errors
 * Requires: npm install puppeteer
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const SERVER_URL = 'http://127.0.0.1:5000';
const TEST_FILE = 'C:\\Users\\glwex\\Documents\\GitHub\\ssf2-idk-140x-original\\src\\Super Smash Flash 2 Beta v1.4.0.1\\data\\misc\\ssf2intro_beta.ssf';

// Helper function for delays
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function testLazyLoading() {
    console.log('Starting lazy loading test...');
    
    const browser = await puppeteer.launch({
        headless: false, // Show browser for debugging
        args: ['--disable-web-security'] // Allow cross-origin requests
    });
    
    const page = await browser.newPage();
    
    // Track console messages and errors
    const consoleMessages = [];
    const errors = [];
    
    page.on('console', msg => {
        const text = msg.text();
        consoleMessages.push(text);
        
        // Check for the specific errors we're looking for
        if (text.includes('getTexture is not a function')) {
            errors.push({ type: 'getTexture', text });
        }
        if (text.includes('drawImage') && text.includes('TypeError')) {
            errors.push({ type: 'drawImage', text });
        }
        
        // Log LAZY messages
        if (text.includes('[LAZY]')) {
            console.log('  ' + text);
        }
    });
    
    page.on('pageerror', error => {
        errors.push({ type: 'pageerror', text: error.message });
        console.error('Page error:', error.message);
    });
    
    try {
        console.log('\n1. Loading editor page...');
        await page.goto(SERVER_URL, { waitUntil: 'networkidle2', timeout: 30000 });
        
        console.log('2. Waiting for editor to initialize...');
        await delay(2000);
        
        console.log('3. Reading test file...');
        if (!fs.existsSync(TEST_FILE)) {
            throw new Error(`Test file not found: ${TEST_FILE}`);
        }
        const fileBuffer = fs.readFileSync(TEST_FILE);
        console.log(`   File size: ${fileBuffer.length} bytes`);
        
        console.log('4. Calling fast import API...');
        const response = await fetch(`${SERVER_URL}/api/swf-to-project-fast`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/octet-stream'
            },
            body: fileBuffer
        });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }
        
        const n2dData = await response.arrayBuffer();
        console.log(`   Response size: ${n2dData.byteLength} bytes`);
        
        console.log('5. Feeding N2D to editor...');
        await page.evaluate((n2dBytes) => {
            // Convert ArrayBuffer to Blob
            const blob = new Blob([n2dBytes], { type: 'application/octet-stream' });
            
            // Call the integration function if it exists
            if (window._feedN2DToTool) {
                window._feedN2DToTool(blob, 'bomberman');
            } else {
                console.error('_feedN2DToTool not found');
            }
        }, Array.from(new Uint8Array(n2dData)));
        
        console.log('6. Waiting for lazy loading to complete...');
        await delay(15000); // Wait for assets to load (longer for large file)
        
        // Check lazy stats
        const stats = await page.evaluate(() => {
            return window.__N2F_LAZY_STATS__;
        });
        
        console.log('\n7. Lazy loading stats:', stats);
        
        // Wait a bit more to catch any delayed errors
        await delay(5000);
        
        console.log('\n8. Results:');
        console.log('   Total console messages:', consoleMessages.length);
        console.log('   Error count:', errors.length);
        
        if (errors.length > 0) {
            console.log('\n   ❌ ERRORS FOUND:');
            errors.forEach((err, i) => {
                console.log(`      ${i + 1}. [${err.type}] ${err.text.substring(0, 100)}...`);
            });
        } else {
            console.log('   ✅ No getTexture or drawImage errors detected!');
        }
        
        // Check for specific error types
        const getTextureErrors = errors.filter(e => e.type === 'getTexture');
        const drawImageErrors = errors.filter(e => e.type === 'drawImage');
        
        console.log(`\n   getTexture errors: ${getTextureErrors.length}`);
        console.log(`   drawImage errors: ${drawImageErrors.length}`);
        
        // Final verdict
        if (getTextureErrors.length === 0 && drawImageErrors.length === 0) {
            console.log('\n✅ TEST PASSED: Lazy loading works without crashes!');
            return true;
        } else {
            console.log('\n❌ TEST FAILED: Errors detected during lazy loading');
            return false;
        }
        
    } catch (error) {
        console.error('Test error:', error);
        return false;
    } finally {
        console.log('\nClosing browser in 5 seconds...');
        await delay(5000);
        await browser.close();
    }
}

// Run the test
testLazyLoading()
    .then(success => {
        process.exit(success ? 0 : 1);
    })
    .catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
