import type { PlaywrightTestConfig } from '@playwright/test'
import { fileURLToPath } from 'node:url'

const config: PlaywrightTestConfig = {
  testDir: 'tests',
  testMatch: '**/*.ts',

  // Safely parallelize across 50% of available CPU cores in CI environments
  workers: process.env.CI ? '50%' : undefined,

  globalTimeout: process.env.CI ? 30 * 60 * 1000 : undefined, // 30 min suite cap

  // ESM-compatible global teardown path
  globalTeardown: fileURLToPath(new URL('./tests/global-teardown.ts', import.meta.url)),

  timeout: 60000,

  expect: {
    // Assertion timeout separate from test timeout
    timeout: 15000
  },

  use: {
    // Navigation/action timeout — how long Playwright waits for a single action
    actionTimeout: 30000,
    navigationTimeout: 30000
  }
}

export default config
