from fastapi import HTTPException

def get_user_session(uid, session_id, firebase_service):
    session_ref = firebase_service.db.collection('outputs').document(uid).collection('sessions').document(session_id)
    session_doc = session_ref.get()
    if not session_doc.exists:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_doc.to_dict()