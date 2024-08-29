import unicodedata
import psycopg2
import requests
import urllib
import os
import re

from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import letter
from decouple import config
from io import BytesIO
from helpers import *
from style import *

def fetch_map(geom, id):
    target_width_px = 1124
    target_height_px = 532
    geom = convert_geom_to_3857(geom)
    wkt = 'MULTIPOLYGON(' + ', '.join('(' + ', '.join('(' + ', '.join('{} {}'.format(x, y) for x, y in poly) + ')'for poly in ring) + ')'for ring in geom) + ')'
    bounds = [min(x for coords in geom for poly in coords for x, y in poly),
            min(y for coords in geom for poly in coords for x, y in poly),
            max(x for coords in geom for poly in coords for x, y in poly),
            max(y for coords in geom for poly in coords for x, y in poly)]
    bbox_width_m = bounds[2] - bounds[0]
    bbox_height_m = bounds[3] - bounds[1]
    scale_width =  bbox_width_m / target_width_px
    scale_height = bbox_height_m / target_height_px
    scale = max(scale_width, scale_height)
    adjusted_bbox_width = (target_width_px * scale) * 1.2
    adjusted_bbox_height = (target_height_px * scale) * 1.2
    center_x = (bounds[0] + bounds[2]) / 2
    center_y = (bounds[1] + bounds[3]) / 2
    new_bounds = [center_x - adjusted_bbox_width / 2,center_y - adjusted_bbox_height / 2,center_x + adjusted_bbox_width / 2,center_y + adjusted_bbox_height / 2]
    qgis_request_url= config('QGIS_REQUEST_URL')
    params = {
        "REQUEST": "GetMap",
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "FORMAT": "image/png",
        "CRS": "EPSG:3857",
        "LAYERS": config('WMS_LAYER'),
        "BBOX": ",".join(map(str, new_bounds)),
        "WIDTH": target_width_px,
        "HEIGHT": target_height_px,
        'HIGHLIGHT_GEOM': wkt,
        'HIGHLIGHT_SYMBOL':'<StyledLayerDescriptor><UserStyle><Name>Highlight</Name><FeatureTypeStyle><Rule><Name>Symbol</Name><LineSymbolizer><Stroke><SvgParameter name="stroke">#ff0000</SvgParameter><SvgParameter name="stroke-opacity">1</SvgParameter><SvgParameter name="stroke-width">2.0</SvgParameter></Stroke></LineSymbolizer></Rule></FeatureTypeStyle></UserStyle></StyledLayerDescriptor>',    }
    request_url = qgis_request_url + "&" + "&".join([f"{k}={v}" for k, v in params.items()])
    response = requests.get(qgis_request_url, params=params)
    if response.status_code == 200:
        return response.content
    else:
        return f"Error: {response.status_code}, {response.text}"

