import { test, expect } from '@playwright/test'

test('add passages', async ({ page }) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByText('Español Latin America (Latin').click()
  await page.getByRole('button', { name: 'Next' }).click()
  const passagesSection = page.locator('#passages-basket')
  await page.getByLabel('Bible Book').selectOption('jos')
  await page.getByLabel('Chapter').selectOption('7')
  await page.getByPlaceholder('e.g., 1,2,5-').fill('1-10')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await page.getByLabel('Bible Book').selectOption('est')
  await page.getByLabel('Chapter').selectOption('7')
  await page.getByPlaceholder('e.g., 1,2,5-').fill('3,12')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await page.getByLabel('Bible Book').selectOption('1th')
  await page.getByLabel('Chapter').selectOption('4')
  await page.getByPlaceholder('e.g., 1,2,5-').fill('1,5-8,11')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await expect(passagesSection).toContainText('Josué 7:1-10 (es-419)')
  await expect(passagesSection).toContainText('Ester 7:3,12 (es-419)')
  await expect(passagesSection).toContainText('1 Tesalonicenses 4:1,5-8,11 (es-419)')
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('button', { name: 'Generate File' }).click()
})

test('select gateway tab after first selecting heart language and hitting next', async ({
  page
}) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByRole('button', { name: 'Heart' }).click()
  await page.getByText('Abure').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByRole('link', { name: 'Language' }).click()
  await page.getByText('Cebuano').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.waitForTimeout(20000)
  await page.getByText("Add NT Survey Reviewers'").click()
  await page.waitForTimeout(30000)
  await expect(page.getByTestId('shown-passages')).toContainText('(ceb)', { timeout: 120000 })
  const passagesSection = page.getByTestId('shown-passages')
  const text = await passagesSection.innerText()
  // console.log('DEBUG TEXT:')
  // console.log(JSON.stringify(text)) // helpful for spotting hidden chars
  expect(text).toMatch(/Mat+t?hieu.*2:1-12.*\(abu\)/i)
  expect(text).toMatch(/Mateo.*2:1-12.*\(ceb\)/i)
})

test('passages checkboxes', async ({ page }) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByText('English').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Add OT Survey RG1 Passages').check()
  await expect(page.locator('body')).toContainText('Genesis 1:1-2:3', { timeout: 32_000 })
  await page.getByLabel('Add OT Survey RG1 Passages').uncheck()
  await expect(page.locator('body')).not.toContainText('Genesis 1:1-2:3', { timeout: 32_000 })
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
  // await page.getByLabel('Add STET Passages').check()
  // await expect(page.locator('body')).toContainText('Matthew 1:1', { timeout: 32_000 })
  // await page.getByLabel('Add STET Passages').uncheck()
  // await expect(page.locator('body')).not.toContainText('Matthew 1:1', { timeout: 32_000 })
  await page.getByLabel("Add all OT Survey Reviewers' Guide (RG) Passages").check()
  await expect(page.locator('body')).toContainText('Genesis 1:1-2:3', { timeout: 32_000 })
  await page.getByLabel("Add all OT Survey Reviewers' Guide (RG) Passages").uncheck()
  await expect(page.locator('body')).not.toContainText('Genesis 1:1-2:3', { timeout: 32_000 })
  await page.getByLabel('Bible Book').selectOption('lev')
  await page.getByLabel('Chapter').selectOption('6')
  await page.getByPlaceholder('e.g., 1,2,5-').click()
  await page.getByPlaceholder('e.g., 1,2,5-').fill('1,2,5-7')
  await page.getByPlaceholder('e.g., 1,2,5-').press('Tab')
  await page.getByRole('button', { name: 'Add Passage' }).click()
  await expect(page.locator('body')).toContainText('Leviticus 6:1,2,5-7')
})

