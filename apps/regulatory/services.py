"""
Servicio de scraping para obtener información oficial de normativas
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from datetime import datetime
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

class LegalScrapingService:
    """Servicio para realizar scraping de información legal oficial"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_ley_1715_2014(self):
        """
        Obtiene información específica de la Ley 1715 de 2014
        desde la fuente oficial de Función Pública
        """
        # Fuente única y oficial de la Ley 1715 (Función Pública)
        urls_oficiales = [
            'https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353',
        ]
        
        data = {
            'title': 'Ley 1715 de 2014 - Promoción de Energías Renovables no Convencionales',
            'summary': self._get_default_summary(),
            'main_objective': self._get_main_objective(),
            'benefits_companies': self._get_benefits_companies(),
            'benefits_citizens': self._get_benefits_citizens(),
            'official_url': 'https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353',
            'content_scraped': '',
            'success': False
        }
        
        # Intentar scraping de diferentes fuentes
        for url in urls_oficiales:
            try:
                content = self._scrape_funcion_publica_url(url) if 'funcionpublica' in url else self._scrape_url(url)
                if content:
                    data['content_scraped'] = content
                    data['success'] = True
                    break
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        # Si no se pudo hacer scraping, usar contenido por defecto
        if not data['success']:
            data['content_scraped'] = self._get_fallback_content()
            data['success'] = True
            
        return data

    def scrape_norma_oficial(self, official_url: str, number: str, year: int):
        """Scrapea una norma específica desde Función Pública usando su URL oficial."""
        data = {
            'title': f'Ley {number} de {year}',
            'summary': self._get_default_summary(),
            'main_objective': self._get_main_objective(),
            'benefits_companies': self._get_benefits_companies(),
            'benefits_citizens': self._get_benefits_citizens(),
            'official_url': official_url,
            'content_scraped': '',
            'success': False
        }

        try:
            content = self._scrape_funcion_publica_url(official_url)
            if content:
                data['content_scraped'] = content
                data['success'] = True
        except Exception as e:
            logger.error(f"Error scraping {official_url}: {str(e)}")

        if not data['success']:
            data['content_scraped'] = self._get_fallback_content()
            data['success'] = True

        return data
    
    def _scrape_funcion_publica_url(self, url):
        """Scraping específico para el portal de Función Pública, preservando HTML cuando sea posible"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Forzar encoding UTF-8

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remover elementos no deseados globales
            for element in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                element.decompose()

            # 1) Intentar extraer HTML del contenedor principal conocido
            container = soup.select_one('div.descripcion-contenido')
            if not container:
                container = soup.select_one('div.contenido, div#contenido, .norma-contenido, .documento, .texto-norma')
            if container:
                # HTML interno del contenedor (preserva títulos, negrillas, listas, etc.)
                html = container.decode_contents().strip()
                return html if html else None

            # 2) Fallback a ensamblar texto (menos preferido)
            content_sections = []

            main_content = soup.find('div', class_='contenido') or soup.find('div', {'id': 'contenido'})
            if main_content:
                text = main_content.get_text("\n", strip=True)
                text = self._clean_text(text)
                content_sections.append(text)

            for selector in ['.norma-contenido', '.documento', '.texto-norma', '.articulo']:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text("\n", strip=True)
                    text = self._clean_text(text)
                    if len(text) > 50 and '1715' in text:
                        content_sections.append(text)

            if not content_sections:
                all_text = soup.get_text()
                all_text = self._clean_text(all_text)
                if '1715' in all_text and ('renovable' in all_text.lower() or 'energía' in all_text.lower()):
                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(" ", strip=True)
                        text = self._clean_text(text)
                        if len(text) > 100 and ('1715' in text or 'renovable' in text.lower()):
                            content_sections.append(text)

            final_content = '\n\n'.join(content_sections) if content_sections else None
            return final_content

        except Exception as e:
            logger.error(f"Error en scraping específico de Función Pública {url}: {str(e)}")
            return None
    
    def _clean_text(self, text):
        """Limpia el texto de caracteres problemáticos y normaliza encoding"""
        if not text:
            return text
        
        # Reemplazar caracteres problemáticos
        replacements = {
            '\u00c2\u00a0': ' ',  # Non-breaking space
            '\u00c2\u00ad': '',   # Soft hyphen
            '\u00a0': ' ',        # Non-breaking space
            '\u2013': '-',        # En dash
            '\u2014': '-',        # Em dash
            '\u201c': '"',        # Left double quotation mark
            '\u201d': '"',        # Right double quotation mark
            '\u2018': "'",        # Left single quotation mark
            '\u2019': "'",        # Right single quotation mark
            '\u2022': '•',        # Bullet point
            '\ufeff': '',         # Zero width no-break space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Normalizar espacios múltiples
        import re
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Asegurarse de que sea texto ASCII seguro para la base de datos
        try:
            text = text.encode('utf-8', 'ignore').decode('utf-8')
        except:
            text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text
    
    def _scrape_url(self, url):
        """Realiza scraping de una URL específica"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Forzar encoding UTF-8
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remover scripts y estilos
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Buscar contenido relevante sobre la Ley 1715
            content_selectors = [
                'article', 'main', '.content', '.documento', 
                '.normativa', '.ley', '#content', '.text-content'
            ]
            
            content = ''
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    text = self._clean_text(text)
                    if '1715' in text and ('2014' in text or 'renovable' in text.lower()):
                        content += text + '\n\n'
            
            return self._clean_text(content.strip()) if content else None
            
        except Exception as e:
            logger.error(f"Error en scraping de {url}: {str(e)}")
            return None
    
    def _get_default_summary(self):
        """Resumen por defecto de la Ley 1715"""
        return """
La Ley 1715 de 2014 establece el marco regulatorio para promover el desarrollo y 
utilización de las fuentes no convencionales de energía renovable (FNCER) en Colombia. 

Esta ley busca fomentar la inversión en energías limpias como la solar, eólica, 
biomasa e hidráulica de pequeña escala, contribuyendo a la diversificación de 
la matriz energética del país y a la reducción de emisiones de gases de efecto invernadero.

La normativa establece incentivos tributarios, mecanismos de financiación y 
procedimientos administrativos simplificados para facilitar el desarrollo de 
proyectos de energías renovables en Colombia.
        """.strip()
    
    def _get_main_objective(self):
        """Objetivo principal de la Ley 1715"""
        return """
Promover el desarrollo y la utilización de las fuentes no convencionales de 
energía renovable, principalmente aquellas de carácter renovable, además de 
promover la gestión eficiente de la energía, que comprende tanto la eficiencia 
energética como la respuesta de la demanda.
        """.strip()
    
    def _get_benefits_companies(self):
        """Beneficios para empresas"""
        return """
Deducción especial del 50% en el impuesto sobre la renta por inversiones en FNCER y gestión eficiente de la energía.

Depreciación acelerada de activos destinados a la generación de energía a partir de FNCER.

Exención del pago de aranceles para la importación de equipos, elementos, maquinaria y servicios destinados exclusivamente al pre-inversión e inversión de proyectos de FNCER.

Exclusión de IVA para equipos y elementos necesarios para la generación de energía eléctrica con FNCER.

Acceso a líneas de financiamiento preferenciales y condiciones especiales de crédito.

Simplificación de trámites administrativos para el desarrollo de proyectos de energías renovables.

Posibilidad de vender excedentes de energía al Sistema Interconectado Nacional (SIN).

Certificación de beneficios ambientales por reducción de emisiones de CO2.
        """.strip()
    
    def _get_benefits_citizens(self):
        """Beneficios para ciudadanos"""
        return """
Reducción significativa en el costo de la factura de energía eléctrica mediante sistemas de generación distribuida.

Posibilidad de instalar sistemas de generación de pequeña escala en viviendas y pequeños negocios.

Acceso a tecnologías limpias y sostenibles para el hogar y la comunidad.

Contribución directa a la protección del medio ambiente y reducción de la huella de carbono.

Generación de empleo local en el sector de energías renovables y tecnologías verdes.

Mayor confiabilidad y calidad en el suministro eléctrico, especialmente en zonas rurales.

Incentivos económicos para comunidades que adopten tecnologías de energías renovables.

Mejoramiento de la calidad de vida a través del acceso a energía limpia y sostenible.
        """.strip()
    
    def _get_fallback_content(self):
        """Contenido de respaldo cuando no se puede hacer scraping"""
        content = """
INFORMACION OFICIAL DE LA LEY 1715 DE 2014

Esta informacion se basa exclusivamente en la fuente oficial del Gobierno de Colombia
(Portal de Funcion Publica - Gestor Normativo).

FUENTE OFICIAL:
https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353

Busqueda avanzada de normas en el mismo dominio:
https://www.funcionpublica.gov.co/eva/gestornormativo/consulta_avanzada.php

Para consultar el texto completo y actualizaciones oficiales, visite la URL oficial indicada.
        """.strip()
        
        return self._clean_text(content)

    def _get_summary_ley_2099(self):
        """Resumen específico para la Ley 2099 de 2021 (transición energética)."""
        return """
OBJETO DE LA LEY
Modernizar la legislación energética para:
- Impulsar la transición energética.
- Dinamizar el mercado eléctrico y de gas con fuentes no convencionales de energía (FNCE).
- Promover la reactivación económica del país.
- Fortalecer la prestación de los servicios públicos de energía y gas.

PRINCIPALES MODIFICACIONES A LA LEY 1715 DE 2014
- Ampliación del objeto: incluye almacenamiento de energía, eficiencia energética y medición inteligente.
- Declaratoria de utilidad pública: los proyectos de FNCE se consideran de interés social y conveniencia nacional.
- Hidrógeno verde y azul: se definen como nuevas fuentes dentro de la matriz energética.
- Fondo FENOGE: fortalecido para financiar proyectos de FNCE, eficiencia energética y microrredes.
- Incentivos tributarios y arancelarios:
  * Deducción en renta (50% de la inversión, hasta 15 años).
  * Exclusión de IVA y exención arancelaria.
  * Depreciación acelerada de activos.
  * Vigencia de beneficios: 30 años desde 2021.
- Autogeneración y ventas: se permite a empresas de petróleo y gas vender excedentes.
- Impulso a la energía geotérmica: regulada, con registro obligatorio y sanciones por incumplimiento.

NUEVAS FUENTES Y TECNOLOGIAS
- Hidrógeno verde y azul: con incentivos fiscales y acceso a recursos del FENOGE.
- CCUS (captura, uso y almacenamiento de carbono): incentivos tributarios y obligación de registro de proyectos.
- Energéticos alternativos: incentivos a combustibles de origen orgánico o renovable.
- Movilidad eléctrica: beneficios fiscales y eliminación de algunas contribuciones.
- Producción limpia: creación de un sello para empresas que usen energías renovables.

ZONAS NO INTERCONECTADAS (ZNI)
- Subsidios garantizados para usuarios y prestadores que migren al SIN.
- Apoyo a soluciones solares, híbridas y proyectos de microrredes.
- Posibilidad de transferir activos de energía y gas a entidades territoriales.
- Creación del Centro Nacional de Monitoreo (CNM) para seguimiento de generación y distribución.

NUEVOS FONDOS
- FENOGE: ampliado, financia proyectos de FNCE y eficiencia energética.
- FONENERGIA: sustituye fondos anteriores (PRONE, FAER, FAZNI, FECFGN) y financia expansión de cobertura, normalización de redes y energías limpias.

FOMENTO DE PROYECTOS Y REACTIVACION ECONOMICA
- Simplificación de trámites y licenciamiento ambiental.
- Declaratoria de proyectos PINES para acelerar ejecución.
- Inclusión de proyectos eléctricos dentro de la Ley de Infraestructura (1682 de 2013).
- Impulso a la coexistencia de proyectos minero-energéticos.

INSTITUCIONALIDAD Y REGULACION
- CREG: reorganizada como unidad especial del Ministerio de Minas y Energía, con expertos de dedicación exclusiva.
- IPSE: podrá estructurar proyectos con fondos públicos en ZNI y SIN.
- UPME: competente para certificar proyectos y expedir listados de bienes y servicios con beneficios tributarios.

OTROS ASPECTOS
- Formación para el empleo en sectores de energías limpias (SENA, MinTrabajo, MinEducación).
- Subsidios focalizados según información socioeconómica (algunos artículos fueron derogados por la Ley 2294 de 2023).
- Obligación de medidores inteligentes: costo asumido por las empresas, no por el usuario.
- Cumplimiento internacional: balance de emisiones cero para hidrógeno y CCUS, en línea con el Acuerdo de París.

CONCLUSION
La Ley 2099 de 2021 fortalece la transición energética en Colombia mediante:
- Ampliación de incentivos tributarios y financieros.
- Regulación de nuevas tecnologías (hidrógeno, CCUS, geotermia).
- Mayor apoyo a zonas no interconectadas.
- Creación de fondos unificados (FENOGE, FONENERGIA).
- Reorganización institucional para dar agilidad y control al sector energético.
        """.strip()


