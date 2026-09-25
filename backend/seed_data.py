"""Demo data for InfraLocal - Jaipur focused.
All values are clearly demo. Real data can be swapped in later.
"""
from datetime import datetime, timezone
import uuid

# Curated realistic Indian property imagery
IMG_APT = "https://images.unsplash.com/photo-1779976955613-b74623824d1c?crop=entropy&cs=srgb&fm=jpg&q=80&w=1200"
IMG_VILLA = "https://images.unsplash.com/photo-1723110994499-df46435aa4b3?crop=entropy&cs=srgb&fm=jpg&q=80&w=1200"
IMG_PLOT = "https://images.unsplash.com/photo-1561352335-f8a297b7d29e?crop=entropy&cs=srgb&fm=jpg&q=80&w=1200"
IMG_SKY = "https://images.unsplash.com/photo-1599982133112-2723acedc13a?crop=entropy&cs=srgb&fm=jpg&q=80&w=1200"
IMG_APT2 = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200&q=80"
IMG_COMM = "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=80"
IMG_HOME = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&q=80"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

LOCALITIES = [
    {"id": "loc-ajmer-road", "name": "Ajmer Road", "city": "Jaipur", "state": "Rajasthan",
     "lat": 26.8901, "lng": 75.7156, "image": IMG_SKY,
     "median_price_per_sq_yd": 12500, "govt_dlc_per_sq_yd": 8200,
     "estimated_range_low": 11000, "estimated_range_high": 14500, "confidence": "HIGH",
     "yoy_change_pct": 8.4, "listings_count": 248,
     "summary": "Fast-developing arterial corridor with strong plot and mid-segment residential activity."},
    {"id": "loc-jagatpura", "name": "Jagatpura", "city": "Jaipur", "state": "Rajasthan",
     "lat": 26.8290, "lng": 75.8555, "image": IMG_APT,
     "median_price_per_sq_yd": 15800, "govt_dlc_per_sq_yd": 10500,
     "estimated_range_low": 14000, "estimated_range_high": 17500, "confidence": "HIGH",
     "yoy_change_pct": 11.2, "listings_count": 312,
     "summary": "Established residential belt near Malviya Nagar with strong apartment supply."},
    {"id": "loc-tonk-road", "name": "Tonk Road", "city": "Jaipur", "state": "Rajasthan",
     "lat": 26.8395, "lng": 75.8047, "image": IMG_COMM,
     "median_price_per_sq_yd": 18200, "govt_dlc_per_sq_yd": 12000,
     "estimated_range_low": 16500, "estimated_range_high": 20500, "confidence": "MEDIUM",
     "yoy_change_pct": 6.1, "listings_count": 176,
     "summary": "Prime commercial-residential mixed corridor."},
    {"id": "loc-vaishali-nagar", "name": "Vaishali Nagar", "city": "Jaipur", "state": "Rajasthan",
     "lat": 26.9124, "lng": 75.7398, "image": IMG_VILLA,
     "median_price_per_sq_yd": 22500, "govt_dlc_per_sq_yd": 15000,
     "estimated_range_low": 20000, "estimated_range_high": 25500, "confidence": "HIGH",
     "yoy_change_pct": 9.6, "listings_count": 205,
     "summary": "Upscale planned residential locality, strong villa and premium apartment demand."},
    {"id": "loc-mansarovar", "name": "Mansarovar", "city": "Jaipur", "state": "Rajasthan",
     "lat": 26.8541, "lng": 75.7645, "image": IMG_APT2,
     "median_price_per_sq_yd": 17200, "govt_dlc_per_sq_yd": 11200,
     "estimated_range_low": 15500, "estimated_range_high": 19000, "confidence": "HIGH",
     "yoy_change_pct": 7.8, "listings_count": 289,
     "summary": "Large planned township with strong end-user demand."},
    {"id": "loc-sikar-road", "name": "Sikar Road", "city": "Jaipur", "state": "Rajasthan",
     "lat": 26.9605, "lng": 75.7833, "image": IMG_PLOT,
     "median_price_per_sq_yd": 9800, "govt_dlc_per_sq_yd": 6500,
     "estimated_range_low": 8500, "estimated_range_high": 11500, "confidence": "MEDIUM",
     "yoy_change_pct": 12.4, "listings_count": 168,
     "summary": "Rapidly appreciating plot belt north of city."},
    {"id": "loc-sirsi-road", "name": "Sirsi Road", "city": "Jaipur", "state": "Rajasthan",
     "lat": 26.9316, "lng": 75.6980, "image": IMG_HOME,
     "median_price_per_sq_yd": 8500, "govt_dlc_per_sq_yd": 5800,
     "estimated_range_low": 7500, "estimated_range_high": 9800, "confidence": "MEDIUM",
     "yoy_change_pct": 14.5, "listings_count": 142,
     "summary": "Emerging western corridor with strong plot activity."},
]

