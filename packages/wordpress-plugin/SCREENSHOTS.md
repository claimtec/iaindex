# IAIndex WordPress Plugin - Screenshots & UI Reference

This document describes the visual interface of the plugin for reference purposes.

## Admin Interface Layouts

### 1. Settings Page - Configuration Section

**Location**: Settings → IAIndex

**Layout**: Two-column grid layout with main content (left) and sidebar (right)

**Main Content - Configuration Card**:
```
┌─────────────────────────────────────────────────────────┐
│ Configuration                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Domain                                                  │
│ ┌─────────────────────────────────────────────────┐   │
│ │ https://yourdomain.com                          │   │
│ └─────────────────────────────────────────────────┘   │
│ Your website domain (e.g., https://example.com)       │
│                                                         │
│ API Key                                                 │
│ ┌─────────────────────────────────────────────────┐   │
│ │ ••••••••••••••••••••                            │ 👁 │
│ └─────────────────────────────────────────────────┘   │
│ Your IAIndex API key for authentication               │
│                                                         │
│ ☑ Automatically regenerate index when posts are       │
│   published                                             │
│                                                         │
│ ┌──────────────────┐                                   │
│ │  Save Settings   │                                   │
│ └──────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

### 2. Settings Page - Domain Verification Section

```
┌─────────────────────────────────────────────────────────┐
│ Domain Verification                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ ✓ Domain verified successfully!                 │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ OR (if not verified):                                   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ ⚠ Domain not verified yet                       │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌────────────────────┐  ⟳                             │
│ │ Verify Domain Now  │                                 │
│ └────────────────────┘                                 │
│                                                         │
│ [Success/Error message appears here after clicking]    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. Settings Page - Index Management Section

```
┌─────────────────────────────────────────────────────────┐
│ Index Management                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Index Status:        ✓ Index file exists              │
│                                                         │
│ Last Generated:      January 17, 2025 at 12:00 PM      │
│                                                         │
│ Entries Count:       42                                 │
│                                                         │
│ Index URL:           https://example.com/.well-known    │
│                      /iaindex.json  [View]              │
│                                                         │
│ ┌──────────────────────┐  ⟳                           │
│ │ Generate Index Now   │                               │
│ └──────────────────────┘                               │
│                                                         │
│ [Success/Error message appears here after clicking]    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4. Settings Page - Sidebar

```
┌───────────────────────────────┐
│ About IAIndex                 │
├───────────────────────────────┤
│ IAIndex helps track and       │
│ verify AI-generated content   │
│ with blockchain-backed        │
│ receipts.                     │
│                               │
│ Features                      │
│ • Automatic index generation  │
│ • Domain verification         │
│ • Receipt tracking            │
│ • API integration             │
│                               │
│ ┌────────────┐               │
│ │ Learn More │               │
│ └────────────┘               │
└───────────────────────────────┘

┌───────────────────────────────┐
│ Need Help?                    │
├───────────────────────────────┤
│ Check out our documentation   │
│ or contact support.           │
│                               │
│ Documentation →               │
└───────────────────────────────┘
```

### 5. Dashboard Widget

**Location**: WordPress Dashboard

**Widget Name**: IAIndex Status

```
┌─────────────────────────────────────────────────────────┐
│ IAIndex Status                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│ │ ✓       │  │ 📄      │  │ 🎫      │                │
│ │ Verified│  │ 42      │  │ 15      │                │
│ │         │  │ Entries │  │ Receipts│                │
│ └─────────┘  └─────────┘  └─────────┘                │
│                                                         │
│ Last Index Generation: 2 hours ago                     │
│                                                         │
│ ┌─────────────┐ ┌──────────┐ ┌──────────────┐        │
│ │ Manage      │ │ View     │ │ View         │        │
│ │ Settings    │ │ Index    │ │ Receipts     │        │
│ └─────────────┘ └──────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

