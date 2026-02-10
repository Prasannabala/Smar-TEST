# Smar-Test Demo Script & Recording Guide

## 🎬 Demo Overview
This guide will help you create a professional demo video/GIF showcasing the Smar-Test tool's key features.

**Demo Duration:** 2-3 minutes
**Tools Recommended:**
- **Screen Recording:** OBS Studio (free), ScreenToGif, or Loom
- **GIF Creation:** ScreenToGif or Gifox
- **Video Editing:** DaVinci Resolve (free) or Camtasia

---

## 📋 Pre-Demo Setup

### 1. Clean Your Browser
- Clear browser cache
- Close unnecessary tabs
- Use Chrome for best compatibility
- Set browser zoom to 100%

### 2. Start the Application
```bash
cd "C:\Users\prasa\OneDrive\Desktop\Claude Projects\testcase-generation-agent-main"
streamlit run app.py
```

### 3. Prepare Sample Files
Create a test requirements document (see sample below)

---

## 🎥 Demo Script - Step by Step

### **Scene 1: Application Launch (5 seconds)**

**Action:** Show the homepage with the large "⚡ Smar-Test" heading

**Narration/Text Overlay:**
> "Smar-Test - AI-Powered Test Case Generation"

**What to Show:**
- Clean, professional interface
- "Smart-Choices" sidebar visible
- Navigation buttons clearly visible

---

### **Scene 2: Create Client Context (30 seconds)**

**Action:** Click "👥 Client Setup" button

**Steps:**
1. Click "Create New Client" or fill the form directly
2. Enter client information:

```
Client Name: E-Commerce Platform - ShopNow
Project Name: ShopNow v2.0
Test Environment: Chrome, Firefox, Safari, Edge
Tech Stack: React, Node.js, PostgreSQL, AWS
Project Description: Modern e-commerce platform with real-time inventory, payment processing, and customer reviews
```

3. Add **Navigation Rules** (one per line):
```
Login -> Dashboard -> Product Catalog
Product Catalog -> Product Details -> Add to Cart
Add to Cart -> Shopping Cart -> Checkout
Checkout -> Payment -> Order Confirmation
Dashboard -> Order History -> Order Details
```

4. Add **Thumb Rules** (one per line):
```
All forms must validate input before submission
Session timeout after 30 minutes of inactivity
Maximum 3 login attempts before account lockout
All API responses must be returned within 2 seconds
All error messages must be user-friendly and actionable
```

5. Add **Business Rules** (one per line):
```
Orders over $100 get free shipping
Users must be logged in to add items to cart
Maximum 10 items per order
Inventory must be checked before order confirmation
Discount codes can only be applied once per order
```

6. Add **Best Practices** (one per line):
```
Test with multiple user roles (guest, customer, admin)
Verify email notifications for order confirmations
Test payment integration in sandbox mode
Validate data persistence across sessions
Check responsive design on mobile and desktop
```

**Action:** Click "Save Client" button

**What to Show:**
- Success message: "✅ Created client: E-Commerce Platform - ShopNow"
- Rules summary displayed

---

### **Scene 3: Configure LLM Settings (20 seconds)**

**Action:** Click "⚙️ LLM Settings" button

**Steps:**
1. Select "Hugging Face" provider
2. Check "Use Inference API (cloud - recommended)"
3. Enter API Token (or show placeholder for privacy)
4. Select Model from dropdown:
   - **Recommended:** `Qwen/Qwen2.5-7B-Instruct`
   - Alternative: `meta-llama/Llama-3.1-8B-Instruct`
5. Click "Save Settings"
6. Verify connection: "✅ Connected"

**Narration/Text Overlay:**
> "Connect to 1000+ models via HuggingFace - no local GPU required"

---

### **Scene 4: Generate Test Cases (60 seconds)**

**Action:** Click "📝 Generate Tests" button

**Steps:**

1. **Select Client Context:**
   - From dropdown, select "E-Commerce Platform - ShopNow"
   - Show rules summary appearing below

2. **Upload Requirements Document:**
   - Click "Browse files" or drag-and-drop
   - Upload the sample requirements file (see below)
   - Show document preview and metrics (words, pages)

3. **Configure Test Options:**
   - Manual Test Cases: ✓ (checked, disabled)
   - Gherkin (BDD): ✓ Check this
   - Selenium: ✓ Check this
   - Playwright: ✓ Check this

   - Include Edge Cases: ✓
   - Include Negative Tests: ✓
   - Include Boundary Tests: ✓

4. **Generate:**
   - Click "Generate Test Cases" button
   - Show progress bar with stages:
     - 📋 Manual Tests
     - 🥒 Gherkin BDD
     - 🐍 Selenium Scripts
     - 🎭 Playwright Specs

**What to Show:**
- Real-time progress updates
- Dynamic progress bar with colors
- Stage-by-stage completion

---

### **Scene 5: View Results (30 seconds)**

