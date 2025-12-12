import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict

async def fetch_papers(drug_name: str, disease_name: str) -> List[Dict[str, str]]:
    """
    Returns a list of up to 4 PubMed articles, each as a dict:
    {
      "pmid": str,
      "title": str,
      "abstract": str,
      "journal": str,
      "year": str,
      "url": str
    }
    """
    try:
        query = f"{drug_name}[Title/Abstract] AND {disease_name}[Title/Abstract]"
        
        async with httpx.AsyncClient() as client:
            # 1. ESearch
            esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": 4,
                "retmode": "json",
                "sort": "relevance"
            }
            search_resp = await client.get(esearch_url, params=search_params)
            search_data = search_resp.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return []
            
            # 2. EFetch
            efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            fetch_resp = await client.get(efetch_url, params=fetch_params)
            root = ET.fromstring(fetch_resp.text)
            
            papers = []
            for article in root.findall(".//PubmedArticle"):
                pmid_node = article.find(".//PMID")
                title_node = article.find(".//ArticleTitle")
                abstract_node = article.find(".//Abstract/AbstractText")
                journal_node = article.find(".//Journal/Title")
                year_node = article.find(".//PubDate/Year")
                
                # Fallback for year if PubDate has no Year (e.g. MedlineDate)
                if year_node is None:
                     medline_date = article.find(".//PubDate/MedlineDate")
                     year_text = medline_date.text.split(" ")[0] if medline_date is not None else "N/A"
                else:
                    year_text = year_node.text

                pmid = pmid_node.text if pmid_node is not None else ""
                
                if not pmid:
                    continue

                papers.append({
                    "pmid": pmid,
                    "title": title_node.text if title_node is not None else "No Title",
                    "abstract": abstract_node.text if abstract_node is not None else "No Abstract",
                    "journal": journal_node.text if journal_node is not None else "No Journal",
                    "year": year_text,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
                
            return papers

    except Exception:
        # On ANY failure return [] (never raise exceptions).
        return []
