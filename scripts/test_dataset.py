"""
test_dataset.py
================
Suite de tests para validar la integridad del dataset final de
Desigualdad Urbana en Barrios de Córdoba.

Qué valida:
  1. Estructura (columnas y tipos esperados en v5)
  2. Filas (494 barrios exactos, sin duplicados)
  3. Rango pct_nbi (0–100)
  4. Cobertura de escuelas (≥50 barrios con escuelas_total > 0)
  5. Consistencia entre columnas de escuelas
  6. Sin valores negativos en columnas numéricas
  7. Retrocompatibilidad con v4 (columnas y valores clave iguales)
  8. Integridad del archivo de escuelas raw (coordenadas, sectores)
  9. Integridad del archivo de escuelas procesadas (barrios asignados)

Uso:
  python -m pytest scripts/test_dataset.py -v
  # o directamente:
  python scripts/test_dataset.py

Autor  : Eber Coronel — DiploDatos 2026 / FAMAF-UNC
Versión: 1.0 — 2026-03-14
"""

import os
import sys
import unittest
import pandas as pd

# Rutas relativas al directorio raíz del proyecto
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4_PATH     = os.path.join(BASE_DIR, "data", "processed", "dataset_final_v4.csv")
V5_PATH     = os.path.join(BASE_DIR, "data", "processed", "dataset_final_v5.csv")
V6_PATH     = os.path.join(BASE_DIR, "data", "processed", "dataset_final_v6.csv")
ESC_RAW     = os.path.join(BASE_DIR, "data", "raw",       "escuelas_cordoba.csv")
ESC_PROC    = os.path.join(BASE_DIR, "data", "processed", "escuelas_idecor_limpio.csv")
CENTR_PATH  = os.path.join(BASE_DIR, "data", "processed", "centroides_barrios_completo.csv")

# Columnas obligatorias en v6 (retrocompatible con v5)
COLS_V4 = [
    "barrio", "poblacion", "hogares", "nbi", "pct_nbi",
    "escuelas_municipales", "centros_salud", "paradas_colectivo",
    "lineas_colectivo", "luminarias_reportes", "comisarias", "centros_vecinales",
]
COLS_NUEVAS = ["escuelas_total", "escuelas_estatales", "escuelas_privadas"]
COLS_V5 = COLS_V4 + COLS_NUEVAS
COLS_V6 = COLS_V5  # mismas columnas, mejores valores por cobertura

# Umbrales de cobertura MEJORADOS gracias a los 560 centroides del CSV censal
# v5 usaba 91 centroides → v6 usa 560 → cobertura mucho mayor
MIN_BARRIOS_TOTAL    = 100   # v5 tenía ~90
MIN_BARRIOS_ESTATALES = 80   # v5 tenía ~80
MIN_BARRIOS_PRIVADAS  = 50   # v5 tenía ~58

# Columnas numéricas que no deben ser negativas
COLS_NUMERICAS = [
    "poblacion", "hogares", "nbi", "pct_nbi",
    "escuelas_municipales", "escuelas_total", "escuelas_estatales",
    "escuelas_privadas", "centros_salud", "paradas_colectivo",
    "lineas_colectivo", "luminarias_reportes", "comisarias", "centros_vecinales",
]


