"""Market (construction ecosystem) demo data - Jaipur.
Zomato-style directory covering the full lifecycle: Design -> Build -> Materials -> Interiors -> Occupancy -> Maintenance.
All demo data.
"""

# Curated imagery for suppliers / trades
IMG_CEMENT = "https://images.unsplash.com/photo-1590093804797-f92aef6a1381?w=800&q=80"
IMG_STEEL = "https://images.unsplash.com/photo-1567613113939-5c17f7f4b06e?w=800&q=80"
IMG_TILE = "https://images.unsplash.com/photo-1615873968403-89e068629265?w=800&q=80"
IMG_ARCH = "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=800&q=80"
IMG_CONTRACTOR = "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=800&q=80"
IMG_INTERIOR = "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=800&q=80"
IMG_ELECT = "https://images.unsplash.com/photo-1620662736427-b8a198f52a4d?w=800&q=80"
IMG_PLUMB = "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?w=800&q=80"
IMG_PAINT = "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=800&q=80"
IMG_RMC = "https://images.unsplash.com/photo-1517646287270-a5a9ca602e5c?w=800&q=80"
IMG_SAND = "https://images.unsplash.com/photo-1618477247222-acbdb0e159b3?w=800&q=80"
IMG_BRICK = "https://images.unsplash.com/photo-1590674899484-13a1a7f42a62?w=800&q=80"
IMG_SURVEY = "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&q=80"
IMG_MEP = "https://images.unsplash.com/photo-1581094488379-6c8303b71d5c?w=800&q=80"
IMG_MOVE = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80"
IMG_HOME = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"

# Lifecycle groups
MARKET_GROUPS = [
    {"id": "grp-design", "name": "Design", "subtitle": "Plan & visualise", "icon": "color-palette-outline"},
    {"id": "grp-build", "name": "Build", "subtitle": "Contractors & consultants", "icon": "construct-outline"},
    {"id": "grp-materials", "name": "Materials", "subtitle": "Cement, steel, tiles & more", "icon": "cube-outline"},
    {"id": "grp-interiors", "name": "Interiors", "subtitle": "Fit-out & finishings", "icon": "bed-outline"},
    {"id": "grp-occupancy", "name": "Move In", "subtitle": "Occupancy essentials", "icon": "home-outline"},
    {"id": "grp-maintenance", "name": "Maintenance", "subtitle": "Post-handover services", "icon": "hammer-outline"},
]

MARKET_CATEGORIES = [
    # Design
    {"id": "cat-architects", "group_id": "grp-design", "name": "Architects", "image": IMG_ARCH},
    {"id": "cat-structural", "group_id": "grp-design", "name": "Structural Consultants", "image": IMG_ARCH},
    {"id": "cat-mep", "group_id": "grp-design", "name": "MEP Consultants", "image": IMG_MEP},
    {"id": "cat-surveyors", "group_id": "grp-design", "name": "Surveyors", "image": IMG_SURVEY},
    # Build
    {"id": "cat-contractors", "group_id": "grp-build", "name": "Contractors", "image": IMG_CONTRACTOR},
    {"id": "cat-labour", "group_id": "grp-build", "name": "Labour Contractors", "image": IMG_CONTRACTOR},
    # Materials
    {"id": "cat-cement", "group_id": "grp-materials", "name": "Cement", "image": IMG_CEMENT},
    {"id": "cat-steel", "group_id": "grp-materials", "name": "Steel", "image": IMG_STEEL},
    {"id": "cat-rmc", "group_id": "grp-materials", "name": "RMC", "image": IMG_RMC},
    {"id": "cat-bricks", "group_id": "grp-materials", "name": "Bricks & AAC", "image": IMG_BRICK},
    {"id": "cat-sand", "group_id": "grp-materials", "name": "Sand & Aggregate", "image": IMG_SAND},
    {"id": "cat-tiles", "group_id": "grp-materials", "name": "Tiles & Stone", "image": IMG_TILE},
    {"id": "cat-electrical", "group_id": "grp-materials", "name": "Electrical", "image": IMG_ELECT},
    {"id": "cat-plumbing", "group_id": "grp-materials", "name": "Plumbing", "image": IMG_PLUMB},
    {"id": "cat-paint", "group_id": "grp-materials", "name": "Paint", "image": IMG_PAINT},
    # Interiors
    {"id": "cat-interior-design", "group_id": "grp-interiors", "name": "Interior Designers", "image": IMG_INTERIOR},
    {"id": "cat-modular", "group_id": "grp-interiors", "name": "Modular Kitchens", "image": IMG_INTERIOR},
    {"id": "cat-furniture", "group_id": "grp-interiors", "name": "Furniture", "image": IMG_INTERIOR},
    # Occupancy
    {"id": "cat-packers", "group_id": "grp-occupancy", "name": "Packers & Movers", "image": IMG_MOVE},
    {"id": "cat-cleaning", "group_id": "grp-occupancy", "name": "Deep Cleaning", "image": IMG_HOME},
    {"id": "cat-security", "group_id": "grp-occupancy", "name": "Home Security", "image": IMG_HOME},
    # Maintenance
    {"id": "cat-pest", "group_id": "grp-maintenance", "name": "Pest Control", "image": IMG_HOME},
    {"id": "cat-ac", "group_id": "grp-maintenance", "name": "AC Service", "image": IMG_MEP},
    {"id": "cat-repairs", "group_id": "grp-maintenance", "name": "Handyman & Repairs", "image": IMG_CONTRACTOR},
]

