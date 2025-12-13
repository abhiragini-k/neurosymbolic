import pickle
import csv
import math
import sys
import os
print(f"[DEBUG] LOADING polo_sci4 from {__file__}")

# ... (omitted)



import math
import networkx as nx
import json 
import json 

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
DAMPING_EXPONENT = 0.4  # Rephetio standard

VIP_TARGETS = {
    "MTOR": "21220",
    "AMPK": "23070",
    "TP53": "9229",
    "EGFR": "17600",
    "BRCA1": "28372",
    "BRCA2": "12104",
    "HER2": "23456",
    "AKT1": "20722",
    "PIK3CA": "13701"
}

REL_MAP = {
    "binds": "binds to", "targets": "targets", "treats": "treats",
    "inhibits": "inhibits", "activates": "activates",
    "upregulates": "upregulates", "downregulates": "downregulates",
    "associates": "is associated with", "participates": "participates in",
    "expresses": "is expressed in", "interacts": "interacts with",
    "regulates": "regulates", "causes": "causes"
# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
DAMPING_EXPONENT = 0.4  # Rephetio standard

VIP_MOLECULES = {
    "MTOR":   "2475", 
    "AMPK":   "5562", 
    "TP53":   "7157",
    "EGFR":   "1956",
    "BRCA1":  "672",
    "HER2":   "2064",
}

REL_MAP = {
    "binds": "binds to", "targets": "targets", "treats": "treats",
    "inhibits": "inhibits", "activates": "activates",
    "upregulates": "upregulates", "downregulates": "downregulates",
    "associates": "is associated with", "participates": "participates in",
    "expresses": "is expressed in", "interacts": "interacts with",
    "regulates": "regulates", "causes": "causes"
}

class RobustPoloAgent:
class RobustPoloAgent:
    def __init__(self):
        print("[*] Initializing Robust Polo Agent (Name Support Enabled)...")

        print("🛡️ Initializing Robust Polo Agent (Name Support Enabled)...")
        self.nodes = {} 
        self.name_map = {} # New: Maps "metformin" -> "DB00331"
        self.G = nx.Graph() 
        self.DirectedG = nx.DiGraph() 
        self.degrees = {}     
        self._load_data()

    def safe_print(self, text):
        try:
             print(text)
        except Exception:
             try:
                 print(text.encode('ascii', 'replace').decode('ascii'))
             except: pass


    def _load_data(self):
        # 1. Load Taxonomy
        self.name_map = {} # New: Maps "metformin" -> "DB00331"
        self.G = nx.Graph() 
        self.DirectedG = nx.DiGraph() 
        self.degrees = {}     
        self._load_data()

    def _load_data(self):
        # 1. Load Taxonomy
        try:
            with open("nodes.csv", "r", encoding="utf-8") as f:
            with open("nodes.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 4 and row[3].strip():
                        nid = row[3].strip()
                        name = row[2].strip()
                        ntype = row[1].strip()
                        
                        self.nodes[nid] = {'name': name, 'type': ntype}
                        # Populate Name Index (Lowercased for easy search)
                        self.name_map[name.lower()] = nid
                        nid = row[3].strip()
                        name = row[2].strip()
                        ntype = row[1].strip()
                        
                        self.nodes[nid] = {'name': name, 'type': ntype}
                        # Populate Name Index (Lowercased for easy search)
                        self.name_map[name.lower()] = nid
        except Exception: pass

        # 2. Load Graph
        print("   Building Dual-Layer Network...")
        try:
            # Use relative path assuming we are in temp/ or root
            # If in temp, go up one level.
            # Try absolute path or resilient check
            if os.path.exists("finalKG/data/graph_index.pkl"):
                 p = "finalKG/data/graph_index.pkl"
            elif os.path.exists("../finalKG/data/graph_index.pkl"):
                 p = "../finalKG/data/graph_index.pkl"
            else:
                 p = r"c:\Users\kabhi\neurosymbolic\finalKG\data\graph_index.pkl" # hard fallback
                 
            print(f"[DEBUG] Loading graph from {p}...", flush=True)
            with open(p, "rb") as f:
                loaded_obj = pickle.load(f)
            
            if hasattr(loaded_obj, 'nodes'):
                 # It is a Graph object
                 self.DirectedG = loaded_obj
                 self.G = self.DirectedG.to_undirected()
                 print(f"   [OK] Loaded NetworkX Graph directly ({self.DirectedG.number_of_nodes()} nodes).")
            else:
                 # Assume dict
                 raw_adj = loaded_obj
                 for u, neighbors in raw_adj.items():
                     for v, rel in neighbors.items():
                         self.G.add_edge(u, v)
                         self.DirectedG.add_edge(u, v, relation=rel)

            for n in self.G.nodes():
                self.degrees[n] = self.G.degree(n)
                
            print(f"   [OK] Graph Ready: {self.G.number_of_nodes()} Nodes")
            
        except Exception as e: print(f"[FAIL] Error: {e}")

        # 2. Load Graph
        print("   Building Dual-Layer Network...")
        try:
            with open("graph_index.pkl", "rb") as f:
                raw_adj = pickle.load(f)
            
            for u, neighbors in raw_adj.items():
                for v, rel in neighbors.items():
                    self.G.add_edge(u, v)
                    self.DirectedG.add_edge(u, v, relation=rel)

            for n in self.G.nodes():
                self.degrees[n] = self.G.degree(n)
                
            print(f"   ✅ Graph Ready: {self.G.number_of_nodes()} Nodes")
            
        except Exception as e: print(f"❌ Error: {e}")

    def get_info(self, nid):
        clean = nid.split("::")[-1]
        info = self.nodes.get(clean, {'name': clean, 'type': 'Unknown'})
        if info['type'] == 'Compound': info['type'] = 'Drug'
        return info

    # --- NEW HELPER: RESOLVE NAME TO ID ---
    def get_id(self, user_input):
        """Finds ID by name (case-insensitive)"""
        clean_input = user_input.strip().lower()
        if clean_input in self.name_map:
            return self.name_map[clean_input]
        return None

    def calc_dwpc(self, path):
        score = 1.0
        intermediates = path[1:-1]
        for node in intermediates:
            degree = self.degrees.get(node, 1)
            weight = math.pow(degree, -DAMPING_EXPONENT)
            score *= weight
        return score

    def get_edge_text(self, u, v):
        if self.DirectedG.has_edge(u, v):
            rel = self.DirectedG[u][v]['relation']
            arrow = "-->"
        elif self.DirectedG.has_edge(v, u):
            rel = self.DirectedG[v][u]['relation']
            arrow = "<--" 
        else:
            return "connected to", "---"

        clean_rel = rel.replace("REV_", "")
        readable = REL_MAP.get(clean_rel.lower(), clean_rel)
        
        if rel.startswith("REV_"):
            if arrow == "-->": arrow = "<--"
            else: arrow = "-->"
            
        return readable, arrow

    def stitch_path(self, source, target, intermediate_id):
        try:
            p1 = nx.shortest_path(self.G, source, intermediate_id)
            p2 = nx.shortest_path(self.G, intermediate_id, target)
            return p1 + p2[1:]
        except: return None

    def get_info(self, nid):
        clean = nid.split("::")[-1]
        info = self.nodes.get(clean, {'name': clean, 'type': 'Unknown'})
        if info['type'] == 'Compound': info['type'] = 'Drug'
        return info

    # --- NEW HELPER: RESOLVE NAME TO ID ---
    def get_id(self, user_input):
        """Finds ID by name (case-insensitive)"""
        clean_input = user_input.strip().lower()
        if clean_input in self.name_map:
            return self.name_map[clean_input]
        return None

    def calc_dwpc(self, path):
        score = 1.0
        intermediates = path[1:-1]
        for node in intermediates:
            degree = self.degrees.get(node, 1)
            weight = math.pow(degree, -DAMPING_EXPONENT)
            score *= weight
        return score

    def get_edge_text(self, u, v):
        if self.DirectedG.has_edge(u, v):
            rel = self.DirectedG[u][v]['relation']
            arrow = "-->"
        elif self.DirectedG.has_edge(v, u):
            rel = self.DirectedG[v][u]['relation']
            arrow = "<--" 
        else:
            return "connected to", "---"

        clean_rel = rel.replace("REV_", "")
        readable = REL_MAP.get(clean_rel.lower(), clean_rel)
        
        if rel.startswith("REV_"):
            if arrow == "-->": arrow = "<--"
            else: arrow = "-->"
            
        return readable, arrow

    def stitch_path(self, source, target, intermediate_id):
        try:
            p1 = nx.shortest_path(self.G, source, intermediate_id)
            p2 = nx.shortest_path(self.G, intermediate_id, target)
            return p1 + p2[1:]
        except: return None

    def export_to_json(self, paths, filename="viz_data.json"):
        elements = {"nodes": [], "edges": []}
        added_nodes = set()
        
        for item in paths:
            path = item['path']
            for node_id in path:
                if node_id not in added_nodes:
                    info = self.get_info(node_id)
                    elements["nodes"].append({
                        "data": {
                            "id": node_id, 
                            "label": info['name'], 
                            "type": info['type']
                            "type": info['type']
                        }
                    })
                    added_nodes.add(node_id)
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                
                if self.DirectedG.has_edge(u, v):
                    src, tgt = u, v
                    rel = self.DirectedG[u][v]['relation']
                elif self.DirectedG.has_edge(v, u):
                    src, tgt = v, u
                    rel = self.DirectedG[v][u]['relation']
                else:
                    src, tgt, rel = u, v, "connected"

                edge_id = f"{src}-{tgt}-{rel}"
                exists = False
                for e in elements["edges"]:
                    if e["data"]["id"] == edge_id: exists = True
                
                if not exists:
                    elements["edges"].append({
                        "data": {"id": edge_id, "source": src, "target": tgt, "label": rel}
                    })
        
                
                if self.DirectedG.has_edge(u, v):
                    src, tgt = u, v
                    rel = self.DirectedG[u][v]['relation']
                elif self.DirectedG.has_edge(v, u):
                    src, tgt = v, u
                    rel = self.DirectedG[v][u]['relation']
                else:
                    src, tgt, rel = u, v, "connected"

                edge_id = f"{src}-{tgt}-{rel}"
                exists = False
                for e in elements["edges"]:
                    if e["data"]["id"] == edge_id: exists = True
                
                if not exists:
                    elements["edges"].append({
                        "data": {"id": edge_id, "source": src, "target": tgt, "label": rel}
                    })
        
        with open(filename, "w") as f:
            json.dump(elements, f, indent=2)
        print(f"\n   [SAVE] Visualization data saved to '{filename}'")

    def print_path_realtime(self, index, path, score, ptype):
        self.safe_print(f"* MECHANISM {index} [{ptype}]")
        self.safe_print(f"   Specific Score: {score:.4f}")

        
        chain_str = ""
        for j in range(len(path)-1):
            u, v = path[j], path[j+1]
            u_n = self.get_info(u)['name']
            v_n = self.get_info(v)['name']
            v_t = self.get_info(v)['type']
            
            readable, arrow = self.get_edge_text(u, v)
            
            if arrow == "-->":
                chain_str = f"{u_n} --[{readable}]--> {v_n} ({v_t})"
            elif arrow == "<--":
                chain_str = f"{u_n} <---[{readable}]--- {v_n} ({v_t})"
            else:
                chain_str = f"{u_n} ---[{readable}]--- {v_n} ({v_t})"
            
            self.safe_print(f"   {u_n} {arrow} {v_n} ({v_t})")
        self.safe_print("")

    def explain(self, source_name, target_name):
        self.safe_print(f"[DEBUG] RobustPoloAgent.explain called for {source_name} -> {target_name}")
        
        # 1. RESOLVE NAMES TO IDS
        # If input is already ID (digits), use it. Else resolve.
        # But our get_id might fail if we don't have mapping in polo?
        # RobustPoloAgent loads nodes.csv which has IDs.
        
        s_clean = None
        if source_name in self.nodes:
            s_clean = source_name
        else:
            s_clean = self.get_id(source_name)
            
        target_clean = None
        if target_name in self.nodes:
            target_clean = target_name
        else:
             target_clean = self.get_id(target_name)
             
        # Map to instance vars for fallback use
        source_id = s_clean
        target_id = target_clean 
        
        # FIX ALIASES FOR LEGACY CODE
        s_clean = source_id
        t_clean = target_id
 

        if not s_clean:
            # Fallback: Maybe user typed raw ID?
            if source_name in self.nodes: s_clean = source_name
            else:
                self.safe_print(f"[FAIL] Error: Drug '{source_name}' not found in database.")
                return []

        if not target_clean:
            # Fallback
            if target_name in self.nodes: target_clean = target_name
            else:
                self.safe_print(f"[FAIL] Error: Disease '{target_name}' not found in database.")
                return []

        # 2. RUN ALGORITHM
        valid_paths = []
        path_counter = 1
        
        # --- PHASE 1: VIP RECONSTRUCTION (Stream Output) ---
        # self.safe_print("   (Phase 1: Reconstructing signaling cascades for VIPs...)")
        for vip_name, vip_id in VIP_TARGETS.items():
    def print_path_realtime(self, index, path, score, ptype):
        print(f"🔷 MECHANISM {index} [{ptype}]")
        print(f"   Specific Score: {score:.4f}")
        
        chain_str = ""
        for j in range(len(path)-1):
            u, v = path[j], path[j+1]
            u_n = self.get_info(u)['name']
            v_n = self.get_info(v)['name']
            v_t = self.get_info(v)['type']
            
            readable, arrow = self.get_edge_text(u, v)
            
            if arrow == "-->":
                chain_str = f"{u_n} --[{readable}]--> {v_n} ({v_t})"
            elif arrow == "<--":
                chain_str = f"{u_n} <---[{readable}]--- {v_n} ({v_t})"
            else:
                chain_str = f"{u_n} ---[{readable}]--- {v_n} ({v_t})"
            
            print(f"      {chain_str}")
        print("")

    def explain(self, drug_input, disease_input):
        # 1. RESOLVE NAMES TO IDS
        s_clean = self.get_id(drug_input)
        if not s_clean:
            # Fallback: Maybe user typed raw ID?
            if drug_input in self.nodes: s_clean = drug_input
            else:
                print(f"❌ Error: Drug '{drug_input}' not found in database.")
                return

        t_clean = self.get_id(disease_input)
        if not t_clean:
            if disease_input in self.nodes: t_clean = disease_input
            else:
                print(f"❌ Error: Disease '{disease_input}' not found in database.")
                return
        
        s_info = self.get_info(s_clean)
        t_info = self.get_info(t_clean)
        
        print(f"\n🔎 Robust Analysis: {s_info['name']} ({s_clean}) -> {t_info['name']} ({t_clean})")
        
        valid_paths = []
        path_counter = 1
        
        # --- PHASE 1: VIP RECONSTRUCTION (Stream Output) ---
        print("   (Phase 1: Reconstructing signaling cascades for VIPs...)")
        for vip_name, vip_id in VIP_MOLECULES.items():
            if vip_id in self.G:
                path = self.stitch_path(s_clean, t_clean, vip_id)
                if path:
                    if len(path) <= 6:
                        score = self.calc_dwpc(path)
                        boosted_score = score * 10
                        ptype = f'VIA {vip_name} (Targeted)'
                        
                        # self.print_path_realtime(path_counter, path, boosted_score, ptype)
                        path_counter += 1
                        
                        valid_paths.append({'path': path, 'score': boosted_score, 'type': ptype})

        # --- PHASE 2: TOPOLOGICAL SEARCH (Stream Output) ---
        # self.safe_print("   (Phase 2: Scanning general connectivity...)")

        try:
            gen = nx.shortest_simple_paths(self.G, s_clean, t_clean)
            
            count = 0
            for _ in range(3000): # Scan deep
                path = next(gen)
                if len(path) > 4: break # Limit depth
                
                is_valid = True
                has_mech = False
                for mid in path[1:-1]:
                    ntype = self.get_info(mid)['type'].lower()
                    if "anatomy" in ntype or "symptom" in ntype or "side" in ntype:
                        is_valid = False
                        break
                    if "gene" in ntype or "pathway" in ntype:
                        has_mech = True
                
                if is_valid and has_mech:
                    if not any(x['path'] == path for x in valid_paths):
                        score = self.calc_dwpc(path)
                        ptype = 'General'
                        
                        self.print_path_realtime(path_counter, path, score, ptype)
                        path_counter += 1
                        
                        valid_paths.append({'path': path, 'score': score, 'type': ptype})
                        count += 1
                        if count >= 20: break 
                        
        except nx.NetworkXNoPath:
            pass

        # --- EXPORT ---
        valid_paths.sort(key=lambda x: x['score'], reverse=True)
        self.export_to_json(valid_paths[:20]) 
        
        print(f"[DONE] Finished. Found {len(valid_paths)} Mechanisms.\n")
        
        if not valid_paths:
            print("[DEBUG] No VIP paths. Trying Undirected Fallback...")
            try:
                # Force converting to string IDs if they aren't
                s_id = str(source_id)
                t_id = str(target_id)
                
                # Check Directed
                if self.G.has_node(s_id) and self.G.has_node(t_id):
                    if nx.has_path(self.G, s_id, t_id):
                        print("[DEBUG] Found DIRECTED path via fallback.")
                        path = nx.shortest_path(self.G, s_id, t_id)
                        valid_paths.append({'path': path, 'score': 0.5, 'tag': 'Direct Link'})
                
                # Check Undirected if still empty
                if not valid_paths:
                     print("[DEBUG] Converting to Undirected...")
                     G_undir = self.G.to_undirected()
                     if G_undir.has_node(s_id) and G_undir.has_node(t_id):
                         if nx.has_path(G_undir, s_id, t_id):
                             print("[DEBUG] Found UNDIRECTED path.")
                             path = nx.shortest_path(G_undir, s_id, t_id)
                             valid_paths.append({'path': path, 'score': 0.3, 'tag': 'Association (Undirected)'})
                         else:
                             print("[DEBUG] No undirected path found.")
                     else:
                         print(f"[DEBUG] Nodes missing in graph: {s_id} in? {G_undir.has_node(s_id)}, {t_id} in? {G_undir.has_node(t_id)}")

            except Exception as e:
                import traceback
                print(f"[DEBUG] Fallback exception: {e}")
                traceback.print_exc()

        return valid_paths

                path = self.stitch_path(s_clean, t_clean, vip_id)
                if path:
                    if len(path) <= 6:
                        score = self.calc_dwpc(path)
                        boosted_score = score * 10
                        ptype = f'VIA {vip_name} (Targeted)'
                        
                        self.print_path_realtime(path_counter, path, boosted_score, ptype)
                        path_counter += 1
                        
                        valid_paths.append({'path': path, 'score': boosted_score, 'type': ptype})

        # --- PHASE 2: TOPOLOGICAL SEARCH (Stream Output) ---
        print("   (Phase 2: Scanning general connectivity...)")
        try:
            gen = nx.shortest_simple_paths(self.G, s_clean, t_clean)
            
            count = 0
            for _ in range(3000): # Scan deep
                path = next(gen)
                if len(path) > 4: break # Limit depth
                
                is_valid = True
                has_mech = False
                for mid in path[1:-1]:
                    ntype = self.get_info(mid)['type'].lower()
                    if "anatomy" in ntype or "symptom" in ntype or "side" in ntype:
                        is_valid = False
                        break
                    if "gene" in ntype or "pathway" in ntype:
                        has_mech = True
                
                if is_valid and has_mech:
                    if not any(x['path'] == path for x in valid_paths):
                        score = self.calc_dwpc(path)
                        ptype = 'General'
                        
                        self.print_path_realtime(path_counter, path, score, ptype)
                        path_counter += 1
                        
                        valid_paths.append({'path': path, 'score': score, 'type': ptype})
                        count += 1
                        if count >= 20: break 
                        
        except nx.NetworkXNoPath:
            pass
            print(f"   ✅ Graph Ready: {self.G.number_of_nodes()} Nodes")
            
        except Exception as e: print(f"❌ Error: {e}")

    def get_info(self, nid):
        clean = nid.split("::")[-1]
        info = self.nodes.get(clean, {'name': clean, 'type': 'Unknown'})
        if info['type'] == 'Compound': info['type'] = 'Drug'
        return info

    # --- NEW HELPER: RESOLVE NAME TO ID ---
    def get_id(self, user_input):
        """Finds ID by name (case-insensitive)"""
        clean_input = user_input.strip().lower()
        if clean_input in self.name_map:
            return self.name_map[clean_input]
        return None

    def calc_dwpc(self, path):
        score = 1.0
        intermediates = path[1:-1]
        for node in intermediates:
            degree = self.degrees.get(node, 1)
            weight = math.pow(degree, -DAMPING_EXPONENT)
            score *= weight
        return score

    def get_edge_text(self, u, v):
        if self.DirectedG.has_edge(u, v):
            rel = self.DirectedG[u][v]['relation']
            arrow = "-->"
        elif self.DirectedG.has_edge(v, u):
            rel = self.DirectedG[v][u]['relation']
            arrow = "<--" 
        else:
            return "connected to", "---"

        clean_rel = rel.replace("REV_", "")
        readable = REL_MAP.get(clean_rel.lower(), clean_rel)
        
        if rel.startswith("REV_"):
            if arrow == "-->": arrow = "<--"
            else: arrow = "-->"
            
        return readable, arrow

    def stitch_path(self, source, target, intermediate_id):
        try:
            p1 = nx.shortest_path(self.G, source, intermediate_id)
            p2 = nx.shortest_path(self.G, intermediate_id, target)
            return p1 + p2[1:]
        except: return None

    def export_to_json(self, paths, filename="viz_data.json"):
        elements = {"nodes": [], "edges": []}
        added_nodes = set()
        
        for item in paths:
            path = item['path']
            for node_id in path:
                if node_id not in added_nodes:
                    info = self.get_info(node_id)
                    elements["nodes"].append({
                        "data": {
                            "id": node_id, 
                            "label": info['name'], 
                            "type": info['type']
                        }
                    })
                    added_nodes.add(node_id)
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                
                if self.DirectedG.has_edge(u, v):
                    src, tgt = u, v
                    rel = self.DirectedG[u][v]['relation']
                elif self.DirectedG.has_edge(v, u):
                    src, tgt = v, u
                    rel = self.DirectedG[v][u]['relation']
                else:
                    src, tgt, rel = u, v, "connected"

                edge_id = f"{src}-{tgt}-{rel}"
                exists = False
                for e in elements["edges"]:
                    if e["data"]["id"] == edge_id: exists = True
                
                if not exists:
                    elements["edges"].append({
                        "data": {"id": edge_id, "source": src, "target": tgt, "label": rel}
                    })
        
        with open(filename, "w") as f:
            json.dump(elements, f, indent=2)
        print(f"\n   📊 Visualization data saved to '{filename}'")

    def print_path_realtime(self, index, path, score, ptype):
        print(f"🔷 MECHANISM {index} [{ptype}]")
        print(f"   Specific Score: {score*100:.4f}")
        
        chain_str = ""
        for j in range(len(path)-1):
            u, v = path[j], path[j+1]
            u_n = self.get_info(u)['name']
            v_n = self.get_info(v)['name']
            v_t = self.get_info(v)['type']
            
            readable, arrow = self.get_edge_text(u, v)
            
            if arrow == "-->":
                chain_str = f"{u_n} --[{readable}]--> {v_n} ({v_t})"
            elif arrow == "<--":
                chain_str = f"{u_n} <---[{readable}]--- {v_n} ({v_t})"
            else:
                chain_str = f"{u_n} ---[{readable}]--- {v_n} ({v_t})"
            
            print(f"      {chain_str}")
        print("")

    def explain(self, drug_input, disease_input):
        # 1. RESOLVE NAMES TO IDS
        s_clean = self.get_id(drug_input)
        if not s_clean:
            # Fallback: Maybe user typed raw ID?
            if drug_input in self.nodes: s_clean = drug_input
            else:
                print(f"❌ Error: Drug '{drug_input}' not found in database.")
                return

        t_clean = self.get_id(disease_input)
        if not t_clean:
            if disease_input in self.nodes: t_clean = disease_input
            else:
                print(f"❌ Error: Disease '{disease_input}' not found in database.")
                return
        
        s_info = self.get_info(s_clean)
        t_info = self.get_info(t_clean)
        
        print(f"\n🔎 Robust Analysis: {s_info['name']} ({s_clean}) -> {t_info['name']} ({t_clean})")
        
        valid_paths = []
        path_counter = 1
        
        # --- PHASE 1: VIP RECONSTRUCTION (Stream Output) ---
        print("   (Phase 1: Reconstructing signaling cascades for VIPs...)")
        for vip_name, vip_id in VIP_MOLECULES.items():
            if vip_id in self.G:
                path = self.stitch_path(s_clean, t_clean, vip_id)
                if path:
                    if len(path) <= 6:
                        score = self.calc_dwpc(path)
                        boosted_score = score * 10
                        ptype = f'VIA {vip_name} (Targeted)'
                        
                        self.print_path_realtime(path_counter, path, boosted_score, ptype)
                        path_counter += 1
                        
                        valid_paths.append({'path': path, 'score': boosted_score, 'type': ptype})

        # --- PHASE 2: TOPOLOGICAL SEARCH (Stream Output) ---
        print("   (Phase 2: Scanning general connectivity...)")
        try:
            gen = nx.shortest_simple_paths(self.G, s_clean, t_clean)
            
            count = 0
            for _ in range(3000): # Scan deep
                path = next(gen)
                if len(path) > 4: break # Limit depth
                
                is_valid = True
                has_mech = False
                for mid in path[1:-1]:
                    ntype = self.get_info(mid)['type'].lower()
                    if "anatomy" in ntype or "symptom" in ntype or "side" in ntype:
                        is_valid = False
                        break
                    if "gene" in ntype or "pathway" in ntype:
                        has_mech = True
                
                if is_valid and has_mech:
                    if not any(x['path'] == path for x in valid_paths):
                        score = self.calc_dwpc(path)
                        ptype = 'General'
                        
                        self.print_path_realtime(path_counter, path, score, ptype)
                        path_counter += 1
                        
                        valid_paths.append({'path': path, 'score': score, 'type': ptype})
                        count += 1
                        if count >= 20: break 
                        
        except nx.NetworkXNoPath:
            pass

        # --- EXPORT ---
        valid_paths.sort(key=lambda x: x['score'], reverse=True)
        self.export_to_json(valid_paths[:20]) 
        
        print(f"✅ Finished. Found {len(valid_paths)} Mechanisms.\n")

# Alias for backward compatibility / ghost references
TargetedAgent = RobustPoloAgent

if __name__ == "__main__":
    agent = RobustPoloAgent()
    agent = RobustPoloAgent()
    while True:
        print("-" * 60)
        d = input("💊 Drug Name (e.g. Metformin): ").strip()
        if d.lower() == 'q': break
        dis = input("🦠 Disease Name (e.g. Breast cancer): ").strip()
        d = input("💊 Drug Name (e.g. Metformin): ").strip()
        if d.lower() == 'q': break
        dis = input("🦠 Disease Name (e.g. Breast cancer): ").strip()
        agent.explain(d, dis)