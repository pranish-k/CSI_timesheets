# CSI Timesheet Generator — UI Design Guide

## Design Philosophy

**Modern + Brutalist + Y2K Hybrid**

A blend of three aesthetics:
- **Modern**: Clean cards, subtle shadows, polished feel
- **Brutalist**: Bold borders, strong structure, no-nonsense typography
- **Y2K**: Window chrome, title bars, status bars, nostalgic UI elements

---

## Color Palette

### Primary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Background** | `#1F2937` | `31, 41, 55` | Main app background |
| **Card/Surface** | `#111827` | `17, 24, 39` | Cards, panels, inputs |
| **Accent** | `#14B8A6` | `20, 184, 166` | Buttons, highlights, active states |
| **Text Primary** | `#F3F4F6` | `243, 244, 246` | Main text, headings |
| **Text Secondary** | `#9CA3AF` | `156, 163, 175` | Labels, captions, muted text |
| **Border** | `#374151` | `55, 65, 81` | Card borders, dividers |

### Color Swatches

```
┌─────────────────────────────────────────────────────────┐
│  ████████   ████████   ████████   ████████   ████████  │
│  #1F2937    #111827    #14B8A6    #F3F4F6    #374151   │
│  BG         Surface    Accent     Text       Border    │
└─────────────────────────────────────────────────────────┘
```

### Semantic Colors

| State | Color | Hex |
|-------|-------|-----|
| Success | Teal (accent) | `#14B8A6` |
| Error | Soft Red | `#EF4444` |
| Warning | Amber | `#F59E0B` |
| Info | Accent Muted | `#0D9488` |

---

## Typography

### Font Stack

```css
font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
```

### Scale

| Element | Size | Weight | Tracking |
|---------|------|--------|----------|
| Window Title | 13px | 600 | 0 |
| Section Header | 11px | 600 | 1.5px (uppercase) |
| Card Value (Large) | 26px | 700 | 0 |
| Card Value (Date) | 18px | 700 | 0 |
| Body Text | 13px | 400 | 0 |
| Label | 11px | 400 | 1.5px (uppercase) |
| Caption/Status | 11px | 400 | 0 |

### Text Colors

- **Primary text**: `#F3F4F6`
- **Secondary/Labels**: `#9CA3AF`
- **Accent text**: `#14B8A6`
- **On accent (button text)**: `#111827`

---

## Spacing

### Base Unit

`8px` — all spacing should be multiples of 8.

### Spacing Scale

| Name | Value | Usage |
|------|-------|-------|
| `xs` | 4px | Tight gaps, icon padding |
| `sm` | 8px | Between related elements |
| `md` | 16px | Card padding, section gaps |
| `lg` | 24px | Content padding, major sections |
| `xl` | 32px | Page margins, large gaps |

### Component Spacing

```
Window padding:      0 (handled by content areas)
Content padding:     24px
Card padding:        18px
Card gap:            16px
Section gap:         20px
```

---

## Borders

### Style

- **Width**: 2px (primary), 1px (subtle)
- **Style**: Solid
- **Color**: `#374151`

### Accent Border

Title bar bottom border uses accent color:
```css
border-bottom: 2px solid #14B8A6;
```

### Card Borders

```css
border: 2px solid #374151;
```

---

## Components

### Window Container

The main application window with Y2K-style chrome.

```
┌─[ Title Bar ]────────────────────────────────[−][□][×]─┐
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Accent border
├────────────────────────────────────────────────────────┤
│                                                        │
│                    [ Content ]                         │
│                                                        │
├────────────────────────────────────────────────────────┤
│  Status Bar                                            │
└────────────────────────────────────────────────────────┘
```

**Specs:**
```css
.window {
    background: #1F2937;
    border: 2px solid #374151;
}

.title-bar {
    background: #111827;
    border-bottom: 2px solid #14B8A6;
    padding: 10px 15px;
}

.window-controls span {
    width: 14px;
    height: 14px;
    border: 1px solid #6B7280;
    color: #6B7280;
}
```

---

### Cards

Used for displaying data groups (employees count, date, etc.)

```
┌──────────────────────┐
│  LABEL               │  ← Accent color, uppercase
│  Value               │  ← Primary text, large
└──────────────────────┘
```

**Specs:**
```css
.card {
    background: #111827;
    border: 2px solid #374151;
    padding: 18px;
}

.card-label {
    color: #14B8A6;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

.card-value {
    color: #F3F4F6;
    font-size: 26px;
    font-weight: 700;
}
```

---

### Buttons

Primary action buttons with solid accent fill.

```
┌─────────────────────────┐
│   GENERATE TIMESHEETS   │
└─────────────────────────┘
```

**Specs:**
```css
.btn-primary {
    background: #14B8A6;
    color: #111827;
    border: none;
    padding: 14px 35px;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    cursor: pointer;
}

.btn-primary:hover {
    background: #0D9488;
}

.btn-primary:active {
    background: #0F766E;
}
```

**Secondary Button (outline):**
```css
.btn-secondary {
    background: transparent;
    color: #14B8A6;
    border: 2px solid #14B8A6;
    padding: 12px 30px;
}

.btn-secondary:hover {
    background: rgba(20, 184, 166, 0.1);
}
```

---

### Progress Bar

Shows generation progress.

```
┌────────────────────────────────────────┐
│████████████████████░░░░░░░░░░░░░░░░░░░░│  65%
└────────────────────────────────────────┘
```

**Specs:**
```css
.progress-bar {
    height: 8px;
    background: #111827;
    border: 1px solid #374151;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #14B8A6;
    transition: width 0.3s ease;
}
```

---

### Employee List / Table

Displays employee data in rows.

