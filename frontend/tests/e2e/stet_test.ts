import { expect, test } from '@playwright/test'

// Group tests with specific settings
test.describe('Desktop Tests', () => {
  test.use({
    viewport: {
      height: 700,
      width: 1200
    }
  })

  test('stet', async ({ page }) => {
    await page.goto('http://localhost:8001/stet')
    await page.getByLabel('English en').check()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByText('Cebuano').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Generate File' }).click()
  })

  test('french stet', async ({ page }) => {
    await page.goto('http://localhost:8001/stet')
    await page.getByText('Français (French)').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByText('Cebuano ceb').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Generate File' }).click()
  })

  test('search by language code', async ({ page }) => {
    await page.goto('http://localhost:8001/stet')
    await page.getByText('Português Brasileiro (').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Heart' }).click()
    await page.getByPlaceholder('Search Heart Languages').click()
    await page.getByPlaceholder('Search Heart Languages').fill('sxw')
    await page.getByText('Sègbé').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await expect(page.locator('body')).toContainText('Sègbé(sxw-x-segbe)')
  })

  test('next then back and edit', async ({ page }) => {
    await page.goto('http://localhost:8001/stet')
    await page.getByText('English').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Back' }).click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByText('Bichelamar (Bislama)').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('link', { name: 'Target Language' }).click()
    await page.getByRole('link', { name: 'Source Language' }).click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Back' }).click()
    await page.getByRole('button', { name: 'Back' }).click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Edit' }).click()
    await page.getByRole('button', { name: 'Edit' }).click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByLabel('Email me a copy of my').check()
    await page.getByPlaceholder('Type email address here (').click()
    await page.getByPlaceholder('Type email address here (').fill('fake@example.com')
    await page.getByRole('button', { name: 'Submit' }).click()
    await page.getByRole('button', { name: 'Generate File' }).click()
  })

  test('tok pisin input language', async ({ page }) => {
    await page.goto('http://localhost:8001/stet')
    await page.getByText('Tok Pisin').click()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByLabel('English en').check()
    await page.getByRole('button', { name: 'Next' }).click()
    await page.getByRole('button', { name: 'Generate File' }).click()
  })

  test('stet passages available when not in production', async ({ page }) => {
    // log every request to the backend endpoint
    page.on('request', (req) => {
      if (req.url().includes('/stet/source_languages')) {
        console.log('Request headers:', req.headers())
      }
    })
    // add console output to test output
    page.on('console', (msg) => {
      console.log('PAGE LOG:', msg.text())
    })
    // mock header for test
    await page.route('**/stet/source_languages', (route) => {
      const headers = {
        ...route.request().headers(),
        'x-is-production': 'false'
      }
      route.continue({ headers })
    })
    await page.goto('http://localhost:8001/stet')
    await expect(page.getByText('English')).toBeVisible({ timeout: 32_000 })
    await expect(page.getByText('Tok Pisin')).toBeVisible({ timeout: 32_000 })
  })

  test('stet input docs available in production should be limited to those with 4th column', async ({
    page
  }) => {
    // log every request to the backend endpoint
    page.on('request', (req) => {
      if (req.url().includes('/stet/source_languages')) {
        console.log('Request headers:', req.headers())
      }
    })
    // add console output to test output
    page.on('console', (msg) => {
      console.log('PAGE LOG:', msg.text())
    })
    // mock header for test
    await page.route('**/stet/source_languages', (route) => {
      const headers = {
        ...route.request().headers(),
        'x-is-production': 'true'
      }
      route.continue({ headers })
    })
    await page.goto('http://localhost:8001/stet')
    await expect(page.getByText('English')).toBeVisible({ timeout: 32_000 })
    await expect(page.getByText('Tok Pisin')).not.toBeVisible({ timeout: 32_000 })
  })
})

// Separate group for mobile tests
test.describe('Mobile Tests', () => {
  test.use({
    viewport: {
      height: 600,
      width: 300
    }
  })

  test('mobile', async ({ page }) => {
    await page.goto('http://localhost:8001/stet')
    await page.getByLabel('English en').check()
    await page.getByRole('button').nth(1).click()
    await page.getByText('Bahasa Indonesia (Indonesian)').click()
    await page.getByRole('button').nth(1).click()
    await page.getByRole('button', { name: '2' }).click()
    await page.getByRole('button', { name: 'Edit' }).nth(1).click()
    await page.getByRole('button').nth(1).click()
    await page.getByRole('button', { name: 'Generate File' }).click()
  })

  test('mobile 2', async ({ page }) => {
    await page.goto('http://localhost:8001/stet')
    await page.getByText('English').click()
    await page.getByRole('button').nth(1).click()
    await page.getByRole('button').first().click()
    await page.getByRole('button').nth(1).click()
    await page.getByRole('button').nth(2).click()
    await page.getByText('Heart languages').click()
    await page.getByRole('button', { name: 'Close' }).click()
    await page.getByText('Abé').click()
    await page.getByRole('button').nth(1).click()
    await page.getByRole('button').first().click()
    // await expect(page.getByLabel('Abé aba')).toBeChecked({ timeout: 1200000 })
  })
})
