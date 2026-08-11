import json
import subprocess
from pathlib import Path
from robot.utils.logger import log

class WifiManager:
    def __init__(self,config_path=None):
        self.path=Path(config_path) if config_path else Path.home()/'.config'/'spy_turtle'/'wifi.json'
        self.nicknames=self._load()

    def _load(self):
        try:
            with self.path.open(encoding='utf-8') as file:data=json.load(file)
            return data if isinstance(data,dict) else {}
        except (FileNotFoundError,json.JSONDecodeError):return {}

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(self.nicknames,indent=2)+'\n',encoding='utf-8')

    @staticmethod
    def _run(args,check=True):
        process=subprocess.run(['nmcli',*args],capture_output=True,text=True,timeout=8)
        if check and process.returncode:raise RuntimeError((process.stderr or process.stdout or 'nmcli failed').strip())
        return process.stdout.strip()

    @staticmethod
    def _sudo(args):
        process=subprocess.run(['sudo','-n','nmcli',*args],capture_output=True,text=True,timeout=20)
        if process.returncode:raise RuntimeError((process.stderr or process.stdout or 'nmcli failed').strip())
        return process.stdout.strip()

    def _profiles(self):
        output=self._run(['-t','-f','NAME,TYPE,DEVICE','connection','show'])
        profiles=[]
        for line in output.splitlines():
            parts=line.rsplit(':',2)
            if len(parts)!=3:continue
            name,kind,device=parts
            if kind not in ('802-11-wireless','wifi'):continue
            try:ssid=self._run(['-g','802-11-wireless.ssid','connection','show',name])
            except RuntimeError:ssid=''
            if not ssid:continue
            try:auto=self._run(['-g','connection.autoconnect','connection','show',name]).lower()=='yes'
            except RuntimeError:auto=True
            profiles.append({'profile':name,'ssid':ssid,'nickname':self.nicknames.get(ssid,ssid),'active':bool(device),'device':device or None,'autoconnect':auto})
        return profiles

    def status(self):
        networks=self._profiles()
        current=next((network for network in networks if network['active']),None)
        return {'networks':networks,'current':current}

    def add(self,nickname,ssid,password):
        nickname=nickname.strip() or ssid
        self.nicknames[ssid]=nickname
        self._save()
        self._sudo(['device','wifi','connect',ssid,'password',password])
        log.info(f'[WIFI] saved nickname={nickname} ssid={ssid}')
        return {'nickname':nickname,'ssid':ssid}

    def connect(self,ssid):
        network=next((item for item in self._profiles() if item['ssid']==ssid),None)
        if not network:raise RuntimeError(f'Unknown Wi-Fi network: {ssid}')
        self._sudo(['connection','up',network['profile']])
        log.info(f"[WIFI] connect {self.nicknames.get(ssid,ssid)} ({ssid})")

    def delete(self,ssid):
        network=next((item for item in self._profiles() if item['ssid']==ssid),None)
        if not network:raise RuntimeError(f'Unknown Wi-Fi network: {ssid}')
        self._sudo(['connection','delete',network['profile']])
        self.nicknames.pop(ssid,None)
        self._save()
        log.info(f'[WIFI] deleted {ssid}')

wifi_manager=WifiManager()
