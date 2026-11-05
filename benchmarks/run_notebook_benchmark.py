"""Execute notebooks in place, one after another, and log wall time, per-cell time and peak memory.

Usage (from the repo root):  python -I benchmarks/run_notebook_benchmark.py 02_xgboost_xai/ALE_leakage_audit.ipynb 04_spatial_lisa_simulation/LISA_scenario_simulation.ipynb

Memory is the summed resident set of the nbconvert process tree (nbconvert + kernel), sampled every 2 s.
Per-cell peaks are the samples that fall inside the cell's execution window, so a cell shorter than 2 s may show no sample.
Stops at the first notebook that fails. Writes benchmarks/<notebook>_cells.csv and benchmarks/<notebook>_summary.json.
"""
import datetime as dt, json, os, subprocess, sys, time
import psutil

OUT = os.path.dirname(os.path.abspath(__file__))


def tree_rss(proc):
    try:
        ps = [proc] + proc.children(recursive=True)
    except psutil.Error:
        return 0
    tot = 0
    for p in ps:
        try:
            tot += p.memory_info().rss
        except psutil.Error:
            pass
    return tot


def run(path):
    path = os.path.abspath(path)
    folder, name = os.path.dirname(path), os.path.splitext(os.path.basename(path))[0]
    vm = psutil.virtual_memory()
    t0 = time.time()
    proc = subprocess.Popen([sys.executable, '-I', '-m', 'jupyter', 'nbconvert', '--to', 'notebook', '--execute',
                             '--inplace', '--ExecutePreprocessor.timeout=-1', os.path.basename(path)],
                            cwd=folder, stdout=subprocess.DEVNULL, stderr=open(os.path.join(OUT, f'{name}_stderr.log'), 'w'))
    ps, samples = psutil.Process(proc.pid), []
    while proc.poll() is None:
        samples.append((time.time(), tree_rss(ps)))
        time.sleep(2)
    wall = time.time() - t0
    nb = json.load(open(path, encoding='utf-8'))
    ts = lambda s: dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
    rows = []
    for i, c in enumerate(nb['cells']):
        e = c.get('metadata', {}).get('execution', {})
        if c['cell_type'] != 'code' or 'shell.execute_reply' not in e:
            continue
        a, b = ts(e['iopub.execute_input']), ts(e['shell.execute_reply'])
        inside = [r for t, r in samples if a <= t <= b]
        first = ''.join(c['source']).strip().splitlines()[0][:60] if c['source'] else ''
        rows.append({'cell': i, 'seconds': round(b - a, 1), 'peak_rss_gb': round(max(inside, default=0) / 1e9, 2), 'first_line': first})
    import csv
    with open(os.path.join(OUT, f'{name}_cells.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['cell', 'seconds', 'peak_rss_gb', 'first_line']); w.writeheader(); w.writerows(rows)
    summ = {'notebook': name, 'returncode': proc.returncode, 'wall_seconds': round(wall), 'sum_cell_seconds': round(sum(r['seconds'] for r in rows)),
            'peak_rss_gb': round(max((r for _, r in samples), default=0) / 1e9, 2),
            'machine_total_gb': round(vm.total / 1e9, 1), 'machine_available_at_start_gb': round(vm.available / 1e9, 1),
            'cpu_count': os.cpu_count(), 'started': dt.datetime.fromtimestamp(t0).isoformat(timespec='seconds')}
    json.dump(summ, open(os.path.join(OUT, f'{name}_summary.json'), 'w'), indent=1)
    print(summ, flush=True)
    return proc.returncode


if __name__ == '__main__':
    for nbp in sys.argv[1:]:
        if run(nbp) != 0:
            sys.exit(f'{nbp} failed, see benchmarks/*_stderr.log')
