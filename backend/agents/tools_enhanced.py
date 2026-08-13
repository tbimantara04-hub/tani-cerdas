"""
tools_enhanced.py — Enhanced Tool Definitions
==============================================
Tools with planning, reasoning, and multi-step capabilities.
"""

import os
import json
import requests
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
import glob


class EnhancedTool:
    """Base class for enhanced tools with planning and reasoning."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.execution_history = []
        self.success_rate = 1.0
        
    def plan_execution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plan for executing this tool."""
        return {
            "tool": self.name,
            "params": params,
            "strategy": "direct",
            "estimated_steps": 1
        }
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        raise NotImplementedError
    
    def record_execution(self, success: bool, result: Any, error: str = None):
        """Record execution for learning."""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "result": result,
            "error": error
        })
        # Update success rate
        if len(self.execution_history) > 0:
            successes = sum(1 for e in self.execution_history if e["success"])
            self.success_rate = successes / len(self.execution_history)


class WeatherTool(EnhancedTool):
    """Real-time weather data tool."""
    
    def __init__(self):
        super().__init__(
            name="cek_cuaca",
            description="Get real-time weather data for a location"
        )
        self.api_key = os.environ.get("OPENWEATHER_API_KEY", "")
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
        
    def plan_execution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Plan weather check with caching strategy."""
        lokasi = params.get("lokasi", "Jakarta")
        
        # Check if we have cached data
        if lokasi in self.cache:
            cache_time = self.cache[lokasi]["timestamp"]
            if datetime.now().timestamp() - cache_time < self.cache_duration:
                return {
                    "tool": self.name,
                    "strategy": "cache",
                    "use_cache": True,
                    "location": lokasi
                }
        
        return {
            "tool": self.name,
            "strategy": "api_call",
            "location": lokasi,
            "estimated_steps": 1
        }
    
    def execute(self, lokasi: str = "Jakarta", **kwargs) -> Dict[str, Any]:
        """Execute weather check."""
        try:
            # Check cache first
            if lokasi in self.cache:
                cache_time = self.cache[lokasi]["timestamp"]
                if datetime.now().timestamp() - cache_time < self.cache_duration:
                    result = self.cache[lokasi]["data"]
                    self.record_execution(True, result)
                    return result
            
            # Call API
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": lokasi,
                "appid": self.api_key,
                "units": "metric",
                "lang": "id"
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "location": lokasi,
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "condition": data["weather"][0]["description"],
                    "wind_speed": data.get("wind", {}).get("speed", 0),
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
                
                # Cache result
                self.cache[lokasi] = {
                    "data": result,
                    "timestamp": datetime.now().timestamp()
                }
                
                self.record_execution(True, result)
                return result
            else:
                error = f"API error: {response.status_code}"
                self.record_execution(False, None, error)
                return {"success": False, "error": error}
                
        except Exception as e:
            self.record_execution(False, None, str(e))
            return {"success": False, "error": str(e)}


class PriceTool(EnhancedTool):
    """Commodity and fertilizer price tool."""
    
    def __init__(self):
        super().__init__(
            name="cek_harga",
            description="Check commodity and fertilizer prices"
        )
        self.price_data = {
            "pangan": {
                "beras": "13500", "cabai rawit": "48000", 
                "bawang merah": "32000", "jagung": "5500",
                "beras merah": "15000", "kacang kedelai": "8000"
            },
            "pupuk": {
                "urea": "2250", "npk": "2300", "sp36": "2100",
                "kcl": "2500", "organic": "5000"
            }
        }
        self.price_history = {}
        
    def plan_execution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Plan price check with history analysis."""
        jenis = params.get("jenis", "pangan")
        komoditas = params.get("komoditas", "")
        
        return {
            "tool": self.name,
            "jenis": jenis,
            "komoditas": komoditas,
            "strategy": "data_lookup",
            "include_trend": True,
            "estimated_steps": 1
        }
    
    def execute(self, jenis: str = "pangan", komoditas: str = "", **kwargs) -> Dict[str, Any]:
        """Execute price check."""
        try:
            jenis = jenis.lower()
            komoditas = komoditas.lower()
            
            if jenis not in self.price_data:
                return {"success": False, "error": f"Jenis tidak dikenal: {jenis}"}
            
            data = self.price_data[jenis]
            
            # Find matching commodity
            found_items = {}
            for item, price in data.items():
                if komoditas in item:
                    found_items[item] = price
            
            if not found_items:
                found_items = data  # Return all if no match
            
            result = {
                "jenis": jenis,
                "items": found_items,
                "currency": "Rp/kg",
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            self.record_execution(True, result)
            return result
            
        except Exception as e:
            self.record_execution(False, None, str(e))
            return {"success": False, "error": str(e)}


class RAGTool(EnhancedTool):
    """RAG-based knowledge retrieval tool."""
    
    def __init__(self):
        super().__init__(
            name="tanya_panduan",
            description="Query agricultural guidance from documents"
        )
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.retriever = None
        self._initialize_retriever()
        
    def _initialize_retriever(self):
        """Initialize or load FAISS retriever."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "..", "vectorstore", "db_faiss_local")
        
        if os.path.exists(db_path):
            try:
                db = FAISS.load_local(db_path, self.embeddings, allow_dangerous_deserialization=True)
                self.retriever = db.as_retriever(search_kwargs={"k": 5})
            except:
                self._build_retriever(base_dir)
        else:
            self._build_retriever(base_dir)
    
    def _build_retriever(self, base_dir):
        """Build retriever from documents."""
        docs_all = []
        data_dir = os.path.join(base_dir, "..", "data")
        
        # Load PDFs
        for pdf_file in glob.glob(os.path.join(data_dir, "*.pdf")):
            try:
                docs_all.extend(PyPDFLoader(pdf_file).load())
            except:
                pass
        
        # Load DOCX
        for docx_file in glob.glob(os.path.join(data_dir, "*.docx")):
            try:
                docs_all.extend(Docx2txtLoader(docx_file).load())
            except:
                pass
        
        # Fallback to root
        if not docs_all:
            for pdf_file in glob.glob(os.path.join(base_dir, "..", "*.pdf")):
                try:
                    docs_all.extend(PyPDFLoader(pdf_file).load())
                except:
                    pass
        
        if docs_all:
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            texts = splitter.split_documents(docs_all)
            db = FAISS.from_documents(texts, self.embeddings)
            db.save_local(os.path.join(base_dir, "..", "vectorstore", "db_faiss_local"))
            self.retriever = db.as_retriever(search_kwargs={"k": 5})
    
    def plan_execution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Plan knowledge query with multi-step retrieval."""
        query = params.get("query", "")
        
        return {
            "tool": self.name,
            "query": query,
            "strategy": "multi_hop_retrieval",
            "steps": [
                {"step": 1, "action": "retrieve_documents", "description": "Find relevant documents"},
                {"step": 2, "action": "synthesize_answer", "description": "Synthesize guidance from documents"}
            ]
        }
    
    def execute(self, query: str = "", **kwargs) -> Dict[str, Any]:
        """Execute RAG query."""
        try:
            if not self.retriever:
                return {"success": False, "error": "RAG tidak tersedia"}
            
            docs = self.retriever.invoke(query)
            context = "\n".join([f"- {doc.page_content[:200]}" for doc in docs])
            
            result = {
                "query": query,
                "context": context,
                "document_count": len(docs),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            self.record_execution(True, result)
            return result
            
        except Exception as e:
            self.record_execution(False, None, str(e))
            return {"success": False, "error": str(e)}


# Tool registry
TOOL_REGISTRY = {
    "cek_cuaca": WeatherTool(),
    "cek_harga": PriceTool(),
    "tanya_panduan": RAGTool(),
}


def get_tool(tool_name: str) -> Optional[EnhancedTool]:
    """Get a tool from the registry."""
    return TOOL_REGISTRY.get(tool_name)


def get_all_tools() -> Dict[str, EnhancedTool]:
    """Get all available tools."""
    return TOOL_REGISTRY
