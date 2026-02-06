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
  await page.getByText('Galatians').click()
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
  await page.getByRole('radio', { name: 'PDF' }).click()
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

test('reviewers guide is only shown when book is chosen that it includes', async ({ page }) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText('English').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('1 Corinthians').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(
    page.locator('li').filter({ hasText: "NT Survey Reviewers' Guide" })
  ).not.toBeVisible({ timeout: 580000 })
})

test('reviewers guide is only shown when book is chosen that it includes - part 2', async ({
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

test('can select gateway tab after first selecting heart language and hitting next', async ({
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
  await page.getByText('Regular').click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
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
  await page.getByRole('radio', { name: 'PDF' }).click()
  await expect(page.getByRole('main')).toContainText('▶ Show Optional Settings')
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
})

test('book name correction happened for pt-br, 1co', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Português Brasileiro (').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Coríntios 1co').check()
  await expect(page.locator('body')).toContainText('1 Coríntios')
})

// Limit words feature is now disabled because tw is handled better/differently
// and limiting the words provided means that cross references won't
// work and we have just done work to ensure cross reference links work
// nicely.
test.skip('limit tw words switch', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Mateo').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible ulb').click()
  await page.getByText('Translation Words').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByRole('main')).toContainText('Limit TW words')
  await page.getByRole('link', { name: 'Resources' }).click()
  await page.getByLabel('Unlocked Literal Bible ulb').uncheck()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByRole('main')).not.toContainText('Limit TW words')
  await page.getByRole('link', { name: 'Resources' }).click()
  await page.getByLabel('Unlocked Literal Bible ulb').check()
  await page.getByLabel('Translation Words tw').uncheck()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByRole('main')).not.toContainText('Limit TW words')
  await page.getByRole('link', { name: 'Resources' }).click()
  await page.getByLabel('Unlocked Literal Bible ulb').check()
  await page.getByLabel('Translation Words tw').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByRole('main')).toContainText('Limit TW words')
})

