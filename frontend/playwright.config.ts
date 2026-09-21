import type { PlaywrightTestConfig } from '@playwright/test'
import { fileURLToPath } from 'node:url'

const config: PlaywrightTestConfig = {
  testDir: 'tests',
  testMatch: '**/*.ts',

  // Safely parallelize across 50% of available CPU cores in CI environments
  workers: process.env.CI ? '50%' : undefined,

  // ESM-compatible global teardown path
  globalTeardown: fileURLToPath(new URL('./tests/global-teardown.ts', import.meta.url)),
  timeout: 380000 // 6.3 minutes per test; e2e tests can take a long time
}

export default config
