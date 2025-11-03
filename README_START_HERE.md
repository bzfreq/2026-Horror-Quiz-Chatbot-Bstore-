# 🩸 Horror Oracle - Quick Start Guide

## 🚨 IMPORTANT: Start Backend First!

If the quiz gets stuck loading, it's because **the backend server isn't running**.

### To Start Everything:

**1. Start the Backend (Required!)**
```
Double-click: START_HERE_FIRST.bat
```
OR
```powershell
python app.py
```

**2. Open Your Browser**
```
Go to: http://localhost:5000
```

**3. Use the Quiz**
- Click "Blood Quiz" button
- Wait 10-30 seconds for AI to generate questions
- Enjoy!

## 📁 Important Files

| File | Purpose |
|------|---------|
| `START_HERE_FIRST.bat` | **Easy way to start the backend** |
| `app.py` | Main backend server |
| `index.html` | Frontend website |
| `FIX_LOADING_STUCK_AT_50_PERCENT.md` | Troubleshooting guide |
| `test_backend_quick.py` | Test if backend is working |

## ✅ Quick Test

After starting the backend, run:
```powershell
python test_backend_quick.py
```

Should show:
```
[OK] Backend is running
[OK] Quiz generated successfully
```

## ⚠️ Common Issues

### Quiz Won't Load
→ Backend not running - start it first!

### Takes Too Long
→ Normal! OpenAI API takes 10-30 seconds

### Port 5000 Already in Use
→ Close other servers or change port in `app.py`

## 🔑 Required

- Python 3.8+
- OpenAI API key (in `.env` file)
- Internet connection

## 📚 Full Documentation

- `START_BACKEND_INSTRUCTIONS.md` - Detailed backend setup
- `FIX_LOADING_STUCK_AT_50_PERCENT.md` - Loading issue fixes
- `TESTING_GUIDE.md` - Complete testing guide

## Need Help?

1. Make sure backend is running
2. Check browser console (F12)
3. Check backend console window
4. Read `FIX_LOADING_STUCK_AT_50_PERCENT.md`

---

**Remember:** Backend server must be running for quiz to work! 🎃

