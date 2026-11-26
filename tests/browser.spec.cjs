const { test, expect } = require('@playwright/test');

test('a paid order is not a shipped order; shipment confirmation changes the correct order', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open order ORD-104' }).click();
  const details = page.getByRole('region', { name: 'Order details' });
  await details.getByRole('button', { name: 'Mark paid', exact: true }).click();
  await expect(details.locator('#paymentStatus')).toHaveText('Paid');
  await expect(details.locator('#shipmentStatus')).toHaveText('Ready');
  await details.getByRole('button', { name: 'Mark shipped', exact: true }).click();
  await page.getByRole('button', { name: 'Confirm shipment', exact: true }).click();
  await expect(details.locator('#shipmentStatus')).toHaveText('Shipped');
  await expect(details.getByRole('log')).toContainText('Shipment confirmed for ORD-104');
  await page.getByRole('button', { name: 'Open order ORD-105' }).click();
  await expect(details.locator('#shipmentStatus')).toHaveText('Ready');
  await page.screenshot({ path: 'test-results/dispatch-desktop.png', fullPage: true });
});

test('fresh context has independent state and shipment is idempotent', async ({ page, browser }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open order ORD-105' }).click();
  await page.getByRole('button', { name: 'Mark shipped', exact: true }).click();
  await page.getByRole('button', { name: 'Confirm shipment', exact: true }).click();
  await expect(page.locator('#shipmentStatus')).toHaveText('Shipped');
  await expect(page.getByRole('button', { name: 'Mark shipped', exact: true })).toBeDisabled();
  await page.reload();
  await page.getByRole('button', { name: 'Open order ORD-105' }).click();
  await expect(page.locator('#shipmentStatus')).toHaveText('Shipped');
  const fresh = await browser.newContext();
  const second = await fresh.newPage();
  await second.goto('http://127.0.0.1:4173');
  await second.getByRole('button', { name: 'Open order ORD-105' }).click();
  await expect(second.locator('#shipmentStatus')).toHaveText('Ready');
  await fresh.close();
});

test('mobile view has no horizontal overflow and confirmation can be canceled', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await page.getByRole('button', { name: 'Open order ORD-104' }).click();
  await page.getByRole('button', { name: 'Mark shipped', exact: true }).click();
  await page.getByRole('button', { name: 'Keep in queue' }).click();
  await expect(page.locator('#shipmentStatus')).toHaveText('Ready');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(errors).toEqual([]);
  await page.screenshot({ path: 'test-results/dispatch-mobile.png', fullPage: true });
});
