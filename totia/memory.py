import json
import os
import time
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

class MemoryStore:
    def __init__(self, persistDirectory: str = "data/memory", collectionName: str = "discord_memories", embeddingModel: str = "all-MiniLM-L6-v2"):
        """Initialize Memory Store using JSON and Numpy."""
        self.persistDirectory = persistDirectory
        self.collectionName = collectionName
        self.filePath = os.path.join(self.persistDirectory, f"{self.collectionName}.json")
        
        os.makedirs(self.persistDirectory, exist_ok=True)
        
        print(f"[MEMORY] Loading {embeddingModel}...")
        self.model = SentenceTransformer(embeddingModel)
        
        self.memories = []
        self._load()

    def _load(self):
        """Load memories from JSON file."""
        if os.path.exists(self.filePath):
            with open(self.filePath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.memories = data.get('memories', [])
                    print(f"[MEMORY] Loaded {len(self.memories)} memories.")
                except json.JSONDecodeError:
                    self.memories = []

    def _save(self):
        """Save memories to JSON file."""
        with open(self.filePath, 'w', encoding='utf-8') as f:
            json.dump({'memories': self.memories}, f, ensure_ascii=False, indent=2)

    def store(self, userId: str, userName: str, text: str) -> None:
        """Store a message in the vector database."""
        timestamp = time.time()
        embedding = self.model.encode(text).tolist()
        
        memoryItem = {
            "id": f"{userId}_{timestamp}",
            "userId": str(userId),
            "userName": userName,
            "text": text,
            "timestamp": timestamp,
            "embedding": embedding
        }
        
        self.memories.append(memoryItem)
        self._save()

    def recall(self, userId: str, query: str, topK: int = 5, minScore: float = 0.4) -> List[str]:
        """Retrieve relevant past messages for a user using cosine similarity."""
        if not query or not self.memories:
            return []

        userMemories = [m for m in self.memories if m["userId"] == str(userId)]
        if not userMemories:
            return []

        queryEmbedding = self.model.encode(query)
        memEmbeddings = np.array([m['embedding'] for m in userMemories])
        
        normQuery = np.linalg.norm(queryEmbedding)
        normMem = np.linalg.norm(memEmbeddings, axis=1)
        
        dotProducts = np.dot(memEmbeddings, queryEmbedding)
        cosineSimilarities = dotProducts / (normMem * normQuery)
        
        scoredMemories = []
        for i, memory in enumerate(userMemories):
            score = cosineSimilarities[i]
            if score >= minScore:
                scoredMemories.append((score, memory['text']))
        
        scoredMemories.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in scoredMemories[:topK]]

    def forgetUser(self, userId: str) -> None:
        """Delete all memories for a user."""
        initialCount = len(self.memories)
        self.memories = [m for m in self.memories if m["userId"] != str(userId)]
        if len(self.memories) < initialCount:
            self._save()
            print(f"[MEMORY] Forgot memories for user {userId}")
