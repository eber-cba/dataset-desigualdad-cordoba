"""
Descarga datos de Establecimientos Educativos desde el WFS de IDECOR (MapasCórdoba)
Sin necesidad de QGIS. Usa requests + geopandas.

URL del mapa: https://mapascordoba.gob.ar/viewer/mapa/77
"""

import json
import os
import sys
import urllib.request
import urllib.parse

# ─────────────────────────────────────────────
# Posibles endpoints del GeoServer de IDECOR
# (descubiertos vía inspección del visor de mapas)
# ─────────────────────────────────────────────
GEOSERVER_URLS = [
    "https://geo.mapascordoba.gob.ar/geoserver/wfs",
    "https://geoserver.mapascordoba.gob.ar/geoserver/wfs",
    "https://mapascordoba.gob.ar/geoserver/wfs",
    "https://idecor-ws.mapascordoba.gob.ar/geoserver/wfs",
    "https://ws.mapascordoba.gob.ar/geoserver/wfs",
]

# Posibles nombres de capa para establecimientos educativos
LAYER_NAMES = [
    "educacion:establecimientos_educativos",
    "establecimientos_educativos",
    "idecor:establecimientos_educativos",
    "educacion:escuelas",
    "Educacion:establecimientos_educativos",
    "idecor:escuelas",
    "public:establecimientos_educativos",
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def probar_endpoint(base_url):
    """Prueba si un endpoint WFS responde con GetCapabilities."""
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetCapabilities",
    }
    url = base_url + "?" + urllib.parse.urlencode(params)
    print(f"  Probando: {base_url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "QGIS/3.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read(5000).decode("utf-8", errors="ignore")
            if "WFS_Capabilities" in content or "FeatureTypeList" in content or "wfs:WFS_Capabilities" in content:
                print(f"  ✓ WFS encontrado en: {base_url}")
                return True
            elif "<?xml" in content or "<html" in content.lower():
                print(f"  ~ Respuesta XML/HTML pero no WFS. Contenido: {content[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def descargar_capa_wfs(base_url, layer_name, output_path):
    """Descarga una capa WFS completa como GeoJSON."""
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": layer_name,
        "outputFormat": "application/json",
        "count": "100000",  # máximo de features
    }
    url = base_url + "?" + urllib.parse.urlencode(params)
    print(f"\n  Descargando capa: {layer_name}")
    print(f"  URL: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "QGIS/3.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        
        # Verificar que es JSON válido con features
        geojson = json.loads(data)
        n_features = len(geojson.get("features", []))
        if n_features > 0:
            with open(output_path, "wb") as f:
                f.write(data)
            print(f"  ✓ Descargados {n_features} registros → {output_path}")
            return n_features
        else:
            print(f"  ✗ Respuesta vacía o sin features: {str(data[:300])}")
            return 0
    except json.JSONDecodeError:
        try:
            text = data.decode("utf-8", errors="ignore")
            print(f"  ✗ Respuesta no es JSON: {text[:400]}")
        except:
            print(f"  ✗ Error decodificando respuesta")
        return 0
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 0


def obtener_capas_disponibles(base_url):
    """Lista todas las capas disponibles en el WFS."""
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetCapabilities",
    }
    url = base_url + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "QGIS/3.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        
        # Extraer nombres de capas del XML
        capas = []
        for line in content.split("\n"):
            if "<Name>" in line and "</" in line:
                nombre = line.split("<Name>")[1].split("</")[0].strip()
                if nombre:
                    capas.append(nombre)
        return capas
    except Exception as e:
        print(f"  Error obteniendo capas: {e}")
        return []


def geojson_a_csv(geojson_path, csv_path):
    """Convierte GeoJSON a CSV con coordenadas lat/lon."""
    try:
        import geopandas as gpd
        gdf = gpd.read_file(geojson_path)
        # Proyectar a WGS84 si es necesario
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
        # Agregar columnas lat/lon
        gdf["lon"] = gdf.geometry.x
        gdf["lat"] = gdf.geometry.y
        df = gdf.drop(columns=["geometry"])
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"  ✓ CSV guardado: {csv_path} ({len(df)} filas, {len(df.columns)} columnas)")
        print(f"  Columnas: {list(df.columns)}")
        return True
    except ImportError:
        print("  geopandas no disponible, guardando solo GeoJSON")
        return False
    except Exception as e:
        print(f"  Error convirtiendo a CSV: {e}")
        return False