```
┌─────────────────────────────────────────────────────┐
│  NAME                          WORK AREA            │  ← Header
├─────────────────────────────────────────────────────┤
│  Rached, Brianna               Archway/Social Media │
│  Glisson, Sarah                CCEC                 │
│  Davis, Savannah               CCEC                 │
└─────────────────────────────────────────────────────┘
```

**Specs:**
```css
.list-header {
    color: #14B8A6;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding-bottom: 10px;
    border-bottom: 1px solid #374151;
}

.list-row {
    padding: 10px 0;
    border-bottom: 1px solid #374151;
    color: #F3F4F6;
    font-size: 13px;
}

.list-row:hover {
    background: rgba(20, 184, 166, 0.05);
}

.list-row.selected {
    background: rgba(20, 184, 166, 0.15);
    border-left: 3px solid #14B8A6;
}
```

---

### Input Fields

Text inputs and date pickers.

```
┌──────────────────────────────────────┐
│  01/31/2026                       ▼  │
└──────────────────────────────────────┘
```

**Specs:**
```css
.input {
    background: #111827;
    border: 2px solid #374151;
    color: #F3F4F6;
    padding: 12px 15px;
    font-size: 13px;
}

.input:focus {
    border-color: #14B8A6;
    outline: none;
}

.input::placeholder {
    color: #6B7280;
}
```

---

### Status Bar

Bottom bar showing app state and metadata.

```
┌────────────────────────────────────────────────────────┐
│  Ready                                v1.0 — Pranish   │
└────────────────────────────────────────────────────────┘
```

**Specs:**
```css
.status-bar {
    background: #111827;
    border-top: 1px solid #374151;
    padding: 8px 15px;
    font-size: 11px;
    color: #6B7280;
    display: flex;
    justify-content: space-between;
}
```

---

## Layout Structure

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│  CSI Timesheet Generator                         [−][□][×]  │
│─────────────────────────────────────────────────────────────│
│                                                             │
│   ┌─────────────────────┐     ┌─────────────────────┐       │
│   │  EMPLOYEES          │     │  START DATE         │       │
│   │  42                 │     │  01/31/2026         │       │
│   └─────────────────────┘     └─────────────────────┘       │
│                                                             │
│   ┌─────────────────────┐     ┌─────────────────────┐       │
│   │  OUTPUT FOLDER      │     │                     │       │
│   │  C:\Timesheets\     │     │  [ BROWSE ]         │       │
│   └─────────────────────┘     └─────────────────────┘       │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  EMPLOYEE LIST                           [ + ADD ]  │   │
│   │  ─────────────────────────────────────────────────  │   │
│   │  NAME                      │ WORK AREA             │   │
│   │  Rached, Brianna           │ Archway/Social Media  │   │
│   │  Glisson, Sarah            │ CCEC                  │   │
│   │  Davis, Savannah           │ CCEC                  │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   [ GENERATE TIMESHEETS ]                                   │
│                                                             │
│   Progress ─────────────────────────────────────────────    │
│   ████████████████████░░░░░░░░░░░░░░░░░░░░  65%             │
│                                                             │
│─────────────────────────────────────────────────────────────│
│  Ready                                      v1.0 — Pranish  │
└─────────────────────────────────────────────────────────────┘
```

---

## Iconography

Use simple, monoline icons. Recommended sources:
- Lucide Icons (https://lucide.dev)
- Feather Icons (https://feathericons.com)

### Common Icons

| Action | Icon |
|--------|------|
| Add | `+` or plus icon |
| Delete | `×` or trash icon |
| Edit | Pencil |
| Browse folder | Folder |
| Calendar | Calendar |
| Minimize | `−` |
| Maximize | `□` |
| Close | `×` |

**Icon Color:**
- Default: `#9CA3AF`
- Hover: `#14B8A6`
- On accent button: `#111827`

---

## States

### Interactive States

| State | Change |
|-------|--------|
| **Default** | Base styles |
| **Hover** | Lighten accent or add subtle bg |
| **Active/Pressed** | Darken accent |
| **Focus** | Accent border |
| **Disabled** | 50% opacity, no pointer |

### Button States Example

```css
.btn { background: #14B8A6; }
.btn:hover { background: #0D9488; }
.btn:active { background: #0F766E; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
```

### Input States

```css
.input { border-color: #374151; }
.input:focus { border-color: #14B8A6; }
.input:invalid { border-color: #EF4444; }
```

---

## Animation

Keep animations subtle and functional.

### Timing

```css
--transition-fast: 150ms ease;
--transition-normal: 250ms ease;
--transition-slow: 400ms ease;
```

### Common Animations

```css
/* Button hover */
.btn {
    transition: background 150ms ease;
}

/* Progress bar */
.progress-fill {
    transition: width 300ms ease;
}

/* List row hover */
.list-row {
    transition: background 150ms ease;
}
```

---

## Do's and Don'ts

### ✅ Do

- Use the accent color sparingly — for CTAs and highlights
- Maintain strong visual hierarchy with type scale
- Keep borders consistent (2px for containers, 1px for subtle dividers)
- Use uppercase + letter-spacing for labels
- Include status feedback (status bar, progress)

### ❌ Don't

- Overuse the teal accent — it should draw attention
- Use rounded corners (keep brutalist sharp edges)
- Add drop shadows (we use borders for depth)
- Mix too many font weights
- Forget hover/focus states

---

## Quick Reference

```
Background:     #1F2937
Surface:        #111827
Accent:         #14B8A6
Text:           #F3F4F6
Text Muted:     #9CA3AF
Border:         #374151

Font:           Segoe UI / system-ui
Border Width:   2px
Spacing Unit:   8px
```

---

*CSI Timesheet Generator — Design Guide v1.0*
*Created for Pranish*