class TestDatasetV5(unittest.TestCase):
    """Tests sobre el dataset_final_v6.csv (v6 = versión actual)."""

    @classmethod
    def setUpClass(cls):
        """Carga los datasets una sola vez para todos los tests."""
        # Apunta a v6 (versión actual con 560 centroides)
        path = V6_PATH if os.path.exists(V6_PATH) else V5_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No se encontró {V6_PATH}\n"
                "Ejecutá primero: python scripts/regenerar_dataset_v6.py"
            )
        cls.df    = pd.read_csv(path)
        cls.df_v4 = pd.read_csv(V4_PATH) if os.path.exists(V4_PATH) else None

    # ── 1. Estructura ─────────────────────────────────────────
    def test_01_columnas_presentes(self):
        """Todas las columnas esperadas deben existir en v6."""
        for col in COLS_V6:
            self.assertIn(col, self.df.columns,
                          f"Falta la columna requerida: '{col}'")

    def test_02_tipos_numericos(self):
        """Columnas numéricas clave deben ser int o float, no object."""
        cols_check = ["poblacion", "hogares", "nbi", "pct_nbi",
                      "escuelas_total", "escuelas_estatales", "escuelas_privadas"]
        for col in cols_check:
            if col in self.df.columns:
                dtype = self.df[col].dtype
                self.assertIn(dtype.kind, ("i", "f", "u"),
                              f"La columna '{col}' tiene tipo {dtype} (esperado numérico)")

    # ── 2. Filas y unicidad ───────────────────────────────────
    def test_03_cantidad_barrios(self):
        """Verificar que haya exactamente 495 barrios (cobertura total ciudad)"""
        self.assertEqual(len(self.df), 495, f"Se esperaban 495 barrios, hay {len(self.df)}")

    def test_04_barrios_sin_duplicados(self):
        """No debe haber barrios duplicados."""
        dup = self.df["barrio"].duplicated()
        n_dup = dup.sum()
        self.assertEqual(n_dup, 0,
                         f"Hay {n_dup} barrios duplicados: {list(self.df[dup]['barrio'])}")

    def test_05_sin_barrio_sin_nombre(self):
        """Ninguna fila debe tener barrio vacío o NaN."""
        nulos = self.df["barrio"].isna() | (self.df["barrio"].str.strip() == "")
        n_nulos = nulos.sum()
        self.assertEqual(n_nulos, 0, f"Hay {n_nulos} barrios sin nombre")

    # ── 3. Rangos ─────────────────────────────────────────────
    def test_06_pct_nbi_rango(self):
        """pct_nbi debe estar entre 0 y 100 (ignorando NaN)."""
        col = self.df["pct_nbi"].dropna()
        fuera = col[(col < 0) | (col > 100)]
        self.assertEqual(len(fuera), 0,
                         f"{len(fuera)} valores de pct_nbi fuera del rango [0,100]: {list(fuera)}")

    def test_07_sin_valores_negativos(self):
        """Ninguna columna numérica debe tener valores negativos."""
        for col in COLS_NUMERICAS:
            if col in self.df.columns:
                negativos = self.df[col].dropna()
                negativos = negativos[negativos < 0]
                self.assertEqual(len(negativos), 0,
                                 f"Columna '{col}' tiene {len(negativos)} valores negativos")

    # ── 4. Cobertura de escuelas ──────────────────────────────
    def test_08_cobertura_escuelas_total(self):
        """Al menos 100 barrios deben tener escuelas_total > 0 (v6 usa 560 centroides)."""
        n = (self.df["escuelas_total"] > 0).sum()
        self.assertGreaterEqual(n, MIN_BARRIOS_TOTAL,
                                f"Solo {n} barrios tienen escuelas_total > 0 (mínimo esperado: {MIN_BARRIOS_TOTAL})")

    def test_09_cobertura_escuelas_estatales(self):
        """Al menos 80 barrios deben tener escuelas_estatales > 0."""
        n = (self.df["escuelas_estatales"] > 0).sum()
        self.assertGreaterEqual(n, MIN_BARRIOS_ESTATALES,
                                f"Solo {n} barrios tienen escuelas_estatales > 0")

    # ── 5. Consistencia entre columnas ────────────────────────
    def test_10_estatales_leq_total(self):
        """escuelas_estatales no puede superar escuelas_total."""
        invalidos = self.df[self.df["escuelas_estatales"] > self.df["escuelas_total"]]
        self.assertEqual(len(invalidos), 0,
                         f"{len(invalidos)} barrios tienen más estatales que total")

    def test_11_privadas_leq_total(self):
        """escuelas_privadas no puede superar escuelas_total."""
        invalidos = self.df[self.df["escuelas_privadas"] > self.df["escuelas_total"]]
        self.assertEqual(len(invalidos), 0,
                         f"{len(invalidos)} barrios tienen más privadas que total")

    def test_12_suma_leq_total(self):
        """escuelas_estatales + escuelas_privadas ≤ escuelas_total."""
        suma = self.df["escuelas_estatales"] + self.df["escuelas_privadas"]
        invalidos = self.df[suma > self.df["escuelas_total"]]
        self.assertEqual(len(invalidos), 0,
                         f"{len(invalidos)} barrios: estatales + privadas > total")

    # ── 6. Retrocompatibilidad con v4 ─────────────────────────
    def test_13_retrocompat_columnas_v4(self):
        """Todas las columnas de v4 deben seguir presentes en v6."""
        if self.df_v4 is None:
            self.skipTest("dataset_final_v4.csv no encontrado, skip retrocompat")
        for col in self.df_v4.columns:
            self.assertIn(col, self.df.columns,
                          f"Columna '{col}' de v4 perdida en v6")

    def test_14_retrocompat_escuelas_municipales(self):
        """escuelas_municipales debe tener exactamente los mismos valores que en v4."""
        if self.df_v4 is None:
            self.skipTest("dataset_final_v4.csv no encontrado")
        merged = self.df[["barrio", "escuelas_municipales"]].merge(
            self.df_v4[["barrio", "escuelas_municipales"]],
            on="barrio", suffixes=("_v6", "_v4")
        )
        diferencias = merged[
            merged["escuelas_municipales_v6"] != merged["escuelas_municipales_v4"]
        ]
        self.assertEqual(len(diferencias), 0,
                         f"{len(diferencias)} barrios cambiaron escuelas_municipales:\n{diferencias}")


