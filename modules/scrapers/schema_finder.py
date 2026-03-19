import requests

from bs4 import BeautifulSoup

import json

from modules.utils.http_client import get_default_client



class SchemaFinder:

    def __init__(self):

        self.headers = {

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        }
        
        # Cliente HTTP con fallback SSL
        self.http_client = get_default_client()

    

    def analyze(self, url):

        """

        Analiza implementacion de Schema.org
        Con fallback SSL para certificados expirados

        """

        try:

            # Usar HttpClient con fallback SSL
            response, fallback_info = self.http_client.get(url, headers=self.headers)
            
            if response is None:
                raise Exception(fallback_info.get('error', 'Request failed'))

            soup = BeautifulSoup(response.content, 'html.parser')

            

            schemas_found = []

            missing_schemas = []

            missing_fields = []

            

            # Buscar todos los schemas

            for script in soup.find_all('script', type='application/ld+json'):

                try:

                    data = json.loads(script.string)

                    # v2.6: Soportar @graph (múltiples schemas en un bloque)
                    if '@graph' in data:
                        for item in data['@graph']:
                            schema_type = item.get('@type', 'Unknown')
                            schemas_found.append({
                                'type': schema_type,
                                'data': item
                            })
                    else:
                        schema_type = data.get('@type', 'Unknown')
                        schemas_found.append({
                            'type': schema_type,
                            'data': data
                        })

                except:

                    continue

            

            # Verificar schemas criticos para hoteles

            schema_types = [s['type'] for s in schemas_found]

            

            required_schemas = ['Hotel', 'LodgingBusiness']

            recommended_schemas = ['FAQPage', 'Review', 'AggregateRating']

            

            for req_schema in required_schemas:

                if req_schema not in schema_types:

                    missing_schemas.append(req_schema)

            

            for rec_schema in recommended_schemas:

                if rec_schema not in schema_types:

                    missing_schemas.append(f"{rec_schema} (recomendado)")

            

            # Verificar campos criticos en schema Hotel

            hotel_schema = next((s for s in schemas_found if s['type'] in ['Hotel', 'LodgingBusiness']), None)

            

            if hotel_schema:

                required_fields = [

                    'name', 'address', 'telephone', 'priceRange',

                    'amenityFeature', 'image', 'url'

                ]

                

                for field in required_fields:

                    if field not in hotel_schema['data']:

                        missing_fields.append(field)

            

            return {

                'schemas_encontrados': schemas_found,

                'total_schemas': len(schemas_found),

                'tiene_hotel_schema': hotel_schema is not None,

                'schemas_faltantes': missing_schemas,

                'campos_faltantes': missing_fields,

                'score_schema': self._calculate_schema_score(schemas_found, missing_fields),

                'ssl_fallback_info': fallback_info  # Trazabilidad SSL

            }

            

        except Exception as e:

            return {

                'schemas_encontrados': [],

                'total_schemas': 0,

                'tiene_hotel_schema': False,

                'schemas_faltantes': ['Todos'],

                'campos_faltantes': ['Todos'],

                'score_schema': 0,

                'error': str(e)

            }

    

    def _calculate_schema_score(self, schemas, missing_fields):

        """Calcula score de implementacion de schema (0-100)"""

        score = 0

        

        # Tiene algun schema? +30

        if schemas:

            score += 30

        

        # Tiene Hotel schema? +40

        schema_types = [s['type'] for s in schemas]

        if any(t in ['Hotel', 'LodgingBusiness'] for t in schema_types):

            score += 40

        

        # Tiene FAQPage? +15

        if 'FAQPage' in schema_types:

            score += 15

        

        # Tiene Rating? +15

        if any(t in ['Review', 'AggregateRating'] for t in schema_types):

            score += 15

        

        # Penalizar por campos faltantes

        penalty = len(missing_fields) * 5

        score = max(0, score - penalty)

        

        return score