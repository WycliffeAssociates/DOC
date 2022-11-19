import { test, expect, type Page } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.goto('http://localhost:8001')
})

test('test pt-br, mat, mrk, ulb, tn, tq, tw, 1c pdf', async ({ page }) => {
  await page.getByRole('button', { name: '1. Languages' }).click()
  await expect(page).toHaveURL('/#/languages')
  await page.getByPlaceholder('Filter languages').fill('Bra')
  await page.getByLabel('Brazilian Português').check()
  await page.getByRole('button', { name: 'Add (1) Languages' }).click()
  await expect(page).toHaveURL('/#/')
  await page.getByRole('button', { name: '2. Books' }).click()
  await expect(page).toHaveURL('/#/books')
  await page.getByRole('button', { name: 'New Testament' }).click()
  await page.getByLabel('Matthew').check()
  await page.getByLabel('Mark').check()
  await page.getByRole('button', { name: 'Add (2) Books' }).click()
  await expect(page).toHaveURL('/#/')
  await page.getByRole('button', { name: '3. Resource types' }).click()
  await expect(page).toHaveURL('/#/resource_types')
  await page.getByLabel("Select all Brazilian Português's resource types").check()
  await page.getByRole('button', { name: 'Add (4) Resource Types' }).click()
  await expect(page).toHaveURL('/#/')
  await page.getByRole('link', { name: 'Settings' }).click()
  await expect(page).toHaveURL('/#/settings')
  await page.getByRole('button', { name: 'Generate Document' }).click()
  await expect(page).toHaveURL('/#/result')
  await expect(page.getByRole('heading', { name: 'Success!' })).toHaveText('Success!')
})

test('test pt-br, fr, mat, ulb, tn, tq, tw, sl-sr pdf', async ({ page }) => {
  await page.getByRole('button', { name: '1. Languages' }).click()
  await expect(page).toHaveURL('/#/languages')
  await expect(page.locator('li:has-text("Brazilian Português")')).toHaveText(
    'Brazilian Português'
  )
  await expect(page.locator('li:has-text("français (French)")')).toHaveText(
    'français (French)'
  )
  await page.getByLabel('Brazilian Português').check()
  await page.getByLabel('français (French)').check()
  await page.getByRole('button', { name: 'Add (2) Languages' }).click()
  await expect(page).toHaveURL('/#/')
  await expect(
    page.locator('span:has-text("Brazilian Português, français (French)")')
  ).toHaveText('Brazilian Português, français (French)')
  await page.getByRole('button', { name: '2. Books' }).click()
  await expect(page).toHaveURL('/#/books')
  await page.getByRole('button', { name: 'New Testament' }).click()
  await page.getByLabel('Matthew').check()
  await page.getByRole('button', { name: 'Add (1) Books' }).click()
  await expect(page).toHaveURL('/#/')
  await page.getByRole('button', { name: '3. Resource types' }).click()
  await expect(page).toHaveURL('/#/resource_types')
  await page.getByText("Select all Brazilian Português's resource types").click()
  await page.getByText("Select all français (French)'s resource types").click()
  await page.getByLabel('French Louis Segond 1910 Bible (f10)').uncheck()
  await page.getByRole('button', { name: 'Add (8) Resource Types' }).click()
  await expect(page).toHaveURL('/#/')
  await page.getByRole('link', { name: 'Settings' }).click()
  await expect(page).toHaveURL('/#/settings')
  await page
    .locator(
      'li:has-text("Print Optimization Enabling this option will remove extra whitespace") div'
    )
    .nth(3)
    .click()
  await page.locator('select[name="assemblyStrategy"]').selectOption('blo')
  await page.getByRole('button', { name: 'Generate Document' }).click()
  await expect(page).toHaveURL('/#/result')
  await expect(page.locator('h3:has-text("Success!")')).toHaveText('Success!')
})