def _prop(pid, loc_id, ptype, price, area, unit, lat_offset, lng_offset, bedrooms=None, verified=True, source="Developer", img=None, title=None, facing="East", road_width=30):
    loc = next(l for l in LOCALITIES if l["id"] == loc_id)
    price_per_unit = round(price / area) if area else 0
    return {
        "id": pid, "locality_id": loc_id, "locality_name": loc["name"],
        "city": loc["city"], "state": loc["state"],
        "title": title or f"{ptype} in {loc['name']}",
        "type": ptype, "price": price, "area": area, "area_unit": unit,
        "price_per_unit": price_per_unit,
        "bedrooms": bedrooms, "facing": facing, "road_width_ft": road_width,
        "lat": loc["lat"] + lat_offset, "lng": loc["lng"] + lng_offset,
        "address": f"{loc['name']}, {loc['city']}",
        "verified": verified, "source": source,
        "images": [img or IMG_APT],
        "listed_at": now_iso(),
        "is_demo": True,
    }

PROPERTIES = [
    # Ajmer Road
    _prop("p-01","loc-ajmer-road","Residential Plot",7200000,600,"sq yd",0.005,0.004,img=IMG_PLOT,source="Owner",title="600 sq yd Plot near Bagru"),
    _prop("p-02","loc-ajmer-road","Apartment",4500000,1180,"sq ft",-0.006,0.003,bedrooms=2,img=IMG_APT,title="2 BHK in Skyline Residency"),
    _prop("p-03","loc-ajmer-road","Villa",18500000,2400,"sq ft",0.008,-0.005,bedrooms=4,img=IMG_VILLA,source="Broker",title="4 BHK Villa near Heerapura"),
    _prop("p-04","loc-ajmer-road","Agricultural Land",3500000,1,"acre",-0.01,0.008,verified=False,img=IMG_PLOT,source="Owner",title="1 Acre Agricultural Land"),
    _prop("p-05","loc-ajmer-road","Commercial",8500000,850,"sq ft",0.002,0.001,img=IMG_COMM,title="Shop-Cum-Office on Highway"),
    # Jagatpura
    _prop("p-06","loc-jagatpura","Apartment",8500000,1650,"sq ft",0.003,0.005,bedrooms=3,img=IMG_APT2,title="3 BHK in Nirmal Aashiyana"),
    _prop("p-07","loc-jagatpura","Villa",25000000,3200,"sq ft",-0.004,-0.003,bedrooms=4,img=IMG_VILLA,source="Developer",title="Luxury 4 BHK Villa"),
    _prop("p-08","loc-jagatpura","Residential Plot",12000000,800,"sq yd",0.006,0.004,img=IMG_PLOT,source="Broker",title="800 sq yd Corner Plot"),
    _prop("p-09","loc-jagatpura","Apartment",5800000,1200,"sq ft",-0.005,0.006,bedrooms=2,img=IMG_APT,title="2 BHK Ready to Move"),
    _prop("p-10","loc-jagatpura","Apartment",11500000,1850,"sq ft",0.001,-0.007,bedrooms=3,img=IMG_APT2,source="Developer",title="Premium 3 BHK"),
    # Tonk Road
    _prop("p-11","loc-tonk-road","Commercial",22000000,1200,"sq ft",0.004,0.003,img=IMG_COMM,source="Broker",title="Retail Space, Tonk Road"),
    _prop("p-12","loc-tonk-road","Apartment",9800000,1400,"sq ft",-0.003,0.005,bedrooms=3,img=IMG_APT,title="3 BHK near Gopalpura"),
    _prop("p-13","loc-tonk-road","Residential Plot",15500000,850,"sq yd",0.005,-0.002,img=IMG_PLOT,title="850 sq yd Prime Plot"),
    _prop("p-14","loc-tonk-road","Villa",32000000,3800,"sq ft",-0.006,-0.004,bedrooms=5,img=IMG_VILLA,source="Developer",title="5 BHK Independent Villa"),
    # Vaishali Nagar
    _prop("p-15","loc-vaishali-nagar","Apartment",12500000,1450,"sq ft",0.004,-0.003,bedrooms=3,img=IMG_APT2,title="Premium 3 BHK"),
    _prop("p-16","loc-vaishali-nagar","Villa",42000000,4500,"sq ft",-0.005,0.006,bedrooms=5,img=IMG_VILLA,source="Developer",title="Luxury 5 BHK Villa"),
    _prop("p-17","loc-vaishali-nagar","Residential Plot",18000000,650,"sq yd",0.003,0.004,img=IMG_PLOT,source="Broker",title="650 sq yd JDA Plot"),
    _prop("p-18","loc-vaishali-nagar","Apartment",7500000,1120,"sq ft",-0.007,-0.003,bedrooms=2,img=IMG_APT,title="2 BHK Vaishali Nagar"),
    # Mansarovar
    _prop("p-19","loc-mansarovar","Apartment",6500000,1350,"sq ft",0.005,0.003,bedrooms=2,img=IMG_APT,title="2 BHK Ready to Move"),
    _prop("p-20","loc-mansarovar","Villa",22000000,2800,"sq ft",-0.004,0.005,bedrooms=4,img=IMG_VILLA,title="4 BHK Independent House"),
    _prop("p-21","loc-mansarovar","Residential Plot",14500000,900,"sq yd",0.006,-0.005,img=IMG_PLOT,source="Owner",title="900 sq yd Corner Plot"),
    _prop("p-22","loc-mansarovar","Apartment",8200000,1500,"sq ft",-0.003,-0.004,bedrooms=3,img=IMG_APT2,source="Developer",title="3 BHK Premium Society"),
    # Sikar Road
    _prop("p-23","loc-sikar-road","Residential Plot",5400000,550,"sq yd",0.005,0.004,img=IMG_PLOT,source="Broker",title="550 sq yd JDA Approved"),
    _prop("p-24","loc-sikar-road","Agricultural Land",2200000,1,"bigha",-0.006,0.005,verified=False,img=IMG_PLOT,source="Owner",title="1 Bigha Agricultural"),
    _prop("p-25","loc-sikar-road","Villa",14500000,2400,"sq ft",0.004,-0.003,bedrooms=4,img=IMG_VILLA,title="4 BHK Villa on Sikar Road"),
    _prop("p-26","loc-sikar-road","Residential Plot",8800000,750,"sq yd",-0.005,0.006,img=IMG_PLOT,title="750 sq yd Plot"),
    # Sirsi Road
    _prop("p-27","loc-sirsi-road","Residential Plot",4200000,500,"sq yd",0.006,0.004,img=IMG_PLOT,source="Owner",title="500 sq yd Plot"),
    _prop("p-28","loc-sirsi-road","Villa",11500000,2200,"sq ft",-0.004,-0.005,bedrooms=3,img=IMG_VILLA,title="3 BHK Villa Sirsi Road"),
    _prop("p-29","loc-sirsi-road","Residential Plot",6500000,720,"sq yd",0.005,0.003,img=IMG_PLOT,source="Broker",title="720 sq yd Corner Plot"),
    _prop("p-30","loc-sirsi-road","Agricultural Land",1800000,1,"bigha",-0.006,0.006,verified=False,img=IMG_PLOT,source="Owner",title="1 Bigha Farm Land"),
]

