import json
import random
import time
from pathlib import Path
from robot.utils.logger import log

CONFIG=Path(__file__).resolve().parents[1]/'config'/'moods.json'

class MoodEngine:
    def __init__(self,robot,config_path=CONFIG):
        self.robot=robot;self.path=Path(config_path);self.config=json.loads(self.path.read_text(encoding='utf-8'))
        self.options=self.config['settings'];self.variants={entry['id']:entry for entry in self.config['moods']}
        self._validate();self.current=None;self.deadline=0.0;self.head_steps=[];self.next_head_at=0.0
        self.manual_head_until=0.0;self._last_motion=None;self.headlights_enabled=False
        self.choose(self.options['default_variant'])

    def _validate(self):
        if not self.variants:raise ValueError('Mood catalog is empty')
        if len(self.variants)!=len(self.config['moods']):raise ValueError('Duplicate mood variant')
        for entry in self.variants.values():
            if entry['weight']<0 or len(entry['duration_seconds'])!=2 or entry['duration_seconds'][0]<=0 or entry['duration_seconds'][1]<entry['duration_seconds'][0]:raise ValueError('Invalid mood weight/duration: '+entry['id'])
            if len(entry['contexts'])<5 or any(not c.get('fr') or not c.get('en') for c in entry['contexts']):raise ValueError('At least five bilingual contexts required: '+entry['id'])
            if entry['head']['pattern'] not in ('none','look','scan','shake'):raise ValueError('Unknown head pattern: '+entry['id'])

    def set_head_enabled(self,enabled):
        self.options['enable_head_movements']=bool(enabled)
        self._save()
        if not enabled:self.head_steps=[]
        return self.status()

    def _save(self):
        self.config['settings']=self.options
        temp=self.path.with_suffix('.tmp');temp.write_text(json.dumps(self.config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(self.path)

    def status(self):return {'enable_head_movements':bool(self.options.get('enable_head_movements',False)),'headlights_enabled':self.headlights_enabled,'mood':self.robot.state.mood,'mood_variant':self.robot.state.mood_variant,'mood_remaining_seconds':round(max(0,self.deadline-time.monotonic()),1),'variants':[{'id':v['id'],'mood':v['mood']} for v in self.variants.values()]}

    def choose(self,variant=None):
        if variant is None:
            candidates=[v for v in self.variants.values() if v['weight']>0]
            if self.options.get('avoid_repeat_variant') and len(candidates)>1:candidates=[v for v in candidates if v['id']!=self.robot.state.mood_variant]
            if not candidates:return
            entry=random.choices(candidates,weights=[v['weight'] for v in candidates],k=1)[0]
        else:
            entry=self.variants.get(variant)
            if entry is None:
                matches=[v for v in self.variants.values() if v['mood']==variant]
                if not matches:raise ValueError('Unknown mood: '+str(variant))
                entry=random.choices(matches,weights=[v['weight'] for v in matches],k=1)[0]
        state=self.robot.state;context=random.choice(entry['contexts'])
        state.mood=entry['mood'];state.mood_variant=entry['id'];state.mood_context_fr=context['fr'];state.mood_context_en=context['en']
        state.emotion=entry['eyes'];self.current=entry;self.deadline=time.monotonic()+random.uniform(*entry['duration_seconds']);state.mood_deadline_monotonic=self.deadline
        self.head_steps=[];self.next_head_at=0.0
        if self.robot.face and not self.robot.face.is_user_locked():
            try:self.robot.face.play(entry['eyes'])
            except Exception as exc:log.warn(f'[MOOD] eyes {entry["eyes"]}: {exc}')
        if self.robot.leds and not self.headlights_enabled and self.robot.power.data.get("shell_light",True):
            try:self.robot.leds.set_mode(entry['leds']);state.led_mode=entry['leds']
            except Exception as exc:log.warn(f'[MOOD] leds {entry["leds"]}: {exc}')
        self._apply_media(entry)
        log.info(f'[MOOD] {entry["id"]} ({entry["mood"]})')
        return self.status()

    def _apply_media(self,entry):
        from robot.assets.assets import get_asset_names
        shell=entry.get('shell')
        if shell and self.robot.shell and self.robot.power.data.get('back_screen',True):
            if self.robot.shell.active_mode=='status':
                try:self.robot.shell.show_image(shell)
                except Exception as error:log.warn(f'[MOOD] shell {shell}: {error}')
            else:log.info(f'[MOOD] shell skipped active={self.robot.shell.active_mode}')
        sound=entry.get('sound')
        if not sound or not self.robot.speaker:return
        if not self.robot.power.data.get('automation_sounds',True) or not self.robot.power.data.get('automation_enabled',True) or self.robot.power.idle_mode:return
        try:
            if sound not in get_asset_names('audio'):
                log.warn(f'[MOOD] sound asset missing: {sound}')
                return
            self.robot.speaker.play(sound)
        except Exception as error:log.warn(f'[MOOD] sound {sound}: {error}')

    def set_headlights(self,enabled):
        enabled=bool(enabled)
        if enabled and self.robot.power.idle_mode:raise ValueError('Disable Idle mode before using headlights')
        if not self.robot.leds:raise ValueError('LED controller unavailable')
        if enabled==self.headlights_enabled:return self.status()
        if enabled:
            if hasattr(self.robot.leds,'set_enabled'):self.robot.leds.set_enabled(True)
            self.robot.leds.set_mode('headlights');self.robot.state.led_mode='headlights';self.headlights_enabled=True
        else:
            self.headlights_enabled=False
            mode=self.current['leds'] if self.current else 'neutral'
            if not self.robot.power.data.get('shell_light',True):mode='off'
            self.robot.leds.set_mode(mode);self.robot.state.led_mode=mode
            if not self.robot.power.data.get('shell_light',True) and hasattr(self.robot.leds,'set_enabled'):self.robot.leds.set_enabled(False)
        log.info(f'[LIGHTS] headlights={"on" if enabled else "off"}')
        return self.status()

    def manual_head_override(self):
        self.manual_head_until=time.monotonic()+float(self.options.get('head_manual_cooldown_seconds',12));self.head_steps=[]

    def update(self):
        if not self.options.get('enabled',True) or not self.robot.power.data.get('automation_enabled',True):return
        now=time.monotonic();state=self.robot.state
        if state.motion!='stop' or state.sleeping_until or now-self._interaction_monotonic()<float(self.options.get('pause_after_interaction_seconds',8)):return
        if now>=self.deadline and not (self.robot.face and self.robot.face.is_user_locked()):self.choose()
        self._update_head(now)

    def _interaction_monotonic(self):
        # state interaction timestamp is wall clock; convert its age to monotonic reference.
        return time.monotonic()-max(0,time.time()-self.robot.state.last_interaction_at)

    def _update_head(self,now):
        if not self.robot.power.data.get('automation_enabled',True) or not self.options.get('enable_head_movements') or not self.robot.servo or now<self.manual_head_until:return
        if not hasattr(self.robot.servo,'pan') or now<self.next_head_at:return
        if not self.head_steps:
            h=self.current['head'];a=float(h.get('amplitude_degrees',0));pattern=h['pattern']
            if pattern=='none' or a<=0:return
            count=max(1,min(5,int(h.get('repetitions',1))))
            center=self.robot.servo.pan.center_angle
            if pattern=='look':self.head_steps=[center+random.choice((-a,a)),center]
            elif pattern=='scan':self.head_steps=[center-a,center+a,center]
            elif pattern=='shake':self.head_steps=[center+a,center-a]*count+[center]
        target=self.head_steps.pop(0)
        try:self.robot.servo.pan.set_target(target)
        except Exception as exc:log.warn(f'[MOOD] head: {exc}');self.head_steps=[];return
        self.next_head_at=now+max(0.2,float(self.current['head'].get('step_interval_seconds',1.0)))
        if not self.head_steps:self.next_head_at=now+random.uniform(5,12)
