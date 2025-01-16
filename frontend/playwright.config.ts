import type { PlaywrightTestConfig } from '@playwright/test'

const config: PlaywrightTestConfig = {
    testDir: 'tests',
    testMatch: '**/*.ts',
    timeout: 240000 // Set global timeout to 4 minutes
}

export default config