def _price_history(loc_id, base):
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    growth = 1.0
    history = []
    for i, y in enumerate(years):
        listing = int(base * (0.72 + 0.06 * i))
        govt = int(listing * 0.65)
        est_low = int(listing * 0.92)
        est_high = int(listing * 1.10)
        history.append({"year": y, "listing": listing, "govt": govt, "est_low": est_low, "est_high": est_high})
    return history

PRICE_HISTORY = {l["id"]: _price_history(l["id"], l["median_price_per_sq_yd"]) for l in LOCALITIES}

INFRASTRUCTURE = [
    {"id": "inf-01", "name": "Jaipur Metro Phase 2", "type": "Metro", "status": "Under Construction",
     "expected_completion": 2028, "locality_ids": ["loc-jagatpura", "loc-mansarovar"],
     "lat": 26.8290, "lng": 75.8555, "distance_km": 1.2,
     "source": "DMRC News", "source_url": "https://example.com",
     "description": "Phase 2 extension connecting Sitapura and Ambabari via Jagatpura."},
    {"id": "inf-02", "name": "Jaipur Ring Road", "type": "Road", "status": "Under Construction",
     "expected_completion": 2027, "locality_ids": ["loc-ajmer-road", "loc-sikar-road"],
     "lat": 26.8901, "lng": 75.7156, "distance_km": 4.2,
     "source": "NHAI", "source_url": "https://example.com",
     "description": "150 km 6-lane orbital road."},
    {"id": "inf-03", "name": "Mahindra World City SEZ Expansion", "type": "SEZ", "status": "Under Development",
     "expected_completion": 2029, "locality_ids": ["loc-tonk-road"],
     "lat": 26.8395, "lng": 75.8047, "distance_km": 12.0,
     "source": "MWC Press Release", "source_url": "https://example.com",
     "description": "Additional 1000 acres IT/Manufacturing zone."},
    {"id": "inf-04", "name": "Sanganer Airport Upgrade", "type": "Airport", "status": "Planned",
     "expected_completion": 2028, "locality_ids": ["loc-tonk-road", "loc-mansarovar"],
     "lat": 26.8242, "lng": 75.8122, "distance_km": 8.5,
     "source": "AAI", "source_url": "https://example.com",
     "description": "New international terminal, cargo hub."},
    {"id": "inf-05", "name": "NH-11 Widening (Sikar Road)", "type": "Highway", "status": "Under Construction",
     "expected_completion": 2026, "locality_ids": ["loc-sikar-road", "loc-sirsi-road"],
     "lat": 26.9605, "lng": 75.7833, "distance_km": 2.0,
     "source": "NHAI", "source_url": "https://example.com",
     "description": "6-lane highway upgrade to Chomu."},
    {"id": "inf-06", "name": "AIIMS Jaipur Satellite Campus", "type": "Hospital", "status": "Planned",
     "expected_completion": 2029, "locality_ids": ["loc-ajmer-road"],
     "lat": 26.8901, "lng": 75.7156, "distance_km": 6.0,
     "source": "Health Ministry", "source_url": "https://example.com",
     "description": "500-bed super-specialty campus."},
    {"id": "inf-07", "name": "Vaishali Nagar Flyover", "type": "Road", "status": "Completed",
     "expected_completion": 2025, "locality_ids": ["loc-vaishali-nagar"],
     "lat": 26.9124, "lng": 75.7398, "distance_km": 0.5,
     "source": "JDA", "source_url": "https://example.com",
     "description": "1.2 km flyover reducing peak-hour congestion."},
]

