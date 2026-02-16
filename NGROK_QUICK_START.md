# ngrok Quick Start Guide

## For Streamlit Cloud Users Who Want to Use Local Ollama

---

## ⚡ **Super Quick (5 minutes)**

### **Step 1: Download ngrok**
- Go to: https://ngrok.com/download
- Download for your OS (Windows/Mac/Linux)
- Unzip the file

### **Step 2: Create Free Account**
- Go to: https://ngrok.com
- Click "Sign Up"
- Verify your email
- Go to: https://dashboard.ngrok.com/auth/your-authtoken
- Copy your authtoken (looks like: `24_L8vN7yP2qR9xK4mZ`)

### **Step 3: Setup ngrok (One-time)**

**Windows (PowerShell as Admin):**
```powershell
cd Downloads
.\ngrok.exe config add-authtoken 24_L8vN7yP2qR9xK4mZ
```

**Mac/Linux (Terminal):**
```bash
cd ~/Downloads
./ngrok config add-authtoken 24_L8vN7yP2qR9xK4mZ
```

Replace `24_L8vN7yP2qR9xK4mZ` with your actual token!

### **Step 4: Start Ollama**
Open a **new terminal** and run:
```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

### **Step 5: Start ngrok (Key Step!)**
Open **another new terminal** and run:

**Windows:**
```powershell
cd Downloads
.\ngrok.exe http 11434
```

**Mac/Linux:**
```bash
cd ~/Downloads
./ngrok http 11434
```

### **Step 6: Copy Your URL**
You'll see output like:
```
Forwarding     https://abc123def456.ngrok.io -> http://localhost:11434
```

Copy: `https://abc123def456.ngrok.io`

### **Step 7: Use in Streamlit App**
1. Go to your Streamlit Cloud app
2. Click **⚙️ LLM Settings**
3. Select **Ollama**
4. Change **Base URL** to: `https://abc123def456.ngrok.io`
5. Click **Save Settings**
6. Done! ✓

---

## ✅ **You Should See**

**Terminal 1 (Ollama):**
```
$ ollama serve
2024/01/15 10:23:45 Listening on 127.0.0.1:11434
```

**Terminal 2 (ngrok):**
```
$ ngrok http 11434

Session Status                online
Forwarding     https://abc123def456.ngrok.io -> http://localhost:11434
```

**Streamlit App:**
- LLM Provider: Ollama
- Base URL: https://abc123def456.ngrok.io
- Model: (select your model)
- ✓ Working!

---

## ⚠️ **Important: URL Changes Each Time**

Every time you restart ngrok, you get a **new URL**:
```
First time:    https://abc123def456.ngrok.io
After restart: https://xyz789abc123.ngrok.io  ← Different!
```

So after each restart:
1. Check ngrok terminal for new URL
2. Update Streamlit app with new URL
3. Save settings
4. Works again! ✓

---

## 🛑 **When to Stop**

When done using Streamlit Cloud:
- Press **Ctrl+C** in ngrok terminal (stops tunnel)
- Press **Ctrl+C** in Ollama terminal (stops Ollama)
- Done!

---

## 🆘 **Common Issues**

### **"ngrok not found"**
Make sure you're in the right directory:
```bash
cd ~/Downloads  # Where you unzipped ngrok
./ngrok http 11434
```

### **"Port 11434 already in use"**
Ollama isn't running first. Check:
1. Start Ollama in **first terminal**
2. Then start ngrok in **second terminal**

### **"Connection refused"**
1. Is Ollama running? (Check terminal 1)
2. Is ngrok running? (Check terminal 2)
3. Is URL correct in Streamlit app?

### **Streamlit says "Connection timeout"**
1. Check ngrok terminal - is it still running?
2. Check the URL - did it change?
3. Update Streamlit app with new URL if needed

---

## 💡 **Pro Tips**

### **Keep It Running**
Leave both terminals open while using the app:
- Terminal 1: Ollama running
- Terminal 2: ngrok tunnel active

### **Script It (Optional)**
Create batch files to automate startup:

**Windows - start_ollama.bat:**
```batch
ollama serve
pause
```

**Windows - start_ngrok.bat:**
```batch
cd Downloads
ngrok http 11434
pause
```

Run both when you want to use Streamlit Cloud!

### **Mobile Testing**
ngrok URLs work on phone/tablet too! Share your ngrok URL with friends to test your app.

---

## ✅ **Checklist**

Before using Streamlit Cloud:
- [ ] ngrok downloaded and unzipped
- [ ] ngrok account created
- [ ] Authtoken configured in ngrok
- [ ] Ollama running (terminal 1)
- [ ] ngrok tunnel started (terminal 2)
- [ ] ngrok URL copied
- [ ] Streamlit app Base URL updated
- [ ] Settings saved
- [ ] Test: Try generating tests ✓

---

## 📞 **Questions?**

See the main **NGROK_TUNNEL_EXPLAINED.md** file for detailed explanations!

---

**You're all set! Enjoy using your local Ollama from Streamlit Cloud!** 🚀