test('use section visual separator setting', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Español Latin America (Latin').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Efesios').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await page.locator('div').filter({ hasText: 'Show visual separator (' }).nth(4).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('ordering of books in document title(s) and body', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByPlaceholder('Search Gateway Languages').click()
  await page.getByPlaceholder('Search Gateway Languages').fill('tpi')
  await page.getByText('Tok Pisin').click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Heart Languages').click()
  await page.getByPlaceholder('Search Heart Languages').fill('ont')
  await page.getByText('Ontenu').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Matyu').click()
  await page.getByText('Mak').click()
  await page.getByText('Luk', { exact: true }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').first().click()
  await page.getByText('Regular').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Interleave content by chapter').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  // Wait for the "View HTML Online" button to appear and become visible
  const viewHtmlButton = page.getByRole('button', { name: 'View HTML Online' })
  await viewHtmlButton.waitFor({ state: 'visible' })
  // Start waiting for the popup BEFORE clicking
  const page1Promise = page.waitForEvent('popup')
  // Click to trigger the popup
  await viewHtmlButton.click()
  // Get the new popup page
  const page1 = await page1Promise
  // Perform text expectations on the popup page
  await expect(page1.locator('body')).toContainText(
    'Tok Pisin (Tok Pisin): Unlocked Literal Bible for Matyu, Mak, Luk'
  )
  await expect(page1.locator('body')).toContainText(
    'Ontenu (Ontenu): Regular for Matthew, Maki, Luk'
  )

  // Order assertions
  const headings = await page1.locator('h2').allTextContents()
  // Ensure expected headings are present
  expect(headings).toContain('Matyu')
  expect(headings).toContain('Matthew')
  expect(headings).toContain('Mak')
  expect(headings).toContain('Maki')
  expect(headings).toContain('Luk')

  // Find the positions of each
  const index1 = headings.indexOf('Matyu')
  const index2 = headings.indexOf('Matthew')
  const index3 = headings.indexOf('Mak')
  const index4 = headings.indexOf('Maki')
  const index5 = headings.indexOf('Luk')

  // Ensure all were found
  expect(index1).not.toBe(-1)
  expect(index2).not.toBe(-1)
  expect(index3).not.toBe(-1)
  expect(index4).not.toBe(-1)
  expect(index5).not.toBe(-1)

  // Check the order
  expect(index1).toBeLessThan(index2)
  expect(index1).toBeLessThan(index3)
  expect(index2).toBeLessThan(index3)
  expect(index1).toBeLessThan(index4)
  expect(index2).toBeLessThan(index4)
  expect(index3).toBeLessThan(index4)
  expect(index1).toBeLessThan(index5)
  expect(index2).toBeLessThan(index5)
  expect(index3).toBeLessThan(index5)
  expect(index4).toBeLessThan(index5)
})

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
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').click()
  await page.getByRole('button', { name: 'Old Testament' }).click()
  await page.getByRole('button', { name: 'New Testament' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').first().click()
  await page.getByText('Unlocked Literal Bible').nth(1).click()
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

test('visibility of optional settings based on resources chosen', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Français (French)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').click()
  await page.getByLabel('French Louis Segond 1910').uncheck()
  await page.getByLabel('Translation Words tw').uncheck()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
  await expect(page.getByRole('main')).toContainText('Translation notes layout:')
  await expect(page.getByRole('main')).toContainText('Translation questions layout:')
  await page.getByRole('button', { name: 'Edit' }).nth(2).click()
  await page.getByText('Translation Questions', { exact: true }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).not.toContainText('Translation questions layout:')
  await page.getByRole('button', { name: 'Edit' }).nth(2).click()
  await page.getByLabel('Translation Notes tn').uncheck()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).not.toContainText('Translation notes layout:')
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
  await page.getByRole('button', { name: 'Edit' }).nth(2).click()
  await page.getByText('Translation Notes').click()
  await page.getByLabel('Unlocked Literal Bible ulb').uncheck()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  // await expect(page.getByRole('main')).toContainText('Translation notes layout:')
  await expect(page.getByRole('main')).not.toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
})

test('burmese', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByPlaceholder('Search Gateway Languages').click()
  await page.getByPlaceholder('Search Gateway Languages').fill('my')
  await page.getByText('ျမန္မာစာ (Burmese)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('ရှင်မဿဲခရစ်ဝင်။').click()
  await page.getByText('ရှင်မာကုခရစ်ဝင်။').click()
  await page.getByText('ရှင်လုကာခရစ်ဝင်။').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Translation Notes').click()
  await page.getByLabel('Translation Notes tn').uncheck()
  await expect(page.locator('body')).toContainText('Translation Notes')
  await expect(page.locator('body')).toContainText('Translation Questions')
  await expect(page.locator('body')).toContainText('Translation Words')
  await expect(page.locator('body')).toContainText('Unlocked Literal Bible')
  await page.getByLabel('Select all').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('merge of data API data and DOC only data', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await expect(page.getByRole('main')).toContainText('Bahasa Indonesia (Indonesian)')
  await page.getByLabel('Bahasa Indonesia (Indonesian').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Matius').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.locator('body')).toContainText('Bahasa Indonesian Bible')
  await expect(page.locator('body')).toContainText('Translation Notes')
})

test('space between end of chunk and beginning of another', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Heart Languages').click()
  await page.getByPlaceholder('Search Heart Languages').fill('Aushi')
  await page.getByLabel('Aushi auh').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Mateo mat').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Regular reg').check()
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
  // Ensure there is a space between the end of a verse span chunk and
  // the verse number for the start of the next chunk, i.e., check
  // spacing at chunk boundaries
  await expect(page1.locator('body')).toContainText('bembu?" 12Ulo')
  await expect(page1.locator('body')).toContainText('lelo naishile ababembu." 14Nolu abasambi')
  await expect(page1.locator('body')).toContainText('bakafunga. 16Takuli')
})

test('lang then book by verse', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByLabel('English en').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Matthew mat').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByText('Translation Words').click()
  await page.getByText('Translation Notes', { exact: true }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByText('Interleave content by verse').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.locator('body')).not.toContainText('Translation notes layout:')
  await expect(page.locator('body')).not.toContainText('Translation questions layout:')
  await page.getByRole('button', { name: 'Generate File' }).click()
  const viewHtmlButton = page.getByRole('button', { name: 'View HTML Online' })
  await viewHtmlButton.waitFor({ state: 'visible' })
  // Start waiting for the popup BEFORE clicking
  const page1Promise = page.waitForEvent('popup')
  // Click to trigger the popup
  await viewHtmlButton.click()
  // Get the new popup page
  const page1 = await page1Promise
  await expect(page1.locator('body')).toContainText(
    '1The book of the genealogy of Jesus Christ, son of David, son of Abraham.'
  )
  await page1.goto(
    'http://localhost:8089/en-tn-mat_en-tw-mat_en-ulb-mat_lvo_1c_chapter_clf_lwt_ssf_1ctn_1ctq.html#en-canaan'
  )
})

