"""Run a trusted local setup and several renders without reopening Blender or the scene.

blender -b -t 0 --python tools/render_warm_batch.py -- /absolute/job.json
Job: setup is a Python script (loads scene/configures native guards once); passes
have output and optional edit script. Edits must mutate loaded datablocks in place.
Changing material graphs/render features can invalidate caches. No speedup assumed.
"""
import bpy, json, runpy, sys, time
from pathlib import Path
job_path = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
job = json.loads(job_path.read_text())
runpy.run_path(str(Path(job['setup']).resolve()), run_name='__warm_setup__')
s = bpy.context.scene
s.render.threads_mode = 'AUTO'
records = []
def passes():
    current=job
    while True:
        yield from current['passes']
        if not current.get('next_job'):break
        next_path=Path(current['next_job']);deadline=time.monotonic()+1200
        print('WARM_BATCH awaiting continuation',next_path,flush=True)
        while not next_path.exists():
            if time.monotonic()>deadline:raise TimeoutError(next_path)
            time.sleep(1)
        current=json.loads(next_path.read_text())
for item in passes():
    output = Path(item['output']).resolve()
    if output.exists():
        raise FileExistsError(output)
    if item.get('edit'):
        runpy.run_path(str(Path(item['edit']).resolve()), run_name='__warm_edit__')
        if bpy.context.scene != s:
            raise RuntimeError('Warm edits must retain the loaded scene')
    output.parent.mkdir(parents=True, exist_ok=True)
    s.render.filepath = str(output)
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    records.append({'output': str(output), 'seconds': time.monotonic()-start})
    Path(job['timings']).write_text(json.dumps(records, indent=2))
    print('WARM_BATCH', records[-1], flush=True)
