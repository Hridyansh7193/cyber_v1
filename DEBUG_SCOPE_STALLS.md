# Debugging Scope Enforcement Stalls

## Problem
Scans get stuck at `scope_enforcement_node` (36% progress) after 10-16+ minutes. The node is performing URL filtering and appears to be hanging.

## Root Cause
The `scope_enforcement_node` is stalling due to one of these reasons:
1. **Too many URLs discovered** by passive_recon (millions)
2. **Slow regex matching** when checking URLs against scope rules
3. **Executor shutdown** if filtering takes too long

## Diagnostic Steps

### Step 1: Check if the scan created a checkpoint
```bash
ls workspaces/testphp.vulnweb.com/sessions/<JOB_ID>/checkpoint.json
```

If the checkpoint exists, the scan progressed at least to `scope_enforcement_node`.

### Step 2: Run the diagnostic script
```bash
python diagnose_stall.py <JOB_ID> testphp.vulnweb.com
```

This will show:
- How many URLs passive_recon discovered
- URLs per netloc (domain)
- Filtering rate (URLs/second)
- **Estimated time** to filter all URLs

Example output:
```
📊 Recon Discovery Results:
   URLs: 250,000 discovered

⏱️  Scope Filtering Profile (sample of first 1000 URLs):
   Rate: 150 URLs/second
   ⚠️  Estimated time for ALL 250,000 URLs: 1667s (27.8 minutes)
   ⚠️  RISK: Filtering will take >5 minutes!
```

### Step 3: Check the logs
```bash
# View the orchestrator adapter logs with lifecycle markers
grep "\[SCOPE\]" bughunter.log

# Look for progress updates
grep "URL progress" bughunter.log
```

You should see entries like:
```
[SCOPE] URL progress: 10000/250000 (4.0%) | rate=150 URLs/s | ETA=1600s
[SCOPE] URL progress: 20000/250000 (8.0%) | rate=150 URLs/s | ETA=1533s
```

## Solutions

### Option 1: Increase URL cap (Quick Fix)
Modify `orchestrator/nodes/scope_enforcement_node.py`:
```python
_MAX_URLS_TO_FILTER = 10_000  # Increase from 5000
```

This will sample more URLs but still cap the total.

### Option 2: Enable aggressive filtering (Medium Fix)
Reduce scope size in your config to filter more URLs:
```yaml
target:
  scope:
    - example.com
  out_of_scope:
    - admin.example.com
    - staging.example.com
```

### Option 3: Optimize regex matching (Advanced Fix)
Profile the `ScopeManager.is_in_scope()` method:
```bash
python -m cProfile -s cumulative scripts/profile_scope_manager.py
```

Look for `re.search()` or `re.compile()` calls taking too much time.

### Option 4: Reduce passive_recon scope
Edit your scan config to disable some passive recon sources:
```bash
bughunter scan example.com --profile=light  # Use lighter profile
```

## Understanding the Timeout

The code now includes a **5-minute timeout** for URL filtering:
- If filtering > 5 min, it aborts and uses partial results
- Logs show: `[SCOPE] URL filtering TIMEOUT after 300s!`
- Prevents indefinite hangs

## Monitoring during scan

To monitor in real-time while scan is running:

### Terminal 1 - Run scan
```bash
bughunter scan testphp.vulnweb.com --debug 2>&1 | tee scan.log
```

### Terminal 2 - Monitor progress
```bash
# Every 2 seconds, show latest URL progress
watch -n 2 'tail -30 scan.log | grep "\[SCOPE\]"'
```

## Expected Timings

For a typical target:
- **Good**: Filtering 1,000 URLs in 1-2 seconds
- **Okay**: Filtering 10,000 URLs in 10-20 seconds
- **Slow**: Filtering 100,000 URLs in 2-5 minutes
- **Too Slow**: Filtering > 5 minutes (triggers timeout)

## If timeout is triggered

When the 5-minute timeout is hit:
1. Log shows: `[SCOPE] URL filtering TIMEOUT`
2. Scan continues with **partial results**
3. Scan completes with warning
4. Check logs for `[SCOPE] URL filtering TIMEOUT after 300s!`

To prevent timeout:
- Reduce URL discovery
- Optimize ScopeManager filtering
- Increase `_URL_FILTER_TIMEOUT_SEC` constant

## Performance Optimization Ideas

1. **Cache scope decisions**: Don't re-check same netloc twice
2. **Batch processing**: Check URLs in parallel batches
3. **Pre-compile regexes**: Move regex compilation outside loop
4. **Use faster matcher**: Replace regex with fnmatch or glob for simple patterns

## Reporting the Issue

If you're still experiencing problems, run:
```bash
# Generate diagnostic report
python diagnose_stall.py <JOB_ID> testphp.vulnweb.com > diagnostic.txt

# Include in bug report
cat diagnostic.txt
grep "\[SCOPE\]" scan.log > scope_logs.txt
```

Include both files when reporting issues.
