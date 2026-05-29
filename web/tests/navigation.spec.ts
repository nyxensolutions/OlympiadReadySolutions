import { test, expect } from '@playwright/test';

test.describe('Navigation & Loading', () => {
  test('Homepage loads correctly', async ({ page }) => {
    await page.goto('/');
    
    // Check if the page title is present. The specific string depends on your actual app title.
    // Assuming 'Olympiad' might be in the title or heading.
    await expect(page).toHaveTitle(/Olympiad/i);
    
    // Wait for a core element to render (e.g., a main heading)
    const mainHeading = page.locator('h1').first();
    await expect(mainHeading).toBeVisible();
  });

  test('Privacy policy page loads correctly', async ({ page }) => {
    await page.goto('/privacy');
    await expect(page).toHaveURL(/.*privacy/);
    await expect(page.locator('h1')).toContainText(/Privacy/i);
  });

  test('Terms page loads correctly', async ({ page }) => {
    await page.goto('/terms');
    await expect(page).toHaveURL(/.*terms/);
    await expect(page.locator('h1')).toContainText(/Terms/i);
  });

  test('404 page renders for invalid routes', async ({ page }) => {
    // Navigate to a route that definitely doesn't exist
    const response = await page.goto('/invalid-route-that-does-not-exist');
    
    // Playwright captures the HTTP status
    expect(response?.status()).toBe(404);
    
    // Check for standard Next.js 404 text or your custom not-found text
    await expect(page.locator('text=/not found/i').first()).toBeVisible();
  });
});
