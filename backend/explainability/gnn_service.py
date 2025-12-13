import os
import sys

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.nn import RGCNConv
    from torch_geometric.data import HeteroData
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: Torch not available. GNN features will be disabled.")
    TORCH_AVAILABLE = False
    # Dummy classes to prevent NameError
    class nn:
        class Module: pass
    class torch:
        class device:
            def __init__(self, x): pass
        def tensor(x, **kwargs): return x
        def no_grad(): 
            class Context:
                def __enter__(self): pass
                def __exit__(self, *args): pass
            return Context()

# --- MODEL DEFINITION (Copied from final_codered_rgcn.py to ensure compatibility) ---
if TORCH_AVAILABLE:
    class RGCNLinkPredictor(nn.Module):
        def __init__(self, in_dim, hid, num_rel, num_bases=8, dropout=0.2, temperature=1.0):
            super().__init__()
            self.conv1 = RGCNConv(in_dim, hid, num_rel, num_bases=num_bases)
            self.conv2 = RGCNConv(hid, hid, num_rel, num_bases=num_bases)
            self.norm1 = nn.LayerNorm(hid)
            self.norm2 = nn.LayerNorm(hid)
            self.relation_emb = nn.Parameter(torch.randn(num_rel, hid) * 0.1)
            self.dropout = dropout
            self.temperature = temperature

        def encode(self, x, ei, et):
            h = self.conv1(x, ei, et)
            h = self.norm1(h)
            h = F.leaky_relu(h, 0.2)
            h = F.dropout(h, p=self.dropout, training=self.training)
            h = self.conv2(h, ei, et)
            h = self.norm2(h)
            h = F.leaky_relu(h, 0.2)
            return F.normalize(h, dim=1)

        def decode(self, z, edge_index, rel_ids):
            z_src = z[edge_index[0]]
            z_dst = z[edge_index[1]]
            r = self.relation_emb[rel_ids]
            return (z_src * r * z_dst).sum(dim=1) / self.temperature

        def forward(self, x, ei, et, pred_edges, rel_ids):
            z = self.encode(x, ei, et)
            return self.decode(z, pred_edges, rel_ids)
else:
    class RGCNLinkPredictor:
        def __init__(self, *args, **kwargs): pass
        def __call__(self, *args, **kwargs): return None
        def eval(self): pass
        def to(self, device): pass
        def load_state_dict(self, state): pass

