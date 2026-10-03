"""Materials shopping ecosystem — 10 shopping-style categories matching the Infra.market style UI.
Each category has multiple stores, each store has a catalogue of products.
Demo data, Jaipur city.
"""

# High-quality category tile images (product-focused)
IMG_CAT_CEMENT_STEEL = "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=600&q=80"
IMG_CAT_ELECTRICALS = "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=600&q=80"
IMG_CAT_BATHWARE = "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=600&q=80"
IMG_CAT_TILING = "https://images.unsplash.com/photo-1615971677499-5467cbab01c0?w=600&q=80"
IMG_CAT_PAINTS = "https://images.unsplash.com/photo-1562259929-b4e1fd3aef09?w=600&q=80"
IMG_CAT_APPLIANCES = "https://images.unsplash.com/photo-1631472612389-a73f44ba3fe8?w=600&q=80"
IMG_CAT_WATERPROOF = "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=600&q=80"
IMG_CAT_PIPES = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80"
IMG_CAT_HARDWARE = "https://images.unsplash.com/photo-1609205625555-f24e18df1b5b?w=600&q=80"
IMG_CAT_PLYWOOD = "https://images.unsplash.com/photo-1619280143735-f1660eb02326?w=600&q=80"

# Store header image
IMG_STORE_DEFAULT = "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=800&q=80"

# 10 shopping categories (match the screenshot)
MATERIALS_CATEGORIES = [
    {"id": "mat-cement-steel", "name": "Cement & steel",       "image": IMG_CAT_CEMENT_STEEL, "order": 1},
    {"id": "mat-electrical",   "name": "Electricals & lighting","image": IMG_CAT_ELECTRICALS,  "order": 2},
    {"id": "mat-bathware",     "name": "Bathware",              "image": IMG_CAT_BATHWARE,     "order": 3},
    {"id": "mat-tiling",       "name": "Tiling & adhesives",    "image": IMG_CAT_TILING,       "order": 4},
    {"id": "mat-paint",        "name": "Paints & finishes",     "image": IMG_CAT_PAINTS,       "order": 5},
    {"id": "mat-appliances",   "name": "Electrical appliances", "image": IMG_CAT_APPLIANCES,   "order": 6},
    {"id": "mat-waterproof",   "name": "Water proofing",        "image": IMG_CAT_WATERPROOF,   "order": 7},
    {"id": "mat-pipes",        "name": "CPVC, PVC & GI fittings","image": IMG_CAT_PIPES,       "order": 8},
    {"id": "mat-hardware",     "name": "Hardware & locks",      "image": IMG_CAT_HARDWARE,     "order": 9},
    {"id": "mat-plywood",      "name": "Plywood & laminates",   "image": IMG_CAT_PLYWOOD,      "order": 10},
]

