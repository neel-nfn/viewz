from fastapi import APIRouter
import os, json, pathlib, time

router = APIRouter(prefix="/api/v1/dev", tags=["dev-diagnostic"])

def _store_dir():
    return os.environ.get("LOCAL_STORE_DIR") or os.path.join(os.getcwd(), "local_dev_store")

@router.post("/test_save")
def test_save():
    d = _store_dir()
    pathlib.Path(d).mkdir(parents=True, exist_ok=True)
    sample = [{"id":"DEV_TEST_"+str(int(time.time())), "title":"Dev Diagnostic Channel"}]
    with open(os.path.join(d,"channels.json"), "w") as f:
        json.dump(sample, f)
    return {"ok": True, "dir": d, "written": "channels.json"}

@router.get("/state")
def state():
    return {
        "LOCAL_STORE_DIR": _store_dir(),
        "SUPABASE_URL": os.environ.get("SUPABASE_URL",""),
        "SUPABASE_SERVICE_KEY_present": bool(os.environ.get("SUPABASE_SERVICE_KEY")),
    }
