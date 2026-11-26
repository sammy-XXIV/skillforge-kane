const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests', testMatch: '**/browser.spec.cjs',
  retries: 0, reporter: [['list'], ['html', { open: 'never' }]],
  use: { baseURL: 'http://127.0.0.1:4173', trace: 'retain-on-failure',
    screenshot: 'only-on-failure', video: 'retain-on-failure' },
  webServer: { command: 'python3 demo/serve.py', url: 'http://127.0.0.1:4173',
    reuseExistingServer: false },
});