**Action:** Show generated test cases

**What to Show:**

1. **Summary Metrics:**
   - Manual Tests: ~15-20 tests
   - Gherkin: ~5-8 scenarios
   - Selenium: ~3-5 scripts
   - Playwright: ~3-5 specs

2. **Browse Tabs:**
   - **Manual Tests Tab:**
     - Show expandable test cases
     - Highlight test ID, priority, category
     - Show test steps with expected results
     - Demonstrate filter by priority

   - **Gherkin Tab:**
     - Show feature file with scenarios
     - Highlight Given-When-Then structure

   - **Selenium Tab:**
     - Show Python code snippet
     - Highlight page objects and assertions

   - **Playwright Tab:**
     - Show JavaScript test code
     - Highlight async/await patterns

   - **Export Tab:**
     - Show download options:
       - Excel (.xlsx)
       - CSV
       - Markdown
       - ZIP (all files)

3. **Download:**
   - Click "Download All as ZIP"
   - Show success notification

---

### **Scene 6: View History (10 seconds)**

**Action:** Click "📊 History" button

**What to Show:**
- Generation record with timestamp
- Test count and types
- Requirement filename

---

## 📄 Sample Requirements Document

Create a file named `ecommerce_checkout_requirements.txt`:

```text
E-COMMERCE CHECKOUT FEATURE - REQUIREMENTS DOCUMENT

Feature: Shopping Cart and Checkout Process

Overview:
Users should be able to add products to their shopping cart, review their selections,
apply discount codes, and complete the checkout process with payment.

Functional Requirements:

1. Add to Cart
   - Users must be logged in to add items to cart
   - Each product page should have an "Add to Cart" button
   - System should display confirmation message when item is added
   - Cart icon should update with item count
   - Users should be able to select quantity (max 10 per item)
   - System should check inventory availability before adding

2. Shopping Cart
   - Display all items with product name, image, price, and quantity
   - Allow users to update quantity or remove items
   - Show subtotal, tax, shipping, and total price
   - Display estimated delivery date
   - Show "Continue Shopping" and "Proceed to Checkout" buttons
   - Cart should persist across sessions for logged-in users
   - Show "Empty Cart" message if no items

3. Discount Codes
   - Provide input field for discount code
   - Validate code against active promotions
   - Display error message for invalid/expired codes
   - Apply discount and update total price
   - Show discount amount separately in price breakdown
   - Only one discount code per order allowed

4. Checkout Process
   - Step 1: Shipping Address
     * Use saved addresses or enter new address
     * Validate required fields (name, street, city, zip, country)
     * Provide option to save address for future use

   - Step 2: Shipping Method
     * Display available shipping options with costs
     * Show estimated delivery dates
     * Free shipping for orders over $100

   - Step 3: Payment
     * Support credit/debit cards and PayPal
     * Validate card number, expiry date, CVV
     * Use secure payment gateway (PCI compliant)
     * Display order summary with final total

   - Step 4: Order Confirmation
     * Generate unique order ID
     * Send confirmation email to customer
     * Display order details and delivery estimate
     * Provide "Track Order" option

5. Order Processing
   - Verify inventory before order confirmation
   - Deduct items from inventory upon successful payment
   - Update order status in database
   - Send notification to warehouse for fulfillment

Non-Functional Requirements:

1. Performance
   - Cart operations should complete within 1 second
   - Checkout page load time < 2 seconds
   - Payment processing < 3 seconds

2. Security
   - Use HTTPS for all transactions
   - Encrypt payment information
   - Implement CSRF protection
   - Session timeout after 30 minutes

3. Usability
   - Mobile-responsive design
   - Clear error messages
   - Progress indicator during checkout
   - Save cart state on each update

4. Browser Compatibility
   - Support Chrome, Firefox, Safari, Edge (latest 2 versions)

Edge Cases to Consider:
- Item goes out of stock during checkout
- Payment gateway timeout or failure
- Discount code expires during checkout
- User abandons cart and returns later
- Multiple browser tabs with same cart
- Network interruption during payment

Business Rules:
- Maximum 10 items per order
- Minimum order value: $10
- Maximum order value: $10,000
- Discount codes cannot be combined
- Free shipping only for domestic orders over $100
- International orders: flat shipping rate $25
```

---

## 🎬 Recording Tips

### Screen Recording Settings
```
Resolution: 1920x1080 (Full HD)
Frame Rate: 30 fps
Format: MP4 (for video) or GIF (for shorter demos)
Audio: Optional narration or background music
```

### GIF-Specific Tips
- Keep GIF under 10MB for easy sharing
- Use ScreenToGif with optimization
- Recommended GIF duration: 60-90 seconds
- Show only key actions (skip waiting times)
- Add text overlays for context

### Video-Specific Tips
- Add smooth transitions between scenes
- Include intro/outro with branding
- Add background music (royalty-free)
- Use zoom effects to highlight important UI elements
- Add captions/annotations for clarity

