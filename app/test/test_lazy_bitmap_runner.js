/**
 * Automated test runner for lazy loading bitmap tests
 * Can be run via Node.js/Puppeteer or in browser
 * Usage: node test_lazy_bitmap_runner.js
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const TEST_REPORT_FILE = path.join(__dirname, '../test-results/lazy-bitmap-test-report.json');
const SERVER_URL = process.env.TEST_SERVER_URL || 'http://127.0.0.1:9876';

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runTests() {
    console.log('='.repeat(70));
    console.log('Lazy Loading Bitmap Unit Test Runner');
    console.log('='.repeat(70));
    
    const browser = await puppeteer.launch({
        headless: process.env.HEADLESS !== 'false',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security'
        ]
    });
    
    const page = await browser.newPage();
    
    // Capture console output
    const consoleMessages = [];
    const errors = [];
    const testResults = {
        total: 0,
        passed: 0,
        failed: 0,
        specs: []
    };
    
    page.on('console', msg => {
        const text = msg.text();
        consoleMessages.push(text);
        
        // Parse test results from console
        if (text.includes('SPEC')) {
            console.log('  ' + text);
        }
        if (text.includes('FAILED') || text.includes('PASSED')) {
            console.log(text);
        }
    });
    
    page.on('pageerror', error => {
        errors.push(error.message);
        console.error('Page Error:', error.message);
    });
    
    try {
        console.log('\n1. Connecting to Karma test server...');
        console.log(`   URL: ${SERVER_URL}`);
        
        await page.goto(SERVER_URL, {
            waitUntil: 'networkidle2',
            timeout: 60000
        });
        
        console.log('2. Waiting for tests to complete...');
        
        // Wait for tests to finish (look for completion message)
        await page.waitForFunction(
            () => {
                const body = document.body.textContent;
                return body.includes('TOTAL:') || body.includes('Finished in');
            },
            { timeout: 120000 }
        );
        
        console.log('3. Tests completed, gathering results...');
        
        // Extract test results
        const results = await page.evaluate(() => {
            const stats = {
                total: 0,
                passed: 0,
                failed: 0,
                suites: []
            };
            
            // Try to get Karma results from window
            if (window.__karma__ && window.__karma__.result) {
                const karmaResult = window.__karma__.result;
                return {
                    total: karmaResult.total || 0,
                    passed: karmaResult.success || 0,
                    failed: karmaResult.failed || 0,
                    error: karmaResult.error || false
                };
            }
            
            // Fallback: parse from DOM
            const summaryElement = document.querySelector('.summary');
            if (summaryElement) {
                const text = summaryElement.textContent;
                const passedMatch = text.match(/(\d+) passed/);
                const failedMatch = text.match(/(\d+) failed/);
                
                if (passedMatch) stats.passed = parseInt(passedMatch[1]);
                if (failedMatch) stats.failed = parseInt(failedMatch[1]);
                stats.total = stats.passed + stats.failed;
            }
            
            return stats;
        });
        
        Object.assign(testResults, results);
        
        console.log('\n' + '='.repeat(70));
        console.log('TEST RESULTS SUMMARY');
        console.log('='.repeat(70));
        console.log(`Total Tests:  ${testResults.total}`);
        console.log(`Passed:       ${testResults.passed} ✓`);
        console.log(`Failed:       ${testResults.failed} ✗`);
        console.log('='.repeat(70));
        
        // Save detailed report
        const report = {
            timestamp: new Date().toISOString(),
            results: testResults,
            errors: errors,
            consoleLog: consoleMessages.slice(-100) // Last 100 messages
        };
        
        // Ensure directory exists
        const reportDir = path.dirname(TEST_REPORT_FILE);
        if (!fs.existsSync(reportDir)) {
            fs.mkdirSync(reportDir, { recursive: true });
        }
        
        fs.writeFileSync(TEST_REPORT_FILE, JSON.stringify(report, null, 2));
        console.log(`\nDetailed report saved to: ${TEST_REPORT_FILE}`);
        
        // Exit with appropriate code
        const exitCode = testResults.failed > 0 ? 1 : 0;
        
        await browser.close();
        
        return exitCode;
        
    } catch (error) {
        console.error('\nTest Runner Error:', error);
        await browser.close();
        return 1;
    }
}

// Run if called directly
if (require.main === module) {
    runTests().then(exitCode => {
        process.exit(exitCode);
    }).catch(err => {
        console.error('Fatal error:', err);
        process.exit(1);
    });
}

module.exports = { runTests };