# Suppliers — realistic Jaipur ecosystem
SUPPLIERS = [
    # Architects
    {"id": "sup-01", "category_id": "cat-architects", "name": "Studio Vastukala",
     "tagline": "Contemporary residential architecture", "city": "Jaipur", "area": "C-Scheme",
     "rating": 4.8, "reviews": 142, "verified": True, "featured": True,
     "starting_price": "₹45/sq ft", "min_project": "1000 sq ft",
     "offerings": ["Residential design", "3D visualisation", "Vastu-compliant plans", "Interior + exterior"],
     "phone": "+91 98290 12345", "image": IMG_ARCH,
     "about": "Award-winning studio blending modern minimalism with Rajasthani craft. 12+ years, 180+ projects across Jaipur."},
    {"id": "sup-02", "category_id": "cat-architects", "name": "Bluecube Design Atelier",
     "tagline": "Villas, farmhouses & boutique homes", "city": "Jaipur", "area": "Malviya Nagar",
     "rating": 4.6, "reviews": 87, "verified": True, "featured": False,
     "starting_price": "₹60/sq ft", "min_project": "2000 sq ft",
     "offerings": ["Villa design", "Landscape", "Farmhouses"],
     "phone": "+91 98290 22345", "image": IMG_ARCH,
     "about": "Boutique studio focused on premium villas and farmhouses on Ajmer Road and Delhi Road belts."},

    # Structural
    {"id": "sup-03", "category_id": "cat-structural", "name": "Rajputana Structures LLP",
     "tagline": "RCC, steel & seismic-safe design", "city": "Jaipur", "area": "Vaishali Nagar",
     "rating": 4.7, "reviews": 63, "verified": True, "featured": False,
     "starting_price": "₹15/sq ft", "min_project": "—",
     "offerings": ["RCC design", "Seismic analysis", "Peer review", "Retrofit"],
     "phone": "+91 98290 33456", "image": IMG_MEP,
     "about": "IIT-Roorkee alumni-led practice serving developers and individual homeowners."},

    # MEP
    {"id": "sup-04", "category_id": "cat-mep", "name": "Grid MEP Consultants",
     "tagline": "Electrical, HVAC, plumbing & fire", "city": "Jaipur", "area": "Mansarovar",
     "rating": 4.5, "reviews": 41, "verified": True, "featured": False,
     "starting_price": "₹18/sq ft", "min_project": "5000 sq ft",
     "offerings": ["Electrical design", "HVAC", "Plumbing", "Fire safety"],
     "phone": "+91 98290 44567", "image": IMG_MEP,
     "about": "Turnkey MEP for residential towers, commercial and hospitality."},

    # Surveyors
    {"id": "sup-05", "category_id": "cat-surveyors", "name": "GeoLine Surveyors",
     "tagline": "DGPS, contour, plot demarcation", "city": "Jaipur", "area": "Sikar Road",
     "rating": 4.4, "reviews": 78, "verified": True, "featured": False,
     "starting_price": "₹8,000/plot", "min_project": "—",
     "offerings": ["Plot demarcation", "Contour survey", "DGPS", "Boundary dispute"],
     "phone": "+91 98290 55678", "image": IMG_SURVEY,
     "about": "20+ years surveying land, colonies and infrastructure sites across Rajasthan."},

    # Contractors
    {"id": "sup-06", "category_id": "cat-contractors", "name": "Marwar Buildtech",
     "tagline": "Turnkey home construction", "city": "Jaipur", "area": "Jagatpura",
     "rating": 4.7, "reviews": 210, "verified": True, "featured": True,
     "starting_price": "₹1,850/sq ft", "min_project": "1000 sq ft",
     "offerings": ["Turnkey construction", "Structure only", "Material + labour"],
     "phone": "+91 98290 66789", "image": IMG_CONTRACTOR,
     "about": "Full-service contractor delivering 30+ homes a year with fixed-price packages."},
    {"id": "sup-07", "category_id": "cat-contractors", "name": "Sunrise Builders",
     "tagline": "Villas & small-scale apartments", "city": "Jaipur", "area": "Tonk Road",
     "rating": 4.3, "reviews": 96, "verified": False, "featured": False,
     "starting_price": "₹1,650/sq ft", "min_project": "1500 sq ft",
     "offerings": ["Villa construction", "G+3 apartments", "Boundary walls"],
     "phone": "+91 98290 77890", "image": IMG_CONTRACTOR,
     "about": "Family-run contractor with focus on cost-optimised builds."},

    # Cement
    {"id": "sup-08", "category_id": "cat-cement", "name": "Shri Balaji Traders",
     "tagline": "UltraTech, Ambuja, Shree Cement", "city": "Jaipur", "area": "Sirsi Road",
     "rating": 4.6, "reviews": 320, "verified": True, "featured": True,
     "starting_price": "₹385/bag", "min_project": "10 bags",
     "offerings": ["OPC 53", "PPC", "PSC", "Bulk supply", "Same-day delivery"],
     "phone": "+91 98290 88901", "image": IMG_CEMENT,
     "about": "Authorised stockist supplying builders and homeowners across Jaipur since 2004."},
    {"id": "sup-09", "category_id": "cat-cement", "name": "Rajputana Cement Agency",
     "tagline": "Wholesale rates for builders", "city": "Jaipur", "area": "Vishwakarma Industrial",
     "rating": 4.5, "reviews": 178, "verified": True, "featured": False,
     "starting_price": "₹372/bag", "min_project": "50 bags",
     "offerings": ["OPC 43", "OPC 53", "White cement", "Waterproof cement"],
     "phone": "+91 98290 99012", "image": IMG_CEMENT,
     "about": "Bulk cement supplier for developer projects and infrastructure jobs."},

    # Steel
    {"id": "sup-10", "category_id": "cat-steel", "name": "Jaipur Steel Syndicate",
     "tagline": "TMT Fe500 / Fe550 — TATA, JSW, SAIL", "city": "Jaipur", "area": "Vishwakarma Industrial",
     "rating": 4.7, "reviews": 265, "verified": True, "featured": True,
     "starting_price": "₹58/kg", "min_project": "1 tonne",
     "offerings": ["TMT bars", "Structural steel", "Angles & channels", "Cut & bent"],
     "phone": "+91 98290 11123", "image": IMG_STEEL,
     "about": "Authorised distributor of premium TMT brands with same-day delivery in Jaipur."},

    # RMC
    {"id": "sup-11", "category_id": "cat-rmc", "name": "MixMaster RMC",
     "tagline": "M20 to M60 ready-mix concrete", "city": "Jaipur", "area": "Ajmer Road",
     "rating": 4.5, "reviews": 132, "verified": True, "featured": False,
     "starting_price": "₹4,600/cum", "min_project": "6 cum",
     "offerings": ["M20", "M25", "M30", "M40", "Self-compacting concrete"],
     "phone": "+91 98290 22234", "image": IMG_RMC,
     "about": "3 batching plants around Jaipur city; delivery via boom pump available."},

    # Bricks
    {"id": "sup-12", "category_id": "cat-bricks", "name": "Sanganer Brick Works",
     "tagline": "Red clay, fly-ash & AAC blocks", "city": "Jaipur", "area": "Sanganer",
     "rating": 4.3, "reviews": 88, "verified": True, "featured": False,
     "starting_price": "₹7.5/piece", "min_project": "1000 pcs",
     "offerings": ["Red clay bricks", "Fly-ash bricks", "AAC blocks", "Solid concrete blocks"],
     "phone": "+91 98290 33345", "image": IMG_BRICK,
     "about": "Local kiln + AAC supply serving Jaipur south belt."},

    # Sand & aggregate
    {"id": "sup-13", "category_id": "cat-sand", "name": "Aravalli Aggregates",
     "tagline": "River sand, M-sand & aggregates", "city": "Jaipur", "area": "Delhi Road",
     "rating": 4.4, "reviews": 156, "verified": True, "featured": False,
     "starting_price": "₹52/cft", "min_project": "100 cft",
     "offerings": ["River sand", "Manufactured sand", "10mm / 20mm / 40mm aggregate", "GSB"],
     "phone": "+91 98290 44456", "image": IMG_SAND,
     "about": "Licensed aggregate supplier with own quarry near Chomu."},

    # Tiles
    {"id": "sup-14", "category_id": "cat-tiles", "name": "Marble & Mosaic Gallery",
     "tagline": "Kajaria, Somany, imported marble", "city": "Jaipur", "area": "Malviya Nagar",
     "rating": 4.6, "reviews": 234, "verified": True, "featured": True,
     "starting_price": "₹42/sq ft", "min_project": "—",
     "offerings": ["Vitrified tiles", "GVT / PGVT", "Marble", "Granite", "Wooden tiles"],
     "phone": "+91 98290 55567", "image": IMG_TILE,
     "about": "6000 sq ft showroom with 200+ SKUs from top Indian and imported brands."},

    # Electrical
    {"id": "sup-15", "category_id": "cat-electrical", "name": "Voltronics Wholesale",
     "tagline": "Wires, MCBs, fans, lights", "city": "Jaipur", "area": "Chandpole Bazaar",
     "rating": 4.5, "reviews": 189, "verified": True, "featured": False,
     "starting_price": "—", "min_project": "—",
     "offerings": ["Polycab / Havells wires", "Schneider / Legrand switchgear", "LED lighting", "Fans"],
     "phone": "+91 98290 66678", "image": IMG_ELECT,
     "about": "Authorised dealer for premium electrical brands. Contractor pricing on request."},

    # Plumbing
    {"id": "sup-16", "category_id": "cat-plumbing", "name": "AquaFit Plumbing Store",
     "tagline": "Jaquar, Kohler, CERA — full range", "city": "Jaipur", "area": "MI Road",
     "rating": 4.4, "reviews": 121, "verified": True, "featured": False,
     "starting_price": "—", "min_project": "—",
     "offerings": ["Sanitaryware", "CP fittings", "PVC / CPVC pipes", "Water tanks"],
     "phone": "+91 98290 77789", "image": IMG_PLUMB,
     "about": "One-stop plumbing shop with installation partners."},

    # Paint
    {"id": "sup-17", "category_id": "cat-paint", "name": "ColourWorks Studio",
     "tagline": "Asian Paints, Dulux, Nippon", "city": "Jaipur", "area": "Raja Park",
     "rating": 4.5, "reviews": 176, "verified": True, "featured": False,
     "starting_price": "—", "min_project": "—",
     "offerings": ["Interior emulsion", "Exterior paint", "Waterproofing", "Painting contractors"],
     "phone": "+91 98290 88890", "image": IMG_PAINT,
     "about": "Retail + contractor supply with in-shop colour consultation."},

    # Interior designers
    {"id": "sup-18", "category_id": "cat-interior-design", "name": "Livspace-style Studio Ivory",
     "tagline": "End-to-end home interiors", "city": "Jaipur", "area": "Vaishali Nagar",
     "rating": 4.7, "reviews": 92, "verified": True, "featured": True,
     "starting_price": "₹2.5 L / room", "min_project": "1 BHK",
     "offerings": ["Modular kitchens", "Wardrobes", "False ceiling", "Full home"],
     "phone": "+91 98290 99901", "image": IMG_INTERIOR,
     "about": "Design + execution studio with a 45-day handover guarantee."},

    # Modular kitchens
    {"id": "sup-19", "category_id": "cat-modular", "name": "Kutchina Modular",
     "tagline": "Modular kitchens & wardrobes", "city": "Jaipur", "area": "Malviya Nagar",
     "rating": 4.4, "reviews": 78, "verified": True, "featured": False,
     "starting_price": "₹1,600/sq ft", "min_project": "8 ft kitchen",
     "offerings": ["L / U / Island kitchens", "Wardrobes", "Loft storage"],
     "phone": "+91 98290 10111", "image": IMG_INTERIOR,
     "about": "Authorised franchise with 10-year warranty on hardware."},

    # Furniture
    {"id": "sup-20", "category_id": "cat-furniture", "name": "Woodmark Furniture",
     "tagline": "Solid wood + engineered furniture", "city": "Jaipur", "area": "Sitapura",
     "rating": 4.3, "reviews": 145, "verified": True, "featured": False,
     "starting_price": "—", "min_project": "—",
     "offerings": ["Sofas", "Beds", "Dining", "Custom pieces"],
     "phone": "+91 98290 21112", "image": IMG_INTERIOR,
     "about": "Factory-direct showroom with custom orders in 3-4 weeks."},

    # Packers
    {"id": "sup-21", "category_id": "cat-packers", "name": "Marwari Packers & Movers",
     "tagline": "Local & intercity relocation", "city": "Jaipur", "area": "Tonk Road",
     "rating": 4.5, "reviews": 289, "verified": True, "featured": False,
     "starting_price": "₹4,500 / 1 BHK local", "min_project": "—",
     "offerings": ["Local shifting", "Intercity", "Office moves", "Insurance"],
     "phone": "+91 98290 32223", "image": IMG_MOVE,
     "about": "GST-registered movers with in-house packing crew and insurance."},

    # Cleaning
    {"id": "sup-22", "category_id": "cat-cleaning", "name": "SparkleHome Deep Clean",
     "tagline": "Handover & festive cleaning", "city": "Jaipur", "area": "C-Scheme",
     "rating": 4.6, "reviews": 167, "verified": True, "featured": False,
     "starting_price": "₹1,800 / BHK", "min_project": "1 BHK",
     "offerings": ["Deep cleaning", "Sofa shampoo", "Bathroom detailing", "Post-construction"],
     "phone": "+91 98290 43334", "image": IMG_HOME,
     "about": "Trained crew with eco-friendly products; same-day slots."},

    # Security
    {"id": "sup-23", "category_id": "cat-security", "name": "SecureHome Systems",
     "tagline": "CCTV, video door phones & alarms", "city": "Jaipur", "area": "Vaishali Nagar",
     "rating": 4.4, "reviews": 82, "verified": True, "featured": False,
     "starting_price": "₹8,500 / 4-cam kit", "min_project": "—",
     "offerings": ["CCTV", "Video door phone", "Biometric locks", "Intrusion alarms"],
     "phone": "+91 98290 54445", "image": IMG_HOME,
     "about": "Dahua & Hikvision channel partner with AMC options."},

    # Pest control
    {"id": "sup-24", "category_id": "cat-pest", "name": "PestGuard India",
     "tagline": "Termite, cockroach, mosquito", "city": "Jaipur", "area": "Mansarovar",
     "rating": 4.5, "reviews": 213, "verified": True, "featured": False,
     "starting_price": "₹1,200 / BHK", "min_project": "1 BHK",
     "offerings": ["General pest", "Termite pre / post construction", "Mosquito fogging", "AMC"],
     "phone": "+91 98290 65556", "image": IMG_HOME,
     "about": "Certified applicators using odourless chemicals; kid & pet safe."},

    # AC service
    {"id": "sup-25", "category_id": "cat-ac", "name": "CoolBreeze AC Care",
     "tagline": "Service, gas fill, installation", "city": "Jaipur", "area": "Sikar Road",
     "rating": 4.4, "reviews": 176, "verified": True, "featured": False,
     "starting_price": "₹499 / service", "min_project": "—",
     "offerings": ["General service", "Gas top-up", "Installation", "AMC"],
     "phone": "+91 98290 76667", "image": IMG_MEP,
     "about": "Same-day service across Jaipur; multi-brand."},

    # Handyman
    {"id": "sup-26", "category_id": "cat-repairs", "name": "FixIt Home Services",
     "tagline": "Electrician, plumber, carpenter on demand", "city": "Jaipur", "area": "Jagatpura",
     "rating": 4.3, "reviews": 254, "verified": True, "featured": False,
     "starting_price": "₹199 / visit", "min_project": "—",
     "offerings": ["Electrical repairs", "Plumbing fixes", "Carpentry", "Wall drilling"],
     "phone": "+91 98290 87778", "image": IMG_CONTRACTOR,
     "about": "60-min response window in most Jaipur pincodes."},
]