class TestCentroides(unittest.TestCase):
    """Tests sobre el archivo de centroides de barrios."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(CENTR_PATH):
            raise FileNotFoundError(f"No se encontró {CENTR_PATH}")
        cls.df = pd.read_csv(CENTR_PATH)

    def test_01_columnas(self):
        """El archivo debe tener barrio, centroide_lat y centroide_lon."""
        for col in ["barrio", "centroide_lat", "centroide_lon"]:
            self.assertIn(col, self.df.columns)

    def test_02_cantidad(self):
        """Debe haber al menos 400 centroides (supera los 91 anteriores)."""
        self.assertGreaterEqual(len(self.df), 400,
                                f"Solo {len(self.df)} centroides (mínimo: 400)")

    def test_03_coords_validas(self):
        """Las coordenadas deben estar en el rango de Córdoba."""
        lat_ok = self.df["centroide_lat"].between(-32.0, -31.0)
        lon_ok = self.df["centroide_lon"].between(-65.0, -64.0)
        n_inv  = (~lat_ok | ~lon_ok).sum()
        self.assertLessEqual(n_inv, len(self.df) * 0.05,  # <= 5% fuera del bbox
                             f"{n_inv} centroides fuera del bbox de Córdoba")


class TestEscuelasRaw(unittest.TestCase):
    """Tests sobre el archivo crudo descargado del WFS."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(ESC_RAW):
            raise FileNotFoundError(f"No se encontró {ESC_RAW}")
        cls.df = pd.read_csv(ESC_RAW)

    def test_01_columnas_basicas(self):
        """El archivo raw debe tener columnas clave."""
        for col in ["nombre", "lat", "lon", "est_sector"]:
            self.assertIn(col, self.df.columns, f"Falta columna '{col}' en escuelas raw")

    def test_02_cantidad_minima(self):
        """Debe haber al menos 5,000 establecimientos en el raw."""
        self.assertGreaterEqual(len(self.df), 5000,
                                f"Solo {len(self.df)} registros en el raw (mínimo esperado: 5000)")

    def test_03_coordenadas_validas(self):
        """Las coordenadas deben estar en el rango de Argentina."""
        lat_validas = self.df["lat"].dropna()
        lon_validas = self.df["lon"].dropna()
        self.assertTrue(all(lat_validas.between(-55, -22)),
                        "Hay latitudes fuera del rango de Argentina")
        self.assertTrue(all(lon_validas.between(-74, -53)),
                        "Hay longitudes fuera del rango de Argentina")

    def test_04_sectores_conocidos(self):
        """Los sectores deben ser 'Estatal' o 'Privado' (o NaN)."""
        sectores_validos = {"Estatal", "Privado"}
        sectores_unicos  = set(self.df["est_sector"].dropna().unique())
        desconocidos     = sectores_unicos - sectores_validos
        self.assertEqual(len(desconocidos), 0,
                         f"Sectores no reconocidos: {desconocidos}")

    def test_05_sin_nombres_vacios(self):
        """El campo 'nombre' no debe tener valores vacíos."""
        vacios = self.df["nombre"].isna() | (self.df["nombre"].str.strip() == "")
        n = vacios.sum()
        self.assertLess(n, len(self.df) * 0.01,  # menos del 1% vacíos
                        f"{n} establecimientos sin nombre ({n/len(self.df)*100:.1f}%)")


class TestEscuelasProcesadas(unittest.TestCase):
    """Tests sobre el archivo de escuelas procesadas (post-integración)."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(ESC_PROC):
            raise FileNotFoundError(
                f"No se encontró {ESC_PROC}\n"
                "Ejecutá primero: python scripts/integrar_escuelas_idecor.py"
            )
        cls.df = pd.read_csv(ESC_PROC)

    def test_01_columna_barrio_asignado(self):
        """El archivo procesado debe tener la columna barrio_asignado."""
        self.assertIn("barrio_asignado", self.df.columns)

    def test_02_tasa_asignacion(self):
        """Al menos el 80% de las escuelas debe tener un barrio asignado."""
        asignados = (self.df["barrio_asignado"].notna() &
                     (self.df["barrio_asignado"].str.strip() != ""))
        tasa = asignados.mean()
        self.assertGreaterEqual(tasa, 0.80,
                                f"Solo {tasa*100:.1f}% de escuelas tienen barrio asignado (mínimo: 80%)")

    def test_03_escuelas_en_ciudad(self):
        """Todas las escuelas procesadas deben estar en la ciudad de Córdoba."""
        self.assertGreater(len(self.df), 0)
        lat_ok = self.df["lat"].between(-31.55, -31.20)
        lon_ok = self.df["lon"].between(-64.35, -64.00)
        fuera  = (~lat_ok | ~lon_ok).sum()
        self.assertEqual(fuera, 0,
                         f"{fuera} escuelas fuera del bbox de la ciudad de Córdoba")


# ─────────────────────────────────────────────────────────────
# Ejecución directa (sin pytest)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.chdir(BASE_DIR)
    print("=" * 65)
    print("TESTS — Dataset Desigualdad Urbana Córdoba v6")
    print("=" * 65)
    loader  = unittest.TestLoader()
    suites  = [
        loader.loadTestsFromTestCase(TestDatasetV5),
        loader.loadTestsFromTestCase(TestCentroides),
        loader.loadTestsFromTestCase(TestEscuelasRaw),
        loader.loadTestsFromTestCase(TestEscuelasProcesadas),
    ]
    suite  = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
