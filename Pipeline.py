from typing import List, Union, Generator, Iterator
from pydantic import BaseModel, Field
import requests
import os
import json
from logging import getLogger
import time

logger = getLogger(__name__)
logger.setLevel("DEBUG")

class Pipeline:
    """
    Eine Pipeline, die Whoogle für die Web-Suche und Crawl4AI für das Crawling verwendet.
    """
    class Valves(BaseModel):
        WHOOGLE_URL: str = Field(default="http://10.10.10.90:5001", description="URL for your Whoogle instance")
        CRAWL4AI_URL: str = Field(default="http://10.10.10.90:11235", description="Base URL for your Crawl4AI instance")
        MAX_URLS: int = Field(default=5, description="Maximum number of URLs to crawl")

    def __init__(self):
        self.name = "Whoogle & Crawl4AI Pipeline"
        self.valves = self.Valves(
            **{k: os.getenv(k, v.default) for k, v in self.Valves.model_fields.items()}
        )

    async def on_startup(self):
        logger.debug(f"on_startup:{self.name}")
        pass

    async def on_shutdown(self):
        logger.debug(f"on_shutdown:{self.name}")
        pass

    def _get_whoogle_urls(self, query: str) -> List[str]:
        """
        Ruft URLs von der Whoogle-Instanz ab.
        """
        try:
            # Senden der Abfrage als URL-Parameter
            response = requests.get(
                f"{self.valves.WHOOGLE_URL}/search",
                params={'q': query},
                timeout=5
            )
            response.raise_for_status()
            search_results = response.json()
            
            # Überprüfen des Suchergebnis-Formats und Extrahieren der Links
            urls = []
            if 'results' in search_results:
                for result in search_results['results']:
                    if 'link' in result:
                        urls.append(result['link'])
            
            logger.info(f"Whoogle-Suche für '{query}' ergab {len(urls)} URLs.")
            return urls[:self.valves.MAX_URLS]
        except Exception as e:
            logger.error(f"Fehler bei der Whoogle-Suche: {e}")
            return []

    def _get_crawled_content(self, urls: List[str]) -> str:
        """
        Crawlt den Inhalt von URLs mit Crawl4AI.
        """
        content = ""
        for url in urls:
            try:
                # Crawl4AI-API erwartet eine POST-Anfrage
                payload = {"url": url}
                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    f"{self.valves.CRAWL4AI_URL}/crawl",
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                crawled_data = response.json()
                
                if 'text' in crawled_data:
                    content += f"\n\n### Inhalt von: {url}\n"
                    content += crawled_data['text']
                
            except Exception as e:
                logger.error(f"Fehler beim Crawling von {url}: {e}")
                continue
        return content

    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[dict],
        body: dict
    ) -> Union[str, Generator, Iterator]:
        logger.info(f"Pipe-Aufruf mit: {user_message}")

        # Suchbegriff ist die letzte Nachricht des Benutzers
        query = user_message.strip()
        
        # Schritt 1: URLs über Whoogle abrufen
        urls = self._get_whoogle_urls(query)
        if not urls:
            yield "Keine relevanten URLs gefunden."
            return

        # Schritt 2: Inhalt der URLs mit Crawl4AI crawlen
        crawled_content = self._get_crawled_content(urls)
        
        if not crawled_content:
            yield "Inhalt konnte nicht extrahiert werden."
            return

        # Den gecrawlten Inhalt dem Modell als Kontext zurückgeben
        yield f"**Gefundene Informationen:**\n{crawled_content}\n\n**Antwort basierend auf den obigen Informationen:**"
