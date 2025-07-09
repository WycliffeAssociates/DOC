import { expect, test } from '@playwright/test'

// Group tests with specific settings
test.describe('Desktop Tests', () => {
    test.use({
        viewport: {
            height: 700,
            width: 1200
        }
    })

    test('test stet', async ({ page }) => {
        await page.goto('http://localhost:8001/stet')
        await page.getByLabel('English en').check()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByText('Cebuano').click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByRole('button', { name: 'Generate File' }).click()
    })

    test('test next back and edit', async ({ page }) => {
        await page.goto('http://localhost:8001/stet')
        await page.getByText('English').click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByRole('button', { name: 'Back' }).click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByText('Bichelamar (Bislama)').click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByRole('link', { name: 'Target Language' }).click()
        await page.getByRole('link', { name: 'Source Language' }).click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByRole('button', { name: 'Back' }).click()
        await page.getByRole('button', { name: 'Back' }).click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByRole('button', { name: 'Edit' }).click()
        await page.getByRole('button', { name: 'Edit' }).click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByLabel('Email me a copy of my').check()
        await page.getByPlaceholder('Type email address here (').click()
        await page.getByPlaceholder('Type email address here (').fill('fake@example.com')
        await page.getByRole('button', { name: 'Submit' }).click()
        await page.getByRole('button', { name: 'Generate File' }).click()
    })

    test('test tok pisin input language', async ({ page }) => {
        await page.goto('http://localhost:8001/stet')
        await page.getByText('Tok Pisin').click()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByLabel('English en').check()
        await page.getByRole('button', { name: 'Next' }).click()
        await page.getByRole('button', { name: 'Generate File' }).click()
    })
})

// Separate group for mobile tests
test.describe('Mobile Tests', () => {
    test.use({
        viewport: {
            height: 600,
            width: 300
        }
    })

    test('test mobile', async ({ page }) => {
        await page.goto('http://localhost:8001/stet')
        await page.getByLabel('English en').check()
        await page.getByRole('button').nth(1).click()
        await page.getByText('Bahasa Indonesia (Indonesian)').click()
        await page.getByRole('button').nth(1).click()
        await page.getByRole('button', { name: '2' }).click()
        await page.getByRole('button', { name: 'Edit' }).nth(1).click()
        await page.getByRole('button').nth(1).click()
        await page.getByRole('button', { name: 'Generate File' }).click()
    })

    test('test mobile 2', async ({ page }) => {
        await page.goto('http://localhost:8001/stet')
        await page.getByText('English').click()
        await page.getByRole('button').nth(1).click()
        await page.getByRole('button').first().click()
        await page.getByRole('button').nth(1).click()
        await page.getByRole('button').nth(2).click()
        await page.getByText('Heart languages').click()
        await page.getByRole('button', { name: 'Close' }).click()
        await page.getByText('Abé').click()
        await page.getByRole('button').nth(1).click()
        await page.getByRole('button').first().click()
        await expect(page.getByLabel('Abé aba')).toBeChecked({ timeout: 1200000 })
    })
})
