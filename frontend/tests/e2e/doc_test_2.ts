import { expect, test } from '@playwright/test'

test('es-419 resource types', async ({ page }) => {
  await page.goto('http://localhost:8001')
  await page.getByText(/.*Español.*/).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Mateo').click({ timeout: 60000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Translation Notes').check()
  await page.getByLabel('Translation Questions').check()
  await page.locator('span').filter({ hasText: 'Español Latin America (Latin American Spanish)' })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test.skip('reviewers guide is only shown when book is chosen that it includes', async ({
  page
}) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText('English').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('1 Corinthians').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(
    page.locator('li').filter({ hasText: "NT Survey Reviewers' Guide" })
  ).not.toBeVisible({ timeout: 580000 })
})

test.skip('reviewers guide is only shown when book is chosen that it includes - part 2', async ({
  page
}) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText('English').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galatians').click({ timeout: 60000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.locator('span').filter({ hasText: "NT Survey Reviewers' Guide" })).toBeVisible({
    timeout: 5800000
  })
})

test.skip('can select gateway tab after first selecting heart language and hitting next', async ({
  page
}) => {
  await page.goto('http://localhost:8001/')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByText('Adhola').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Thesalonika 1th').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Regular').click({ timeout: 120_000 })
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByRole('button', { name: 'Next' }).click()
  // await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByLabel('Interleave content by chapter').check()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('optional settings', async ({ page }) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText('Bichelamar (Bislama)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Matiu').click({ timeout: 120000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Regular').click()
  await page.getByRole('button', { name: 'Next' }).click()
  // await page.getByRole('radio', { name: 'PDF' }).click()
  await expect(page.getByRole('main')).toContainText('▶ Show Optional Settings')
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
})