**Widget (Not Verified State)**:
```
┌─────────────────────────────────────────────────────────┐
│ IAIndex Status                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│ │ ⚠       │  │ 📄      │  │ 🎫      │                │
│ │ Not     │  │ 42      │  │ 0       │                │
│ │ Verified│  │ Entries │  │ Receipts│                │
│ └─────────┘  └─────────┘  └─────────┘                │
│                                                         │
│ ℹ Your domain needs to be verified to use IAIndex      │
│   features.                                             │
│                                                         │
│ ┌─────────────┐ ┌──────────┐ ┌──────────────┐        │
│ │ Manage      │ │ View     │ │ View         │        │
│ │ Settings    │ │ Index    │ │ Receipts     │        │
│ └─────────────┘ └──────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 6. Receipts List Page

**Location**: Tools → IAIndex Receipts

```
┌──────────────────────────────────────────────────────────────────────┐
│ IAIndex Receipts                                  [Add New] [Search] │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ☐  Receipt ID         Content URL         Provider    Timestamp    │
│ ───────────────────────────────────────────────────────────────────  │
│ ☐  receipt-123        example.com/post    OpenAI      2025-01-17... │
│ ☐  receipt-124        example.com/about   Anthropic   2025-01-17... │
│ ☐  receipt-125        example.com/news    Google      2025-01-16... │
│                                                                      │
│ [< Previous]  1 2 3 ... 10  [Next >]                                │
└──────────────────────────────────────────────────────────────────────┘
```

### 7. AJAX Success Message (Domain Verification)

```
┌─────────────────────────────────────────────────────────┐
│ ✓ Domain verified successfully!                        │
│                                                         │
│   Response data:                                        │
│   • Domain: example.com                                │
│   • Status: verified                                    │
│   • Timestamp: 2025-01-17T12:00:00Z                    │
└─────────────────────────────────────────────────────────┘
```

### 8. AJAX Success Message (Index Generation)

```
┌─────────────────────────────────────────────────────────┐
│ ✓ Index generated successfully!                        │
│                                                         │
│   • Entries: 42                                        │
│   • File: wp-content/uploads/iaindex/iaindex.json     │
│   • URL: https://example.com/.well-known/iaindex.json │
└─────────────────────────────────────────────────────────┘
```

### 9. AJAX Error Message

```
┌─────────────────────────────────────────────────────────┐
│ ✗ Verification failed                                   │
│                                                         │
│   Error: Index file not accessible. Please ensure the  │
│   file exists and is publicly accessible.              │
└─────────────────────────────────────────────────────────┘
```

## Color Scheme

The plugin uses WordPress admin color scheme with custom accents:

- **Success States**: `#46b450` (green)
- **Warning States**: `#ffb900` (yellow/orange)
- **Error States**: `#dc3232` (red)
- **Info States**: `#0073aa` (blue)
- **Accent**: `#826eb4` (purple for receipts)

## Status Indicators

### Verified Status
```
┌────────────────────────┐
│ ✓ Verified            │  Green background (#d4edda)
│                        │  Green text (#155724)
└────────────────────────┘
```

### Not Verified Status
```
┌────────────────────────┐
│ ⚠ Not Verified        │  Yellow background (#fff3cd)
│                        │  Yellow text (#856404)
└────────────────────────┘
```

### Error Status
```
┌────────────────────────┐
│ ✗ Error               │  Red background (#f8d7da)
│                        │  Red text (#721c24)
└────────────────────────┘
```

## Interactive Elements

### Buttons

**Primary Button** (Generate, Verify, Save):
```
┌──────────────────┐
│  Primary Action  │  Blue background (#0073aa)
└──────────────────┘  White text
```

**Secondary Button** (View, Cancel):
```
┌──────────────────┐
│ Secondary Action │  Light gray background (#f3f5f6)
└──────────────────┘  Dark text
```

**Small Button**:
```
┌────────┐
│  View  │  Smaller padding, 12px font
└────────┘
```

### Loading States

**Spinner** (shows during AJAX):
```
┌──────────────────┐  ⟳
│  Verify Domain   │     ← Spinning indicator
└──────────────────┘
```

**Button Disabled State**:
```
┌──────────────────┐
│  Please Wait...  │  Grayed out, not clickable
└──────────────────┘
```

### Form Fields

