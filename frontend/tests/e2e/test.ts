import { expect, test } from '@playwright/test'

test('test ui part 1', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Tiếng Việt (Vietnamese)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Ga-la-ti gal').click()
  await page.getByText('LU-CA luk').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByRole('button', { name: 'Edit' }).first().click()
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByRole('button', { name: 'Gateway' }).click()
  await page.getByText('অসমীয়া (Assamese) as').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').nth(1).click({ timeout: 320000 })
  await page.getByText('Translation Notes').first().click()
  await page.getByText('Translation Notes').nth(1).click()
  await page.getByText('Translation Questions').first().click()
  await page.getByText('Translation Questions').nth(1).click()
  await page.getByText('Translation Words').first().click()
  await page.getByText('Translation Words').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('test ui part 2', async ({ page }) => {
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
  await page.getByText('PDF').click()
  await page.getByText('Interleave content by chapter').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('test books retained in basket on back button to languages and then forward', async ({
  page
}) => {
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

test('test transfer from biel', async ({ page }) => {
  await page.goto(
    'http://localhost:8001/transfer/repo_url=https%3A%2F%2Fcontent.bibletranslationtools.org%2Fchunga_moses%2Fleb-x-bisa_col_text_reg&book_name=Colossians'
  )
  await expect(page.getByText('Bisa')).toBeVisible()
  await expect(page.getByText('Colossians')).toBeVisible({ timeout: 1200000 })
})

test('test transfer from biel 2', async ({ page }) => {
  await page.goto(
    'http://localhost:8001/transfer/repo_url=https:%2F%2Fcontent.bibletranslationtools.org%2FWycliffeAssociates%2Fen_ulb'
  )
  await expect(page.getByText('English')).toBeVisible({ timeout: 20000 })
  await expect(page.getByText('Genesis')).toBeVisible()
  await expect(page.getByText('Deuteronomy')).toBeVisible()
  await expect(page.getByText('(60) items hidden')).toBeVisible()
})

test('test es-419 resource types', async ({ page }) => {
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

test('test that reviewers guide is only shown when book is chosen that it includes', async ({
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

test('test that reviewers guide is only shown when book is chosen that it includes - part 2', async ({
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

test('test that you can select gateway tab after first selecting heart language and hitting next', async ({
  page
}) => {
  await page.goto('http://localhost:8001/')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByText('Adhola').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('1 Thesalonika').click({ timeout: 580000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('link', { name: 'Languages' }).click()
  await page.getByRole('button', { name: 'Gateway' }).click()
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Mga taga tesalonica 1th').click({ timeout: 580000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByText('Regular', { exact: true }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('PDF').click()
  await page.getByText('Interleave content by chapter').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('test optional settings', async ({ page }) => {
  await page.goto('http://localhost:8001/languages')
  await page.getByText('Bichelamar (Bislama)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Matiu').click({ timeout: 120000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Regular').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('PDF').click()
  await expect(page.getByRole('main')).toContainText('▶ Show Optional Settings')
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
})

test.skip('test aba philemon', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByText('Abé aba').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Philémon').click({ timeout: 580000 })
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Regular').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('PDF').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
  await expect(page.locator('body')).toContainText('Philémon')
  await expect(page.locator('body')).toContainText('Regular (aba)')
})

test('test that book name correction happened for pt-br, 1co', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Português Brasileiro (').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Coríntios 1co').check()
  await expect(page.locator('body')).toContainText('1 Coríntios')
})

test('test limit tw words switch', async ({ page }) => {
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

test('test use section visual separator setting', async ({ page }) => {
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

test('test ordering of books in document title(s) and body', async ({ page }) => {
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
  await page.getByText('Unlocked Literal Bible').nth(1).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('PDF').click()
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
    'Ontenu (Ontenu): Unlocked Literal Bible for Matthew, Maki, Luk'
  )
  await expect(page1.locator('body')).toContainText(
    'Tok Pisin (Tok Pisin): Unlocked Literal Bible for Matyu, Mak, Luk'
  )

  // Order assertions
  const headings = await page1.locator('h2').allTextContents()
  // Ensure expected headings are present
  expect(headings).toContain('Matthew')
  expect(headings).toContain('Matyu')
  expect(headings).toContain('Maki')
  expect(headings).toContain('Mak')
  expect(headings).toContain('Luk')

  // Find the positions of each
  const index1 = headings.indexOf('Matthew')
  const index2 = headings.indexOf('Matyu')
  const index3 = headings.indexOf('Maki')
  const index4 = headings.indexOf('Mak')
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

test('test use prince with lots of books', async ({ page }) => {
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
  await page.getByText('PDF').click()
  await page.getByText('Interleave content by chapter').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('test acq', async ({ page }) => {
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
  await page.getByText('PDF').click()
  await page.getByText('Use PrinceXml to produce the').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await page
    .getByText('Use 2 column layout for translation questions resource (note: some languages')
    .click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('test visibility of optional settings based on resources chosen', async ({ page }) => {
  await page.goto('http://localhost:8001/')
  await page.getByText('Français (French)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Select all').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Unlocked Literal Bible').click()
  await page.getByText('Translation Notes').click()
  await page.getByText('Translation Questions').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('PDF').click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
  await page.getByRole('button', { name: 'Edit' }).nth(2).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).toContainText(
    "Use 2 column layout for translation notes resource (note: some languages don't layout well with this setting, e.g., Khmer)"
  )
  await expect(page.getByRole('main')).toContainText(
    "Use 2 column layout for translation questions resource (note: some languages don't layout well with this setting, e.g., Khmer)"
  )
  await page.getByRole('button', { name: 'Edit' }).nth(2).click()
  await page.getByLabel('Translation Questions tq').uncheck()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).not.toContainText(
    "Use 2 column layout for translation questions resource (note: some languages don't layout well with this setting, e.g., Khmer)"
  )
  await page.getByRole('button', { name: 'Edit' }).nth(2).click()
  await page.getByLabel('Translation Notes tn').uncheck()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).not.toContainText(
    "Use 2 column layout for translation notes resource (note: some languages don't layout well with this setting, e.g., Khmer)"
  )
  await page.getByRole('button', { name: 'Edit' }).nth(2).click()
  await page.getByText('Translation Notes').click()
  await page.getByText('Unlocked Literal Bible', { exact: true }).click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: '▶ Show Optional Settings' }).click()
  await expect(page.getByRole('main')).not.toContainText(
    "Use chapter labels, e.g., 'Chapter 1' instead of '1'"
  )
  await expect(page.getByRole('main')).toContainText(
    "Use 2 column layout for translation notes resource (note: some languages don't layout well with this setting, e.g., Khmer)"
  )
})
