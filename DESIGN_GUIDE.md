# Smar-Test Design Guide

## Brand Identity

### Name & Meaning
**Smar-Test** = **Smart** + **Test** = **Smartest**

A clever wordplay that communicates:
- Intelligence (Smart)
- Purpose (Test)
- Excellence (Smartest)

### Logo & Icon
- **Symbol**: ⚡ (Lightning Bolt)
- **Meaning**: Speed, power, intelligence, innovation
- **Color**: Gradient (Indigo → Purple → Cyan)

---

## Color System

### Primary Palette

```
┌─────────────────────────────────────────┐
│ Primary (Indigo)    │ #6366f1 │ ███████ │
│ Primary Dark        │ #4f46e5 │ ███████ │
│ Accent (Purple)     │ #8b5cf6 │ ███████ │
│ Accent 2 (Cyan)     │ #06b6d4 │ ███████ │
└─────────────────────────────────────────┘
```

### Semantic Colors

```
┌─────────────────────────────────────────┐
│ Success (Emerald)   │ #10b981 │ ███████ │
│ Warning (Amber)     │ #f59e0b │ ███████ │
│ Error (Red)         │ #ef4444 │ ███████ │
│ Info (Blue)         │ #3b82f6 │ ███████ │
└─────────────────────────────────────────┘
```

### Neutral Colors

```
┌─────────────────────────────────────────┐
│ Text                │ #0f172a │ ███████ │
│ Text Secondary      │ #475569 │ ███████ │
│ Text Muted          │ #94a3b8 │ ███████ │
│ Background          │ #f8fafc │ ███████ │
│ Surface (White)     │ #ffffff │ ███████ │
│ Border              │ #e2e8f0 │ ███████ │
└─────────────────────────────────────────┘
```

---

## Typography

### Font Family
**Inter** - Modern, clean, professional sans-serif