test('OT rg1, rg3, and rg4', async ({ page }) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByText('English').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await page.getByText('Add OT Survey RG1 Passages').click()
  await expect(page.locator('body')).toContainText('Genesis 1:1-2:3', { timeout: 32_000 })
  await page.locator('.collapse > input').check()
  await expect(page.locator('body')).toContainText('Exodus 1:1-2:10', { timeout: 32_000 })
  await expect(page.locator('body')).toContainText('Exodus 12:1-20', { timeout: 32_000 })
  await expect(page.locator('body')).toContainText('Exodus 12:21-42', { timeout: 32_000 })
  await expect(page.locator('body')).toContainText('Deuteronomy 12:29-13:5', { timeout: 32_000 })
  await page.getByText('Add OT Survey RG3 Passages').click()
  await expect(page.locator('body')).toContainText('Song of songs 1:1-4', { timeout: 32_000 })
  await expect(page.locator('body')).toContainText('Song of songs 4:9-15', { timeout: 32_000 })
  await expect(page.locator('body')).toContainText('Song of songs 5:9-16', { timeout: 32_000 })
  await page.getByText('Add OT Survey RG4 Passages').click()
  await expect(page.locator('body')).toContainText('Isaiah 52:13-53:12', { timeout: 32_000 })
})

test('checkboxes are only shown when language chosen has books in each checkbox group respectively', async ({
  page
}) => {
  await page.goto('http://localhost:8001/passages')
  await page.getByLabel('Bahasa Malaysia zlm').check()
  await page.getByRole('button', { name: 'Next' }).click()
  // await expect(page.locator('body')).not.toContainText('Add OT Survey RG1 Passages')
  // await expect(page.locator('body')).not.toContainText('Add OT Survey RG2 Passages')
  // await expect(page.locator('body')).not.toContainText('Add OT Survey RG3 Passages')
  // await expect(page.locator('body')).not.toContainText('Add OT Survey RG4 Passages')
  await expect(page.locator('body')).toContainText("Add NT Survey Reviewers' Guide (RG) Passages", {
    timeout: 32_000
  })
  // await expect(page.locator('#stet-passages')).toContainText('Add STET Passages')
  await page.getByText("Add NT Survey Reviewers'").click()
  await expect(page.locator('body')).toContainText('Matius 2:1-12', { timeout: 32_000 })
  await expect(page.locator('body')).toContainText('Matius 3:13-17', { timeout: 32_000 })
  // await page.getByLabel('Add STET Passages').check()
  // await expect(page.locator('body')).toContainText('Matius 1:1', { timeout: 32_000 })
  await page.getByRole('link', { name: 'Language' }).click()
  await page.getByText('Français (French)').click()
  await page.getByRole('button', { name: 'Next' }).click()
  await expect(page.locator('body')).toContainText(
    "Add all OT Survey Reviewers' Guide (RG) Passages",
    {
      timeout: 32_000
    }
  )
  await expect(page.locator('#add-ot-rg1-passages')).toContainText(
    'Add OT Survey RG1 Passages only (Genesis to Deuteronomy)',
    { timeout: 32_000 }
  )
  await expect(page.locator('#add-ot-rg2-passages')).toContainText(
    'Add OT Survey RG2 Passages only (Joshua to Esther)',
    { timeout: 32_000 }
  )
  await expect(page.locator('#add-ot-rg3-passages')).toContainText(
    'Add OT Survey RG3 Passages only (Job to Song of Songs)',
    { timeout: 32_000 }
  )
  await expect(page.locator('#add-ot-rg4-passages')).toContainText(
    'Add OT Survey RG4 Passages only (Isaiah to Malachi)',
    { timeout: 32_000 }
  )
  await expect(page.locator('#add-nt-passages')).toContainText(
    "Add NT Survey Reviewers' Guide (RG) Passages",
    {
      timeout: 32_000
    }
  )
  // await expect(page.locator('#stet-passages')).toContainText('Add STET Passages', {
  //   timeout: 32_000
  // })
})
// We do not provide STET passages checkbox in Passages app currently by request of PO
test.skip('stet passages not available in production', async ({ page }) => {
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

// We do not provide STET passages checkbox in Passages app currently by request of PO
test.skip('stet passages available when not in production', async ({ page }) => {
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
  await page.waitForSelector('#stet-passages', { state: 'visible' })
  await expect(page.locator('#stet-passages')).toBeVisible()
})