NEWS = [
    {"id": "n-01", "title": "Jaipur Metro Phase 2 tunnel work reaches Jagatpura", "summary": "The 12 km underground stretch connecting Sitapura and Ambabari via Jagatpura hits key milestone. Expected impact on nearby residential prices.", "category": "Infrastructure", "locality_id": "loc-jagatpura", "date": "2026-04-12", "source": "InfraLocal Desk"},
    {"id": "n-02", "title": "JDA revises DLC rates on Ajmer Road corridor", "summary": "Rates revised upward by an average 12% across residential and commercial pockets. Effective from next fiscal.", "category": "Government", "locality_id": "loc-ajmer-road", "date": "2026-04-05", "source": "JDA Notice"},
    {"id": "n-03", "title": "New township approved off Sikar Road", "summary": "500-acre integrated township with schools and hospital approved for development, close to NH-11 corridor.", "category": "Development", "locality_id": "loc-sikar-road", "date": "2026-03-28", "source": "Times Property"},
    {"id": "n-04", "title": "Mansarovar sees surge in ready-to-move apartment demand", "summary": "Buyers prefer completed inventory. Median transaction time down to 32 days from 48 last year.", "category": "Residential", "locality_id": "loc-mansarovar", "date": "2026-03-20", "source": "InfraLocal Analytics"},
    {"id": "n-05", "title": "Ring Road Phase 3 tender awarded", "summary": "NHAI awards ₹1,240 Cr contract for southern arc. Impact on Ajmer Road and Sikar Road connectivity expected by 2027.", "category": "Infrastructure", "locality_id": "loc-ajmer-road", "date": "2026-03-14", "source": "NHAI Press"},
    {"id": "n-06", "title": "Vaishali Nagar villa prices cross ₹22,000 / sq yd", "summary": "Sustained end-user demand pushes locality into premium bracket. Inventory tightening across 500-800 sq yd segment.", "category": "Residential", "locality_id": "loc-vaishali-nagar", "date": "2026-03-08", "source": "InfraLocal Analytics"},
    {"id": "n-07", "title": "SEZ expansion to add 40,000 jobs off Tonk Road", "summary": "MWC's second phase focused on IT-BPM and clean manufacturing. Nearby rentals expected to firm up.", "category": "Industrial", "locality_id": "loc-tonk-road", "date": "2026-02-25", "source": "Economic Times"},
]
