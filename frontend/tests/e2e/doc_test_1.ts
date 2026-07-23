import { expect, test } from '@playwright/test'

test('ui part 1', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Tiếng Việt (Vietnamese)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Ga-la-ti').click()
  await page.getByText('Lu-ca').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByRole('button', { name: 'Edit' }).first().click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByRole('button', { name: 'Gateway' }).click()
  await page.getByText('অসমীয়া (Assamese)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').nth(1).click({ timeout: 32_000 })
  await page.getByText('Translation Notes tn').first().click()
  await page.getByText('Translation Notes').nth(1).click()
  await page.getByText('Translation Questions').first().click()
  await page.getByText('Translation Questions').nth(1).click()
  await page.getByText('Translation Words').first().click()
  await page.getByText('Translation Words tw').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('ui part 2', async ({ page }) => {
  await page.goto('http://localhost:8001')
  await page.getByText('English').click()
  await page.getByText('Español Latin America (Latin').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galatians').click({ timeout: 32_000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page
    .getByText(/.*Unlocked Literal Bible.*/)
    .first()
    .click()
  await page
    .getByText(/.*Unlocked Literal Bible.*/)
    .nth(1)
    .click()
  await page
    .getByText(/.*Translation Notes.*/)
    .nth(1)
    .click({ timeout: 8200000 })
  await page
    .getByText(/.*Translation Notes.*/)
    .nth(2)
    .click()
  await page.getByRole('button', { name: 'Next' }).click()
  // await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Interleave content by chapter').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('books retained in basket on back button to languages and then forward', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByPlaceholder('Search Gateway Languages').click()
  await page.getByPlaceholder('Search Gateway Languages').fill('Amh')
  await page.getByText('አማርኛ (Amharic)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('2 ኛ ቆሮንቶስ').click({ timeout: 680000 })
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Heart Languages').click()
  await page.getByPlaceholder('Search Heart Languages').fill('adh')
  await page.getByText('Adhola adh').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByPlaceholder('Search NT books').click()
  await page.getByPlaceholder('Search NT books').fill('2 ኛ ዮሐንስ')
  await page.getByText('2 ኛ ዮሐንስ').click({ timeout: 5800000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.locator('body')).toContainText('Adhola')
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByText('Regular', { exact: true }).click()
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByPlaceholder('Search NT books').click()
  await page.getByPlaceholder('Search NT books').fill('2 ኛ ዮሐንስ')
})

test('transfer from biel', async ({ page }) => {
  await page.goto(
    'http://localhost:8001/transfer/repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fchunga_moses%2Fleb-x-bisa_col_text_reg&book_name=Colossians'
  )
  await expect(page.getByText('Bisa')).toBeVisible()
  await expect(page.getByText('Colossians')).toBeVisible({ timeout: 1200000 })
})

test('transfer from biel 2', async ({ page }) => {
  await page.goto(
    'http://localhost:8001/transfer/repo_url=https:%2F%2Fcontent.bibletranslationtools.org%2FWycliffeAssociates%2Fen_ulb'
  )
  await expect(page.getByText('English')).toBeVisible({ timeout: 20000 })
  await expect(page.getByText('Genesis')).toBeVisible()
  await expect(page.getByText('Deuteronomy')).toBeVisible()
  await expect(page.getByText('(60) items hidden')).toBeVisible()
})
