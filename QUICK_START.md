# 🚀 Quick Start - example_astronauts DAG

## Run Your DAG in 3 Steps

### 1️⃣ Start Airflow
```bash
astro dev start
```
⏱️ Wait 2-3 minutes for startup

### 2️⃣ Open Airflow UI
Open: **http://localhost:8080**
- Username: `admin`
- Password: `admin`

### 3️⃣ Trigger the DAG
1. Find `example_astronauts` in the DAG list
2. Click the **▶️ Play button** (top right)
3. Click "Trigger"
4. Watch tasks turn green! ✅

---

## ✅ Success Checklist (1 Minute)

After the DAG runs, quickly verify:

- [ ] **All tasks are green** (no red/failed tasks)
- [ ] **Multiple astronaut tasks** appear (`print_astronaut_craft[0]`, `[1]`, `[2]`, etc.)
- [ ] **Click on `generate_summary_report`** → View Logs → See beautiful report
- [ ] **Report shows:** "✓ PASS" for all data quality checks

---

## 🎯 What Success Looks Like

### In the Graph View:
```
get_astronauts → [get_astronaut_metadata]
                 [print_astronaut_craft[0]]
                 [print_astronaut_craft[1]]
                 [print_astronaut_craft[2]]
                 ... (10-15 total)

get_iss_location → get_weather_at_iss_location → print_iss_location

All tasks → generate_summary_report
```
**All boxes should be dark green!**

### In the Logs:
Click `generate_summary_report` → Logs → Should see:
```
╔====================================================================╗
║               SPACE DATA PIPELINE - SUMMARY REPORT                 ║
╚====================================================================╝

👨‍🚀 ASTRONAUTS IN SPACE
   Total Astronauts: XX

🛰️  ISS CURRENT LOCATION
   Coordinates:  XX.XXXX°N, XX.XXXX°E

✅ DATA QUALITY CHECKS
   ✓ PASS - Astronaut data retrieved
   ✓ PASS - ISS location valid
   ✓ PASS - Weather data available
   ✓ PASS - CSV export successful
   ✓ PASS - JSON export successful

🚀 Pipeline execution completed successfully!
```

---

## ❌ Troubleshooting (30 seconds)

| Problem | Quick Fix |
|---------|-----------|
| DAG not showing | `astro dev restart` |
| Red import error | Check `requirements.txt` has `pandas` and `requests` |
| Tasks stuck yellow | Wait 30 seconds, or `astro dev restart` |
| "cannot map over XCom" error | ✅ Already fixed in your code! |

---

## 📖 Full Guide
See `TESTING_GUIDE.md` for detailed instructions, advanced testing, and troubleshooting.

---

## 🆘 Quick Help
```bash
# Stop Airflow
astro dev stop

# View real-time logs
astro dev logs -f

# Deploy to production
astro deploy
```

**Your DAG is ready to run! Just do:** `astro dev start` 🚀