test('interleave by book shows tn and tq two column option', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Mateo mat').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByText('Translation Questions').click()
  await page.getByText('Translation Words').click()
  await page.getByText('Translation Notes', { exact: true }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByText('Interleave content by book').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.locator('body')).toContainText('Translation notes layout:')
  await expect(page.locator('body')).toContainText('Translation questions layout:')
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('two languages settings available', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Cebuano').click()
  await page.getByText('English').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Mateo').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').first().click()
  await page.getByText('Translation Words').first().click()
  await page.getByText('Translation Notes').first().click()
  await page.getByText('Translation Notes').nth(2).click()
  await page.getByText('Translation Words').nth(1).click()
  await page.getByText('Unlocked Literal Bible').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('radio', { name: 'PDF' }).click()
  await expect(page.getByRole('main')).toContainText(
    'Interleave content by verse one book at a time'
  )
  await expect(page.getByRole('main')).toContainText('Interleave content by chapter')
  await expect(page.getByRole('main')).toContainText(
    'Interleave content by verse one chapter at a time'
  )
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText('Translation notes layout:')
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('rmp galatians', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByPlaceholder('Search Heart Languages').click()
  await page.getByPlaceholder('Search Heart Languages').fill('rmp')
  await page.getByText('Rempi').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByRole('main')).toContainText('Galasians', { timeout: 10000 })
  await page.getByLabel('Titus ti').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Regular').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Docx').click()
  await page.getByText('Interleave content by verse').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('two languages, interleave by verse one chapter at a time', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('English').click()
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galatians').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').first().click()
  await page.locator('#select-all-lang0-resource-types').uncheck()
  await page.getByLabel('Bible Commentary bc').check()
  await page.getByLabel("NT Survey Reviewers' Guide rg").check()
  await page.locator('#lang0-resourcetype-3').check()
  await page.locator('#lang0-resourcetype-4').check()
  await page.locator('#lang0-resourcetype-5').check()
  await page.getByText('Select all').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Docx').click()
  await page.getByText('Interleave content by verse one book at a time').click()
  await expect(page.getByRole('main')).toContainText('Interleave content by book')
  await expect(page.getByRole('main')).toContainText(
    'Interleave content by verse one book at a time'
  )
  await expect(page.getByRole('main')).toContainText('Interleave content by chapter')
  await expect(page.getByRole('main')).toContainText(
    'Interleave content by verse one chapter at a time'
  )
  await page.getByText('Interleave content by verse one chapter at a time').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
  await expect(page.getByRole('main')).toContainText(
    'Show visual separator (horizontal line) between sections'
  )
  await expect(page.getByRole('main')).toContainText('Include TN book intro')
  await expect(page.getByRole('main')).toContainText('Include BC book intro')
  await expect(page.getByRole('main')).toContainText('Include TN chapter intro')
  await expect(page.getByRole('main')).toContainText('Include BC chapter commentary')
  await expect(page.getByRole('main')).toContainText('Include RG chapter commentary')
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('include tn book and chapter intros is checked by default for this case', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByLabel('Français (French) fr').check()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galates').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('French Louis Segond 1910 Bible').click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByText('Translation Notes').click()
  await page.getByText('Translation Words').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.locator('#use-two-column-layout-for-tn')).not.toBeChecked()
  await expect(page.locator('#show-tn-book-intro')).toBeChecked()
  await expect(page.locator('#show-tn-chapter-intro')).toBeChecked()
})

test('include tn book and chapter intros is not checked by default for this case', async ({
  page
}) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Français (French)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Galates').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('French Louis Segond 1910 Bible').click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByText('Translation Notes').click()
  await page.getByText('Translation Words').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Interleave content by verse').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.locator('#use-two-column-layout-for-tn')).toHaveCount(0)
  await expect(page.locator('#show-tn-book-intro')).not.toBeChecked()
  await expect(page.locator('#show-tn-chapter-intro')).not.toBeChecked()
})