# Stores (one supplier can span multiple categories via `category_ids`)
MATERIALS_STORES = [
    # Cement & steel ------------------------------------------------------
    {"id": "mst-balaji", "name": "Shri Balaji Traders", "tagline": "UltraTech, Ambuja, Shree — authorised stockist",
     "category_ids": ["mat-cement-steel"], "area": "Sirsi Road", "city": "Jaipur",
     "rating": 4.6, "reviews": 320, "verified": True, "featured": True,
     "delivery_mins": 90, "min_order": "₹5,000",
     "phone": "+91 98290 88901", "image": IMG_STORE_DEFAULT,
     "about": "20+ years, same-day delivery across Jaipur."},
    {"id": "mst-steelsynd", "name": "Jaipur Steel Syndicate", "tagline": "TATA, JSW, SAIL TMT · Fe500/550",
     "category_ids": ["mat-cement-steel"], "area": "Vishwakarma Industrial", "city": "Jaipur",
     "rating": 4.7, "reviews": 265, "verified": True, "featured": True,
     "delivery_mins": 120, "min_order": "₹10,000",
     "phone": "+91 98290 11123", "image": IMG_STORE_DEFAULT,
     "about": "Authorised distributor of premium TMT brands."},
    {"id": "mst-rajcement", "name": "Rajputana Cement Agency", "tagline": "Builder-rate cement & white cement",
     "category_ids": ["mat-cement-steel"], "area": "Vishwakarma Industrial", "city": "Jaipur",
     "rating": 4.4, "reviews": 178, "verified": True, "featured": False,
     "delivery_mins": 180, "min_order": "₹8,000",
     "phone": "+91 98290 99012", "image": IMG_STORE_DEFAULT,
     "about": "Bulk cement supplier for developers & infrastructure jobs."},

    # Electricals & lighting ---------------------------------------------
    {"id": "mst-voltronics", "name": "Voltronics Wholesale", "tagline": "Polycab, Havells, Schneider, Legrand",
     "category_ids": ["mat-electrical"], "area": "Chandpole Bazaar", "city": "Jaipur",
     "rating": 4.5, "reviews": 189, "verified": True, "featured": True,
     "delivery_mins": 60, "min_order": "₹1,500",
     "phone": "+91 98290 66678", "image": IMG_STORE_DEFAULT,
     "about": "Authorised dealer for premium electrical brands."},
    {"id": "mst-signify", "name": "Signify LED House", "tagline": "Philips LED lighting · residential + commercial",
     "category_ids": ["mat-electrical"], "area": "MI Road", "city": "Jaipur",
     "rating": 4.6, "reviews": 112, "verified": True, "featured": False,
     "delivery_mins": 60, "min_order": "₹500",
     "phone": "+91 98290 60012", "image": IMG_STORE_DEFAULT,
     "about": "Full LED range — panels, downlights, strips & smart lighting."},
    {"id": "mst-havells", "name": "Havells Galaxy", "tagline": "Switches, MCBs, fans & LEDs",
     "category_ids": ["mat-electrical", "mat-appliances"], "area": "Vaishali Nagar", "city": "Jaipur",
     "rating": 4.5, "reviews": 203, "verified": True, "featured": False,
     "delivery_mins": 75, "min_order": "₹1,000",
     "phone": "+91 98290 60998", "image": IMG_STORE_DEFAULT,
     "about": "Flagship Havells showroom with contractor pricing."},

    # Bathware ------------------------------------------------------------
    {"id": "mst-jaquar", "name": "Jaquar World Jaipur", "tagline": "Faucets, showers & sanitaryware",
     "category_ids": ["mat-bathware"], "area": "C-Scheme", "city": "Jaipur",
     "rating": 4.7, "reviews": 148, "verified": True, "featured": True,
     "delivery_mins": 120, "min_order": "₹2,000",
     "phone": "+91 98290 70011", "image": IMG_STORE_DEFAULT,
     "about": "Jaquar brand store — Essco, Artize, Alive ranges."},
    {"id": "mst-cera", "name": "CERA Bath Gallery", "tagline": "Full-range bath solutions",
     "category_ids": ["mat-bathware"], "area": "Malviya Nagar", "city": "Jaipur",
     "rating": 4.5, "reviews": 91, "verified": True, "featured": False,
     "delivery_mins": 150, "min_order": "₹2,000",
     "phone": "+91 98290 70022", "image": IMG_STORE_DEFAULT,
     "about": "WC, basins, showers, faucets — all CERA designs."},
    {"id": "mst-hindware", "name": "Hindware Lounge", "tagline": "Italian-design sanitaryware",
     "category_ids": ["mat-bathware"], "area": "Tonk Road", "city": "Jaipur",
     "rating": 4.4, "reviews": 76, "verified": True, "featured": False,
     "delivery_mins": 150, "min_order": "₹1,500",
     "phone": "+91 98290 70033", "image": IMG_STORE_DEFAULT,
     "about": "Hindware + Moonbow kitchen & bath essentials."},

    # Tiling & adhesives --------------------------------------------------
    {"id": "mst-marblemosaic", "name": "Marble & Mosaic Gallery", "tagline": "Kajaria, Somany, imported marble",
     "category_ids": ["mat-tiling"], "area": "Malviya Nagar", "city": "Jaipur",
     "rating": 4.6, "reviews": 234, "verified": True, "featured": True,
     "delivery_mins": 180, "min_order": "₹5,000",
     "phone": "+91 98290 55567", "image": IMG_STORE_DEFAULT,
     "about": "6000 sq ft showroom · 200+ SKUs top Indian & imported."},
    {"id": "mst-laticrete", "name": "MYK Laticrete Depot", "tagline": "Tile adhesives, grouts & screeds",
     "category_ids": ["mat-tiling", "mat-waterproof"], "area": "Sitapura", "city": "Jaipur",
     "rating": 4.5, "reviews": 98, "verified": True, "featured": False,
     "delivery_mins": 90, "min_order": "₹2,000",
     "phone": "+91 98290 55599", "image": IMG_STORE_DEFAULT,
     "about": "MYK Laticrete authorised stockist."},

    # Paints & finishes ---------------------------------------------------
    {"id": "mst-colourworks", "name": "ColourWorks Studio", "tagline": "Asian Paints · Dulux · Nippon",
     "category_ids": ["mat-paint"], "area": "Raja Park", "city": "Jaipur",
     "rating": 4.5, "reviews": 176, "verified": True, "featured": True,
     "delivery_mins": 60, "min_order": "₹1,000",
     "phone": "+91 98290 88890", "image": IMG_STORE_DEFAULT,
     "about": "Retail + contractor supply with in-shop colour consult."},
    {"id": "mst-asianpaints", "name": "Asian Paints Signature", "tagline": "Royale, Apex, Ace & Woodtech",
     "category_ids": ["mat-paint"], "area": "C-Scheme", "city": "Jaipur",
     "rating": 4.6, "reviews": 142, "verified": True, "featured": False,
     "delivery_mins": 90, "min_order": "₹500",
     "phone": "+91 98290 88877", "image": IMG_STORE_DEFAULT,
     "about": "Flagship Asian Paints store, free painter sourcing."},

    # Electrical appliances ----------------------------------------------
    {"id": "mst-crompton", "name": "Crompton Appliances Centre", "tagline": "Fans, geysers, mixers & pumps",
     "category_ids": ["mat-appliances"], "area": "Mansarovar", "city": "Jaipur",
     "rating": 4.5, "reviews": 134, "verified": True, "featured": True,
     "delivery_mins": 75, "min_order": "₹1,000",
     "phone": "+91 98290 50505", "image": IMG_STORE_DEFAULT,
     "about": "Factory outlet with full after-sales support."},
    {"id": "mst-bajaj", "name": "Bajaj Electricals Hub", "tagline": "Appliances, fans & lighting",
     "category_ids": ["mat-appliances"], "area": "Vaishali Nagar", "city": "Jaipur",
     "rating": 4.3, "reviews": 97, "verified": True, "featured": False,
     "delivery_mins": 90, "min_order": "₹500",
     "phone": "+91 98290 50006", "image": IMG_STORE_DEFAULT,
     "about": "Bajaj & Morphy Richards full range."},

    # Water proofing ------------------------------------------------------
    {"id": "mst-drfixit", "name": "Dr Fixit Experience Centre", "tagline": "Pidilite waterproofing systems",
     "category_ids": ["mat-waterproof"], "area": "Ajmer Road", "city": "Jaipur",
     "rating": 4.6, "reviews": 112, "verified": True, "featured": True,
     "delivery_mins": 90, "min_order": "₹1,500",
     "phone": "+91 98290 41111", "image": IMG_STORE_DEFAULT,
     "about": "Full Dr Fixit range + on-site consultation."},
    {"id": "mst-fosroc", "name": "Fosroc Jaipur Depot", "tagline": "Industrial waterproofing & admixtures",
     "category_ids": ["mat-waterproof"], "area": "Vishwakarma Industrial", "city": "Jaipur",
     "rating": 4.4, "reviews": 48, "verified": True, "featured": False,
     "delivery_mins": 150, "min_order": "₹3,000",
     "phone": "+91 98290 41122", "image": IMG_STORE_DEFAULT,
     "about": "Fosroc authorised distributor for Rajasthan."},

    # CPVC, PVC & GI fittings --------------------------------------------
    {"id": "mst-astral", "name": "Astral Piping Jaipur", "tagline": "CPVC, PVC, SWR & agri pipes",
     "category_ids": ["mat-pipes"], "area": "Tonk Road", "city": "Jaipur",
     "rating": 4.6, "reviews": 167, "verified": True, "featured": True,
     "delivery_mins": 90, "min_order": "₹1,500",
     "phone": "+91 98290 62001", "image": IMG_STORE_DEFAULT,
     "about": "Authorised Astral stockist with contractor rates."},
    {"id": "mst-prince", "name": "Prince Piping Centre", "tagline": "Prince, Supreme & Finolex",
     "category_ids": ["mat-pipes"], "area": "Chandpole", "city": "Jaipur",
     "rating": 4.4, "reviews": 134, "verified": True, "featured": False,
     "delivery_mins": 90, "min_order": "₹1,000",
     "phone": "+91 98290 62002", "image": IMG_STORE_DEFAULT,
     "about": "Multi-brand pipe stockist · GI, CPVC, PPR."},

    # Hardware & locks ----------------------------------------------------
    {"id": "mst-dorset", "name": "Dorset Hardware House", "tagline": "Door hardware, locks & accessories",
     "category_ids": ["mat-hardware"], "area": "MI Road", "city": "Jaipur",
     "rating": 4.5, "reviews": 89, "verified": True, "featured": True,
     "delivery_mins": 90, "min_order": "₹1,000",
     "phone": "+91 98290 33001", "image": IMG_STORE_DEFAULT,
     "about": "Dorset full range · premium architectural hardware."},
    {"id": "mst-hettich", "name": "Hettich Studio Jaipur", "tagline": "Modular fittings & kitchen hardware",
     "category_ids": ["mat-hardware"], "area": "Malviya Nagar", "city": "Jaipur",
     "rating": 4.7, "reviews": 76, "verified": True, "featured": False,
     "delivery_mins": 120, "min_order": "₹2,000",
     "phone": "+91 98290 33002", "image": IMG_STORE_DEFAULT,
     "about": "Hettich global brand — hinges, slides, tandem boxes."},
    {"id": "mst-godrejlock", "name": "Godrej Locks & Security", "tagline": "Door locks, digital locks & safes",
     "category_ids": ["mat-hardware"], "area": "Raja Park", "city": "Jaipur",
     "rating": 4.5, "reviews": 102, "verified": True, "featured": False,
     "delivery_mins": 90, "min_order": "₹500",
     "phone": "+91 98290 33003", "image": IMG_STORE_DEFAULT,
     "about": "Godrej locks + Locks galaxy multi-brand."},

    # Plywood & laminates -------------------------------------------------
    {"id": "mst-greenply", "name": "Greenply Studio", "tagline": "Plywood, laminates & doors",
     "category_ids": ["mat-plywood"], "area": "Sitapura", "city": "Jaipur",
     "rating": 4.6, "reviews": 123, "verified": True, "featured": True,
     "delivery_mins": 150, "min_order": "₹3,000",
     "phone": "+91 98290 70700", "image": IMG_STORE_DEFAULT,
     "about": "Greenply full range · Greenlam laminates partner."},
    {"id": "mst-century", "name": "Century Plyboards Centre", "tagline": "Club Prime, Sainik & Century doors",
     "category_ids": ["mat-plywood"], "area": "Sanganer", "city": "Jaipur",
     "rating": 4.5, "reviews": 89, "verified": True, "featured": False,
     "delivery_mins": 180, "min_order": "₹3,000",
     "phone": "+91 98290 70701", "image": IMG_STORE_DEFAULT,
     "about": "Century Ply authorised dealer."},
    {"id": "mst-merino", "name": "Merino Laminates Gallery", "tagline": "1500+ laminate designs",
     "category_ids": ["mat-plywood"], "area": "C-Scheme", "city": "Jaipur",
     "rating": 4.4, "reviews": 56, "verified": True, "featured": False,
     "delivery_mins": 180, "min_order": "₹2,000",
     "phone": "+91 98290 70702", "image": IMG_STORE_DEFAULT,
     "about": "Merino & Virgo laminate studio."},
]


