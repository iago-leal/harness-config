import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

import os
import urllib.request
import urllib.error

# Matriz correspondente a vendor-pins.yaml
vendor_pins = [
    {
        "name": "three",
        "url": "https://unpkg.com/three@0.147.0/build/three.min.js",
        "local": "assets/vendor/three.min.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/three.js/0.147.0/three.min.js"
        ]
    },
    {
        "name": "orbit_controls",
        "url": "https://raw.githubusercontent.com/mrdoob/three.js/r147/examples/js/controls/OrbitControls.js",
        "local": "assets/vendor/OrbitControls.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/gh/mrdoob/three.js@r147/examples/js/controls/OrbitControls.js"
        ]
    },
    {
        "name": "d3",
        "url": "https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js",
        "local": "assets/vendor/d3.v7.min.js",
        "fallbacks": [
            "https://unpkg.com/d3@7.8.5/dist/d3.min.js",
            "https://d3js.org/d3.v7.min.js"
        ]
    },
    {
        "name": "highcharts",
        "url": "https://code.highcharts.com/11.4.8/highcharts.js",
        "local": "assets/vendor/highcharts.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/npm/highcharts@11.4.8/highcharts.js",
            "https://unpkg.com/highcharts@11.4.8/highcharts.js"
        ]
    },
    {
        "name": "highcharts_accessibility",
        "url": "https://code.highcharts.com/11.4.8/modules/accessibility.js",
        "local": "assets/vendor/highcharts-accessibility.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/npm/highcharts@11.4.8/modules/accessibility.js"
        ]
    },
    {
        "name": "highcharts_exporting",
        "url": "https://code.highcharts.com/11.4.8/modules/exporting.js",
        "local": "assets/vendor/highcharts-exporting.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/npm/highcharts@11.4.8/modules/exporting.js"
        ]
    },
    {
        "name": "highcharts_treemap",
        "url": "https://code.highcharts.com/11.4.8/modules/treemap.js",
        "local": "assets/vendor/highcharts-treemap.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/npm/highcharts@11.4.8/modules/treemap.js"
        ]
    },
    {
        "name": "highcharts_sankey",
        "url": "https://code.highcharts.com/11.4.8/modules/sankey.js",
        "local": "assets/vendor/highcharts-sankey.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/npm/highcharts@11.4.8/modules/sankey.js"
        ]
    },
    {
        "name": "highcharts_timeline",
        "url": "https://code.highcharts.com/11.4.8/modules/timeline.js",
        "local": "assets/vendor/highcharts-timeline.js",
        "fallbacks": [
            "https://cdn.jsdelivr.net/npm/highcharts@11.4.8/modules/timeline.js"
        ]
    }
]

doc_dir = "/Users/iagoleal/dev/harness/.reversa/documentation"

print("Iniciando download dos arquivos do vendor bundle...")
cdn_fallback_used = False
cdn_fallback_details = []
vendor_missing = []

for item in vendor_pins:
    dest_path = os.path.join(doc_dir, item["local"])
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Se já existe, não precisamos baixar de novo
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        print(f"Arquivo já existe: {item['local']}")
        continue

    urls_to_try = [item["url"]] + item["fallbacks"]
    success = False
    
    for idx, url in enumerate(urls_to_try):
        try:
            print(f"Tentando {url}...")
            # HEAD request para checar status
            req = urllib.request.Request(url, method="HEAD")
            # Adiciona User-Agent básico para evitar bloqueios
            req.add_header("User-Agent", "Mozilla/5.0 ReversaDocs/1.0")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    # Se ok, faz o download
                    # Vamos usar urlretrieve direto
                    # Mas urlretrieve também pode receber headers se usarmos Opener, mas por simplicidade tentaremos direto
                    urllib.request.urlretrieve(url, dest_path)
                    print(f"Salvo em: {dest_path}")
                    success = True
                    if idx > 0:
                        cdn_fallback_used = True
                        cdn_fallback_details.append({
                            "lib": item["name"],
                            "primary": item["url"],
                            "used": url
                        })
                    break
        except Exception as e:
            print(f"Erro ao baixar de {url}: {e}")
            continue
            
    if not success:
        # Se falhou, vamos tentar o download sem HEAD check primeiro
        for idx, url in enumerate(urls_to_try):
            try:
                print(f"Tentando download direto de {url}...")
                urllib.request.urlretrieve(url, dest_path)
                print(f"Salvo em (direto): {dest_path}")
                success = True
                if idx > 0:
                    cdn_fallback_used = True
                    cdn_fallback_details.append({
                        "lib": item["name"],
                        "primary": item["url"],
                        "used": url
                    })
                break
            except Exception as e2:
                print(f"Erro no download direto de {url}: {e2}")
                
    if not success:
        print(f"ERRO: Não foi possível obter {item['name']}.")
        vendor_missing.append(item["name"])

# Atualiza informações no state.json temporário se necessário, ou apenas escrevemos no console
print("Processo de download concluído.")
if vendor_missing:
    print(f"Avisos de vendor ausentes: {vendor_missing}")