def _sanitize_scraped_content(instance, raw_content):
    """Sanitiza contenido HTML obtenido por scraping usando la configuración del modelo."""
    raw_content = raw_content or ''
    try:
        sanitized_html = instance.clean_content(raw_content)
    except Exception:
        sanitized_html = raw_content

    try:
        return sanitized_html.encode('ascii', 'ignore').decode('ascii')
    except Exception:
        import re as _re
        return _re.sub(r'[^\x00-\x7F<>/="\-\w\s]+', ' ', sanitized_html)


def update_legal_framework_entry(
    document_type,
    document_number,
    year,
    *,
    official_url=None,
    defaults=None,
    allow_create=False,
    override_defaults=False,
    scraped_data=None,
):
    """Actualiza un marco legal utilizando la URL oficial registrada.

    Si el registro no existe se requiere que haya sido creado previamente por CRUD, a menos que
    se permita explícitamente su creación mediante `allow_create` y se proporcionen los
    `defaults` obligatorios.
    """
    from apps.regulatory.models import LegalFramework

    defaults = defaults or {}
    lookup = {
        'document_type': document_type,
        'document_number': str(document_number),
        'year': year,
    }

    legal_framework = None
    created = False

    try:
        legal_framework = LegalFramework.objects.get(**lookup)
    except LegalFramework.DoesNotExist:
        if not allow_create:
            raise ValueError(
                'No existe un marco legal con esos datos. Regístralo primero mediante el CRUD antes de actualizar.'
            )

    if legal_framework is None:
        create_payload = {
            'title': defaults.get('title') or f"{document_type.title()} {document_number} de {year}",
            'summary': defaults.get('summary', ''),
            'main_objective': defaults.get('main_objective', ''),
            'benefits_companies': defaults.get('benefits_companies', ''),
            'benefits_citizens': defaults.get('benefits_citizens', ''),
            'official_url': defaults.get('official_url') or official_url,
            'is_active': defaults.get('is_active', True),
        }

        missing_fields = [
            field for field in ('title', 'summary', 'main_objective', 'official_url')
            if not create_payload.get(field)
        ]
        if missing_fields:
            raise ValueError(
                'No se puede crear el marco legal automáticamente; faltan campos requeridos: '
                + ', '.join(missing_fields)
            )

        legal_framework = LegalFramework.objects.create(**lookup, **create_payload)
        created = True

    official_url_to_use = official_url or defaults.get('official_url') or legal_framework.official_url
    if not official_url_to_use:
        raise ValueError('El marco legal no tiene URL oficial configurada; edítalo en el CRUD antes de actualizar.')

    if scraped_data is not None:
        scraped = scraped_data
    else:
        scraper = LegalScrapingService()
        scraped = scraper.scrape_norma_oficial(
            official_url_to_use,
            number=str(lookup['document_number']),
            year=lookup['year']
        )

    safe_content = _sanitize_scraped_content(legal_framework, scraped.get('content_scraped'))

    fields_to_update = {
        'content_scraped': safe_content,
        'last_scraped': timezone.now(),
        'official_url': official_url_to_use,
    }

    if defaults:
        for field in ('title', 'summary', 'main_objective', 'benefits_companies', 'benefits_citizens'):
            new_value = defaults.get(field)
            if not new_value:
                continue
            current_value = getattr(legal_framework, field, '')
            if override_defaults or not current_value:
                fields_to_update[field] = new_value

    for field, value in fields_to_update.items():
        setattr(legal_framework, field, value)

    legal_framework.save(update_fields=list(fields_to_update.keys()))

    action = 'creado' if created else 'actualizado'
    logger.info(
        'Registro de %s %s/%s %s exitosamente',
        legal_framework.get_document_type_display(),
        legal_framework.document_number,
        legal_framework.year,
        action
    )

    return legal_framework, created


