from openui import tool
from openui.pipelines.pipeline import Pipeline
from openui.tools.websearch import WebSearch
from openui.tools.webcrawler import WebCrawler

# Ihre konfigurierten URLs aus Open WebUI
WHOOGLE_URL = "http://10.10.10.90:5001"
CRAWL4AI_URL = "http://10.10.10.90:11235/crawl"  # Stellen Sie sicher, dass dies der korrekte API-Endpunkt ist

@tool
class WhoogleSearch(WebSearch):
    """
    Ein Tool, um die Whoogle-Suche zu verwenden.
    """
    def __init__(self, api_url=WHOOGLE_URL, **kwargs):
        super().__init__(api_url=api_url, **kwargs)

@tool
class Crawl4AI(WebCrawler):
    """
    Ein Tool, um den Inhalt von URLs mit Crawl4AI zu crawlen.
    """
    def __init__(self, api_url=CRAWL4AI_URL, **kwargs):
        super().__init__(api_url=api_url, **kwargs)

class WhoogleCrawlPipeline(Pipeline):
    """
    Eine Pipeline, die Whoogle zum Suchen und Crawl4AI zum Crawlen verwendet.
    """
    def run(self, query: str):
        """
        Führt die Such- und Crawl-Schritte aus.
        """
        # Schritt 1: Suche nach den Top-5-URLs mit Whoogle.
        # Passen Sie die Anzahl der Suchergebnisse bei Bedarf an.
        search_tool = WhoogleSearch()
        search_results = search_tool.search(query=query)
        
        # Extrahieren Sie die URLs aus den Suchergebnissen.
        urls = [result.get('link') for result in search_results]

        # Schritt 2: Crawlen des Inhalts der gefundenen URLs mit Crawl4AI.
        crawl_tool = Crawl4AI()
        crawled_content = crawl_tool.crawl(urls=urls)
        
        # Gibt den gecrawlten Inhalt zurück.
        return crawled_content

# Fügen Sie diese Zeile am Ende der Datei hinzu, um die Pipeline zu registrieren.
pipeline = WhoogleCrawlPipeline()