import sqlite3
import os
import time
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import torch

torch.set_num_threads(1)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class MemoryStore:
    def __init__(self, persistDirectory: str = "data/memory", collectionName: str = "discord_memories", embeddingModel: str = "all-MiniLM-L6-v2"):
        """Initialize Memory Store using SQLite and local SentenceTransformers."""
        self.persistDirectory = persistDirectory
        self.collectionName = collectionName
        self.dbPath = os.path.join(self.persistDirectory, f"{self.collectionName}.db")
        
        os.makedirs(self.persistDirectory, exist_ok=True)
        self._initDb()
        
        print(f"[MEMORY] Loading local model {embeddingModel}...")
        self.model = SentenceTransformer(embeddingModel)

    def _initDb(self):
        """Create the SQLite database and schema if it does not exist."""
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        # Create memories table with strict typing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                userId TEXT NOT NULL,
                userName TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp REAL NOT NULL,
                embedding BLOB NOT NULL
            )
        ''')
        # Index on userId for instant query lookups regardless of database size
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON memories(userId)")
        conn.commit()
        
        # Count loaded DB elements
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        print(f"[MEMORY DB] Connected to SQLite. Local memories: {count}")
        conn.close()

    async def astore(self, userId: str, userName: str, text: str) -> None:
        """Store a message and its vector as a binary BLOB in SQLite."""
        timestamp = time.time()
        
        # Offload CPU-heavy local encoding to background thread
        embeddingArray = await asyncio.to_thread(self.model.encode, text, convert_to_numpy=True)
        
        # Convert float array to pure binary bytes for high-efficiency disk storage
        embeddingBlob = embeddingArray.astype(np.float32).tobytes()
        memoryId = f"{userId}_{timestamp}"

        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memories (id, userId, userName, text, timestamp, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (memoryId, str(userId), userName, text, timestamp, embeddingBlob))
        conn.commit()
        conn.close()

    async def arecall(self, userId: str, query: str, topK: int = 5, minScore: float = 0.4) -> List[str]:
        """Fetch a specific user's binary memory BLOBs, reconstruct vectors, and compute Gemini Cosine Similarity."""
        if not query:
            return []

        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        # Database optimization: Only pull this specific user into RAM
        cursor.execute("SELECT text, embedding FROM memories WHERE userId = ?", (str(userId),))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        print(f"[MEMORY] Encoding query locally: '{query}'...")
        queryEmbedding = await asyncio.to_thread(self.model.encode, query, convert_to_numpy=True)
        print("[MEMORY] Query encoded locally. Calculating similarity matrix...")
        
        # Reconstruct numpy arrays from binary SQLite BLOBs
        userTexts = [row[0] for row in rows]
        memEmbeddings = np.array([np.frombuffer(row[1], dtype=np.float32) for row in rows])
        
        normQuery = np.linalg.norm(queryEmbedding)
        normMem = np.linalg.norm(memEmbeddings, axis=1)
        
        dotProducts = np.dot(memEmbeddings, queryEmbedding)
        cosineSimilarities = dotProducts / (normMem * normQuery)
        
        scoredMemories = []
        for i, text in enumerate(userTexts):
            score = cosineSimilarities[i]
            if score >= minScore:
                scoredMemories.append((score, text))
        
        scoredMemories.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in scoredMemories[:topK]]

    def forgetUser(self, userId: str) -> None:
        """Surgically delete all SQLite entries for a specific user."""
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE userId = ?", (str(userId),))
        deletedCount = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"[MEMORY DB] Deleted {deletedCount} legacy records for User {userId}.")
