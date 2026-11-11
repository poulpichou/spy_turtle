from pathlib import Path
import shutil,sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
main=root/'robot/startup/main.py';admin=root/'robot/api/admin.py';manager=root/'robot/system/robot_reset_manager.py'
if not all(p.exists() for p in (main,admin)):raise SystemExit('ERROR: run from spy_turtle repository root')
a=main.read_text(encoding='utf-8');b=admin.read_text(encoding='utf-8')
old='''    while True:
        try:
            robot.update()
            health.update()
'''
new='''    from robot.system.robot_reset_manager import reset_manager,reconstruct
    while True:
        request=reset_manager.pending()
        if request is not None:
            try:
                robot,result=reconstruct(robot)
                if result['ok']:health=HealthMonitor(robot)
            except Exception as error:
                from robot.system.runtime import set_robot
                set_robot(None)
                result={'ok':False,'phase':'reconstruct','error':f'{type(error).__name__}: {error}'}
                log.error(f'[RESET] full robot reconstruction failed: {error}')
            finally:reset_manager.finish(request,result)
        try:
            if robot is not None:
                robot.update()
                health.update()
'''
if a.count(old)!=1:raise SystemExit('ERROR: main.py differs from expected version')
a=a.replace(old,new)
start=b.index("@router.post('/turtle/reset')")
end=b.index("@router.post('/turtle/restart')",start)
replacement='''@router.post('/turtle/reset')
def reset_turtle(request:Request):
    from robot.system.robot_reset_manager import reset_manager
    log.warn(f'[ADMIN] full robot soft reset requested {source(request)}')
    try:return reset_manager.request(timeout=45)
    except RuntimeError as error:raise HTTPException(status_code=409,detail=str(error)) from error
    except TimeoutError as error:raise HTTPException(status_code=504,detail=str(error)) from error

'''
b=b[:start]+replacement+b[end:]
for p in (main,admin):shutil.copy2(p,p.with_suffix(p.suffix+'.pre_full_reset.bak'))
main.write_text(a,encoding='utf-8');admin.write_text(b,encoding='utf-8')
manager.write_text((Path(__file__).parent/'robot_reset_manager.py').read_text(encoding='utf-8'),encoding='utf-8')
print('Patched:',main,admin,manager,sep='\n  ')
