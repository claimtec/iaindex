/**
 * Bubble.io Element: AIIndex Badge
 * Displays a verification badge for AIIndex
 */

function(instance, properties) {
  const domain = properties.domain || window.location.hostname;
  const theme = properties.theme || 'dark';
  const size = properties.size || 'medium';
  const position = properties.position || 'bottom-right';
  const showPulse = properties.show_pulse || false;

  // Badge dimensions based on size
  const dimensions = {
    small: { padding: '6px 10px', fontSize: '11px', iconSize: '12px' },
    medium: { padding: '10px 16px', fontSize: '13px', iconSize: '16px' },
    large: { padding: '12px 20px', fontSize: '15px', iconSize: '18px' }
  };

  // Theme colors
  const themes = {
    dark: {
      background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)',
      color: '#ffffff',
      border: 'none'
    },
    light: {
      background: 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
      color: '#000000',
      border: '1px solid #e0e0e0'
    },
    purple: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: '#ffffff',
      border: 'none'
    },
    blue: {
      background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      color: '#ffffff',
      border: 'none'
    },
    green: {
      background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      color: '#000000',
      border: 'none'
    }
  };

  // Position styles
  const positions = {
    'top-left': { top: '20px', left: '20px' },
    'top-right': { top: '20px', right: '20px' },
    'bottom-left': { bottom: '20px', left: '20px' },
    'bottom-right': { bottom: '20px', right: '20px' }
  };

  const currentTheme = themes[theme] || themes.dark;
  const currentDimensions = dimensions[size] || dimensions.medium;
  const currentPosition = positions[position] || positions['bottom-right'];

  // Create badge HTML
  const badgeHTML = `
    <a href="https://aiindex.org/verify/${domain}"
       target="_blank"
       rel="noopener"
       style="
         display: inline-flex;
         align-items: center;
         padding: ${currentDimensions.padding};
         background: ${currentTheme.background};
         color: ${currentTheme.color};
         text-decoration: none;
         border-radius: 6px;
         font-size: ${currentDimensions.fontSize};
         font-weight: 600;
         font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
         transition: all 0.3s ease;
         ${currentTheme.border};
         ${showPulse ? 'animation: aiindex-pulse 2s ease-in-out infinite;' : ''}
       "
       onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(0, 0, 0, 0.2)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0, 0, 0, 0.15)';">
      <svg width="${currentDimensions.iconSize}" height="${currentDimensions.iconSize}"
           viewBox="0 0 24 24" fill="none" style="margin-right: 8px; flex-shrink: 0;">
        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      AI Index Verified
    </a>
  `;

  // Add pulse animation keyframes if enabled
  const animationCSS = showPulse ? `
    <style>
      @keyframes aiindex-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
      }
    </style>
  ` : '';

  // Render badge in the container
  instance.canvas.empty();
  instance.canvas.append(animationCSS + badgeHTML);

  // Set container position if not inline
  if (properties.position !== 'inline') {
    instance.canvas.css({
      position: 'fixed',
      zIndex: 9999,
      ...currentPosition
    });
  }

  // Update instance data
  instance.publishState('domain', domain);
  instance.publishState('theme', theme);
  instance.publishState('visible', true);
}

// Element update function
function update(instance, properties) {
  // Re-render the badge when properties change
  render(instance, properties);
}

// Element reset function
function reset(instance) {
  instance.canvas.empty();
  instance.publishState('visible', false);
}

// Export element functions
return {
  initialize: function(instance, properties) {
    render(instance, properties);
  },
  update: update,
  reset: reset
};
