# 🧪 Testing Guide for example_astronauts DAG

## 🚀 Getting Started

### 1. Start Airflow Locally
```bash
# Make sure you're in your project directory
cd /path/to/your/project

# Start Airflow with Astro CLI
astro dev start
```

**Wait 2-3 minutes** for all services to start, then open: **http://localhost:8080**
- Username: `admin`
- Password: `admin`

---

## ✅ Pre-Flight Checklist

### Step 1: Verify DAG Loaded Successfully
- [ ] Go to the Airflow UI (http://localhost:8080)
- [ ] Find `example_astronauts` in the DAG list
- [ ] **Check: No red "Import Error" banner** at the top
- [ ] DAG should show as "Paused" (toggle is OFF/gray)

**If you see import errors:**
- Click on the DAG to see error details
- Check that all packages in `requirements.txt` are installed
- Restart Airflow: `astro dev restart`

---

### Step 2: Inspect the DAG Structure
- [ ] Click on the `example_astronauts` DAG name
- [ ] Click the **"Graph"** view
- [ ] **Verify you see these tasks:**
  - `get_astronauts`
  - `get_astronaut_metadata`
  - `print_astronaut_craft` (will show as `[mapped]`)
  - `get_iss_location`
  - `get_weather_at_iss_location`
  - `print_iss_location`
  - `export_astronaut_data_to_csv`
  - `export_iss_data_to_json`
  - `generate_summary_report`

---

### Step 3: Trigger a Manual Run
- [ ] Click the **▶️ Play button** (top right) → "Trigger DAG"
- [ ] Click "Trigger" in the confirmation dialog
- [ ] **Watch the Graph view** as tasks execute

**What to expect:**
- Tasks will turn **light green** (running) → **dark green** (success)
- `print_astronaut_craft` will expand into multiple tasks (one per astronaut)
- Total run time: ~30-60 seconds

---

## 🔍 Detailed Verification Steps

### Step 4: Check Dynamic Task Mapping
- [ ] After DAG completes, click on `print_astronaut_craft`
- [ ] You should see **multiple instances** (mapped tasks)
- [ ] **Expected:** 10-15 task instances (one for each astronaut)
- [ ] All should be green (success)

**What this means:**
✅ Dynamic task mapping is working correctly!

---

### Step 5: Inspect Task Logs

#### Check `get_astronauts` logs:
1. Click on `get_astronauts` task box
2. Click "Log" button
3. **Look for:**
   ```
   [2024-XX-XX] {python.py:XXX} INFO - Done. Returned value was: [...]
   ```
4. **Should show:** A list of astronauts with names and crafts

#### Check `print_astronaut_craft[0]` logs:
1. Click on any mapped `print_astronaut_craft` instance
2. Click "Log" button
3. **Look for:**
   ```
   👨‍🚀 <Name> is currently in space flying on the <Craft>! Hello from Earth! 🌍
   ```

#### Check `print_iss_location` logs:
1. Click on `print_iss_location` task
2. Click "Log" button
3. **Look for:**
   ```
   ============================================================
   🛰️  INTERNATIONAL SPACE STATION - CURRENT STATUS
   ============================================================

   📍 LOCATION:
      Latitude:  XX.XXXX°N
      Longitude: XX.XXXX°E
   ```

#### Check `generate_summary_report` logs:
1. Click on `generate_summary_report` task
2. Click "Log" button
3. **Look for:**
   ```
   ╔====================================================================╗
   ║               SPACE DATA PIPELINE - SUMMARY REPORT                 ║
   ╚====================================================================╝

   📅 Report Generated: ...
   👨‍🚀 ASTRONAUTS IN SPACE
   ...
   ✅ DATA QUALITY CHECKS
      ✓ PASS - Astronaut data retrieved
      ✓ PASS - ISS location valid
      ...
   ```

---

### Step 6: Verify Data Exports

#### Check CSV Export:
1. Click on `export_astronaut_data_to_csv` task
2. Click "Log" button
3. **Look for:**
   ```
   ✅ Astronaut data exported to: /tmp/astronauts_YYYYMMDD_HHMMSS.csv
      Total records: XX
      Columns: name, craft, total_in_space, data_retrieved
   ```

#### Check JSON Export:
1. Click on `export_iss_data_to_json` task
2. Click "Log" button
3. **Look for:**
   ```
   ✅ ISS data exported to: /tmp/iss_data_YYYYMMDD_HHMMSS.json
      File size: XXX bytes
   ```

---

## 🎯 Success Criteria

### ✅ You're Doing It Well If:

1. **All tasks are green** (dark green = success)
2. **Dynamic mapping works:** Multiple `print_astronaut_craft` instances appear
3. **Logs show data:** Astronaut names, ISS coordinates, formatted reports
4. **No errors in logs:** Check all task logs for Python exceptions
5. **Data quality checks pass:** All "✓ PASS" in summary report
6. **Files created:** CSV and JSON export messages appear in logs

---

## ❌ Common Issues & Solutions

### Issue: DAG doesn't appear in UI
**Solution:**
- Check `dags/` folder contains the file
- Restart Airflow: `astro dev restart`
- Check Airflow logs: `astro dev logs`

### Issue: Import Error
**Solution:**
- Check `requirements.txt` has all packages:
  ```
  pandas>=2.0.0
  requests>=2.28.0
  ```
- Rebuild: `astro dev stop && astro dev start`

### Issue: Dynamic mapping error (ValueError)
**Solution:**
- This is the error we just fixed!
- Make sure you have the latest code changes
- `get_astronauts()` should return a list directly
- Check line 369: `person_in_space=astronaut_list`

### Issue: API connection timeout
**Solution:**
- Check internet connection
- API might be temporarily down
- Try again in a few minutes

### Issue: Tasks stay yellow (running) forever
**Solution:**
- Check scheduler is running: `astro dev ps`
- Restart scheduler: `astro dev restart`
- Check task logs for stuck processes

---

## 🔧 Advanced Testing

### Test Individual Tasks (Optional)
```bash
# Test a single task without running the whole DAG
astro dev run dags test example_astronauts get_astronauts 2024-01-01
```

### Check XCom Values (Optional)
1. Go to Admin → XComs in Airflow UI
2. Filter by `dag_id = example_astronauts`
3. **Check:**
   - `get_astronauts` returns a list
   - Custom keys: `number_of_people_in_space`, `timestamp`, `message`
   - `get_astronaut_metadata` returns a dict

---

## 📊 Expected Output Summary

When everything works correctly, you should see:

```
✅ 10-15 astronauts currently in space
✅ ISS coordinates with Google Maps link
✅ Weather/location information for ISS position
✅ CSV file with astronaut data
✅ JSON file with ISS data
✅ Beautiful formatted summary report
✅ All data quality checks passing
```

---

## 🎓 Next Steps

Once your DAG runs successfully:

1. **Explore the data:** Check the exported CSV and JSON files
2. **Modify the schedule:** Change from `@daily` to `@hourly` if you want
3. **Add alerts:** Set up email notifications on failure
4. **Extend the pipeline:** Add more data sources or transformations
5. **Deploy to production:** `astro deploy` when ready

---

## 📚 Useful Commands

```bash
# Start Airflow
astro dev start

# Stop Airflow
astro dev stop

# Restart Airflow (after code changes)
astro dev restart

# View logs
astro dev logs

# Access Airflow CLI
astro dev bash
airflow dags list

# Deploy to Astro Cloud
astro deploy
```

---

## 🆘 Need Help?

- **Airflow Docs:** https://docs.astronomer.io/learn/get-started-with-airflow
- **Astro CLI Docs:** https://docs.astronomer.io/astro/cli/overview
- **Dynamic Task Mapping:** https://docs.astronomer.io/learn/dynamic-tasks

Happy orchestrating! 🚀
