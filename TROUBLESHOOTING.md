# 🚨 DAG Troubleshooting Guide - Upstream Failures

## 🔍 How to Find the Root Cause

When you see "upstream_failed", it means a task failed early and caused a cascade.

### **Step 1: Identify the First Failed Task**

In Airflow UI Graph View:
- 🔴 **Red box** = The actual failure (THIS IS WHAT WE NEED!)
- 🟠 **Orange/light red box** = "upstream_failed" (ignore these for now)

**Find the FIRST red box** - that's the root cause!

---

## 📋 Most Likely Issues

### **Issue 1: `get_astronauts` Failed**

**Symptoms:**
- `get_astronauts` task is red
- All other tasks are orange "upstream_failed"

**Possible Causes:**

#### A. API Connection Error
**Error in logs:**
```
requests.exceptions.ConnectionError
requests.exceptions.Timeout
```

**Fix:** This is usually temporary. Try:
1. Trigger the DAG again
2. If it persists, the API might be down

#### B. Import Error
**Error in logs:**
```
ModuleNotFoundError: No module named 'requests'
ModuleNotFoundError: No module named 'pendulum'
```

**Fix:** Redeploy after verifying requirements.txt:
```bash
astro deploy
# or
astro dev restart
```

---

### **Issue 2: `get_astronaut_metadata` Failed**

**Symptoms:**
- `get_astronauts` is green ✅
- `get_astronaut_metadata` is red 🔴

**Possible Causes:**

#### A. XCom Pull Returns None
**Error in logs:**
```
TypeError: 'NoneType' object is not subscriptable
KeyError: ...
```

**Root Cause:** The `get_astronaut_metadata` task runs independently and might execute before `get_astronauts` stores XCom data.

**Fix Needed:** Add task dependency! Let me check your orchestration:

---

### **Issue 3: `export_astronaut_data_to_csv` Failed**

**Symptoms:**
- Earlier tasks are green
- `export_astronaut_data_to_csv` is red

**Possible Causes:**

#### A. pandas Import Error
**Error in logs:**
```
ModuleNotFoundError: No module named 'pandas'
ImportError: Missing optional dependency 'openpyxl'
```

**Fix:** Verify pandas is in requirements.txt and redeploy

#### B. Data Format Issue
**Error in logs:**
```
KeyError: 'astronauts'
TypeError: ...
```

**Fix:** Check that `get_astronaut_metadata` completed successfully

---

## 🎯 Quick Diagnostic Checklist

Follow these steps IN ORDER:

### ✅ Step 1: Identify First Red Task
- [ ] Open Graph View in Airflow UI
- [ ] Find the FIRST red task (not orange)
- [ ] Note the task name: ________________

### ✅ Step 2: Check Task Logs
- [ ] Click on the red task
- [ ] Click "Log" button
- [ ] Scroll to the bottom
- [ ] Look for error message (usually in red/yellow)

### ✅ Step 3: Common Error Patterns

**If you see:**
```
ModuleNotFoundError: No module named 'X'
```
→ Missing dependency - redeploy after checking requirements.txt

**If you see:**
```
requests.exceptions.ConnectionError
```
→ API is down or network issue - try again in a few minutes

**If you see:**
```
TypeError: 'NoneType' object...
```
→ Task dependency issue - task ran before data was ready

**If you see:**
```
KeyError: 'astronauts' or 'number_of_people_in_space'
```
→ XCom data missing - check task dependencies

---

## 🔧 Most Common Fix Needed

Based on your code structure, the most likely issue is:

### **Missing Task Dependency for `get_astronaut_metadata`**

**Problem:**
The `get_astronaut_metadata` task tries to pull XCom data from `get_astronauts`, but there's no explicit dependency to ensure `get_astronauts` runs first.

**Current Code (Lines 366-374):**
```python
astronaut_list = get_astronauts()
print_astronaut_craft.partial(...).expand(person_in_space=astronaut_list)
astronaut_data = get_astronaut_metadata()
```

**Issue:** `get_astronaut_metadata()` has no dependency on `get_astronauts()`, so it might run before the XCom data is pushed!

**Fix Required:** Add explicit dependency

---

## 🆘 What to Share With Me

To help you faster, please share:

1. **Which task is RED (not orange)?**
   - Task name: ________________

2. **Error message from logs:**
   ```
   [Paste the error here]
   ```

3. **Are all tasks failing or just some?**
   - All: ☐
   - Just one/few: ☐

---

## 🚀 Quick Fixes to Try NOW

### **Fix 1: Redeploy (Ensures packages are installed)**
```bash
astro deploy
# or for local
astro dev restart
```

### **Fix 2: Clear Failed Run & Retry**
In Airflow UI:
1. Click the failed DAG run
2. Click "Clear" button (broom icon)
3. Confirm clear
4. Trigger again

### **Fix 3: Check API Status**
Test if the API is working:
```bash
curl http://api.open-notify.org/astros.json
```
Should return JSON with astronaut data.

---

## 📊 Expected vs Actual

### **Expected (Success):**
```
get_astronauts              ✅ Green
get_astronaut_metadata      ✅ Green
print_astronaut_craft[0-14] ✅ Green (multiple)
get_iss_location            ✅ Green
get_weather_at_iss_location ✅ Green
print_iss_location          ✅ Green
export_astronaut_data_to_csv ✅ Green
export_iss_data_to_json     ✅ Green
generate_summary_report     ✅ Green
```

### **Actual (Your Report):**
```
[FIRST TASK]                🔴 Red (Failed)
[OTHER TASKS]               🟠 Orange (Upstream Failed)
```

**We need to fix the FIRST red task!**

---

## 💡 Next Steps

1. **Find the first red task name**
2. **Copy the error from logs**
3. **Share with me**
4. **I'll provide exact fix!**

Ready to fix this! 🔧
