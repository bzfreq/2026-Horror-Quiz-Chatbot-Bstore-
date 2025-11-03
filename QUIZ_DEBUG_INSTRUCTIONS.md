# Quiz Not Showing Questions - Debug Instructions

## What I Found

The backend is **working correctly** and generating 5 questions properly. I tested it directly:

```bash
# Backend test result:
✅ Backend returns 5 valid quiz questions
✅ Questions have correct structure (question, options, correct, is_profile)
✅ Theme and difficulty are included
```

## The Issue

The problem is somewhere in the **frontend JavaScript flow** where quiz data gets passed between functions. I've added extensive debugging to help identify where it's failing.

## How to Debug

1. **Open your browser** (Chrome, Edge, Firefox)
2. **Press F12** to open Developer Tools
3. **Click the "Console" tab**
4. **Refresh the page** (Ctrl+R or F5)
5. **Click "Face Your Nightmares" button**
6. **Watch the console output**

## What to Look For

You should see debug messages like this:

```
[DEBUG] Calling /generate-adaptive-quiz with: {...}
[DEBUG] Backend response: {...}
[DEBUG] data.questions: [Array(5)]
[DEBUG] Returning quiz data: {...}
[DEBUG] proceedToQuiz called with: {...}
[DEBUG] displayQuizWithData called with: {...}
[DEBUG] currentQuiz.questions: [Array(5)]
[DEBUG] questions length: 5
[DEBUG] showQuestion called
[DEBUG] currentQuestion: 0
[DEBUG] total questions: 5
[DEBUG] Showing question: {...}
```

## Possible Issues to Check

### Issue 1: Quiz Data is NULL
If you see:
```
[DEBUG] quizData is null
[DEBUG] Fallback - loading quiz via startQuizModal
```

This means the quiz data wasn't passed correctly from the intro screen.

### Issue 2: Questions Array is Empty
If you see:
```
[DEBUG] questions length: 0
[DEBUG] Showing results - no more questions
```

This means the backend returned data but without questions, or they weren't assigned correctly.

### Issue 3: Backend Error
If you see a fetch error or backend error in console, there's an API issue.

## Quick Fix to Test

If you want to bypass the intro screen and test directly:

1. Open browser console (F12)
2. Paste this and press Enter:

```javascript
async function testQuiz() {
    const response = await fetch('http://localhost:5000/generate-adaptive-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            googleId: null,
            quizNumber: 1,
            movieTitle: null
        })
    });
    const data = await response.json();
    console.log('Direct backend test:', data);
    console.log('Number of questions:', data.questions.length);
}
testQuiz();
```

This will test the backend directly and show you what it returns.

## What to Do Next

1. **Run the debug steps above**
2. **Copy the console output** (especially the DEBUG messages)
3. **Share the output** so I can pinpoint the exact issue

## Files Modified

I added debugging to:
- `script-js-combined.js` - Added console.log statements to:
  - `preloadQuizData()` - Shows backend call and response
  - `proceedToQuiz()` - Shows quiz data being passed
  - `displayQuizWithData()` - Shows quiz data assignment
  - `showQuestion()` - Shows when questions are displayed

These logs will help us identify exactly where the quiz flow breaks.

