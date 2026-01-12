from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.model_name = "all-MiniLM-L6-v2"
        return cls._instance

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading Embedding Model ({self.model_name})...")
            # Force CPU usage (device='cpu') since these models are small and fast on CPU
            # This saves GPU memory for the heavy VTON models
            self._model = SentenceTransformer(self.model_name, device='cpu')
            logger.info("Embedding Model Loaded.")
        return self._model

    def generate_embedding(self, text: str):
        """
        Generates a 384-dimensional embedding for the given text.
        """
        if not text:
            return None
            
        try:
            # Encode returns numpy array, convert to list for PGVector/JSON compatibility
            # normalize_embeddings=True makes cosine similarity == dot product (better for valid search)
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

embedding_service = EmbeddingService()