def main():
    print("="*60)
    print("DESCARGA DE ESTABLECIMIENTOS EDUCATIVOS - IDECOR")
    print("="*60)
    
    # 1. Buscar endpoint WFS activo
    endpoint_activo = None
    print("\n[1/3] Buscando endpoint WFS de IDECOR...")
    for url in GEOSERVER_URLS:
        if probar_endpoint(url):
            endpoint_activo = url
            break
    
    if not endpoint_activo:
        print("\n  ✗ No se encontró ningún endpoint WFS activo.")
        print("  Intentando descarga directa por URL conocidas del mapa...")
        # Intento de descarga alternativa
        intentar_descarga_alternativa()
        return
    
    # 2. Listar capas disponibles
    print(f"\n[2/3] Listando capas disponibles en {endpoint_activo}...")
    capas = obtener_capas_disponibles(endpoint_activo)
    
    capas_educacion = [c for c in capas if any(
        kw in c.lower() for kw in ["educ", "escuela", "school", "establecimiento", "estab"]
    )]
    
    if capas_educacion:
        print(f"  Capas de educación encontradas: {capas_educacion}")
        layer_a_usar = capas_educacion[0]
    else:
        print(f"  Total capas disponibles: {len(capas)}")
        if capas:
            print(f"  Primeras 20: {capas[:20]}")
        layer_a_usar = LAYER_NAMES[0]
        print(f"  Usando nombre de capa por defecto: {layer_a_usar}")
    
    # 3. Descargar la capa
    print(f"\n[3/3] Descargando datos de escuelas...")
    geojson_out = os.path.join(OUTPUT_DIR, "escuelas_cordoba_wfs.geojson")
    csv_out = os.path.join(OUTPUT_DIR, "escuelas_cordoba.csv")
    
    n = descargar_capa_wfs(endpoint_activo, layer_a_usar, geojson_out)
    
    if n == 0:
        # Probar con otros nombres de capa
        print("\n  Probando nombres de capa alternativos...")
        for layer in LAYER_NAMES[1:]:
            n = descargar_capa_wfs(endpoint_activo, layer, geojson_out)
            if n > 0:
                break
    
    if n > 0:
        print(f"\n  Convirtiendo GeoJSON a CSV...")
        geojson_a_csv(geojson_out, csv_out)
        print(f"\n✓ DATOS GUARDADOS EN:")
        print(f"  GeoJSON: {geojson_out}")
        print(f"  CSV:     {csv_out}")
    else:
        print("\n✗ No se pudieron descargar los datos por WFS.")
        intentar_descarga_alternativa()


def intentar_descarga_alternativa():
    """Intenta descargar usando la API REST del portal de IDECOR."""
    print("\n  Intentando API REST de IDECOR/datos abiertos...")
    
    # URLs alternativas conocidas para datos del gobierno de Córdoba
    apis = [
        # API del visor de mapas (endpoint interno)
        "https://mapascordoba.gob.ar/viewer/api/map/77",
        # Datos abiertos de Córdoba
        "https://datosabiertos.cba.gov.ar/api/3/action/datastore_search?resource_id=escuelas",
    ]
    
    for url in apis:
        print(f"  Probando: {url}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read(10000).decode("utf-8", errors="ignore")
            print(f"  Respuesta ({len(data)} chars): {data[:500]}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n  SUGERENCIA: Ejecuta este script en QGIS Python Console:")
    print("    uri = 'https://geo.mapascordoba.gob.ar/geoserver/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=educacion:establecimientos_educativos&outputFormat=application/json'")
    print("    vlayer = QgsVectorLayer(uri, 'escuelas', 'WFS')")
    print("    QgsProject.instance().addMapLayer(vlayer)")


if __name__ == "__main__":
    main()
