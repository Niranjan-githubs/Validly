import os
import json
from typing import Dict, Any, Optional
from firebase_admin import firestore, credentials
import firebase_admin
from dotenv import load_dotenv

load_dotenv()

class FirebaseService:
    def __init__(self):
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Save session data to Firestore"""
        try:
            self.db.collection('sessions').document(session_id).set(session_data)
        except Exception as e:
            print(f"Error saving session to Firebase: {e}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Firestore"""
        try:
            doc = self.db.collection('sessions').document(session_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error getting session from Firebase: {e}")
            return None

    def delete_session(self, session_id: str) -> None:
        """Delete session from Firestore"""
        try:
            self.db.collection('sessions').document(session_id).delete()
        except Exception as e:
            print(f"Error deleting session from Firebase: {e}")

    def save_analysis_result(self, session_id: str, analysis_data: Dict[str, Any]) -> None:
        """Save analysis results to Firestore"""
        try:
            self.db.collection('analysis_results').document(session_id).set(analysis_data)
        except Exception as e:
            print(f"Error saving analysis result to Firebase: {e}")

    def get_analysis_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis results from Firestore"""
        try:
            doc = self.db.collection('analysis_results').document(session_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error getting analysis result from Firebase: {e}")
            return None

    def save_output(self, session_id: str, output_data: Dict[str, Any]) -> None:
        """Save output data to Firestore"""
        try:
            self.db.collection('outputs').document(session_id).set(output_data)
        except Exception as e:
            print(f"Error saving output to Firebase: {e}")

    def get_output(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get output data from Firestore"""
        try:
            doc = self.db.collection('outputs').document(session_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error getting output from Firebase: {e}")
            return None 