```
Primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

### Font Sizes

```
H1 (Page Title)      : 2.25rem (36px) - Bold 700
H2 (Section)         : 1.75rem (28px) - Bold 700
H3 (Subsection)      : 1.375rem (22px) - Bold 600
Body                 : 1rem (16px) - Regular 400
Small Text           : 0.875rem (14px) - Regular 400
Caption              : 0.75rem (12px) - Regular 400
```

### Font Weights

```
Regular      : 400
Medium       : 500
Semibold     : 600
Bold         : 700
Extra Bold   : 800
```

---

## Gradients

### Primary Brand Gradient

```css
background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
```

**Usage:**
- Main headings
- Brand logo
- Primary buttons
- Progress bars
- Status indicators

### Success Gradient

```css
background: linear-gradient(135deg, #10b981 0%, #059669 100%);
```

### Warning Gradient

```css
background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
```

### Error Gradient

```css
background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
```

---

## UI Components

### Buttons

**Primary Button:**
```
┌──────────────────────┐
│  Primary Button      │ ← Gradient background
└──────────────────────┘
   Hover: Lift + Glow
```

**Styles:**
- Background: Gradient (Indigo → Purple)
- Hover: Gradient shift + elevation
- Shadow: 0 2px 4px rgba(99,102,241,0.2)
- Border Radius: 8px
- Padding: 0.625rem 1.25rem

**Secondary Button:**
```
┌──────────────────────┐
│  Secondary Button    │ ← Transparent bg, colored border
└──────────────────────┘
   Hover: Fill with color
```

### Cards

**Standard Card:**
```
┌────────────────────────────────────┐
│  Card Header                       │
│  ────────────────────────────────  │
│                                    │
│  Card Content Here                 │
│                                    │
└────────────────────────────────────┘
```

**Styling:**
- Background: White (#ffffff)
- Border: 1px solid #e2e8f0
- Border Radius: 12px
- Shadow: 0 4px 6px rgba(0,0,0,0.1)
- Hover: Elevation increases

**Gradient Card (Special):**
```
┌────────────────────────────────────┐
│                                    │ ← Gradient background
│  Gradient Card Content             │
│                                    │
└────────────────────────────────────┘
```

### Status Badges

**Connected:**
```
 ✅ Connected  ← Green gradient
```

**Disconnected:**
```
 ❌ Not Connected  ← Red gradient
```

**Info:**
```
 ℹ️ Information  ← Blue gradient
```

### Priority Badges

```
 High    ← Red gradient
 Medium  ← Amber gradient
 Low     ← Green gradient
```

---

## Spacing System

```
0.25rem = 4px   (tight spacing)
0.5rem  = 8px   (small spacing)
0.75rem = 12px  (medium spacing)
1rem    = 16px  (standard spacing)
1.25rem = 20px  (large spacing)
1.5rem  = 24px  (extra large spacing)
2rem    = 32px  (section spacing)
```

---

## Border Radius

```
Small Components : 4px
Inputs/Fields    : 8px
Cards/Containers : 12px
Pills/Badges     : 20px (rounded)
Circles          : 50% (full round)
```

---

## Shadows

### Elevation Levels

**Level 1 (Subtle):**
```css
box-shadow: 0 1px 3px rgba(0,0,0,0.1);
```

**Level 2 (Standard):**
```css
box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
```

**Level 3 (Elevated):**
```css
box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
```

**Level 4 (Floating):**
```css
box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
```

**Colored Shadow (Brand):**
```css
box-shadow: 0 4px 12px rgba(99,102,241,0.3);
```

---

## Animations

### Transitions

**Standard:**
```css
transition: all 0.3s ease;
```

**Fast:**
```css
transition: all 0.2s ease;
```

**Slow:**
```css
transition: all 0.5s ease;
```

### Hover Effects

**Button Lift:**
```css
transform: translateY(-1px);
```

**Card Lift:**
```css
transform: translateY(-2px);
```

**Rule Item Slide:**
```css
transform: translateX(4px);
```

### Pulse Animation

```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

**Usage:** Status dots, loading indicators

---

## Layout

### Container Max Width
```
Standard: 1400px
Compact: 1200px
```

### Grid System

**Two Columns:**
```
┌─────────────────┬──────────┐
│                 │          │
│  Main (70%)     │  Side    │
│                 │  (30%)   │
└─────────────────┴──────────┘
```

**Three Columns:**
```
┌──────────┬──────────┬──────────┐
│          │          │          │
│   33%    │   33%    │   33%    │
│          │          │          │
└──────────┴──────────┴──────────┘
```

### Sidebar
```
Width: 300px (Streamlit default)
Background: Linear gradient (White → Light Gray)
Border: 1px solid #e2e8f0
```

---

## Brand Header (Homepage)

```
       ⚡ Smar-Test
Smart + Test = Smartest Test Case Generation
AI-Powered Test Case Generation for Modern QA Teams
```

**Styling:**
- Centered alignment
- H1: 3.5rem gradient text
- Tagline: 1.125rem medium gray
- Subtitle: 0.875rem light gray
- Padding: 1rem 0 2rem 0

---

## Sidebar Logo

```
    ⚡ Smar-Test
  Smart + Test = Smartest
```

**Styling:**
- Centered
- H2: 1.75rem gradient text
- Caption: 0.7rem light gray
- Padding: 0.5rem 0 1rem 0

---

## Status Indicators

### Connection Status

**Connected:**
```
┌──────────────────────────┐
│ ⚫ ✅ Connected          │ ← Pulsing green dot
│ Provider: 🖥️ Ollama     │
│ Model: qwen2.5:7b        │
│ Access: Local            │
└──────────────────────────┘
```

**Disconnected:**
```
┌──────────────────────────┐
│ ⚫ ❌ Not Connected      │ ← Pulsing red dot
│ Provider: 🖥️ Ollama     │
│ Model: qwen2.5:7b        │
│ Access: Local            │
│ 💡 Configure in Settings │
└──────────────────────────┘
```

---

## Accessibility

### Color Contrast

```
Text on White       : 13.08:1 (AAA)
Text Secondary      : 7.19:1 (AA)
Text Muted          : 4.51:1 (AA)
Primary on White    : 4.67:1 (AA)
```

### Focus Indicators

**Input Focus:**
```css
border-color: #6366f1;
box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
```

**Button Focus:**
```css
outline: 2px solid #6366f1;
outline-offset: 2px;
```

---

## Usage Examples

### Page Title
```html
<h1 style="background: gradient; ...">
    ⚡ Smar-Test
</h1>
```

### Success Message
```html
<div class="success-box">
    ✓ Test cases generated successfully!
</div>
```

### Info Message
```html
<div class="info-box">
    ℹ️ Select a client context for better results
</div>
```

### Status Badge
```html
<span class="status-badge status-success">
    Active
</span>
```

### Priority Badge
```html
<span class="priority-high">High</span>
<span class="priority-medium">Medium</span>
<span class="priority-low">Low</span>
```

---

## Best Practices

### DO ✓
- Use gradients for brand elements
- Maintain consistent spacing
- Follow the color system
- Use Inter font throughout
- Keep animations subtle
- Provide hover feedback
- Use semantic colors correctly

### DON'T ✗
- Mix different color systems
- Use too many gradients
- Create jarring animations
- Ignore accessibility
- Use random spacing values
- Mix font families
- Overuse bold text

---

## Component Library

### Inputs

**Text Input:**
- Border: 2px solid #e2e8f0
- Focus: Border #6366f1 + glow
- Border Radius: 8px
- Padding: 0.625rem 0.875rem

**Select Dropdown:**
- Same as text input
- Dropdown: White bg, shadow

**File Uploader:**
- Dashed border: 2px dashed #e2e8f0
- Hover: Gradient background (subtle)
- Border Radius: 12px
- Padding: 2rem

### Progress Bar

```
┌────────────────────────────────┐
│██████████████                  │ ← Gradient fill
└────────────────────────────────┘
```

**Styling:**
- Background: Light gray
- Fill: Brand gradient
- Height: 8px
- Border Radius: 10px

### Tabs

```
┌─────────┬─────────┬─────────┐
│ Active  │  Tab 2  │  Tab 3  │
└─────────┴─────────┴─────────┘
    ▔▔▔  ← Gradient underline
```

**Active Tab:**
- Color: Primary
- Border bottom: 3px primary
- Background: Light gray

---

## Responsive Design

Streamlit handles most responsive behavior, but ensure:

- Cards stack on mobile
- Text sizes scale appropriately
- Sidebar collapsible on mobile
- Touch targets minimum 44px
- Readable text on all screens

---

## Summary

Smar-Test uses a modern, gradient-based design system that:

1. **Communicates Intelligence**: Through the gradient theme
2. **Ensures Professionalism**: Via clean typography and spacing
3. **Provides Delight**: With smooth animations and transitions
4. **Maintains Accessibility**: Through proper contrast and semantics
5. **Creates Consistency**: Via a well-defined color and component system

**Brand Essence**: Smart, Fast, Professional, Modern, Trustworthy

⚡ **Smar-Test** - Where smart meets test to create the smartest test generation experience.
