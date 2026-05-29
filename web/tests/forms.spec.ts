import { test, expect } from '@playwright/test';

test.describe('Form Validations', () => {
  test('Contact or Signup form shows validation errors on empty submission', async ({ page }) => {
    // Navigate to a page with a form (using sign-up as an example, but adjust to your app's contact form)
    await page.goto('/sign-up');
    
    // Find the submit button and click it without filling any fields
    const submitButton = page.locator('button[type="submit"]').first();
    
    if (await submitButton.isVisible()) {
      await submitButton.click();
      
      // Look for standard HTML5 validation or custom React validation error messages
      // Example: 'This field is required', 'Invalid email'
      // We look for any text that might indicate an error state
      const errorMessage = page.locator('text=/required|invalid/i').first();
      await expect(errorMessage).toBeVisible();
    }
  });

  // Example test for a successful form submission
  test.skip('Successful form submission shows success message', async ({ page }) => {
    // Navigate to form
    await page.goto('/contact');
    
    // Fill out fields
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('textarea[name="message"]', 'This is an automated test message.');
    
    // Submit
    await page.locator('button[type="submit"]').click();
    
    // Verify success toast/message
    const successMessage = page.locator('text=/Success|Thank you/i');
    await expect(successMessage).toBeVisible();
  });
});
