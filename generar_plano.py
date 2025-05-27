# -*- coding: utf-8 -*-
"""
Script paramétrico para generar planos en FreeCAD.
Instrucciones:
1) Coloca este archivo en tu carpeta de proyecto.
2) En FreeCAD (Workbench Part o Draft), abre la Consola Python.
3) Ejecuta:
   import sys
   sys.path.append(r"D:\FORMULARIO - VIVIENDA")
   import generar_plano
   generar_plano.crear_plano(frontis=8, profundidad=10, tipologia='Compacta', dormitorios=3, espacio_productivo=True)
"""
import os
import FreeCAD
import FreeCADGui
import Draft
import Part
from PIL import Image

# --- Configuración de salida ---
BASE = r"D:\FORMULARIO - VIVIENDA"
OUTPUT_DIR = os.path.join(BASE, "planos_generados")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Parámetros de muro ---
MURO_ESPESOR = 400  # mm (40 cm)

# --- Función principal ---
def crear_plano(frontis, profundidad, tipologia, dormitorios, espacio_productivo):
    # Crear documento nuevo
    doc = FreeCAD.newDocument()
    FreeCADGui.ActiveDocument = FreeCADGui.getDocument(doc.Name)
    view = FreeCADGui.ActiveDocument.ActiveView

    # Unidades en mm
    f = frontis * 1000
    p = profundidad * 1000

    # Dibujar muros perimetrales como contornos
    x0, y0 = 0, 0
    Draft.makeRectangle(
        length=f,
        height=p,
        placement=FreeCAD.Placement(FreeCAD.Vector(x0, y0, 0), FreeCAD.Rotation()),
        face=False
    )
    Draft.makeRectangle(
        length=f - 2 * MURO_ESPESOR,
        height=p - 2 * MURO_ESPESOR,
        placement=FreeCAD.Placement(FreeCAD.Vector(MURO_ESPESOR, MURO_ESPESOR, 0), FreeCAD.Rotation()),
        face=False
    )
    doc.recompute()

    # Subdivisión según tipología
    if tipologia == 'Compacta':
        subdividir_compacta(doc, f, p, dormitorios)
    # (En el futuro se implementarán L, U, I)

    # Añadir espacio productivo si aplica
    if espacio_productivo:
        anadir_espacio_productivo(doc, f, p)

    doc.recompute()

    # Ajustar cámara a vista ortográfica cenital y encuadrar todo
    view.viewTop()
    view.setCameraType("Orthographic")
    view.fitAll()

    # Exportar imagen
    base = f"plano_{tipologia}_{int(frontis)}x{int(profundidad)}_{dormitorios}_{'prod' if espacio_productivo else 'no-prod'}"
    img_path = os.path.join(OUTPUT_DIR, base + ".png")
    view.saveImage(img_path, 1600, 1200, 'White')

    # Convertir a PDF
    pdf_path = os.path.join(OUTPUT_DIR, base + ".pdf")
    img = Image.open(img_path)
    img.convert('RGB').save(pdf_path, "PDF")

    return pdf_path, img_path

# --- Funciones auxiliares ---

def subdividir_compacta(doc, f, p, dormitorios):
    """Genera distribución Compacta según tu boceto con dimensiones reales y etiquetas."""
    # Dimensiones reales en mm de tu boceto
    # Frente dividido: 0.4m muro, 3.0m dorm, 0.4m muro, 2.0m sala-comedor, 0.4m muro, 1.5m vestíbulo (suma 7.7m)
    splits_x = [400, 3000, 400, 2000, 400, 1500]
    # Profundidad dividida: 0.4m muro, 1.6m dorm, 0.8m pasillo, 1.6m dorm, 0.4m muro (suma 4.8m)
    splits_y = [400, 1600, 800, 1600, 400]
    # Coordenadas acumuladas
    xs = [0]
    for w in splits_x:
        xs.append(xs[-1] + w)
    ys = [0]
    for h in splits_y:
        ys.append(ys[-1] + h)

    # Dibujar muros interiores según splits
    # Muros verticales
    for x in xs[1:-1]:
        Draft.makeLine(
            FreeCAD.Vector(x, 0, 0),
            FreeCAD.Vector(x, p, 0)
        )
    # Muros horizontales
    for y in ys[1:-1]:
        Draft.makeLine(
            FreeCAD.Vector(0, y, 0),
            FreeCAD.Vector(f, y, 0)
        )

    # Etiquetas de texto
    # Dormitorios (2): ubicados en centro de cada recuadro trasero
    for i in range(2):
        tx = xs[1] + splits_x[1]/2 + i*(splits_x[1] + splits_x[2])
        ty = ys[-1] - splits_y[1]/2
        Draft.makeText(["DORMITORIO"],
            placement=FreeCAD.Placement(
                FreeCAD.Vector(tx-400, ty-200, 0), FreeCAD.Rotation()
            )
        )
    # Sala-Comedor
    tx = xs[3] + splits_x[3]/2
    ty = ys[-2] + splits_y[3]/2
    Draft.makeText(["SALA - COMEDOR"],
        placement=FreeCAD.Placement(
            FreeCAD.Vector(tx-1000, ty-200, 0), FreeCAD.Rotation()
        )
    )
    # Tapon
    tx = xs[4] + splits_x[4]/2
    ty = ys[2] + splits_y[2]/2
    Draft.makeText(["TAPON"],
        placement=FreeCAD.Placement(
            FreeCAD.Vector(tx-400, ty-200, 0), FreeCAD.Rotation()
        )
    )

    doc.recompute()


def anadir_espacio_productivo(doc, f, p):
    size = min(f, p) * 0.2
    x0 = f - size - MURO_ESPESOR
    y0 = p - size - MURO_ESPESOR

    # Dibujar contorno de espacio productivo
    Draft.makeWire([
        FreeCAD.Vector(x0, y0, 0),
        FreeCAD.Vector(x0 + size, y0, 0),
        FreeCAD.Vector(x0 + size, y0 + size, 0),
        FreeCAD.Vector(x0, y0 + size, 0)
    ], closed=True)
    doc.recompute()

