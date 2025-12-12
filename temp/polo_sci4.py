import pickle
import csv
import networkx as nx

# --- CONFIGURATION: PRIORITY TARGETS ---
# The agent will FORCE these paths to be checked first.
VIP_TARGETS = {
    "MTOR": "2475", 
    "AMPK": "PRKAA1", 
    "TP53": "7157", 
    "EGFR": "1956",
    "BRCA1": "672", 
    "BRCA2": "675", 
    "HER2": "2064",
    "AKT1": "207",
    "PIK3CA": "5290"
}

# --- SCORING DICTIONARY ---
EDGE_SCORES = {
    "inhibits": 1.0, "activates": 1.0, "targets": 1.0, "binds": 1.0,
    "treats": 0.95, "regulates": 0.8, "upregulates": 0.7, "downregulates": 0.7,
    "associates": 0.3, "interacts": 0.3, "presents": 0.4
}

class TargetedAgent:
    def __init__(self):
        print("🎯 Initializing Target-Aware Scientific Agent...")
        self.nodes = {} 
        self.load_nodes("nodes.csv")
        self.G = nx.DiGraph()
        self.load_graph_data("graph_index.pkl")
        
        # FINAL CHECK
        if "2475" in self.G:
            print("✅ DIAGNOSTIC: mTOR (2475) is active and ready for targeting.")
        else:
            print("⚠️ WARNING: mTOR (2475) is missing. The Hunter phase will fail for mTOR.")
            
        print("✅ System Ready.")

    def load_nodes(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 4 and row[3].strip():
                        self.nodes[row[3].strip()] = {'name': row[2].strip(), 'type': row[1].strip()}
        except Exception: pass

    def load_graph_data(self, filename):
        try:
            with open(filename, "rb") as f:
                raw_adj = pickle.load(f)
            for u, neighbors in raw_adj.items():
                for v, relation in neighbors.items():
                    # WEIGHTING (Lower = Better for search)
                    w = 1.0
                    if "associates" in relation.lower(): w = 5.0
                    self.G.add_edge(u, v, relation=relation, weight=w)
        except Exception as e: print(f"❌ Error: {e}")

    def get_info(self, n_id):
        clean = n_id.split("::")[-1]
        return self.nodes.get(clean, {'name': clean, 'type': 'Unknown'})

    def calculate_confidence(self, path):
        total_score = 0
        step_count = len(path) - 1
        vip_boost = False
        
        for i in range(step_count):
            u, v = path[i], path[i+1]
            rel = self.G[u][v]['relation'].lower()
            
            # 1. Edge Score
            edge_val = 0.4
            for key, val in EDGE_SCORES.items():
                if key in rel:
                    edge_val = val
                    break
            total_score += edge_val
            
            # 2. VIP Boost
            if v in VIP_TARGETS.values(): vip_boost = True

        avg_score = (total_score / step_count) * 100
        if vip_boost: avg_score += 10 # Reward VIPs
        
        return min(round(avg_score, 1), 99.9)

    def explain(self, drug_id, disease_id):
        source = drug_id.split("::")[-1]
        target = disease_id.split("::")[-1]

        if source not in self.G or target not in self.G:
            print("❌ Source or Target node not found.")
            return

        s_name = self.get_info(source)['name']
        t_name = self.get_info(target)['name']
        print(f"\n🔎 Query: {s_name} -> {t_name}")
        
        found_paths = []
        
        # --- PHASE 1: THE VIP HUNTER (Force check mTOR) ---
        print("   (Phase 1: Forcing checks on known cancer drivers...)")
        for vip_name, vip_id in VIP_TARGETS.items():
            if vip_id in self.G:
                try:
                    # Look for: Drug -> ... -> VIP -> ... -> Disease
                    # We accept up to 2 hops to reach VIP, and 2 hops to reach Disease
                    p1 = nx.shortest_path(self.G, source, vip_id, weight='weight')
                    p2 = nx.shortest_path(self.G, vip_id, target, weight='weight')
                    
                    full_path = p1 + p2[1:] # Merge
                    
                    # Verify it's not crazy long
                    if len(full_path) <= 6:
                        score = self.calculate_confidence(full_path)
                        found_paths.append({'path': full_path, 'score': score + 5, 'tag': f'VIA {vip_name} ⭐'})
                except nx.NetworkXNoPath:
                    pass # It's okay, not every drug hits every target

        # --- PHASE 2: GENERAL EXPLORATION ---
        # Only run if we need more options
        if len(found_paths) < 10:
            print("   (Phase 2: Scanning for other mechanisms...)")
            try:
                gen = nx.shortest_simple_paths(self.G, source, target, weight='weight')
                for _ in range(20):
                    p = next(gen)
                    if len(p) > 5: break
                    
                    # Avoid duplicates
                    if any(x['path'] == p for x in found_paths): continue
                    
                    # Filter
                    is_valid = True
                    for mid in p[1:-1]:
                        if "anatomy" in self.get_info(mid)['type'].lower(): is_valid = False
                    
                    if is_valid:
                        score = self.calculate_confidence(p)
                        found_paths.append({'path': p, 'score': score, 'tag': 'General'})
            except: pass

        # --- SORT & DISPLAY ---
        found_paths.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Found {len(found_paths)} pathways. (Priority given to Key Regulators)\n")
        
        for i, item in enumerate(found_paths):
            score = item['score']
            path = item['path']
            tag = item['tag']
            
            print(f"🔷 PATHWAY {i+1} [{tag}] Confidence: {score}%")
            
            for j in range(len(path)-1):
                u, v = path[j], path[j+1]
                rel = self.G[u][v]['relation']
                
                u_n = self.get_info(u)['name']
                v_n = self.get_info(v)['name']
                v_t = self.get_info(v)['type']
                
                arrow = f"--[{rel}]-->"
                if rel.startswith("REV_"): arrow = f"<--[{rel[4:]}]--"
                
                print(f"   {u_n} {arrow} {v_n} ({v_t})")
            print("")

if __name__ == "__main__":
    agent = TargetedAgent()
    while True:
        print("-" * 60)
        d = input("💊 Drug ID: ").strip()
        if d == 'q': break
        dis = input("🦠 Disease ID: ").strip()
        agent.explain(d, dis)