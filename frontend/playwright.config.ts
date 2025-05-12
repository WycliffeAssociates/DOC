import type { PlaywrightTestConfig } from '@playwright/test'

const config: PlaywrightTestConfig = {
    testDir: 'tests',
    testMatch: '**/*.ts',
    timeout: 640000 // Set global timeout 
}

export default config
