"""Session-level password checking. This does not replace an identity provider."""
import hmac

MAX_FAILURES=5
LOCK_SECONDS=60


def verify(state,submitted,expected,now):
    if now<float(state.get('auth_retry_at',0)):return 'locked'
    if hmac.compare_digest(str(submitted).encode('utf-8'),str(expected).encode('utf-8')):
        state['authed']=True;state['auth_failures']=0;state.pop('auth_retry_at',None)
        return 'ok'
    attempts=int(state.get('auth_failures',0))+1
    state['auth_failures']=attempts
    if attempts>=MAX_FAILURES:
        state['auth_failures']=0;state['auth_retry_at']=now+LOCK_SECONDS
        return 'locked'
    return 'invalid'
