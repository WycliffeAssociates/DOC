import { test, expect } from '@playwright/test'

test('add passages', async ({ page }) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByText('Español Latin America (Latin').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Bible Book').selectOption('jos')
  await page.getByLabel('Chapter').selectOption('7')
  await page.getByPlaceholder('e.g., 1,2,5-').click()
  await page.getByPlaceholder('e.g., 1,2,5-').fill('1-10')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await page.getByLabel('Bible Book').selectOption('est')
  await page.getByLabel('Chapter').selectOption('7')
  await page.getByPlaceholder('e.g., 1,2,5-').click()
  await page.getByPlaceholder('e.g., 1,2,5-').fill('3,12')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await page.getByLabel('Bible Book').selectOption('1th')
  await page.getByLabel('Chapter').selectOption('4')
  await page.getByPlaceholder('e.g., 1,2,5-').click()
  await page.getByPlaceholder('e.g., 1,2,5-').fill('1,5-8,11')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('select gateway tab after first selecting heart language and hitting next', async ({
  page
}) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByText('Abure abu').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('link', { name: 'Language' }).click()
  await page.getByRole('button', { name: 'Gateway' }).click()
  await page.getByText('Bahasa Indonesia (Indonesian)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText("Add NT Survey Reviewers'").click()
  await expect(page.getByText('Matius 2:1-12')).toBeVisible({ timeout: 32000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByText('Matius 2:1-12')).toBeVisible()
})

test('stet passages not available in production', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, 'location', {
      value: {
        ...window.location,
        hostname: 'bibleineverylanguage.org'
      },
      configurable: true
    })
  })
  await page.goto('http://localhost:8001/passages')
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.locator('#stet-passages')).not.toBeVisible()
})

test('stet passages available when not in production', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, 'location', {
      value: {
        ...window.location,
        hostname: 'walink.org'
      },
      configurable: true
    })
  })
  await page.goto('http://localhost:8001/passages')
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  // Wait for the element that proves loading is done
  await page.waitForSelector('#stet-passages', { state: 'visible' })
  await expect(page.locator('#stet-passages')).toBeVisible()
})

test('passages checkboxes', async ({ page }) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByText('English').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Add OT Survey RG1 Passages').check()
  await expect(page.locator('body')).toContainText('Genesis 1:1-2', { timeout: 32_000 })
  await page.getByLabel('Add OT Survey RG1 Passages').uncheck()
  await expect(page.locator('body')).not.toContainText('Genesis 1:1-2')
  await page.getByLabel('Add OT Survey RG2 Passages').check()
  await expect(page.locator('body')).toContainText('Joshua 1:1-9', { timeout: 32_000 })
  await page.getByLabel('Add OT Survey RG2 Passages').uncheck()
  await expect(page.locator('body')).not.toContainText('Joshua 1:1-9', { timeout: 32_000 })
  await page.getByLabel('Add OT Survey RG3 Passages').check()
  await expect(page.locator('body')).toContainText('Job 1:6-22')
  await page.getByLabel('Add OT Survey RG3 Passages').uncheck()
  await expect(page.locator('body')).not.toContainText('Job 1:6-22')
  await page.getByLabel('Add OT Survey RG4 Passages').check()
  await expect(page.locator('body')).toContainText('Isaiah 1:1-9', { timeout: 32_000 })
  await page.getByLabel('Add OT Survey RG4 Passages').uncheck()
  await expect(page.locator('body')).not.toContainText('Isaiah 1:1-9', { timeout: 32_000 })
  await page.getByLabel("Add NT Survey Reviewers'").check()
  await expect(page.locator('body')).toContainText('Matthew 2:1-12', { timeout: 32_000 })
  await page.getByLabel("Add NT Survey Reviewers'").uncheck()
  await expect(page.locator('body')).not.toContainText('Matthew 2:1-12', { timeout: 32_000 })
  await page.getByLabel('Add STET Passages').check()
  await expect(page.locator('body')).toContainText('Matthew 1:1', { timeout: 32_000 })
  await page.getByLabel('Add STET Passages').uncheck()
  await expect(page.locator('body')).not.toContainText('Matthew 1:1', { timeout: 32_000 })
  await page.getByLabel('Add all OT RG Passages').check()
  await expect(page.locator('body')).toContainText('Genesis 1:1-2', { timeout: 32_000 })
  await page.getByLabel('Add all OT RG Passages').uncheck()
  await expect(page.locator('body')).not.toContainText('Genesis 1:1-2', { timeout: 32_000 })
  await page.getByLabel('Bible Book').selectOption('lev')
  await page.getByLabel('Chapter').selectOption('6')
  await page.getByPlaceholder('e.g., 1,2,5-').click()
  await page.getByPlaceholder('e.g., 1,2,5-').fill('1,2,5-7')
  await page.getByPlaceholder('e.g., 1,2,5-').press('Tab')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await expect(page.locator('body')).toContainText('Leviticus 6:1,2,5-7')
})
