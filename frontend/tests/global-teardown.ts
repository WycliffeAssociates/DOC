import type { FullConfig } from '@playwright/test'

async function globalTeardown(config: FullConfig) {
  // Allow reporters to flush stdout
  await new Promise((resolve) => setTimeout(resolve, 500))
  // Force-terminate the Node runner process so Docker exits cleanly
  if (process.env.CI) {
    process.exit(0)
  }
}

export default globalTeardown
