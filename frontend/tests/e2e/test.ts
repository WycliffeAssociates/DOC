import { expect, test } from '@playwright/test'

test('test ui part 1', async ({ page }) => {
  await page.goto('http://localhost')
  await page.getByText('Assamese').click()
  await page.getByText('Vietnamese').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Old Testament' }).click()
  await page.getByLabel('Genesis gen').check()
  await page.getByRole('button', { name: 'New Testament' }).click()
  // await page.getByText('Matthew').click();
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Translation Notes (tn)').first().click()
  await page.getByText('Translation Questions (tq)').first().click()
  await page.getByText('Translation Words (tw)').first().click()
  await page.getByText('Assamese Unlocked Literal').click()
  await page.getByText('Translation Notes (tn)').nth(1).click()
  await page.getByText('Translation Questions (tq)').nth(1).click()
  await page.getByText('Translation Words (tw)').nth(1).click()
  await page.getByText('Vietnamese Unlocked Literal').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  await expect(page.locator('body')).toContainText('Assamese')
  await expect(page.locator('body')).toContainText('Vietnamese')
  await expect(page.locator('body')).toContainText('Genesis')
  await expect(page.locator('body')).toContainText('Translation Notes (tn)')
  await expect(page.locator('body')).toContainText('Translation Questions (tq)')
  await expect(page.locator('body')).toContainText('Translation Words (tw)')
  await expect(page.locator('body')).toContainText('Assamese Unlocked Literal Bible (ulb)')
  await expect(page.locator('body')).toContainText('Vietnamese Unlocked Literal Bible (ulb)')
})

test('test ui part 2', async ({ page }) => {
  await page.goto('http://localhost')
  await page.getByText('Assamese as').click()
  await page.getByText('Español (Latin American Spanish)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galatians gal').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Assamese Unlocked Literal Bible (ulb)').click()
  await page.getByText('Español Latino Americano ULB (ulb)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  await page.getByRole('button', { name: 'Download Docx' }).click()
})

test('test books retained in basket on back button to languages and then forward', async ({
  page
}) => {
  await page.goto('http://localhost')
  await page.getByText('Amharic').click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Languages').click()
  await page.getByPlaceholder('Search Languages').fill('agn')
  await page.getByLabel('Agni Bona any-x-agnibona').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Philemon').click()
  await page.getByText('Philemon').nth(1).click()
  await page
    .locator('div')
    .filter({ hasText: /^Amharic\(am\)$/ })
    .first()
    .click()
  await page.locator('.flex-shrink-0 > div:nth-child(4)').click()
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Philemon').nth(1).click()
  await page
    .locator('div')
    .filter({ hasText: /^Amharic\(am\)$/ })
    .first()
    .click()
})

test('test transfer from biel', async ({ page }) => {
  await page.goto(
    'http://localhost/transfer/repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fbahasatech.indotengah%2Fbne_gal_text_reg&book_name=Galatians'
  )
  await expect(page.getByText('Bintauna')).toBeVisible()
  await expect(page.getByText('Galatians')).toBeVisible()
})

test('test transfer from biel 2', async ({ page }) => {
  await page.goto(
    'https://doc.bibleineverylanguage.org/transfer/repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fchunga_moses%2Fleb-x-bisa_col_text_reg&book_name=Colossians'
  )
  await expect(page.getByText('Bisa')).toBeVisible()
  await expect(page.getByText('Colossians')).toBeVisible()
})

test('test transfer from biel 3', async ({ page }) => {
  await page.goto(
    'https://doc.bibleineverylanguage.org/transfer/repo_url=https:%2F%2Fcontent.bibletranslationtools.org%2FWycliffeAssociates%2Fen_ulb'
  )
  await expect(page.getByText('English')).toBeVisible()
  await expect(page.getByText('Genesis')).toBeVisible()
  await expect(page.getByText('Deuteronomy')).toBeVisible()
  await expect(page.getByText('(60) items hidden')).toBeVisible()
})

test('test es-419 resource types', async ({ page }) => {
  await page.goto('http://localhost')
  await page.getByText('Español (Latin American').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Matthew').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Translation Notes (tn)').check()
  await page.getByLabel('Translation Questions (tq)').check()
  await page.getByLabel('Translation Words (tw)').check()
  await page.getByLabel('Español Latino Americano ULB').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})
