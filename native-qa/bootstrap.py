"""One-use encrypted transport for an authorized Windows package verification."""
import base64, io, json, os, pathlib, subprocess, sys, time, urllib.request, urllib.error, zipfile
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

root = pathlib.Path(os.environ['RUNNER_TEMP']) / 'eds-native-private'
root.mkdir(exist_ok=True)
repo, branch, run_id = (os.environ[k] for k in ('GITHUB_REPOSITORY','GITHUB_REF_NAME','GITHUB_RUN_ID'))
api = 'https://raw.githubusercontent.com/' + repo + '/' + branch + '/'
def public_get(path):
    req=urllib.request.Request(api+path,headers={'User-Agent':'EDS-native-QA','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
def b64(data):return base64.b64encode(data).decode()
key_path=root/'session_private.pem'
if sys.argv[1:] == ['keygen']:
    key=rsa.generate_private_key(public_exponent=65537,key_size=3072)
    key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
    public_dir=pathlib.Path(os.environ['GITHUB_WORKSPACE'])/'native-handshake'
    public_dir.mkdir(exist_ok=True)
    (public_dir/'public.pem').write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
    print('Created one-use public key for native Windows verification',flush=True)
    sys.exit(0)
key=serialization.load_pem_private_key(key_path.read_bytes(),password=None)
print('Windows runner ready for encrypted test package; run '+run_id,flush=True)
packet=None
for _ in range(60):
    try:
        packet=public_get('native-qa/requests/'+run_id+'.json?check='+str(time.time_ns()));break
    except urllib.error.HTTPError as e:
        if e.code!=404:raise
    time.sleep(15)
if packet is None:raise RuntimeError('No encrypted test request received')
decode=base64.b64decode
aes=key.decrypt(decode(packet['wrapped_key']),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
payload=AESGCM(aes).decrypt(decode(packet['nonce']),decode(packet['ciphertext']),run_id.encode())
with zipfile.ZipFile(io.BytesIO(payload)) as z:z.extractall(root)
key_path.unlink()
del payload, aes, packet, key
result_public=serialization.load_pem_public_key((root/'result_public.pem').read_bytes())
status=1
try:
    proc=subprocess.run([sys.executable,str(root/'run_native.py')],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=1200)
    (root/'results').mkdir(exist_ok=True)
    (root/'results'/'runner-private.log').write_bytes(proc.stdout)
    status=proc.returncode
except Exception as e:
    (root/'results').mkdir(exist_ok=True)
    (root/'results'/'runner-error.txt').write_text(type(e).__name__+': '+str(e),encoding='utf-8')
finally:
    memory=io.BytesIO()
    with zipfile.ZipFile(memory,'w',zipfile.ZIP_DEFLATED) as z:
        for p in (root/'results').rglob('*'):
            if p.is_file():z.write(p,p.relative_to(root/'results'))
    aes=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12)
    encrypted={'wrapped_key':b64(result_public.encrypt(aes,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))),'nonce':b64(nonce),'ciphertext':b64(AESGCM(aes).encrypt(nonce,memory.getvalue(),run_id.encode()))}
    artifact=pathlib.Path(os.environ['GITHUB_WORKSPACE'])/'native-output';artifact.mkdir(exist_ok=True)
    (artifact/'encrypted-results.json').write_text(json.dumps(encrypted),encoding='utf-8')
    (artifact/'status.json').write_text(json.dumps({'run_id':run_id,'native_windows':os.name=='nt','test_process_exit_code':status}),encoding='utf-8')
    print('Native verification finished. Exit code: '+str(status)+'. Detailed evidence encrypted for the requester.',flush=True)
sys.exit(status)
