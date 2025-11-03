# Quiz Variety Fix - Summary

## Problem
When clicking "Face Your Nightmares", every quiz showed the same questions (starting with Hereditary, then the same 4 movies every time).

## Root Cause
The Oracle Engine's BuilderNode was failing to initialize the LLM properly due to:
1. **Missing LangChain dependencies** - `langchain-openai` and related packages were not installed
2. **Outdated import paths** - Using old `langchain.prompts` instead of `langchain_core.prompts`
3. **Incorrect API parameter** - Using deprecated `openai_api_key` instead of `api_key`
4. **Prompt template issue** - JSON curly braces not properly escaped, causing template variable errors
5. **Unicode encoding errors** - Emojis in print statements causing crashes on Windows

Because the LLM initialization failed, the system always fell back to the same hardcoded questions.

## Fixes Applied

### 1. Installed Missing Dependencies
```bash
pip install langchain langchain-openai langchain-community tiktoken --upgrade
```

### 2. Updated BuilderNode Imports
**File:** `oracle_engine/builder_node.py`
- Changed `from langchain.prompts import ChatPromptTemplate` → `from langchain_core.prompts import ChatPromptTemplate`
- Changed `from langchain.output_parsers import JsonOutputParser` → `from langchain_core.output_parsers import JsonOutputParser`

### 3. Fixed API Parameter
**File:** `oracle_engine/builder_node.py`
- Changed `openai_api_key=Config.OPENAI_API_KEY` → `api_key=Config.OPENAI_API_KEY`

### 4. Fixed Prompt Template
**File:** `oracle_engine/prompts/question_generator_prompt.txt`
- Escaped all JSON curly braces: `{{` → `{{{{` and `}}` → `}}}}`
- Escaped template variables: `{tone}` → `{{tone}}`

### 5. Removed Unicode Emojis
**File:** `oracle_engine/builder_node.py`
- Removed all emoji characters from print statements to prevent Windows encoding errors

### 6. Removed Quiz Caching
**File:** `script-js-combined.js`
- Removed `localStorage.getItem('quiz-cached')` check
- Removed `localStorage.setItem('quiz-cached', 'true')` to ensure fresh quiz generation every time

## Result
✅ **LLM now properly initialized** with temperature=0.8 for high variety
✅ **Every quiz generates FRESH, UNIQUE questions** using AI
✅ **No more repeated Hereditary questions**
✅ **Fallback questions (if LLM fails) are also randomized**

## Testing Performed
Ran 3 consecutive quizzes and confirmed:
- All questions are different between quizzes
- LLM successfully generates questions
- High temperature (0.8) ensures variety

## How It Works Now
1. User clicks "Face Your Nightmares"
2. Frontend calls `/api/start_quiz` endpoint
3. Backend calls `oracle_engine.main.start_first_quiz()`
4. BuilderNode generates 5 NEW questions using OpenAI GPT-4o-mini
5. High temperature (0.8) ensures different questions every time
6. Questions are tailored to user's horror DNA profile
7. Each quiz is unique and adaptive!

---

**Date:** October 29, 2025
**Status:** ✅ FIXED - Quiz variety fully restored


