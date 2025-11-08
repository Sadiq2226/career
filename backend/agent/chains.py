from __future__ import annotations

from typing import List, Optional
import math

from rank_bm25 import BM25Okapi

# Google Gemini imports for LLM integration
try:
    import google.generativeai as genai
    from langchain.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import GoogleGenerativeAIEmbeddings
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Gemini not available. Using offline mode.")

from .config import settings


class OfflineRetriever:
    """A simple BM25-based retriever over in-memory documents."""

    def __init__(self, documents: List[dict]):
        self.documents = documents
        corpus = [d["text"].split() for d in documents]
        self.bm25 = BM25Okapi(corpus)

    def query(self, question: str, top_k: int = 5) -> List[dict]:
        scores = self.bm25.get_scores(question.split())
        ranked = sorted(
            zip(self.documents, scores), key=lambda x: x[1], reverse=True
        )
        return [doc for doc, _ in ranked[:top_k]]


class GeminiRetriever:
    """Gemini-powered retriever using embeddings and vector search."""
    
    def __init__(self, documents: List[dict]):
        self.documents = documents
        self.vectorstore = None
        self.embeddings = None
        
        if GEMINI_AVAILABLE and settings.online_mode:
            self._setup_gemini_retriever()
    
    def _setup_gemini_retriever(self):
        """Setup Gemini-based retrieval system."""
        try:
            # Configure Gemini
            genai.configure(api_key=settings.google_api_key)
            
            # Initialize embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.google_api_key
            )
            
            # Prepare documents for vector store
            texts = [doc["text"] for doc in self.documents]
            metadatas = [doc["meta"] for doc in self.documents]
            
            # Create vector store
            self.vectorstore = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            print("Gemini retriever initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Gemini retriever: {e}")
            self.vectorstore = None
    
    def query(self, question: str, top_k: int = 5) -> List[dict]:
        """Query using Gemini embeddings if available, fallback to BM25."""
        if self.vectorstore and GEMINI_AVAILABLE:
            try:
                # Use vector similarity search
                docs = self.vectorstore.similarity_search(question, k=top_k)
                return [{"text": doc.page_content, "meta": doc.metadata} for doc in docs]
            except Exception as e:
                print(f"Gemini query failed, falling back to BM25: {e}")
        
        # Fallback to BM25
        offline_retriever = OfflineRetriever(self.documents)
        return offline_retriever.query(question, top_k)


def gemini_summarize(text: str, question: str = "") -> str:
    """Use Gemini 2.5 Flash for intelligent summarization."""
    if not GEMINI_AVAILABLE or not settings.online_mode:
        return offline_summarize(text)
    
    try:
        # Configure Gemini
        genai.configure(api_key=settings.google_api_key)
        
        # Initialize Gemini 2.5 Flash model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create prompt
        prompt = f"""
You are a career outcomes analyst specializing in Indian educational institutions. 
Based on the following context about career outcomes, provide a comprehensive and insightful summary that answers the user's question.

Context: {text}

Question: {question}

Please provide:
1. Key insights and trends
2. Specific data points and statistics  
3. Actionable recommendations
4. Institution-specific information if relevant

Keep the response clear, professional, and focused on career outcomes for Indian students.
Format your response in a structured way with clear sections.
"""
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini summarization failed: {e}")
        return offline_summarize(text)


def offline_summarize(text: str, max_sentences: int = 5) -> str:
    """Very lightweight extractive summarizer: picks the first N non-empty sentences."""
    if not text:
        return "No content available."
    # naive sentence split
    parts = [p.strip() for p in text.replace("\n", " ").split(".")]
    parts = [p for p in parts if p]
    return ". ".join(parts[:max_sentences]) + ("." if parts else "")


def gemini_synthesize_insights(bullets: List[str], context: str = "") -> str:
    """Use Gemini 2.5 Flash to synthesize insights into a comprehensive report."""
    if not GEMINI_AVAILABLE or not settings.online_mode:
        return synthesize_parent_friendly_insights(bullets)
    
    try:
        # Configure Gemini
        genai.configure(api_key=settings.google_api_key)
        
        # Initialize Gemini 2.5 Flash model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create prompt
        prompt = f"""
You are a career counselor providing insights to parents and students about Indian educational institutions.

Based on the following data points and context, create a comprehensive, parent-friendly report:

Data Points:
{chr(10).join(f"- {b}" for b in bullets)}

Additional Context:
{context}

Please create a well-structured report that includes:
1. Executive Summary
2. Key Findings
3. Recommendations for Parents
4. Future Outlook
5. Action Items

Make it professional, informative, and easy to understand for parents making educational decisions.
Use clear headings and bullet points for better readability.
"""
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini insight synthesis failed: {e}")
        return synthesize_parent_friendly_insights(bullets)


def synthesize_parent_friendly_insights(bullets: List[str]) -> str:
    if not bullets:
        return "No insights available yet."
    header = "Parent-Focused Insights:\n"
    body = "\n".join(f"- {b}" for b in bullets)
    return header + body


def score_support_index(services: List[str]) -> float:
    """Compute a simple support index: sqrt(weighted coverage)."""
    if not services:
        return 0.0
    unique = set(s.strip().lower() for s in services if s and s.strip())
    # Weight some common high-impact services
    weights = {
        "career counseling": 1.5,
        "internships": 1.3,
        "mentorship": 1.3,
        "alumni network": 1.2,
        "job fairs": 1.1,
        "resume workshops": 1.0,
        "mock interviews": 1.0,
    }
    score = 0.0
    for s in unique:
        score += weights.get(s, 0.8)
    # Normalize to 0-100
    max_possible = 12.0
    normalized = min(100.0, (score / max_possible) * 100.0)
    return round(math.sqrt(normalized) * 10.0 / math.sqrt(100.0), 2) * 10
