import pickle
import sys

def inspect_pickle():
    path = r'c:\Users\kabhi\neurosymbolic\finalKG\data\graph_index.pkl'
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
            
        print(f"Loaded {path}")
        print(f"Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())[:20]}")
            for key, value in list(data.items())[:5]:
                print(f"Key: {key}, Type: {type(value)}")
                if hasattr(value, '__len__'):
                    print(f"  Length: {len(value)}")
                print(f"  Sample: {str(value)[:100]}")
        elif isinstance(data, list):
            print(f"Length: {len(data)}")
            print(f"Sample: {data[:5]}")
        else:
             print(f"Value: {str(data)[:200]}")

    except Exception as e:
        print(f"Error reading pickle: {e}")

if __name__ == "__main__":
    inspect_pickle()