# --- SERVICE CLASS ---
class GNNService:
    def __init__(self):
        self.model = None
        self.data_homo = None
        self.node_offset = None
        self.relation_names = None
        self.relname2id = None
        self.gene_node_mask = None # Boolean mask for Gene nodes in homogeneous graph
        self.gene_id_map = {} # Maps homogenous index -> Gene Name (or ID)
        self.device = torch.device("cpu") # Use CPU for inference to avoid VRAM fighting
        
        # Paths
        # Paths
        # __file__ = backend/explainability/gnn_service.py
        # 1. explainability
        # 2. backend
        # 3. neurosymbolic (ROOT)
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.RGCN_MODEL_DIR = os.path.join(self.BASE_DIR, "R-GCN-MODEL")
        self.GRAPH_PATH = os.path.join(self.RGCN_MODEL_DIR, "graph.pt")
        self.MODEL_PATH = os.path.join(self.RGCN_MODEL_DIR, "best_rgcn_model.pt")

        self.NODES_CSV_PATH = os.path.join(self.BASE_DIR, "temp", "nodes.csv")
        self.COMPOUND_MAPPING_PATH = os.path.join(self.BASE_DIR, "backend", "compound_id_to_name.json")
        self.DISEASE_MAPPING_PATH = os.path.join(self.BASE_DIR, "backend", "disease_id_to_name.json")

        
        self.name_to_compound_id = {}
        self.name_to_disease_id = {}


    def load_gene_mapping(self):
        import pandas as pd
        if not os.path.exists(self.NODES_CSV_PATH):
            print(f"Warning: {self.NODES_CSV_PATH} not found. Returning empty gene map.")
            return

        try:
            df = pd.read_csv(self.NODES_CSV_PATH)
            # Filter for Gene nodes
            # Assuming label column exists and 'Gene' is the label
            # And 'new_id' matches the HeteroData index
            if 'label' in df.columns and 'new_id' in df.columns and 'name' in df.columns:
                # Filter for Gene
                genes = df[df['label'] == 'Gene'].reset_index(drop=True)
                print(f"Gene Mapping DataFrame Head:\n{genes[['name', 'new_id']].head()}")
                
                # Robust Mapping: 
                # We assume the order of Gene rows in CSV matches the PyG 'Gene' node order (0..N).
                # We create a map: int(local_index) -> str(name)
                # This ignores 'new_id' column which might be global or offset-based.
                self.gene_id_map = genes['name'].to_dict()
                
                print(f"Loaded {len(self.gene_id_map)} gene names (using positional indexing).")
            else:
                print("Warning: nodes.csv missing required columns (label, new_id, name).")
        except Exception as e:
            print(f"Error loading node mapping: {e}")


    def hetero_to_homo(self, hetero_data, default_dim=128):
        # Exact replica of the function in final_codered_rgcn.py
        node_offset = {}
        offset = 0
        feat_dim = None
        node_features = []

        gene_indices = []
        gene_names = []

        for ntype in hetero_data.node_types:
            node_offset[ntype] = offset
            n = hetero_data[ntype].num_nodes
            
            # Capture Gene indices for later mapping
            if ntype == 'Gene':
                gene_indices.extend(range(offset, offset + n))
                # Assuming 'name' or 'id' attribute exists, or we index by range.
                # HeteroData nodes usually don't store names unless added as attribute.
                # We will rely on mapping files if needed, but for now we just track indices.
            
            if hasattr(hetero_data[ntype], "x") and hetero_data[ntype].x is not None:
                ft = hetero_data[ntype].x
                if feat_dim is None:
                    feat_dim = ft.size(1)
                else:
                    # In case dimensions mismatch (shouldn't if trained correctly), pad/cut?
                    # The script asserted assert ft.size(1) == feat_dim. We assume graph.pt is valid.
                    pass 
            else:
                if feat_dim is None:
                    feat_dim = default_dim
                ft = torch.zeros((n, feat_dim))
            
            offset += n
            node_features.append(ft)

        x = torch.cat(node_features, dim=0)
        x = F.normalize(x, p=2, dim=1)

        edge_index_list = []
        edge_type_list = []
        relation_names = []
        relname2id = {}

        for rel_id, edge_type in enumerate(hetero_data.edge_types):
            src, relname, dst = edge_type
            eidx = hetero_data[edge_type].edge_index.clone()
            eidx[0] += node_offset[src]
            eidx[1] += node_offset[dst]
            edge_index_list.append(eidx)
            edge_type_list.append(torch.full((eidx.size(1),), rel_id, dtype=torch.long))
            relation_names.append(edge_type)
            relname2id[edge_type] = rel_id

        edge_index = torch.cat(edge_index_list, dim=1)
        edge_type = torch.cat(edge_type_list, dim=0)

        # Add self-loop relation
        N = x.size(0)
        loop_edges = torch.arange(N).unsqueeze(0).repeat(2, 1)
        self_rel_id = len(relation_names)

        edge_index = torch.cat([edge_index, loop_edges], dim=1)
        edge_type = torch.cat([edge_type, torch.full((N,), self_rel_id)], dim=0)

        relation_names.append(('SELF', 'SELF', 'SELF'))
        relname2id[('SELF', 'SELF', 'SELF')] = self_rel_id

        return x, edge_index, edge_type, node_offset, relation_names, relname2id, gene_indices

    def load_resources(self):
        if self.model is not None:
            return

        if not TORCH_AVAILABLE:
            print("GNN Service: Torch not available. Skipping resource load.")
            self.load_entity_mappings() # Still load mappings if possible
            return

        print("Loading GNN Service resources...")
        if not os.path.exists(self.GRAPH_PATH):
            raise FileNotFoundError(f"Graph not found at {self.GRAPH_PATH}")
        
        # weights_only=False required for complex PyG data objects
        data = torch.load(self.GRAPH_PATH, map_location=self.device, weights_only=False)
        
        # Determine dimension from data.Drug.x if available, else 128

        # The script used 128 default.
        # Check actual dimension
        in_dim = 128
        if 'Compound' in data.node_types and data['Compound'].x is not None:
             in_dim = data['Compound'].x.size(1)
        
        # Convert to Homo
        x, edge_index, edge_type, node_offset, relation_names, relname2id, gene_indices = self.hetero_to_homo(data, default_dim=128) # 128 was hardcoded default in script
        
        # Ensure x is float, create requires_grad=True replica for Saliency
        # But for 'load', we just store tensors.
        self.data_homo = {
            'x': x,
            'edge_index': edge_index,
            'edge_type': edge_type
        }
        self.node_offset = node_offset
        self.relation_names = relation_names
        self.relname2id = relname2id
        self.node_offset = node_offset
        self.relation_names = relation_names
        self.relname2id = relname2id
        self.gene_indices = gene_indices
        
        print(f"Node Offsets: {self.node_offset}")
        print(f"Num Genes in Graph: {len(self.gene_indices)}")
        
        # Initialize Model
        # Script parameters: hid=128, num_bases=8
        self.model = RGCNLinkPredictor(x.size(1), 128, len(relation_names))
        
        # Load Weights
        if os.path.exists(self.MODEL_PATH):
            print(f"Loading weights from {self.MODEL_PATH}")
            # weights_only=True is usually fine for state_dict, but False checks strictly for safety warnings
            state_dict = torch.load(self.MODEL_PATH, map_location=self.device, weights_only=False)
            self.model.load_state_dict(state_dict)
        else:
            print("Warning: Model weights not found, using random init (MOCK MODE via un-trained model)")

            
        self.model.to(self.device)
        self.model.eval()
        
        # Load Mappings
        self.load_gene_mapping()
        self.load_entity_mappings()
        
        print("GNN Service Loaded.")

    def load_entity_mappings(self):
        import json
        try:
            if os.path.exists(self.COMPOUND_MAPPING_PATH):
                with open(self.COMPOUND_MAPPING_PATH, 'r') as f:
                    c_map = json.load(f) # "0": "Metformin", ...
                    self.name_to_compound_id = {v.lower().strip(): int(k) for k, v in c_map.items()}
            
            if os.path.exists(self.DISEASE_MAPPING_PATH):
                with open(self.DISEASE_MAPPING_PATH, 'r') as f:
                    d_map = json.load(f)
                    self.name_to_disease_id = {v.lower().strip(): int(k) for k, v in d_map.items()}
            
            print(f"Loaded {len(self.name_to_compound_id)} compounds and {len(self.name_to_disease_id)} diseases for name resolution.")
        except Exception as e:

            print(f"Error loading entity mappings: {e}")


    def resolve_id(self, id_str, mapping, label):
        # 1. Try integer
        try:
            return int(id_str)
        except ValueError:
            pass
        
        # 2. Try Name lookup
        clean_name = str(id_str).lower().strip()
        if clean_name in mapping:
            return mapping[clean_name]
            
        print(f"Warning: Could not resolve {label} ID '{id_str}'")
        return None

    def get_gene_importance(self, drug_id_str, disease_id_str):
        try:
            self.load_resources()
            
            if not TORCH_AVAILABLE:
                return {}

            # 1. Map IDs
            drug_idx = self.resolve_id(drug_id_str, self.name_to_compound_id, "Drug")
            disease_idx = self.resolve_id(disease_id_str, self.name_to_disease_id, "Disease")
            
            if drug_idx is None or disease_idx is None:
                return {}

                
            # Homogeneous IDs
            h_drug = drug_idx + self.node_offset['Compound']
            h_disease = disease_idx + self.node_offset['Disease']
            
            # 2. Prepare Input for Saliency
            x = self.data_homo['x'].clone().detach().to(self.device)
            x.requires_grad = True # Enable gradient tracking on FEATURES
            
            edge_index = self.data_homo['edge_index'].to(self.device)
            edge_type = self.data_homo['edge_type'].to(self.device)
            
            # Edge to predict
            edge = torch.tensor([[h_drug], [h_disease]], dtype=torch.long, device=self.device)
            
            # Relation ID for 'treats'
            if ('Compound', 'treats', 'Disease') in self.relname2id:
                rel_id = self.relname2id[('Compound', 'treats', 'Disease')]
            else:
                # Fallback
                rel_id = 0 
            rel_ids = torch.tensor([rel_id], dtype=torch.long, device=self.device)
            
            # 3. Forward Pass
            # We use a fresh model call to avoid messing up global state
            # compute score
            score = self.model(x, edge_index, edge_type, edge, rel_ids)
            
            # 4. Backward Pass
            score.backward()
            
            # 5. Extract Gradients for Gene Nodes
            # x.grad is [NumNodes, NumFeatures]
            # We want scalar importance per node = L2 norm of gradient
            with torch.no_grad():
                node_saliency = x.grad.norm(dim=1) # [NumNodes]
                
                # Filter for Genes Only
                gene_saliency = node_saliency[self.gene_indices]
                
                # Normalize to 0-1 range for this query
                if gene_saliency.max() > 0:
                    gene_saliency = gene_saliency / gene_saliency.max()

                # Map to Names
                # gene_indices list corresponds to HeteroData Gene indices 0..N in order
                # layout in homo graph is sequential.
                # So gene_saliency[i] corresponds to Gene ID 'i' (if sorted).
                # The hetero_to_homo loop iterates data['Gene']. 
                # PyG nodes are 0-indexed.
                
                result_map = {}
                saliency_list = gene_saliency.tolist()
                
                for i, score in enumerate(saliency_list):
                    # i is local Gene index (0..NumGenes)
                    # self.gene_indices[i] gives global homo ID, but our new map is 0-indexed local.
                    # So we just look up 'i' directly in self.gene_id_map
                    
                    if i in self.gene_id_map:
                        gene_name = self.gene_id_map[i]
                        result_map[gene_name] = score
                    else:
                        # Fallback if no name found
                        # skipping unnamed genes to reduce noise or use ID
                        pass
                
                return result_map
        except Exception as e:
            print(f"ERROR in get_gene_importance: {e}")
            import traceback
            traceback.print_exc()
            return {}


# Global Instance
gnn_service = GNNService()
