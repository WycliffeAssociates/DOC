import type { PlaywrightTestConfig } from '@playwright/test'

const config: PlaywrightTestConfig = {
  testDir: 'tests',
  testMatch: '**/*.ts',
  timeout: 640000, // global test timeout
  use: {
    // headless: false, // so you can see the UI
    slowMo: 100, // slow each action by 100ms
    actionTimeout: 30000, // max time per action (click, check, etc.)
    navigationTimeout: 30000 // max time for page.goto and navigation
  }
}

export default config
