"""PAM authentication for the fixed sqlink system account. No secret logging."""
import ctypes as C
class Message(C.Structure):_fields_=[('style',C.c_int),('msg',C.c_char_p)]
class Response(C.Structure):_fields_=[('resp',C.c_void_p),('code',C.c_int)]
Callback=C.CFUNCTYPE(C.c_int,C.c_int,C.POINTER(C.POINTER(Message)),C.POINTER(C.POINTER(Response)),C.c_void_p)
class Conversation(C.Structure):_fields_=[('callback',Callback),('data',C.c_void_p)]
def authenticate(username,password):
 if username!='sqlink' or not isinstance(password,str) or not password or len(password)>512 or '\x00' in password:return False
 pam=C.CDLL('libpam.so.0');libc=C.CDLL(None)
 libc.calloc.argtypes=[C.c_size_t,C.c_size_t];libc.calloc.restype=C.c_void_p
 libc.strdup.argtypes=[C.c_char_p];libc.strdup.restype=C.c_void_p
 libc.free.argtypes=[C.c_void_p]
 pam.pam_start.argtypes=[C.c_char_p,C.c_char_p,C.POINTER(Conversation),C.POINTER(C.c_void_p)];pam.pam_start.restype=C.c_int
 for name in ('pam_authenticate','pam_acct_mgmt','pam_end'):
  getattr(pam,name).argtypes=[C.c_void_p,C.c_int];getattr(pam,name).restype=C.c_int
 @Callback
 def converse(n,messages,out,data):
  if not 1<=n<=16:return 19
  raw=libc.calloc(n,C.sizeof(Response))
  if not raw:return 5
  answers=C.cast(raw,C.POINTER(Response));allocated=[]
  try:
   for i in range(n):
    style=messages[i].contents.style
    if style in (1,2):
     ptr=libc.strdup((password if style==1 else username).encode())
     if not ptr:raise MemoryError()
     allocated.append(ptr);answers[i].resp=ptr
    elif style not in (3,4):raise ValueError()
   out[0]=answers;return 0
  except Exception:
   for ptr in allocated:libc.free(ptr)
   libc.free(raw);return 19
 handle=C.c_void_p();conv=Conversation(converse,None)
 result=pam.pam_start(b'sqlink-web',b'sqlink',C.byref(conv),C.byref(handle))
 if result:return False
 try:
  result=pam.pam_authenticate(handle,0)
  if result==0:result=pam.pam_acct_mgmt(handle,0)
  return result==0
 finally:pam.pam_end(handle,result)
