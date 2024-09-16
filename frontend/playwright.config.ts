import type { PlaywrightTestConfig } from '@playwright/test'

const config: PlaywrightTestConfig = {
    testDir: 'tests',
    testMatch: '**/*.ts',
    timeout: 120000 // Set global timeout to 2 minutes
}

export default config