def create_pdf(parcelle, proprios, locaux):
    map_data = fetch_map(parcelle['geometry']['coordinates'], parcelle['properties']['dnupla'])
    title_paragraph = Paragraph(f"Relevé Parcellaire - Parcelle {parcelle['id']}", title_style)
    title_table_data = [[title_paragraph]]
    title_table = Table(title_table_data, colWidths=[562])
    title_table.setStyle(title_table_style)
    title_global = Paragraph("Information parcelle", title_style)
    img = Image(BytesIO(map_data), width= 562, height= 266)
    image_table_data = [[img]]
    image_table = Table(image_table_data, colWidths=[562])
    image_table.setStyle(image_table_style)
    parcelle_table_data = [
        ['Parcelle', parcelle["id"]],
        ['Code', (parcelle["properties"]["ccosec"] + parcelle["properties"]["dnupla"])],
        ['Commune', parcelle["properties"]["ccocom"]],
        ['Code Rivoli', parcelle["properties"]["ccoriv"]],
        ['Date de l\'acte', parcelle["properties"]["jdatat"]],
        ['Contenance', str(parcelle["properties"]["dcntpa"]) + " m\u00B2"],
        ['Adresse', " ".join(filter(None, [parcelle["properties"].get("dnuvoi"),parcelle["properties"].get("dindic"),parcelle["properties"].get("cconvo"),parcelle["properties"].get("dvoilib")])).title()],
        ['Urbaine', 'Oui' if parcelle["properties"]["gurbpa"].lower() == 'u' else 'Non'],
    ]
    parcelle_table = Table(parcelle_table_data, colWidths=[281 , 281])
    parcelle_table.setStyle(style)
    content = [title_table, Spacer(1, 20), title_global, Spacer(1, 5), image_table, Spacer(1, 20), parcelle_table]
    title_prop = Paragraph("Information propriétaire", title_style)
    proprietaires_table_data = [['Code', 'Type', 'Propriétaire', 'Adresse', 'Date de naissance', 'Né.e']]
    for prop in proprios:
        nomprop = (
            f"{(prop.get('dqualp') or '').strip().capitalize() + ('. ' if (prop.get('dqualp') or '').strip() else '')}"
            f"{(prop.get('dnomus') or '').strip()} "
            f"{((prop.get('ddenom') or '').split('/')[-1].strip())}"
        ).strip().capitalize()
        adrprop = (
            f"{(prop.get('dlign3') or '').strip()}"
            f"{re.sub(r'([^\\\\p{Print}])(RUE)', r'\\1 \\2', re.sub(r'(PARC|QUAI)([^\\\\p{Print}])', r'\\1 \\2', (prop.get('dlign4') or '').strip('0')))}"
            f"{(prop.get('dlign5') or '').strip()} { (prop.get('dlign6') or '').strip()}"
        ).strip().capitalize()
        nomnss = (
            f"{(prop.get('dqualp') or '').strip().capitalize() + ('. ' if (prop.get('dqualp') or '').strip() else '')}"
            f"{(prop.get('dnomlp') or '').strip()} "
            f"{((prop.get('ddenom') or '').split('/')[-1].strip())}"
            if (prop.get('dnomus') or '').strip() != (prop.get('dnomlp') or '').strip() else ''
        ).strip().capitalize()
        proprietaires_table_data.append([P(prop["dnuper"]), P(prop["ccodro"]), P(nomprop), P(adrprop.title()), P("Le " + prop["jdatnss"] or+ " à " + prop["dldnss"] ) if prop["jdatnss"] else '', P(nomnss)])
    proprietaires_table = Table(proprietaires_table_data, colWidths=[62, 90, 90, 130, 100, 90], repeatRows=1)
    proprietaires_table.setStyle(style)
    if len(proprios) < 3:
        content.extend([Spacer(1, 20), title_prop, Spacer(1, 5), proprietaires_table, PageBreak()])
    else:
        content.extend([Spacer(1, 20), title_prop, Spacer(1, 5), proprietaires_table, Spacer(1, 20)])
    title_detail_local = Paragraph("Détail Bâti", title_style)
    local_detail_table_data = [['Invariant', 'Porte', 'Rivoli', 'Bat-Ent-Niv.', 'Adresse', 'Nature', 'Evalutation', 'TXOM']]
    for local in locaux:
        numeroinvar = (f"{(local.get('invar') or '')[3:] + ' ' + (local.get('cleinvar') or '')}").strip()
        ndevoirie = (f"{str(local.get('dnvoiri') or '').lstrip('0')}{str(local.get('dindic') or '')}").strip()
        local_detail_table_data.append([numeroinvar, local["dpor"], local["ccoriv"], local["dnubat"]+'-'+local["descc"]+'-'+ local["dniv"], P(ndevoirie + ' ' + local["dvoilib"].title()), local["cconlc"], local["ccoeva"], local["gtauom"]])
    local_detail_table = Table(local_detail_table_data, colWidths=[90, 50, 60, 70, 112, 50, 70, 50], repeatRows=1)
    local_detail_table.setStyle(style)
    content.extend([title_detail_local, Spacer(1, 5), local_detail_table])
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    doc.build(content)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
