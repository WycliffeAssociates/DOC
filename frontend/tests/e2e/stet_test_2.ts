import { expect, test } from '@playwright/test'

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
