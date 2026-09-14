from pathlib import Path
import re
import shutil
import sys
from runtime import atomic_json,digest,entry,files,inside,parser,read_json

DENY=re.compile(r'(?i)(^\.env($|\.)|password|passwd|credential|cookie|token|secret|login data|web data|^id_(rsa|ed25519|ecdsa)|^\.ssh$|^\.aws$|^\.azure$|^\.gnupg$|^\.git$|^appdata$)')
def allowed(path):
    return not any(DENY.search(p) for p in Path(path).parts) and Path(path).suffix.lower() not in ('.pem','.key','.pfx','.p12','.kdbx')

def plan(sources):
    result=[];skipped=0
    for index,source in enumerate(sources):
        root=Path(source).resolve()
        for path in files(root):
            relative=path.relative_to(root)
            if not allowed(relative):skipped+=1;continue
            result.append({'source':str(path),'relative':f'{index+1}-{root.name}/{relative.as_posix()}','size':path.stat().st_size})
    return {'files':result,'excluded_count':skipped,'total_bytes':sum(p['size'] for p in result)}

def backup(sources,destination):
    destination=Path(destination).resolve()
    for source in sources:
        if destination.is_relative_to(Path(source).resolve()):raise ValueError('Backup nie może być wewnątrz źródła.')
    data=plan(sources);destination.mkdir(parents=True,exist_ok=False)
    entries=[];errors=[]
    for index,item in enumerate(data['files']):
        target=inside(destination,item['relative']);target.parent.mkdir(parents=True,exist_ok=True)
        try:
            source=Path(item['source']);before=source.stat()
            if source.is_symlink():raise ValueError('Źródło stało się dowiązaniem.')
            shutil.copy2(source,target)
            value=digest(target);after=source.stat()
            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns) or value!=digest(source):
                target.unlink();raise ValueError('Zmiana źródła podczas kopii.')
            entries.append({'path':item['relative'],'sha256':value,'size':target.stat().st_size})
        except (OSError,ValueError) as exc:errors.append({'path':item['relative'],'error':type(exc).__name__})
        atomic_json(destination/'manifest.json',{'schema_version':1,'files':entries,'errors':errors,'complete':index+1==len(data['files']) and not errors})
        if (index+1)%100==0:print(f'Postęp: {index+1}/{len(data["files"])}',file=sys.stderr)
    if not data['files']:atomic_json(destination/'manifest.json',{'schema_version':1,'files':[],'errors':[],'complete':True})
    return {'copied':len(entries),'excluded':data['excluded_count'],'errors':errors,'ok':not errors,'destination':str(destination)}

def verify(directory):
    directory=Path(directory);data=read_json(directory/'manifest.json')
    if data.get('schema_version')!=1 or not isinstance(data.get('files'),list):raise ValueError('Nieprawidłowy manifest.')
    problems=[]
    for item in data['files']:
        p=inside(directory,item['path'])
        if not p.is_file():problems.append({'path':item['path'],'status':'MISSING'})
        elif digest(p)!=item['sha256']:problems.append({'path':item['path'],'status':'CHANGED'})
    return {'problems':problems,'ok':not problems and data.get('complete') is True}

def build():
    p=parser('Backup do nowego katalogu. Filtry wykluczają znane magazyny sekretów.')
    p.add_argument('command',nargs='?',choices=['plan','backup','verify'])
    p.add_argument('--source',action='append');p.add_argument('--destination');p.add_argument('--apply',action='store_true')
    return p

def handle(a):
    if a.command=='verify':
        if not a.destination:raise ValueError('Podaj destination.')
        return verify(a.destination)
    if not a.source:raise ValueError('Wskaż foldery przez --source.')
    if a.command=='plan' or (a.command=='backup' and not a.apply):return plan(a.source)
    if a.command=='backup' and a.destination:return backup(a.source,a.destination)
    raise ValueError('Wybierz polecenie i destination.')

if __name__=='__main__':sys.exit(entry(build,handle))