### Recording Tools Setup

#### ScreenToGif (Recommended for GIF)
1. Download: https://www.screentogif.com/
2. Configure:
   - Region: Select browser window
   - FPS: 15 (for smaller file size)
   - Quality: High
3. Record -> Stop -> Edit -> Export as GIF

#### OBS Studio (Recommended for Video)
1. Download: https://obsproject.com/
2. Configure:
   - Scene: Display Capture or Window Capture
   - Settings -> Output -> Recording Quality: High
   - Format: MP4
3. Record -> Stop -> Edit in video editor

---

## 📊 Demo Checklist

### Before Recording
- [ ] Browser window clean (no extra tabs)
- [ ] Application running smoothly
- [ ] Sample data prepared
- [ ] Sample requirements document ready
- [ ] HuggingFace API token ready
- [ ] Test recording setup (audio/video quality)

### During Recording
- [ ] Speak clearly (if adding narration)
- [ ] Move mouse slowly and deliberately
- [ ] Pause briefly between actions
- [ ] Highlight important UI elements
- [ ] Show success messages clearly

### After Recording
- [ ] Trim unnecessary parts
- [ ] Add transitions
- [ ] Add text overlays/annotations
- [ ] Add background music (optional)
- [ ] Export in appropriate format
- [ ] Test playback on different devices

---

## 🎨 Text Overlays to Add

Use these text overlays at key moments:

```
Scene 1:
"⚡ Smar-Test - AI-Powered Test Generation"

Scene 2:
"1. Create Client Context"
"Add navigation rules, business logic, and best practices"

Scene 3:
"2. Configure AI Provider"
"Access 1000+ models via HuggingFace"

Scene 4:
"3. Upload Requirements"
"Smart extraction from TXT, PDF, DOCX"

Scene 5:
"4. Generate Test Cases"
"Manual, Gherkin, Selenium, Playwright - All in one click"

Scene 6:
"5. Export & Share"
"Download as Excel, CSV, Markdown, or ZIP"
```

---

## 🎯 Key Messages to Highlight

1. **Client-Specific Context:** "Apply your team's testing rules automatically"
2. **Multi-Provider Support:** "Connect to any LLM - Local or Cloud"
3. **Comprehensive Generation:** "4 test formats from 1 requirement document"
4. **Production-Ready:** "Export to Excel, CSV, or ZIP for immediate use"
5. **Smart Automation:** "Edge cases, negative tests, and boundary conditions included"

---

## 🔧 Troubleshooting During Recording

### If Generation Takes Too Long
- Use a smaller requirements document
- Or: Record up to the progress bar, then splice in pre-generated results

### If Connection Fails
- Have a backup: Pre-record the connection success
- Or: Use Ollama local model for demo (faster, no API needed)

### If UI Looks Different
- Check browser zoom (should be 100%)
- Clear browser cache and restart
- Use Chrome for consistency

---

## 📤 Export & Sharing

### GIF Export
```
Recommended Settings:
- Size: 1280x720 (720p)
- FPS: 12-15
- Duration: 60-90 seconds
- File Size: < 10MB
- Format: GIF with optimization
```

### Video Export
```
Recommended Settings:
- Resolution: 1920x1080 (1080p)
- Format: MP4 (H.264)
- Frame Rate: 30 fps
- Bitrate: 5-10 Mbps
- Audio: 128 kbps (if narration included)
```

### Platforms to Share
- GitHub README
- LinkedIn post
- YouTube (unlisted for portfolio)
- Product Hunt
- Twitter/X
- Dev.to article

---

## 🎓 Advanced Tips

### Add Picture-in-Picture
- Show your face in corner while demoing
- Adds personal touch and professionalism

### Add Cursor Highlights
- Use tools like Cursor Highlighter
- Makes cursor more visible in recordings

### Add Click Animations
- Use tools like Mouse Highlighter
- Shows where you're clicking

### Speed Up Boring Parts
- 2x speed for form filling
- Real-time for results display

---

## 📝 Sample Narration Script

> "Welcome to Smar-Test - the AI-powered test case generation platform."
>
> "First, let's create a client context with specific business rules and navigation flows for our e-commerce platform."
>
> "Next, we'll configure HuggingFace to access state-of-the-art language models without needing a local GPU."
>
> "Now, we upload our requirements document. Smar-Test automatically extracts and analyzes the content."
>
> "With one click, we generate comprehensive test cases - manual tests, Gherkin scenarios, Selenium scripts, and Playwright specs."
>
> "In just seconds, we have production-ready test cases that include edge cases, negative tests, and boundary conditions."
>
> "Finally, export everything as Excel, CSV, or a complete ZIP package ready for your QA team."
>
> "Smar-Test - Smart testing, made simple."

---

## 🚀 Ready to Record!

Follow this script step-by-step, and you'll have a professional demo that showcases all the key features of Smar-Test.

**Good luck with your recording! 🎬**