def update_ley_1715_data():
    """Función para actualizar la información de la Ley 1715"""
    service = LegalScrapingService()
    scraped = service.scrape_ley_1715_2014()
    scraper_defaults = {
        'title': scraped.get('title') or 'Ley 1715 de 2014 - Promoción de Energías Renovables no Convencionales',
        'summary': scraped.get('summary') or service._get_default_summary(),
        'main_objective': scraped.get('main_objective') or service._get_main_objective(),
        'benefits_companies': scraped.get('benefits_companies') or service._get_benefits_companies(),
        'benefits_citizens': scraped.get('benefits_citizens') or service._get_benefits_citizens(),
        'official_url': scraped.get('official_url') or 'https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=57353',
    }

    return update_legal_framework_entry(
        document_type='ley',
        document_number='1715',
        year=2014,
        defaults=scraper_defaults,
        allow_create=True,
        scraped_data=scraped,
    )


def update_ley_2099_data():
    """Actualiza la información de la Ley 2099 de 2021 desde la URL oficial."""
    scraper = LegalScrapingService()
    scraped = scraper.scrape_norma_oficial(
        'https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=166326',
        number='2099',
        year=2021,
    )
    scraped['summary'] = scraper._get_summary_ley_2099()

    scraper_defaults = {
        'title': scraped.get('title') or 'Ley 2099 de 2021 - Transicion Energetica',
        'summary': scraped.get('summary'),
        'main_objective': scraped.get('main_objective') or scraper._get_main_objective(),
        'benefits_companies': scraped.get('benefits_companies') or scraper._get_benefits_companies(),
        'benefits_citizens': scraped.get('benefits_citizens') or scraper._get_benefits_citizens(),
        'official_url': scraped.get('official_url') or 'https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=166326',
    }

    return update_legal_framework_entry(
        document_type='ley',
        document_number='2099',
        year=2021,
        defaults=scraper_defaults,
        allow_create=True,
        override_defaults=True,
        scraped_data=scraped,
    )
