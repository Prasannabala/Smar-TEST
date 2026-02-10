# 🎬 Smar-Test Demo - Quick Reference Card

## ⚡ 5-Minute Demo Flow

### 1️⃣ CLIENT SETUP (30 sec)
```
Client Name: E-Commerce Platform - ShopNow
Project: ShopNow v2.0
Environment: Chrome, Firefox, Safari, Edge
Tech Stack: React, Node.js, PostgreSQL, AWS

Navigation Rules:
Login -> Dashboard -> Product Catalog
Product Catalog -> Add to Cart -> Checkout
Checkout -> Payment -> Confirmation

Thumb Rules:
All forms validate before submission
Session timeout after 30 minutes
Max 3 login attempts before lockout

Business Rules:
Orders over $100 get free shipping
Users must be logged in to add to cart
Maximum 10 items per order
Inventory checked before confirmation
```

### 2️⃣ LLM SETTINGS (15 sec)
```
Provider: Hugging Face
✓ Use Inference API (cloud)
Model: Qwen/Qwen2.5-7B-Instruct
Token: [Your HF token]
Click: Save Settings
```

### 3️⃣ GENERATE TESTS (90 sec)
```
1. Select Client: E-Commerce Platform - ShopNow
2. Upload: demo_requirements_ecommerce.txt
3. Options:
   ✓ Manual Test Cases
   ✓ Gherkin (BDD)
   ✓ Selenium (Python)
   ✓ Playwright (JavaScript)
   ✓ Include Edge Cases
   ✓ Include Negative Tests
   ✓ Include Boundary Tests
4. Click: Generate Test Cases
5. Watch progress bar
6. View results in tabs
7. Download All as ZIP
```

---

## 📸 Screenshot Moments

**Must Capture:**
1. Main heading "⚡ Smar-Test" (large and bold)
2. Client creation form filled out
3. HuggingFace settings page with model selected
4. Requirements upload with file preview
5. Progress bar showing stages
6. Generated test cases in different tabs
7. Export options page

---

## 🎯 Key Talking Points

- "Client-specific context ensures relevant test cases"
- "1000+ AI models available via HuggingFace"
- "Generate 4 test formats from 1 document"
- "Edge cases and negative tests included automatically"
- "Export to Excel, CSV, or ZIP in seconds"

---

## ⚙️ Recording Settings

**GIF (Recommended for README):**
- Tool: ScreenToGif
- Size: 1280x720
- FPS: 15
- Duration: 60-90 sec
- Optimize: Yes

**Video (Recommended for YouTube):**
- Tool: OBS Studio
- Size: 1920x1080
- FPS: 30
- Format: MP4
- Quality: High

---

## 🐛 Quick Troubleshooting

**If LLM won't connect:**
- Check API token is valid
- Try switching to Ollama (local)

**If generation is slow:**
- Use smaller requirements file
- Try different model (SmolLM3-3B is faster)

**If UI looks wrong:**
- Clear browser cache
- Set zoom to 100%
- Use Chrome

---

## ✅ Pre-Recording Checklist

- [ ] Application running
- [ ] Browser clean (no extra tabs)
- [ ] HuggingFace token ready
- [ ] Requirements file saved
- [ ] Client data copied (ready to paste)
- [ ] Recording software tested
- [ ] Audio levels checked (if narrating)

---

## 🚀 Start Recording Now!

**Open terminal:**
```bash
cd "C:\Users\prasa\OneDrive\Desktop\Claude Projects\testcase-generation-agent-main"
streamlit run app.py
```

**Open browser:**
```
http://localhost:8501
```

**Ready? Action! 🎬**