# Product catalogue — organised by (store_id, category_id)
# Each product: {id, store_id, category_id, name, brand, image, unit, price, mrp, moq}
IMG_PROD_CEMENT_BAG = "https://images.unsplash.com/photo-1590093804797-f92aef6a1381?w=500&q=80"
IMG_PROD_STEEL = "https://images.unsplash.com/photo-1567613113939-5c17f7f4b06e?w=500&q=80"
IMG_PROD_WIRE = "https://images.unsplash.com/photo-1620662736427-b8a198f52a4d?w=500&q=80"
IMG_PROD_SWITCH = "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500&q=80"
IMG_PROD_LED = "https://images.unsplash.com/photo-1550985543-f8db2eb4e6d8?w=500&q=80"
IMG_PROD_FAUCET = "https://images.unsplash.com/photo-1620626011761-996317b8d101?w=500&q=80"
IMG_PROD_SHOWER = "https://images.unsplash.com/photo-1600488992839-ad26576d6181?w=500&q=80"
IMG_PROD_WC = "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=500&q=80"
IMG_PROD_TILE = "https://images.unsplash.com/photo-1615873968403-89e068629265?w=500&q=80"
IMG_PROD_ADHESIVE = "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=500&q=80"
IMG_PROD_PAINT = "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=500&q=80"
IMG_PROD_FAN = "https://images.unsplash.com/photo-1631472612389-a73f44ba3fe8?w=500&q=80"
IMG_PROD_AC = "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500&q=80"
IMG_PROD_GEYSER = "https://images.unsplash.com/photo-1631870010406-c87d4ea2eca7?w=500&q=80"
IMG_PROD_WATERPROOF = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&q=80"
IMG_PROD_PIPE = "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?w=500&q=80"
IMG_PROD_LOCK = "https://images.unsplash.com/photo-1601581875309-fafbf2d3ed3a?w=500&q=80"
IMG_PROD_HINGE = "https://images.unsplash.com/photo-1581094488379-6c8303b71d5c?w=500&q=80"
IMG_PROD_PLY = "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?w=500&q=80"
IMG_PROD_LAMINATE = "https://images.unsplash.com/photo-1618219740975-d40978bb7378?w=500&q=80"


