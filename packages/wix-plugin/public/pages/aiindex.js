/**
 * AI Index Public Page Code
 *
 * This code runs on the frontend and provides user-facing functionality
 * for the AI Index integration on Wix pages.
 *
 * @module public/pages/aiindex
 */

import { fetch } from 'wix-fetch';
import wixWindow from 'wix-window';

/**
 * Initialize AI Index page
 */
$w.onReady(function () {
  console.log('AI Index page loaded');

  // Load verification badge if element exists
  if ($w('#aiIndexBadge')) {
    loadVerificationBadge();
  }

  // Set up publish button
  if ($w('#publishButton')) {
    $w('#publishButton').onClick(() => handlePublish());
  }

  // Set up refresh button
  if ($w('#refreshButton')) {
    $w('#refreshButton').onClick(() => loadStatus());
  }

  // Load initial status
  loadStatus();
});

/**
 * Load verification badge
 */
async function loadVerificationBadge() {
  try {
    const response = await fetch('/_functions/ai-index.json');
    if (response.ok) {
      const data = await response.json();
      if (data && data.version) {
        $w('#aiIndexBadge').html = `
          <div style="display: inline-flex; align-items: center; padding: 8px 16px;
                      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      border-radius: 8px; color: white; font-family: sans-serif;">
            <svg width="20" height="20" viewBox="0 0 20 20" style="margin-right: 8px;">
              <path fill="currentColor" d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm-2 15l-5-5 1.41-1.41L8 12.17l7.59-7.59L17 6l-9 9z"/>
            </svg>
            <span style="font-weight: 600;">AI Index Verified</span>
          </div>
        `;
      }
    }
  } catch (error) {
    console.error('Error loading verification badge:', error);
  }
}

/**
 * Load current status
 */
async function loadStatus() {
  try {
    if ($w('#statusText')) {
      $w('#statusText').text = 'Loading...';
    }

    const response = await fetch('/_functions/ai-index.json');
    const status = response.ok ? 'Active' : 'Not configured';
    const statusColor = response.ok ? '#00C853' : '#FF6B6B';

    if ($w('#statusText')) {
      $w('#statusText').text = status;
      $w('#statusText').style.color = statusColor;
    }

    if (response.ok && $w('#lastUpdated')) {
      const data = await response.json();
      const lastUpdate = new Date(data.metadata.last_updated);
      $w('#lastUpdated').text = `Last updated: ${lastUpdate.toLocaleString()}`;
    }

    if ($w('#pageCount') && response.ok) {
      const data = await response.json();
      $w('#pageCount').text = `${data.pages.length} pages indexed`;
    }
  } catch (error) {
    console.error('Error loading status:', error);
    if ($w('#statusText')) {
      $w('#statusText').text = 'Error loading status';
      $w('#statusText').style.color = '#FF6B6B';
    }
  }
}

/**
 * Handle publish button click
 */
async function handlePublish() {
  if ($w('#publishButton')) {
    $w('#publishButton').disable();
    $w('#publishButton').label = 'Publishing...';
  }

  try {
    // Call backend function to publish
    const { publishToAPI, generateAIIndex } = await import('backend/aiindex');
    const aiIndex = await generateAIIndex();
    const result = await publishToAPI(aiIndex);

    if ($w('#publishButton')) {
      $w('#publishButton').label = 'Published!';
    }

    // Show success message
    wixWindow.lightbox.open('SuccessLightbox', {
      message: 'Successfully published to AI Index!',
      details: result
    });

    // Reload status after 2 seconds
    setTimeout(() => {
      loadStatus();
      if ($w('#publishButton')) {
        $w('#publishButton').enable();
        $w('#publishButton').label = 'Publish Now';
      }
    }, 2000);
  } catch (error) {
    console.error('Error publishing:', error);

    if ($w('#publishButton')) {
      $w('#publishButton').enable();
      $w('#publishButton').label = 'Publish Now';
    }

    // Show error message
    wixWindow.lightbox.open('ErrorLightbox', {
      message: 'Failed to publish',
      error: error.message
    });
  }
}

/**
 * Export for use in other pages
 */
export function getAIIndexUrl() {
  const siteUrl = wixWindow.rendering.env === 'browser'
    ? window.location.origin
    : 'https://yoursite.com';
  return `${siteUrl}/_functions/ai-index.json`;
}

/**
 * Check if AI Index is active
 */
export async function isAIIndexActive() {
  try {
    const response = await fetch('/_functions/ai-index.json');
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Get AI Index data
 */
export async function getAIIndexData() {
  try {
    const response = await fetch('/_functions/ai-index.json');
    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error fetching AI Index data:', error);
    return null;
  }
}
