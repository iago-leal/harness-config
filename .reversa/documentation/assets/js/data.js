// data.js - Fonte unica de dados para as paginas do Reversa Docs
window.RV_DATA = {
  modules: [
  {
    "name": "bootstrap",
    "folder": "harness-core/src/core",
    "loc": 58,
    "complexity": 3,
    "type": "code"
  },
  {
    "name": "formatting",
    "folder": "harness-core/src/core",
    "loc": 94,
    "complexity": 6,
    "type": "code"
  },
  {
    "name": "sync",
    "folder": "harness-core/src/core",
    "loc": 70,
    "complexity": 6,
    "type": "code"
  },
  {
    "name": "decisions",
    "folder": "harness-core/src/core",
    "loc": 148,
    "complexity": 12,
    "type": "code"
  },
  {
    "name": "commands",
    "folder": "harness-core/src/core",
    "loc": 93,
    "complexity": 12,
    "type": "code"
  },
  {
    "name": "documentation",
    "folder": "harness-core/src/core",
    "loc": 114,
    "complexity": 6,
    "type": "code"
  },
  {
    "name": "install",
    "folder": "harness-core/src/core",
    "loc": 143,
    "complexity": 6,
    "type": "code"
  },
  {
    "name": "session",
    "folder": "harness-core/src/core",
    "loc": 193,
    "complexity": 12,
    "type": "code"
  },
  {
    "name": "domain",
    "folder": "harness-core/src/core",
    "loc": 189,
    "complexity": 6,
    "type": "code"
  },
  {
    "name": "ports",
    "folder": "harness-core/src/core",
    "loc": 60,
    "complexity": 3,
    "type": "code"
  },
  {
    "name": "adapters",
    "folder": "harness-core/src",
    "loc": 220,
    "complexity": 12,
    "type": "code"
  }
],
  deps: {
  "nodes": [
    {
      "id": "bootstrap"
    },
    {
      "id": "formatting"
    },
    {
      "id": "sync"
    },
    {
      "id": "decisions"
    },
    {
      "id": "commands"
    },
    {
      "id": "documentation"
    },
    {
      "id": "install"
    },
    {
      "id": "session"
    },
    {
      "id": "domain"
    },
    {
      "id": "ports"
    },
    {
      "id": "adapters"
    }
  ],
  "edges": [
    {
      "from": "bootstrap",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "formatting",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "sync",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "sync",
      "to": "domain",
      "weight": 1
    },
    {
      "from": "decisions",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "decisions",
      "to": "domain",
      "weight": 1
    },
    {
      "from": "commands",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "commands",
      "to": "domain",
      "weight": 1
    },
    {
      "from": "commands",
      "to": "session",
      "weight": 1
    },
    {
      "from": "documentation",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "install",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "session",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "session",
      "to": "domain",
      "weight": 1
    },
    {
      "from": "domain",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "adapters",
      "to": "ports",
      "weight": 1
    },
    {
      "from": "adapters",
      "to": "domain",
      "weight": 1
    },
    {
      "from": "adapters",
      "to": "bootstrap",
      "weight": 1
    },
    {
      "from": "adapters",
      "to": "commands",
      "weight": 1
    }
  ],
  "cycles": []
},
  metrics: {
  "schemaVersion": 1,
  "generatedAt": "2026-06-24T13:34:31.810307Z",
  "treemap_loc_by_folder": [
    {
      "folder": "harness-core/src/core",
      "loc": 1162,
      "modules": 10
    },
    {
      "folder": "harness-core/src",
      "loc": 220,
      "modules": 1
    }
  ],
  "top_complexity": [
    {
      "id": "decisions",
      "complexity": 12,
      "loc": 148
    },
    {
      "id": "commands",
      "complexity": 12,
      "loc": 93
    },
    {
      "id": "session",
      "complexity": 12,
      "loc": 193
    },
    {
      "id": "adapters",
      "complexity": 12,
      "loc": 220
    },
    {
      "id": "formatting",
      "complexity": 6,
      "loc": 94
    },
    {
      "id": "sync",
      "complexity": 6,
      "loc": 70
    },
    {
      "id": "documentation",
      "complexity": 6,
      "loc": 114
    },
    {
      "id": "install",
      "complexity": 6,
      "loc": 143
    },
    {
      "id": "domain",
      "complexity": 6,
      "loc": 189
    },
    {
      "id": "bootstrap",
      "complexity": 3,
      "loc": 58
    },
    {
      "id": "ports",
      "complexity": 3,
      "loc": 60
    }
  ],
  "loc_histogram": {
    "bins": [
      0,
      50,
      100,
      200,
      500,
      1000
    ],
    "counts": [
      0,
      5,
      5,
      1,
      0
    ]
  },
  "dependency_sankey": {
    "nodes": [
      {
        "id": "sync"
      },
      {
        "id": "install"
      },
      {
        "id": "session"
      },
      {
        "id": "formatting"
      },
      {
        "id": "documentation"
      },
      {
        "id": "adapters"
      },
      {
        "id": "domain"
      },
      {
        "id": "commands"
      },
      {
        "id": "ports"
      },
      {
        "id": "decisions"
      },
      {
        "id": "bootstrap"
      }
    ],
    "links": [
      {
        "source": "bootstrap",
        "target": "ports",
        "value": 1
      },
      {
        "source": "formatting",
        "target": "ports",
        "value": 1
      },
      {
        "source": "sync",
        "target": "ports",
        "value": 1
      },
      {
        "source": "sync",
        "target": "domain",
        "value": 1
      },
      {
        "source": "decisions",
        "target": "ports",
        "value": 1
      },
      {
        "source": "decisions",
        "target": "domain",
        "value": 1
      },
      {
        "source": "commands",
        "target": "ports",
        "value": 1
      },
      {
        "source": "commands",
        "target": "domain",
        "value": 1
      },
      {
        "source": "commands",
        "target": "session",
        "value": 1
      },
      {
        "source": "documentation",
        "target": "ports",
        "value": 1
      },
      {
        "source": "install",
        "target": "ports",
        "value": 1
      },
      {
        "source": "session",
        "target": "ports",
        "value": 1
      },
      {
        "source": "session",
        "target": "domain",
        "value": 1
      },
      {
        "source": "domain",
        "target": "ports",
        "value": 1
      },
      {
        "source": "adapters",
        "target": "ports",
        "value": 1
      },
      {
        "source": "adapters",
        "target": "domain",
        "value": 1
      },
      {
        "source": "adapters",
        "target": "bootstrap",
        "value": 1
      },
      {
        "source": "adapters",
        "target": "commands",
        "value": 1
      }
    ]
  },
  "language_distribution": [
    {
      "language": "Python",
      "modules": 11,
      "loc": 1382
    }
  ]
},
  timeline: {},
  glossary: {},
  featuresIndex: {
  "specs": [
    {
      "id": "bootstrap",
      "label": "bootstrap"
    },
    {
      "id": "comandos-customizados",
      "label": "comandos-customizados"
    },
    {
      "id": "documentacao-uso-html",
      "label": "documentacao-uso-html"
    },
    {
      "id": "format-on-edit",
      "label": "format-on-edit"
    },
    {
      "id": "install",
      "label": "install"
    },
    {
      "id": "microdecisoes",
      "label": "microdecisoes"
    },
    {
      "id": "run-harness-core-local",
      "label": "run-harness-core-local"
    },
    {
      "id": "session",
      "label": "session"
    },
    {
      "id": "sync-check",
      "label": "sync-check"
    }
  ]
},
  sealSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="100%" height="100%">
  <defs>
    <linearGradient id="seal-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#10b981" />
    </linearGradient>
  </defs>
  <circle cx="400" cy="400" r="350" fill="none" stroke="url(#seal-grad)" stroke-width="4" stroke-dasharray="10 15" opacity="0.4" />
  <circle cx="400" cy="400" r="300" fill="none" stroke="url(#seal-grad)" stroke-width="2" opacity="0.2" />
  <polygon points="400,220 550,310 550,490 400,580 250,490 250,310" fill="none" stroke="url(#seal-grad)" stroke-width="8" />
  <text x="400" y="415" font-family="system-ui, sans-serif" font-size="42" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="10">REVERSA</text>
  <text x="400" y="465" font-family="system-ui, sans-serif" font-size="20" font-weight="700" fill="#64748b" text-anchor="middle" letter-spacing="5">HARNESS</text>
  <text x="400" y="520" font-family="monospace" font-size="16" fill="#3b82f6" text-anchor="middle">SEED: 49f75646</text>
</svg>`,
  sealMiniSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="100%" height="100%">
  <defs>
    <linearGradient id="mini-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#10b981" />
    </linearGradient>
  </defs>
  <polygon points="32,8 52,20 52,44 32,56 12,44 12,20" fill="none" stroke="url(#mini-grad)" stroke-width="3" />
  <circle cx="32" cy="32" r="6" fill="#ffffff" />
</svg>`,
  seedShort: "49f75646",
  nav: [
  {
    "id": "index",
    "href": "index.html",
    "label": "Vis\u00e3o geral"
  },
  {
    "id": "arquitetura",
    "href": "arquitetura.html",
    "label": "Arquitetura 3D"
  },
  {
    "id": "modulos",
    "href": "modulos.html",
    "label": "M\u00f3dulos"
  },
  {
    "id": "topologia",
    "href": "topologia.html",
    "label": "Topologia"
  },
  {
    "id": "metricas",
    "href": "metricas.html",
    "label": "M\u00e9tricas"
  },
  {
    "id": "feature-bootstrap",
    "href": "features/bootstrap.html",
    "label": "Spec: Bootstrap"
  },
  {
    "id": "feature-comandos-customizados",
    "href": "features/comandos-customizados.html",
    "label": "Spec: Comandos Customizados"
  },
  {
    "id": "feature-documentacao-uso-html",
    "href": "features/documentacao-uso-html.html",
    "label": "Spec: Documentacao Uso Html"
  },
  {
    "id": "feature-format-on-edit",
    "href": "features/format-on-edit.html",
    "label": "Spec: Format On Edit"
  },
  {
    "id": "feature-install",
    "href": "features/install.html",
    "label": "Spec: Install"
  },
  {
    "id": "feature-microdecisoes",
    "href": "features/microdecisoes.html",
    "label": "Spec: Microdecisoes"
  },
  {
    "id": "feature-run-harness-core-local",
    "href": "features/run-harness-core-local.html",
    "label": "Spec: Run Harness Core Local"
  },
  {
    "id": "feature-session",
    "href": "features/session.html",
    "label": "Spec: Session"
  },
  {
    "id": "feature-sync-check",
    "href": "features/sync-check.html",
    "label": "Spec: Sync Check"
  }
],
  config: {
  "readerProfile": "novo_dev",
  "depth": "full",
  "visualStyle": "sober"
}
};
