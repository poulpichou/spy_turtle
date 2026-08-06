from pathlib import Path
def edit(path,old,new):
    file=Path(path);text=file.read_text(encoding="utf-8")
    if old not in text:
        print(f"WARN: pattern not found in {path}: {old[:60]}")
        return
    file.write_text(text.replace(old,new),encoding="utf-8",newline="\n")

edit("robot/api/app.py","from robot.api import actions","from robot.api import actions\nfrom robot.api.admin import router as admin_router\nfrom robot.system.https_status import get_https_status")
edit("robot/api/app.py","app=FastAPI()","app=FastAPI()\napp.include_router(admin_router)")
edit("robot/api/app.py","PHOTOS.mkdir(exist_ok=True)","PHOTOS.mkdir(exist_ok=True)\nSTARTED_AT=datetime.now().isoformat()\n\n@app.middleware(\"http\")\nasync def no_cache(request,call_next):\n    response=await call_next(request)\n    if request.url.path==\"/\" or request.url.path.endswith((\".html\",\".css\",\".js\",\".webmanifest\")):\n        response.headers[\"Cache-Control\"]=\"no-store, no-cache, must-revalidate, max-age=0\"\n        response.headers[\"Pragma\"]=\"no-cache\"\n        response.headers[\"Expires\"]=\"0\"\n    return response")
edit("robot/api/app.py","@app.get('/state')\ndef get_state(): return state()","@app.get('/state')\ndef get_state(): return state()\n\n@app.get('/version')\ndef get_version(): return {'frontend':'2026.08.06.1','started_at':STARTED_AT}")
edit("robot/api/app.py","'ok':True,'timestamp':datetime.now().isoformat(),","'ok':True,'timestamp':datetime.now().isoformat(),'https':get_https_status(),")
edit("robot/api/app.py","@app.get('/camera/frame')\ndef camera_frame(): return Response(content=actions.camera_frame(),media_type='image/jpeg')","@app.get('/camera/frame')\ndef camera_frame(): return Response(content=actions.camera_frame(),media_type='image/jpeg',headers={'Cache-Control':'no-store'})\n\n@app.get('/thermal/frame')\ndef thermal_frame(): return Response(content=actions.camera_frame(),media_type='image/jpeg',headers={'Cache-Control':'no-store','X-Thermal-Fallback':'rgb-camera'})")

edit("frontend/index.html",'<link rel="stylesheet" href="css/mobile.css?v=6">','<link rel="stylesheet" href="css/mobile.css?v=8"><link rel="stylesheet" href="css/admin.css?v=1">')
edit("frontend/index.html",'<button class="center-tab active" data-view="camera">Camera</button>','<button class="center-tab active" data-view="camera">Camera</button><button class="center-tab" data-view="thermal">Thermal</button>')
edit("frontend/index.html",'<button class="center-tab" data-view="status">Status</button>','<button class="center-tab" data-view="status">Status</button><button class="center-tab" data-view="admin">Admin</button>')
edit("frontend/index.html",'<div id="camera-view" class="center-view active"><img id="camera-stream" src="/camera/frame" alt="Camera"></div>','<div id="camera-view" class="center-view active"><img id="camera-stream" src="/camera/frame" alt="Camera"></div><div id="thermal-view" class="center-view"><img id="thermal-stream" alt="Thermal camera"><span class="view-badge">RGB fallback until thermal camera is installed</span></div>')
edit("frontend/index.html",'</section>\n</section>\n<section id="right-panel">','<div id="admin-view" class="center-view"><div id="admin-panel"><div class="admin-actions"><button data-admin-action="restart">Restart Turtle</button><button data-admin-action="reboot">Reboot Pi</button><button data-admin-action="shutdown">Shutdown Pi</button></div><input id="wifi-ssid" placeholder="Wi-Fi SSID"><input id="wifi-password" type="password" placeholder="Wi-Fi password"><button id="wifi-add">Add Wi-Fi</button><pre id="admin-result">Limited local admin actions only. Requests are logged with their source IP.</pre></div></div>\n</section>\n</section>\n<section id="right-panel">')
edit("frontend/index.html",'<script src="js/center.js?v=5"></script>','<script src="js/center.js?v=7"></script><script src="js/admin.js?v=1"></script>')

edit("frontend/js/center.js",'let activeView="camera";','let activeView="camera";\nlet thermalTimer=null;')
edit("frontend/js/center.js","    stopHealth();","    stopHealth();\n    if(thermalTimer){clearInterval(thermalTimer);thermalTimer=null;}")
edit("frontend/js/center.js",'    if(name==="camera")startCameraRefresh();','    if(name==="camera")startCameraRefresh();\n    else if(name==="thermal"){stopCameraRefresh();const refresh=()=>document.getElementById("thermal-stream").src=`/thermal/frame?t=${Date.now()}`;refresh();thermalTimer=setInterval(refresh,250);}')

print("Update applied. Review with git diff.")
