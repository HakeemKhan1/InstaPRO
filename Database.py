"""
RAG Database for Instagram Content Analysis
Uses ChromaDB for vector storage and similarity search
"""

import chromadb
from chromadb.config import Settings
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
import uuid
import os

class RAGDatabase:
    def __init__(self, db_path: str = "./chroma_db"):
        """Initialize ChromaDB and sentence transformer model"""
        self.db_path = db_path
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="instagram_posts",
            metadata={"description": "Instagram posts with embeddings"}
        )
        
        # Initialize sentence transformer for embeddings
        print("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ RAG Database initialized")
    
    def add_post(self, post_data: Dict) -> str:
        """Add a post to the vector database"""
        post_id = str(uuid.uuid4())
        
        # Create embedding from caption and hashtags
        text_for_embedding = f"{post_data['caption']} {' '.join(post_data.get('hashtags', []))}"
        embedding = self.model.encode(text_for_embedding).tolist()
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=[embedding],
            documents=[post_data['caption']],
            metadatas=[{
                'type': post_data['type'],
                'engagement': post_data['engagement'],
                'hashtags': json.dumps(post_data.get('hashtags', [])),
                'date_posted': post_data['date_posted']
            }],
            ids=[post_id]
        )
        
        return post_id
    
    def search_similar_content(self, query: str, limit: int = 5) -> List[Tuple[Dict, float]]:
        """Search for similar content using vector similarity"""
        query_embedding = self.model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        similar_posts = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                post_data = {
                    'caption': results['documents'][0][i],
                    'type': results['metadatas'][0][i]['type'],
                    'engagement': results['metadatas'][0][i]['engagement'],
                    'hashtags': json.loads(results['metadatas'][0][i]['hashtags']),
                    'date_posted': results['metadatas'][0][i]['date_posted']
                }
                similarity_score = 1 - results['distances'][0][i]  # Convert distance to similarity
                similar_posts.append((post_data, similarity_score))
        
        return similar_posts
    
    def get_all_posts(self) -> List[Dict]:
        """Get all posts from the database"""
        results = self.collection.get()
        
        posts = []
        if results['documents']:
            for i in range(len(results['documents'])):
                post_data = {
                    'id': results['ids'][i],
                    'caption': results['documents'][i],
                    'type': results['metadatas'][i]['type'],
                    'engagement': results['metadatas'][i]['engagement'],
                    'hashtags': json.loads(results['metadatas'][i]['hashtags']),
                    'date_posted': results['metadatas'][i]['date_posted']
                }
                posts.append(post_data)
        
        return posts
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent posts sorted by date"""
        posts = self.get_all_posts()
        
        # Sort by date (most recent first)
        posts.sort(key=lambda x: x['date_posted'], reverse=True)
        
        return posts[:limit]
    
    def get_posts_by_type(self, post_type: str) -> List[Dict]:
        """Get all posts of a specific type"""
        results = self.collection.get(
            where={"type": post_type}
        )
        
        posts = []
        if results['documents']:
            for i in range(len(results['documents'])):
                post_data = {
                    'caption': results['documents'][i],
                    'type': results['metadatas'][i]['type'],
                    'engagement': results['metadatas'][i]['engagement'],
                    'hashtags': json.loads(results['metadatas'][i]['hashtags']),
                    'date_posted': results['metadatas'][i]['date_posted']
                }
                posts.append(post_data)
        
        return posts
    
    def get_high_engagement_posts(self, min_engagement: int = 1000) -> List[Dict]:
        """Get posts with high engagement"""
        results = self.collection.get(
            where={"engagement": {"$gte": min_engagement}}
        )
        
        posts = []
        if results['documents']:
            for i in range(len(results['documents'])):
                post_data = {
                    'caption': results['documents'][i],
                    'type': results['metadatas'][i]['type'],
                    'engagement': results['metadatas'][i]['engagement'],
                    'hashtags': json.loads(results['metadatas'][i]['hashtags']),
                    'date_posted': results['metadatas'][i]['date_posted']
                }
                posts.append(post_data)
        
        # Sort by engagement (highest first)
        posts.sort(key=lambda x: x['engagement'], reverse=True)
        
        return posts
    
    def get_post_count(self) -> int:
        """Get total number of posts in database"""
        return self.collection.count()
    
    def get_content_analysis(self) -> Dict:
        """Get analysis of content patterns"""
        posts = self.get_all_posts()
        
        if not posts:
            return {}
        
        # Analyze post types
        type_counts = {}
        type_engagement = {}
        
        # Analyze hashtags
        hashtag_counts = {}
        hashtag_engagement = {}
        
        total_engagement = 0
        
        for post in posts:
            # Post type analysis
            post_type = post['type']
            type_counts[post_type] = type_counts.get(post_type, 0) + 1
            if post_type not in type_engagement:
                type_engagement[post_type] = []
            type_engagement[post_type].append(post['engagement'])
            
            # Hashtag analysis
            for hashtag in post['hashtags']:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
                if hashtag not in hashtag_engagement:
                    hashtag_engagement[hashtag] = []
                hashtag_engagement[hashtag].append(post['engagement'])
            
            total_engagement += post['engagement']
        
        # Calculate averages
        avg_engagement_by_type = {}
        for post_type, engagements in type_engagement.items():
            avg_engagement_by_type[post_type] = sum(engagements) / len(engagements)
        
        avg_engagement_by_hashtag = {}
        for hashtag, engagements in hashtag_engagement.items():
            if len(engagements) >= 2:  # Only include hashtags used multiple times
                avg_engagement_by_hashtag[hashtag] = sum(engagements) / len(engagements)
        
        return {
            'total_posts': len(posts),
            'avg_engagement': total_engagement / len(posts) if posts else 0,
            'type_distribution': type_counts,
            'avg_engagement_by_type': avg_engagement_by_type,
            'top_hashtags': dict(sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'best_performing_hashtags': dict(sorted(avg_engagement_by_hashtag.items(), key=lambda x: x[1], reverse=True)[:10])
        }