def _p(pid, store, cat, name, brand, image, unit, price, mrp=None, moq=1):
    return {
        "id": pid, "store_id": store, "category_id": cat,
        "name": name, "brand": brand, "image": image,
        "unit": unit, "price": price, "mrp": mrp or int(price * 1.15), "moq": moq,
    }


MATERIALS_PRODUCTS = [
    # --- Cement & steel ---------------------------------------------------
    _p("p-mat-001", "mst-balaji",   "mat-cement-steel", "UltraTech Super Cement",       "UltraTech", IMG_PROD_CEMENT_BAG, "50 kg bag", 385, 420, 10),
    _p("p-mat-002", "mst-balaji",   "mat-cement-steel", "Ambuja Cement PPC",            "Ambuja",    IMG_PROD_CEMENT_BAG, "50 kg bag", 372, 410, 10),
    _p("p-mat-003", "mst-balaji",   "mat-cement-steel", "Shree Jung Rodhak Cement",     "Shree",     IMG_PROD_CEMENT_BAG, "50 kg bag", 378, 415, 10),
    _p("p-mat-004", "mst-balaji",   "mat-cement-steel", "Birla A1 Premium Cement",      "Birla A1",  IMG_PROD_CEMENT_BAG, "50 kg bag", 390, 430, 10),
    _p("p-mat-005", "mst-steelsynd","mat-cement-steel", "TATA Tiscon Fe 500D TMT 8mm",  "TATA",      IMG_PROD_STEEL,      "kg",    62, 70, 100),
    _p("p-mat-006", "mst-steelsynd","mat-cement-steel", "TATA Tiscon Fe 500D TMT 10mm", "TATA",      IMG_PROD_STEEL,      "kg",    61, 68, 100),
    _p("p-mat-007", "mst-steelsynd","mat-cement-steel", "JSW NEOSTEEL Fe 550D 12mm",    "JSW",       IMG_PROD_STEEL,      "kg",    60, 68, 100),
    _p("p-mat-008", "mst-steelsynd","mat-cement-steel", "SAIL TMT Fe 500 16mm",         "SAIL",      IMG_PROD_STEEL,      "kg",    59, 66, 100),
    _p("p-mat-009", "mst-rajcement","mat-cement-steel", "JK Super Cement OPC 53",       "JK Super",  IMG_PROD_CEMENT_BAG, "50 kg bag", 370, 408, 50),
    _p("p-mat-010", "mst-rajcement","mat-cement-steel", "Birla White Wall Care Putty",  "Birla",     IMG_PROD_CEMENT_BAG, "40 kg bag", 1120, 1250, 2),

    # --- Electricals & lighting -----------------------------------------
    _p("p-mat-101", "mst-voltronics","mat-electrical", "Polycab Green Wire 2.5 sq mm",     "Polycab",  IMG_PROD_WIRE,  "90 m coil", 2450, 2800, 1),
    _p("p-mat-102", "mst-voltronics","mat-electrical", "Polycab Green Wire 4 sq mm",       "Polycab",  IMG_PROD_WIRE,  "90 m coil", 3850, 4300, 1),
    _p("p-mat-103", "mst-voltronics","mat-electrical", "Havells Reo 6A Modular Switch",    "Havells",  IMG_PROD_SWITCH,"piece",      75, 95, 1),
    _p("p-mat-104", "mst-voltronics","mat-electrical", "Schneider Livia 16A Socket",       "Schneider",IMG_PROD_SWITCH,"piece",     215, 260, 1),
    _p("p-mat-105", "mst-voltronics","mat-electrical", "Legrand Myrius 20A DP Switch",     "Legrand",  IMG_PROD_SWITCH,"piece",     295, 350, 1),
    _p("p-mat-106", "mst-signify",   "mat-electrical", "Philips LED Panel 15W 6'' Round",  "Philips",  IMG_PROD_LED,   "piece",     385, 450, 1),
    _p("p-mat-107", "mst-signify",   "mat-electrical", "Philips Hue Smart LED Bulb 9W",    "Philips",  IMG_PROD_LED,   "piece",     1299, 1499, 1),
    _p("p-mat-108", "mst-signify",   "mat-electrical", "Philips LED Downlight 7W",         "Philips",  IMG_PROD_LED,   "piece",     215, 260, 1),
    _p("p-mat-109", "mst-havells",   "mat-electrical", "Havells Crabtree Verona Switch 6A","Crabtree", IMG_PROD_SWITCH,"piece",     110, 140, 1),
    _p("p-mat-110", "mst-havells",   "mat-electrical", "Havells LHS DT 25A MCB",           "Havells",  IMG_PROD_SWITCH,"piece",     195, 240, 1),

    # --- Bathware -------------------------------------------------------
    _p("p-mat-201", "mst-jaquar",   "mat-bathware", "Jaquar Fonte Basin Mixer",           "Jaquar",   IMG_PROD_FAUCET, "piece",  7850, 9200, 1),
    _p("p-mat-202", "mst-jaquar",   "mat-bathware", "Jaquar Continental Health Faucet",   "Jaquar",   IMG_PROD_FAUCET, "piece",  1950, 2400, 1),
    _p("p-mat-203", "mst-jaquar",   "mat-bathware", "Jaquar Alive Rain Shower 200mm",     "Jaquar",   IMG_PROD_SHOWER, "piece",  5850, 7200, 1),
    _p("p-mat-204", "mst-jaquar",   "mat-bathware", "Essco Delight Wall Mix Shower",      "Essco",    IMG_PROD_SHOWER, "piece",  2250, 2800, 1),
    _p("p-mat-205", "mst-cera",     "mat-bathware", "CERA Vigo Wall-Hung WC",             "CERA",     IMG_PROD_WC,     "piece", 12500, 14500, 1),
    _p("p-mat-206", "mst-cera",     "mat-bathware", "CERA Verita Counter Basin",          "CERA",     IMG_PROD_WC,     "piece",  3850, 4500, 1),
    _p("p-mat-207", "mst-cera",     "mat-bathware", "CERA Pristine Faucet",               "CERA",     IMG_PROD_FAUCET, "piece",  3250, 3800, 1),
    _p("p-mat-208", "mst-hindware", "mat-bathware", "Hindware Element Wall-Hung WC",      "Hindware", IMG_PROD_WC,     "piece", 10800, 12500, 1),
    _p("p-mat-209", "mst-hindware", "mat-bathware", "Hindware F1200 Health Faucet",       "Hindware", IMG_PROD_FAUCET, "piece",  1495, 1850, 1),
    _p("p-mat-210", "mst-hindware", "mat-bathware", "Hindware Italian Basin",             "Hindware", IMG_PROD_WC,     "piece",  2850, 3400, 1),

    # --- Tiling & adhesives --------------------------------------------
    _p("p-mat-301", "mst-marblemosaic","mat-tiling", "Kajaria Glossy Floor Tile 600x600", "Kajaria",   IMG_PROD_TILE,     "sq ft", 42, 55, 100),
    _p("p-mat-302", "mst-marblemosaic","mat-tiling", "Somany Wall Tile Vitrosa 300x600",  "Somany",    IMG_PROD_TILE,     "sq ft", 38, 48, 100),
    _p("p-mat-303", "mst-marblemosaic","mat-tiling", "Imported Marble Statuario Slab",    "Imported",  IMG_PROD_TILE,     "sq ft", 320, 400, 50),
    _p("p-mat-304", "mst-marblemosaic","mat-tiling", "Rajasthan Green Marble",            "Local",     IMG_PROD_TILE,     "sq ft", 95, 125, 100),
    _p("p-mat-305", "mst-marblemosaic","mat-tiling", "Johnson GVT 800x1600 Carrara",      "Johnson",   IMG_PROD_TILE,     "sq ft", 85, 110, 50),
    _p("p-mat-306", "mst-laticrete","mat-tiling",    "MYK Laticrete 305 Tile Adhesive",   "Laticrete", IMG_PROD_ADHESIVE, "20 kg bag", 495, 580, 2),
    _p("p-mat-307", "mst-laticrete","mat-tiling",    "MYK Laticrete 325 Marble Adhesive", "Laticrete", IMG_PROD_ADHESIVE, "20 kg bag", 695, 780, 2),
    _p("p-mat-308", "mst-laticrete","mat-tiling",    "MYK Laticrete Permacolor Grout",    "Laticrete", IMG_PROD_ADHESIVE, "5 kg pack", 685, 800, 1),
    _p("p-mat-309", "mst-laticrete","mat-tiling",    "Roff T20 Tile Adhesive",            "Roff",      IMG_PROD_ADHESIVE, "20 kg bag", 420, 490, 2),

    # --- Paints & finishes ---------------------------------------------
    _p("p-mat-401", "mst-colourworks","mat-paint", "Asian Paints Royale Luxury Emulsion", "Asian Paints", IMG_PROD_PAINT, "4 L bucket", 1950, 2250, 1),
    _p("p-mat-402", "mst-colourworks","mat-paint", "Asian Paints Apex Ultima Exterior",   "Asian Paints", IMG_PROD_PAINT, "4 L bucket", 2850, 3250, 1),
    _p("p-mat-403", "mst-colourworks","mat-paint", "Dulux Velvet Touch Platinum",          "Dulux",       IMG_PROD_PAINT, "4 L bucket", 2250, 2600, 1),
    _p("p-mat-404", "mst-colourworks","mat-paint", "Nippon Weatherbond Pro Exterior",      "Nippon",      IMG_PROD_PAINT, "4 L bucket", 2450, 2850, 1),
    _p("p-mat-405", "mst-colourworks","mat-paint", "Asian Paints Primer Interior",         "Asian Paints",IMG_PROD_PAINT, "10 L bucket", 1850, 2150, 1),
    _p("p-mat-406", "mst-asianpaints","mat-paint", "Asian Paints Royale Shyne",            "Asian Paints",IMG_PROD_PAINT, "20 L bucket", 7250, 8400, 1),
    _p("p-mat-407", "mst-asianpaints","mat-paint", "Asian Paints Woodtech Melamyne",       "Asian Paints",IMG_PROD_PAINT, "1 L tin",     485, 580, 1),
    _p("p-mat-408", "mst-asianpaints","mat-paint", "Asian Paints Ace Exterior Emulsion",   "Asian Paints",IMG_PROD_PAINT, "4 L bucket",  1250, 1480, 1),

    # --- Electrical appliances -----------------------------------------
    _p("p-mat-501", "mst-crompton","mat-appliances", "Crompton Hill Briz Ceiling Fan 48''","Crompton", IMG_PROD_FAN, "piece",  2250, 2650, 1),
    _p("p-mat-502", "mst-crompton","mat-appliances", "Crompton Energion HS BLDC Fan",      "Crompton", IMG_PROD_FAN, "piece",  3850, 4500, 1),
    _p("p-mat-503", "mst-crompton","mat-appliances", "Crompton Solarium Qube 15L Geyser",  "Crompton", IMG_PROD_GEYSER, "piece", 7850, 9200, 1),
    _p("p-mat-504", "mst-crompton","mat-appliances", "Crompton 1.5HP Submersible Pump",    "Crompton", IMG_PROD_GEYSER, "piece", 11500, 13500, 1),
    _p("p-mat-505", "mst-havells", "mat-appliances", "Havells Stealth Air Ceiling Fan",    "Havells",  IMG_PROD_FAN, "piece",  3450, 4000, 1),
    _p("p-mat-506", "mst-havells", "mat-appliances", "Havells Monza 25L Storage Geyser",   "Havells",  IMG_PROD_GEYSER, "piece", 9500, 11000, 1),
    _p("p-mat-507", "mst-havells", "mat-appliances", "Havells Lloyd 1.5T Split Inverter AC","Lloyd",   IMG_PROD_AC, "piece",  39500, 46000, 1),
    _p("p-mat-508", "mst-bajaj",   "mat-appliances", "Bajaj Esteem 1200mm Ceiling Fan",    "Bajaj",    IMG_PROD_FAN, "piece",  1850, 2200, 1),
    _p("p-mat-509", "mst-bajaj",   "mat-appliances", "Bajaj Majesty 10L Instant Geyser",   "Bajaj",    IMG_PROD_GEYSER, "piece", 6250, 7500, 1),

    # --- Water proofing ------------------------------------------------
    _p("p-mat-601", "mst-drfixit","mat-waterproof", "Dr Fixit LW+ Integral Waterproofing","Dr Fixit", IMG_PROD_WATERPROOF, "1 L can",   155, 185, 2),
    _p("p-mat-602", "mst-drfixit","mat-waterproof", "Dr Fixit Pidiproof 101 LW+",         "Dr Fixit", IMG_PROD_WATERPROOF, "5 L can",   725, 850, 1),
    _p("p-mat-603", "mst-drfixit","mat-waterproof", "Dr Fixit Raincoat Exterior",         "Dr Fixit", IMG_PROD_WATERPROOF, "4 L bucket",2850, 3250, 1),
    _p("p-mat-604", "mst-drfixit","mat-waterproof", "Dr Fixit Roofseal Flex",             "Dr Fixit", IMG_PROD_WATERPROOF, "20 kg bag", 3950, 4600, 1),
    _p("p-mat-605", "mst-drfixit","mat-waterproof", "Dr Fixit Bathseal",                  "Dr Fixit", IMG_PROD_WATERPROOF, "20 kg bag", 3250, 3800, 1),
    _p("p-mat-606", "mst-fosroc", "mat-waterproof", "Fosroc Nitoproof 100 Membrane",      "Fosroc",   IMG_PROD_WATERPROOF, "20 kg bag", 4500, 5200, 1),
    _p("p-mat-607", "mst-fosroc", "mat-waterproof", "Fosroc Brushbond Flex",              "Fosroc",   IMG_PROD_WATERPROOF, "30 kg kit", 5950, 6800, 1),

    # --- CPVC/PVC & GI fittings ----------------------------------------
    _p("p-mat-701", "mst-astral","mat-pipes", "Astral CPVC Pro 3/4'' Pipe (3 m)",         "Astral",  IMG_PROD_PIPE, "piece",  485, 580, 10),
    _p("p-mat-702", "mst-astral","mat-pipes", "Astral CPVC Pro 1'' Pipe (3 m)",           "Astral",  IMG_PROD_PIPE, "piece",  685, 820, 10),
    _p("p-mat-703", "mst-astral","mat-pipes", "Astral SWR Pipe 110mm (3 m)",              "Astral",  IMG_PROD_PIPE, "piece",  895, 1050, 5),
    _p("p-mat-704", "mst-astral","mat-pipes", "Astral CPVC Elbow 3/4''",                  "Astral",  IMG_PROD_PIPE, "piece",   48, 60, 20),
    _p("p-mat-705", "mst-astral","mat-pipes", "Astral CPVC Tee 1''",                      "Astral",  IMG_PROD_PIPE, "piece",   95, 115, 20),
    _p("p-mat-706", "mst-prince","mat-pipes", "Prince CPVC Flowguard 1'' (3 m)",          "Prince",  IMG_PROD_PIPE, "piece",  650, 780, 10),
    _p("p-mat-707", "mst-prince","mat-pipes", "Supreme SWR Pipe 75mm (3 m)",              "Supreme", IMG_PROD_PIPE, "piece",  595, 720, 5),
    _p("p-mat-708", "mst-prince","mat-pipes", "Finolex GI Pipe 1/2'' (6 m)",              "Finolex", IMG_PROD_PIPE, "piece",  485, 580, 10),

    # --- Hardware & locks ----------------------------------------------
    _p("p-mat-801", "mst-dorset","mat-hardware", "Dorset Mortise Lock 85mm SS",           "Dorset",  IMG_PROD_LOCK,  "piece",  1850, 2200, 1),
    _p("p-mat-802", "mst-dorset","mat-hardware", "Dorset Lever Handle Pair",              "Dorset",  IMG_PROD_LOCK,  "pair",   2250, 2600, 1),
    _p("p-mat-803", "mst-dorset","mat-hardware", "Dorset Night Latch Deadbolt",           "Dorset",  IMG_PROD_LOCK,  "piece",   985, 1200, 1),
    _p("p-mat-804", "mst-hettich","mat-hardware", "Hettich Tandem Box 450mm",             "Hettich", IMG_PROD_HINGE, "set",    3250, 3800, 1),
    _p("p-mat-805", "mst-hettich","mat-hardware", "Hettich Hinge Sensys 110°",            "Hettich", IMG_PROD_HINGE, "pair",    295, 360, 4),
    _p("p-mat-806", "mst-hettich","mat-hardware", "Hettich Soft-Close Drawer Slide",      "Hettich", IMG_PROD_HINGE, "pair",   1250, 1480, 1),
    _p("p-mat-807", "mst-godrejlock","mat-hardware", "Godrej Advantis Digital Lock",      "Godrej",  IMG_PROD_LOCK,  "piece", 15500, 18000, 1),
    _p("p-mat-808", "mst-godrejlock","mat-hardware", "Godrej Ultra Mortise 65mm",         "Godrej",  IMG_PROD_LOCK,  "piece",  1250, 1480, 1),
    _p("p-mat-809", "mst-godrejlock","mat-hardware", "Godrej NX Pro Home Safe",           "Godrej",  IMG_PROD_LOCK,  "piece", 11500, 13500, 1),

    # --- Plywood & laminates -------------------------------------------
    _p("p-mat-901", "mst-greenply","mat-plywood", "Greenply Club Prime 19mm BWP (8x4)",   "Greenply",IMG_PROD_PLY,       "sheet", 3850, 4500, 1),
    _p("p-mat-902", "mst-greenply","mat-plywood", "Greenply Ecotec 12mm MR (8x4)",         "Greenply",IMG_PROD_PLY,       "sheet", 1950, 2300, 1),
    _p("p-mat-903", "mst-greenply","mat-plywood", "Greenlam Decolam 1mm 8x4",              "Greenlam",IMG_PROD_LAMINATE,  "sheet", 1250, 1480, 1),
    _p("p-mat-904", "mst-greenply","mat-plywood", "Greenply Flush Door 32mm",              "Greenply",IMG_PROD_PLY,       "piece", 3450, 4000, 1),
    _p("p-mat-905", "mst-century","mat-plywood",  "Century Club Prime 19mm BWP",           "Century", IMG_PROD_PLY,       "sheet", 3950, 4600, 1),
    _p("p-mat-906", "mst-century","mat-plywood",  "Century Sainik 18mm MR",                "Century", IMG_PROD_PLY,       "sheet", 2550, 3000, 1),
    _p("p-mat-907", "mst-century","mat-plywood",  "Century Cent-Ply 710 Grade",            "Century", IMG_PROD_PLY,       "sheet", 4250, 4900, 1),
    _p("p-mat-908", "mst-merino","mat-plywood",   "Merino Premium Laminate 1mm",           "Merino",  IMG_PROD_LAMINATE,  "sheet", 1495, 1750, 1),
    _p("p-mat-909", "mst-merino","mat-plywood",   "Merino Suede Finish Laminate",          "Merino",  IMG_PROD_LAMINATE,  "sheet", 1850, 2150, 1),
    _p("p-mat-910", "mst-merino","mat-plywood",   "Virgo Decorative Laminate",             "Virgo",   IMG_PROD_LAMINATE,  "sheet", 1150, 1350, 1),
]
