import { test, expect } from '@playwright/test';

test.describe('Authentication & Authorization', () => {
  test('Unauthenticated user is redirected to sign-in from protected route', async ({ page }) => {
    // Attempt to access a protected route
    await page.goto('/dashboard');
    
    // Clerk usually redirects to its own sign-in page or a custom sign-in page like /sign-in
    await expect(page).toHaveURL(/.*sign-in.*/);
  });

  // Note: To test actual login flows without hitting CAPTCHAs or rate limits, 
  // you should use Clerk's Testing Tokens in your environment variables.
  // We can also create a "global setup" file to authenticate once and save the state.
  test('User can see sign-up option', async ({ page }) => {
    await page.goto('/sign-in');
    
    // Check if the "Sign up" link is visible
    const signUpLink = page.locator('text=/Sign up/i').first();
    await expect(signUpLink).toBeVisible();
  });
});
