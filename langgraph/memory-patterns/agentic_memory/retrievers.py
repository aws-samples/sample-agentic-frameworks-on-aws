from sklearn.cluster import KMeans
import numpy as np
import boto3
import json
import os
from typing import List, Dict, Any, Optional
import networkx as nx
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from agentic_memory.base import BaseRetriever, BaseLongTermStore
from agentic_memory.automotive import AutomotiveKnowledgeToolkit
from collections import defaultdict
import botocore
import time



class LocalHuggingFaceEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input).tolist()

class SemanticStoreRetrieval(BaseRetriever):
    def __init__(
        self,
        long_term_store: BaseLongTermStore,
        n_clusters: int = 5,
        vector_store_path: str = "semantic_vector_store",
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    ):
        self.long_term_store = long_term_store
        self.vector_store_path = vector_store_path
        self.n_clusters = n_clusters
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.embeddings = LocalHuggingFaceEmbeddingFunction(embedding_model)
        self.chroma_client = chromadb.PersistentClient(path=self.vector_store_path)

        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="semantic_store",
                embedding_function=self.embeddings
            )
            print(f"Chroma collection loaded or created at {self.vector_store_path}")
        except Exception as e:
            print(f"Failed to load or create Chroma collection: {e}")
            self.collection = None

    def load_all_entries(self) -> List[Dict[str, Any]]:
        entries = []
        auto_tool_kit = AutomotiveKnowledgeToolkit()
        if hasattr(self.long_term_store, 'storage_file') and os.path.exists(self.long_term_store.storage_file):
            with open(self.long_term_store.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for vin, record in data.items():
                make, model, year = auto_tool_kit.get_vehicle_info(vin)
                entry = record.copy()
                entry['vin'] = vin
                entry['make'] = make
                entry['model'] = model
                entries.append(entry)
        return entries

    def cluster_entries(self, entries: List[Dict[str, Any]], n_clusters: int = 5) -> List[List[Dict[str, Any]]]:
         # Group entries by (make, model)
        grouped = defaultdict(list)
        for entry in entries:
            make = entry.get("make", "")
            model = entry.get("model", "")
            grouped[(make, model)].append(entry)
        
        all_clusters = []
        for (make, model), group_entries in grouped.items():
            if not group_entries:
                continue
            texts = [
                " ".join([issue.get('issue_summary', '') for issue in entry.get('service_history', [])])
                for entry in group_entries
            ]
            vectors = self.embeddings(texts)
            n = min(n_clusters, len(group_entries))
            if n < 1:
                continue
            kmeans = KMeans(n_clusters=n, random_state=42)
            labels = kmeans.fit_predict(vectors)
            clusters = [[] for _ in range(max(labels) + 1)]
            for idx, label in enumerate(labels):
                clusters[label].append(group_entries[idx])
            all_clusters.extend(clusters)
        return all_clusters

    def call_bedrock_nova(self, prompt: str, max_retries: int = 3) -> str:
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        retries = 0
        while retries < max_retries:
            try:
                response = self.bedrock_client.invoke_model(
                    modelId="us.amazon.nova-pro-v1:0",
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(request_body)
                )
                result = json.loads(response['body'].read())
                # Adjust this line if Nova's output format changes
                return result.get('output', [{}]).get('message',{}).get('content',[])[0].get('text')
            except botocore.exceptions.ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == "ThrottlingException":
                    print(f"ThrottlingException encountered {retries}. Waiting 60 seconds before retrying...")
                    time.sleep(60)
                    retries += 1
                else:
                    raise
            except Exception as e:
                raise
        raise RuntimeError("Max retries exceeded for Bedrock Nova call due to throttling.")

    def summarize_cluster(self, cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
        combined_text = ""
        for entry in cluster:
            vin = entry.get('vin', '')
            issues = [issue.get('issue_summary', '') for issue in entry.get('service_history', [])]
            issues_str = "; ".join(issues)
            combined_text += f"VIN: {vin} - Issues: {issues_str}\n"
        prompt = (
            "Summarize the following vehicle issues and resolutions into a consolidated summary, "
            "highlighting common patterns and resolutions:\n" +
            combined_text +
            "\nSummary:"
        )
        summary = self.call_bedrock_nova(prompt)
        first = cluster[0]
        meta = {
            "make": first.get("make", ""),
            "model": first.get("model", ""),
            "year": first.get("year", ""),
            "summary": summary
        }
        return meta

    def build(self):
        """Cluster, summarize, and store summaries in Chroma vector store."""
        entries = self.load_all_entries()
        if not entries:
            print("No entries found in long term store.")
            return
        clusters = self.cluster_entries(entries, self.n_clusters)
        summaries = [self.summarize_cluster(cluster) for cluster in clusters]
        documents = [summary["summary"] for summary in summaries]
        metadatas = [{"make": s["make"], "model": s["model"], "year": s["year"]} for s in summaries]
        ids = [f"summary_{i}" for i in range(len(documents))]
        # Remove existing collection and recreate to avoid duplicates
        try:
            self.chroma_client.delete_collection("semantic_store")
        except Exception:
            pass  # Collection may not exist yet
        self.collection = self.chroma_client.create_collection(
            "semantic_store",
            embedding_function=self.embeddings
        )
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        #self.chroma_client.persist()

    def search(self, make: Optional[str], model: Optional[str], issue: Optional[str]) -> List[Dict[str, Any]]:
        """Search summaries filtered by metadata and issue similarity using Chroma native API."""
        if self.collection is None:
            raise ValueError("Vector store not initialized. Call build() first.")
        filters = []
        if make:
            filters.append({"make": make})
        if model:
            filters.append({"model": model})
        where = {"$and": filters} if filters else None
        results = self.collection.query(
            query_texts=[issue or ""],
            n_results=5,
            where=where 
        )
        output = []
        for i in range(len(results["documents"][0])):
            doc = results["documents"][0][i]
            meta = results["metadatas"][0][i]
            output.append({
                "summary": doc,
                **meta
            })
        return output


class GraphRetrieval(BaseRetriever):
    def __init__(self, long_term_store, graph_json_path="semantic_graph_store/vehicle_graph.json"):
        self.long_term_store = long_term_store
        self.graph_json_path = graph_json_path
        self.G = nx.MultiDiGraph()
        if os.path.exists(self.graph_json_path):
            self.load_graph()
        else:
            self.build()
            self.save_graph()

    def build(self):
        """Extracts nodes and edges from long-term store and builds the graph."""
        self.G.clear()

        if hasattr(self.long_term_store, 'storage_file') and os.path.exists(self.long_term_store.storage_file):
            with open(self.long_term_store.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for vin, record in data.items():

                vehicle_node = f"VIN:{vin}"
                self.G.add_node(vehicle_node, type="Vehicle", vin=vin, make=record.get("make"), model=record.get("model"), year=record.get("year"))

                for idx, service in enumerate(record.get("service_history", [])):
                    issue_node = f"Issue:{vin}:{idx}"
                    self.G.add_node(issue_node, type="Issue", summary=service.get("issue_summary"), date=service.get("service_date"))
                    self.G.add_edge(vehicle_node, issue_node, relation="has_issue")

                    resolution_node = f"Resolution:{vin}:{idx}"
                    self.G.add_node(resolution_node, type="Resolution", resolution=service.get("resolution"), engineer=service.get("service_engineer"))
                    self.G.add_edge(issue_node, resolution_node, relation="resolved_by")

                    if service.get("service_engineer"):
                        engineer_node = f"Engineer:{service.get('service_engineer')}"
                        self.G.add_node(engineer_node, type="Engineer", name=service.get("service_engineer"))
                        self.G.add_edge(resolution_node, engineer_node, relation="performed_by")

    def save_graph(self):
        """Persist the graph as a JSON file."""
        directory = os.path.dirname(self.graph_json_path)
        os.makedirs(directory, exist_ok=True)
        with open(self.graph_json_path, 'w', encoding='utf-8') as f:
            json.dump(nx.node_link_data(self.G), f, indent=2)

    def load_graph(self):
        """Load the graph from a JSON file."""
        with open(self.graph_json_path, 'r', encoding='utf-8') as f:
            self.G = nx.node_link_graph(json.load(f))

    def search(self, make: Optional[str]=None, model: Optional[str]=None, issue: Optional[str]=None) -> List[Dict[str, Any]]:
        """Search for vehicles/issues/resolutions by metadata and keyword."""
        results = []
        for node, data in self.G.nodes(data=True):
            if data.get("type") == "Vehicle":
                if (make and data.get("make") != make) or (model and data.get("model") != model):
                    continue

                for _, issue_node, edge_data in self.G.out_edges(node, data=True):
                    if edge_data.get("relation") == "has_issue":
                        issue_data = self.G.nodes[issue_node]

                        if issue and issue.lower() not in (issue_data.get("summary") or "").lower():
                            continue

                        for _, res_node, res_edge in self.G.out_edges(issue_node, data=True):
                            if res_edge.get("relation") == "resolved_by":
                                res_data = self.G.nodes[res_node]
                                results.append({
                                    "vin": data.get("vin"),
                                    "make": data.get("make"),
                                    "model": data.get("model"),
                                    "year": data.get("year"),
                                    "issue_summary": issue_data.get("summary"),
                                    "issue_date": issue_data.get("date"),
                                    "resolution": res_data.get("resolution"),
                                    "engineer": res_data.get("engineer")
                                })
        return results
