import { expect, test } from '@playwright/test'

test('test ui part 1', async ({ page }) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText('Tiếng Việt (Vietnamese)').click()
  await page.getByText('অসমীয়া (Assamese) as').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'New Testament' }).click()
  await page.getByText('Galatians').click()
  await page.getByText('Luke').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').first().click()
  await page.getByText('Unlocked Literal Bible').nth(1).click()
  await page.getByText('Translation Notes').first().click()
  await page.getByText('Translation Notes').nth(1).click()
  await page.getByText('Translation Questions').first().click()
  await page.getByText('Translation Questions').nth(1).click()
  await page.getByText('Translation Words').first().click()
  await page.getByText('Translation Words').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  await expect(page.locator('body')).toContainText('Assamese')
  await expect(page.locator('body')).toContainText('Vietnamese')
  await expect(page.locator('body')).toContainText('Galatians')
  await expect(page.locator('body')).toContainText('Translation Notes')
  await expect(page.locator('body')).toContainText('Translation Questions')
  await expect(page.locator('body')).toContainText('Translation Words')
  await expect(page.locator('body')).toContainText('Unlocked Literal Bible')
})

test('test ui part 2', async ({ page }) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText(/.*Español.*/).click()
  await page.getByText(/.*English.*/).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galatians').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').first().click()
  await page.getByText('Unlocked Literal Bible').nth(1).click()
  await page.getByText('Translation Notes').first().click()
  await page.getByText('Translation Notes').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('PDF').click()
  await page.getByText('Interleave content by chapter').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('test books retained in basket on back button to languages and then forward', async ({
  page
}) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText(/.*Amharic.*/).click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Languages').click()
  await page.getByPlaceholder('Search Languages').fill('agn')
  await page.getByLabel(/.*Agni Bona.*/).check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Philemon').click()
  await page.getByText('Philemon').nth(1).click()
  await page
    .locator('div')
    .filter({ hasText: /.*Amharic.*/ })
    .first()
    .click()
  await page.locator('.flex-shrink-0 > div:nth-child(4)').click()
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Philemon').nth(1).click()
  await page
    .locator('div')
    .filter({ hasText: /.*Amharic.*/ })
    .first()
    .click()
})

test('test transfer from biel', async ({ page }) => {
  await page.goto(
    'https://doc.bibleineverylanguage.org/transfer/repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fchunga_moses%2Fleb-x-bisa_col_text_reg&book_name=Colossians'
  )
  await expect(page.getByText('Bisa')).toBeVisible()
  await expect(page.getByText('Colossians')).toBeVisible()
})

test('test transfer from biel 2', async ({ page }) => {
  await page.goto(
    'https://doc.bibleineverylanguage.org/transfer/repo_url=https:%2F%2Fcontent.bibletranslationtools.org%2FWycliffeAssociates%2Fen_ulb'
  )
  await expect(page.getByText('English')).toBeVisible()
  await expect(page.getByText('Genesis')).toBeVisible()
  await expect(page.getByText('Deuteronomy')).toBeVisible()
  await expect(page.getByText('(60) items hidden')).toBeVisible()
})

test('test es-419 resource types', async ({ page }) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText(/.*Español.*/).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Matthew').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Translation Notes').check()
  await page.getByLabel('Translation Questions').check()
  await page.getByLabel('Translation Words').check()
  await page.locator('span').filter({ hasText: 'Español Latin America (Latin American Spanish)' })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})
