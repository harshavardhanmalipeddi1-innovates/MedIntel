import logging
from typing import Dict, Any, Optional
from uuid import uuid4

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

logger = logging.getLogger(__name__)

class FirestoreService:
    """
    Abstraction layer for Firestore to support testing and decoupling.
    Do not trust client-side rules alone for production.
    """
    
    def __init__(self, mock_db=None):
        self.mock_db = mock_db
        self.is_mock = False

        if self.mock_db is not None:
            self.db = self.mock_db
            self.is_mock = True
        elif FIREBASE_AVAILABLE:
            try:
                # Initializes with default application credentials
                # Requires GOOGLE_APPLICATION_CREDENTIALS in env
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                self.db = firestore.client()
            except Exception as e:
                logger.warning(f"Failed to initialize real Firestore client: {e}")
                self.db = {}
                self.is_mock = True
        else:
            self.db = {}
            self.is_mock = True

    def _get_collection_store(self, collection: str) -> Dict[str, Dict[str, Any]]:
        if isinstance(self.db, dict):
            return self.db.setdefault(collection, {})
        raise RuntimeError("Firestore collection store only available in mock mode")

    def add_document(self, collection: str, data: Dict[str, Any]) -> str:
        if self.is_mock:
            logger.info(f"Mock add_document to {collection}.")
            collection_store = self._get_collection_store(collection)
            doc_id = str(uuid4())
            collection_store[doc_id] = data.copy()
            return doc_id
            
        doc_ref = self.db.collection(collection).document()
        doc_ref.set(data)
        return doc_ref.id
        
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        if self.is_mock:
            logger.info(f"Mock get_document from {collection}/{doc_id}.")
            collection_store = self._get_collection_store(collection)
            return collection_store.get(doc_id)
            
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def list_documents(self, collection: str) -> list[Dict[str, Any]]:
        if self.is_mock:
            collection_store = self._get_collection_store(collection)
            return [
                {**data.copy(), "id": doc_id}
                for doc_id, data in collection_store.items()
            ]

        docs = self.db.collection(collection).stream()
        documents = []
        for doc in docs:
            doc_data = doc.to_dict() or {}
            doc_data["id"] = doc.id
            documents.append(doc_data)
        return documents

    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        if self.is_mock:
            logger.info(f"Mock update_document {collection}/{doc_id}.")
            collection_store = self._get_collection_store(collection)
            if doc_id not in collection_store:
                raise KeyError(f"Document {doc_id} not found in collection {collection}")
            collection_store[doc_id].update(data)
            return
            
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.update(data)
