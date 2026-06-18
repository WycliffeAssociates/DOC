import { expect, test } from '@playwright/test'

test('languages are sorted in clicked order', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Français (French)').click()
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.locator('.w-full > div:nth-child(3)')).toContainText('Français (French)')
  await expect(page.locator('.w-full > div:nth-child(4)')).toContainText('Cebuano')
  await page.getByText('Matthieu').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible ulb').first().click()
  await page.getByText('Unlocked Literal Bible').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  const viewHtmlButton = page.getByRole('button', { name: 'View HTML Online' })
  await viewHtmlButton.waitFor({ state: 'visible' })
  // Start waiting for the popup BEFORE clicking
  const page1Promise = page.waitForEvent('popup')
  // Click to trigger the popup
  await viewHtmlButton.click()
  // Get the new popup page
  const page1 = await page1Promise
  // French was clicked before Cebuano and we see this order is
  // retained into the resulting document.
  await expect(page1.locator('body')).toContainText(
    'French (Français): Unlocked Literal Bible for Matthieu Cebuano (Cebuano): Unlocked Literal Bible for Mateo'
  )
})

test('use prince with lots of books', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByPlaceholder('Search Gateway Languages').click()
  await page.getByPlaceholder('Search Gateway Languages').fill('tpi')
  await page.getByText('Tok Pisin').click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Heart Languages').click()
  await page.getByPlaceholder('Search Heart Languages').fill('ont')
  await page.getByText('Ontenu').click()
  await expect(page.getByRole('button', { name: 'Next' })).toBeEnabled({ timeout: 15_000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').click()
  await page.getByRole('button', { name: 'Old Testament' }).click()
  await page.getByRole('button', { name: 'New Testament' }).click()
  await expect(page.getByRole('button', { name: 'Next' })).toBeEnabled({ timeout: 15_000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').first().click({ timeout: 120_000 })
  await page.getByText('Regular').click({ timeout: 30_000 })
  await expect(page.getByRole('button', { name: 'Next' })).toBeEnabled({ timeout: 60_000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Interleave content by chapter').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('acq', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Heart Languages').click()
  await page.getByPlaceholder('Search Heart Languages').fill('acq')
  await page.getByText('لهجة تعزية-عدنية (Arabic, Ta’').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Regular').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
  await page.getByRole('button', { name: 'Generate File' }).click()
})
