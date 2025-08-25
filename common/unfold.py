from django.templatetags.static import static

UNFOLD_CONFIG = {
    "SITE_TITLE": "Oppora Marketing",
    "SITE_HEADER": "Oppora Marketing",
    "SITE_SYMBOL": "interests",
    "BORDER_RADIUS": "5px",
    "STYLES": [
        lambda request: static("css/admin.css"),
    ],
    "COLORS": {
        "base": {
            "50": "250 250 250",
            "100": "240 240 240",
            "200": "224 224 224",
            "300": "192 192 192",
            "400": "160 160 160",
            "500": "112 112 112",
            "600": "80 80 80",
            "700": "48 48 48",
            "800": "28 28 28",
            "900": "16 16 16",
            "950": "8 8 8",
        },
        "primary": {
            "50": "236 254 255",
            "100": "207 250 254",
            "200": "165 243 252",
            "300": "103 232 249",
            "400": "34 211 238",
            "500": "6 182 212",
            "600": "8 145 178",
            "700": "14 116 144",
            "800": "21 94 117",
            "900": "22 78 99",
            "950": "8 51 68",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-800)",
            "default-dark": "var(--color-base-200)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-50)",
        },
    },
}