**Text Input**:
```
┌─────────────────────────────────────────────────┐
│ https://example.com                             │
└─────────────────────────────────────────────────┘
```

**Password Input** (API Key):
```
┌─────────────────────────────────────────────┐ 👁
│ ••••••••••••••••••••••••                    │
└─────────────────────────────────────────────┘
  ↑ Click eye icon to toggle visibility
```

**Checkbox**:
```
☑ Automatically regenerate index when posts are published
```

**Code Block** (URLs, IDs):
```
┌─────────────────────────────────────────────────┐
│ https://example.com/.well-known/iaindex.json   │  Click to copy
└─────────────────────────────────────────────────┘
```

## Responsive Behavior

### Desktop (> 1024px)
- Two-column layout (main content + sidebar)
- Dashboard widget shows 3 columns of stats
- Full button labels

### Tablet (768px - 1024px)
- Single column layout (sidebar moves below)
- Dashboard widget shows 2 columns of stats
- Full button labels

### Mobile (< 768px)
- Single column layout
- Dashboard widget shows 1 column (stacked)
- Buttons stack vertically
- Full-width buttons

## Iconography

The plugin uses WordPress Dashicons:

- ✓ (dashicons-yes-alt) - Success, verified
- ⚠ (dashicons-warning) - Warning, not verified
- ✗ (dashicons-dismiss) - Error, failed
- ℹ (dashicons-info) - Information
- 📄 (dashicons-media-document) - Index entries
- 🎫 (dashicons-tickets-alt) - Receipts
- 👁 (dashicons-visibility) - Show password
- 🔒 (dashicons-hidden) - Hide password
- ⟳ (spinner) - Loading

## Accessibility Features

- **ARIA Labels**: All buttons and interactive elements have descriptive labels
- **Color Contrast**: All text meets WCAG AA standards
- **Keyboard Navigation**: Tab order follows logical flow
- **Focus States**: Visible focus indicators on all interactive elements
- **Screen Reader Text**: Hidden labels for icon-only buttons
- **Semantic HTML**: Proper heading hierarchy and landmarks

## Animations

### AJAX Loading
- Fade in spinner on button click
- Pulse animation during loading
- Fade out spinner on completion

### Success/Error Messages
- Slide down when displayed
- Auto-fade out after 5 seconds (success only)
- Click to dismiss

### Page Transitions
- Smooth 2-second reload after successful verification
- Smooth 3-second reload after successful generation

## Copy-to-Clipboard Feature

All code blocks (URLs, file paths) are clickable:

```
Initial State:
┌─────────────────────────────────────────┐
│ https://example.com/.well-known/...    │  ← Click to copy
└─────────────────────────────────────────┘

After Click:
┌─────────────────────────────────────────┐
│ Copied!                                 │  ← Green background
└─────────────────────────────────────────┘
                  ↓
                (2 seconds)
                  ↓
┌─────────────────────────────────────────┐
│ https://example.com/.well-known/...    │  ← Returns to normal
└─────────────────────────────────────────┘
```

## Plugin Links

On the Plugins page, the plugin shows:

```
IAIndex Integration
By ClaimTec | Version 1.0.0

[Settings] | Deactivate | Edit

Integration with IAIndex for AI content tracking and receipts
```

## Menu Items

The plugin adds items to:

1. **Settings Menu**:
   - Settings → IAIndex

2. **Tools Menu**:
   - Tools → IAIndex Receipts

3. **Dashboard**:
   - Widget: "IAIndex Status"

---

## UI/UX Best Practices Implemented

✅ **Consistency**: Matches WordPress admin design language
✅ **Feedback**: Immediate visual feedback for all actions
✅ **Error Prevention**: Confirmation dialogs for destructive actions
✅ **Help**: Contextual help text and documentation links
✅ **Accessibility**: WCAG AA compliant
✅ **Responsiveness**: Works on all screen sizes
✅ **Performance**: Fast loading, efficient AJAX
✅ **Progressive Enhancement**: Works with JS disabled (basic functionality)

---

This visual reference provides a complete overview of the plugin's user interface without requiring actual screenshots.
