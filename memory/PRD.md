# InfraLocal — Product Requirements

## Vision
A Zillow-style map-first real estate + intelligence platform for India (MVP focused on Jaipur). Answers:
- What is available here?
- What is it worth?
- What infrastructure is coming?
- What should I know about this locality?

## Stack
- Frontend: Expo (React Native) with expo-router, react-native-maps (OpenStreetMap tiles native), @gorhom/bottom-sheet, react-native-svg for charts.
- Backend: FastAPI + MongoDB (motor) with `/api` prefix.
- Storage: Emergent Managed Object Storage for property image uploads.
- Design tokens: Ivory (#FFFFF0) surface, Deep Navy (#0A192F) brand, Terracotta (#C25934) accent.

## Onboarding
- Name + mobile + **city / town / village** (free text) + **profession** (Buyer, Investor, Seller, Broker, Developer, Architect, Contractor, Loan Advisor, Lawyer, Other). No OTP.

## Screens
- **Onboarding** — name/mobile/city-town-village.
- **Explore (tab)** — Zillow / Airbnb-style: sticky header (Hi user + **menu icon → Profile** + List button + search + **Buy/Rent segmented control** + filter chips + Heat toggle) over map (native) or list (web). Bottom sheet with Map / List view toggle, Pin Preview (photo, price, InfraValue vs Govt DLC, Best-deal ribbon, Listed-by mini card with WhatsApp + Call, Similar Properties horizontal slider with **Show on map** button on each). Deep-linkable via `?highlight={id}` — used by "Show on map" buttons across the app.
- **Property Detail** — hero, InfraValue vs Govt DLC, details, Listed-by agent card, **Similar properties** horizontal slider with per-item **Show on map** button, WhatsApp + Call bar. Every visit is stored to Recently Viewed.
- **Profile** — user card with initials avatar, mobile, profession + city pills. Stats row (Saved / Following / Enquiries / Listings). Sections:
   - **Account**: History (recently viewed) · Enquiries & orders · Subscriptions
   - **Business**: Work with us / Become an agent · List with us
   - **Help**: Contact us · About InfraLocal
   - Sign out
- **History** — Recently viewed properties from AsyncStorage.
- **Enquiries & orders** — Agent enquiries + supplier quote requests, each linked to the agent/supplier.
- **Subscriptions** — Free / Pro / Business tiers (payments coming soon).
- **Work with us / Become an agent** — Structured application form (name, mobile, firm, role chips, area, RERA).
- **Contact us / Help** — WhatsApp / Call / Email support + common help topics.
- **Agents (tab)** — 7 role categories × 13 seeded agents with **Bronze / Silver / Gold** tier badges (computed from RERA + reviews + rating), search, top-agent list.
- **News (tab)** — Inshorts-style locality news feed.
- **Market (tab)** — Zomato-style construction ecosystem (Design → Move-In → Maintenance).
- **Saved (tab)** — Saved properties + followed localities + **Compare mode** (2–4 side-by-side).
- **Property Detail** — hero, InfraValue vs Govt DLC, details, "Listed by" agent card, WhatsApp + Call bar.
- **Locality Detail** — hero, metric cards, InfraValue range, **Neighbourhood Lifestyle Score card** (walkability, schools, hospitals, connectivity, safety, overall), price history chart, Govt vs Market, infrastructure timeline, news, listings.
- **Agent Detail** — avatar, tier badge, RERA ID, rating/reviews/years, specialties, coverage, WhatsApp + Call + Send-enquiry.
- **Agent Category** — list with tier badges and filters (top-rated / most experienced / verified).
- **Supplier Detail** — reviews section + WhatsApp/Call/Quote.
- **Compare** — side-by-side table (up to 4).
- **Market Category** — supplier list with sort + verified filter.
- **List Property** — 7-step wizard.

## Data
- Seeded 7 Jaipur localities, ~30 properties, 7 infrastructure projects, 7 news items — all clearly demo.

## Key API
- `POST /api/auth/onboard`
- `GET /api/localities`, `GET /api/localities/{id}` (includes price_history + infra + news)
- `GET /api/properties?type=&locality_id=&q=&verified_only=`
- `GET /api/properties?listing_type=Buy|Rent&type=&locality_id=&q=&verified_only=`
- `GET /api/properties/{id}` (includes infravalue estimate + govt_value + **lister**)
- `GET /api/properties/{id}/similar` — up to 6 similar (same type + listing_type, price ±60%, same locality first)
- `GET /api/user/{uid}/activity` — saved (with property snapshot), follows (with locality snapshot), my_listings, quote_requests (with supplier), agent_enquiries (with agent)
- `POST /api/properties`
- `GET /api/compare?ids=a,b,c` — side-by-side compare payload
- `GET /api/heatmap` — locality points + normalised intensity
- `GET /api/infrastructure`, `GET /api/news`
- `POST /api/saved/toggle`, `GET /api/saved`
- `POST /api/follows/toggle`, `GET /api/follows`
- `POST /api/upload`, `GET /api/files/{path}`
- `GET /api/market/groups` (with categories + supplier counts)
- `GET /api/market/categories?group_id=`
- `GET /api/market/suppliers?category_id=&group_id=&q=&featured_only=&verified_only=&city=`
- `GET /api/market/suppliers/{id}` (with attached category)
- `POST /api/market/quote-requests`
- `GET /api/market/suppliers/{id}/reviews`
- `POST /api/market/suppliers/{id}/reviews`
- `GET /api/agent-categories`
- `GET /api/agents?category_id=&q=&verified_only=&featured_only=&area=`
- `GET /api/agents/{id}` (with category + recent_listings for brokers)
- `POST /api/agents/{id}/enquiries`

## Materials shopping (Infra.Market-style)
Within the Market tab, the **Materials** group is a shopping-style catalogue:
- 10 category tiles in a 3-col grid matching the reference screenshot: Cement & steel, Electricals & lighting, Bathware, Tiling & adhesives, Paints & finishes, Electrical appliances, Water proofing, CPVC/PVC & GI fittings, Hardware & locks, Plywood & laminates.
- Header: "Materials" + "Materials across **Jaipur**" + cart button with live badge.
- Category screen: stores listed vertically, each with a horizontal catalogue of products (brand, name, image, MRP/price, unit, discount %, ADD → +/- qty).
- Store screen: full catalogue grouped by category tabs, with in-catalogue search and WhatsApp enquiry CTA.
- Cart: persisted via `zustand` + AsyncStorage (`infrajagat.materials.cart.v1`). Groups by store, per-store subtotals, "Send on WhatsApp" per store (deep-link with line items & subtotal), sticky "Request quotes" that posts to backend.
- 24 demo stores + 85 products across 10 categories, seeded fresh on every backend restart.

### New endpoints
- `GET /api/materials/categories`
- `GET /api/materials/categories/{id}/stores` (products embedded, per category)
- `GET /api/materials/stores/{id}` (catalogue grouped by category)
- `GET /api/materials/products?q=&category_id=`
- `POST /api/materials/cart-enquiry` — rolls up `per_store` subtotals and total
- `GET /api/user/{uid}/activity` now includes `materials_orders`

## Phase 2 — Monetisation & Intelligence (Oct 2026) ✅ Shipped
Seven features that take InfraJagat from map browser to full real-estate operating system:

### a. Featured Listings & Lead-Based Pricing
- Any owner can **promote** a listing for 7/14/30 days (₹499/₹899/₹1499). Mock UPI/Card payment.
- `/promote-listing?property_id=` flow. Boosted listings pin above the type-filtered list (sort: `featured desc, listed_at desc`) and show a gold "Featured" ribbon on the card.
- Every WhatsApp/Call tap on a property detail logs a lead with per-channel cost (₹25 / ₹35 / ₹75).
- Endpoints: `GET /api/promote/plans`, `POST /api/properties/{pid}/promote`, `POST /api/properties/{pid}/leads`, `GET /api/properties/{pid}/leads?admin_token=`.

### b. Agent / Developer Subscription Tiers
- Four tiers **Gold / Silver / Bronze / Unverified** with distinct listing-caps, lead-caps, perks and badge colour.
- `/subscriptions` now has **Buyers** and **Agents & Developers** tabs with Monthly / Annual (save 17%) toggle.
- Agent detail page renders a **Live performance** block: 30-day views/leads/conversion/city-rank + a 14-day sparkline + current perks + "Upgrade tier" CTA.
- Endpoints: `GET /api/agent-subscription-tiers`, `GET /api/agents/{aid}/analytics`.

### c. Document-Verified Badge Workflow
- Owners submit `/verify-listing?property_id=` with up to N doc photos (Patta / Sale Deed / Khasra / RERA / Owner-ID) via `expo-image-picker` + Emergent object-storage.
- Admin reviews pending requests from `/admin-verification` (shared-secret token `infrajagat-admin`), approve/reject toggles `property.verified` and status.
- Endpoints: `POST /api/properties/{pid}/verification-request`, `GET /api/verification-requests?status=&admin_token=`, `POST /api/verification-requests/{vid}/review`.

### d. Saved-Search Alerts
- Explore chip **"Save & alert me"** stores current search (type / listing-type / q / price / bedrooms) under the user.
- `/saved-searches` screen lists all alerts with live match counts, delete, and jump-to-explore.
- Endpoints: `POST /api/saved-searches`, `GET /api/saved-searches?user_id=`, `GET /api/saved-searches/{sid}/matches`, `DELETE /api/saved-searches/{sid}?user_id=`.

### e. Locality Compare
- "Compare this locality" CTA on `/locality/[id]` opens `/compare-localities?ids=`.
- Side-by-side matrix across 14 criteria grouped into price / lifestyle / activity with per-row **Best** badges. Supports adding up to 4 localities via modal picker.
- Endpoint: `GET /api/compare/localities?ids=`.

### f. Home-Loan Instant Quote
- Property detail renders an **EMI card** with pill-controls for down-payment %, tenure, monthly income input.
- Server returns EMI, total interest, total payable, eligibility note, and 4 illustrative bank offers.
- Endpoint: `POST /api/finance/emi`.

### g. AI-Backed InfraValue
- Property detail shows **AI InfraValue** section: fair-value range + verdict (under / within / above fair) + 3-4 key factors + 2-3 risks.
- Backend calls Emergent LLM (gpt-4o-mini) with locality snapshot, lifestyle scores, and infrastructure context; falls back to deterministic heuristic if LLM fails. Result cached in `ai_valuations` collection.
- Endpoint: `GET /api/properties/{pid}/ai-valuation?refresh=`.

### Admin token
- `infrajagat-admin` (stored in `/app/backend/.env` as `ADMIN_TOKEN`). Used for news review, verification review, and admin lead inspection.

## Phase 3 — Fixes & Convenience (Oct 2026) ✅ Shipped

### Removed
- **"Save & alert me" chip** on Explore and the Profile → "Saved searches & alerts" menu entry (backend endpoints retained but unused).

### Fixed
- **Vertical scroll** in Explore's list view: trending areas, verified spotlight, under-₹50 L, plots under ₹80 L, ready-to-move and all-properties now scroll inside a proper ScrollView container.
- **"Back to listings"** pill on the Explore map pin-preview is now a highlighted brandTertiary pill (large hitSlop) on both native and web variants.
- **Property-detail back button** now falls back to `/(tabs)/explore` when `router.canGoBack()` is false (handles deep links).
- **Hamburger (`menu-outline`) icon** replaced with gear (`settings-outline`) across all 5 tab headers (Explore, Agents, News, Market, Saved).

### New
- **Finance & Investment Advisors** agent category (`acat-finance`) with 3 seeded agents (CA Nikhil Mehta, Riya Khandelwal, Suresh Kabra). Agent categories are now re-synced on every backend startup so seed edits propagate.
- **Zomato-style location picker** (`/location-picker`): current-location detection via `expo-location`, locality search, popular cities grid (Jaipur / Jodhpur / Udaipur / Ajmer / Kota / Bikaner), saved places list.
- **Saved addresses** (`/addresses`): add/edit/remove multiple addresses with Home / Work / Other tags, pincode support; one is marked ACTIVE and surfaces in the Explore header's new `header-location-pill`.
- Location is persisted via Zustand + AsyncStorage under `infrajagat.location.v1`.
- **News sharing** — each news card now has a Share button → modal with **WhatsApp**, **Instagram** and **More** (native share sheet) options.
- **Offline news reads** (`/offline-news`): tap "Save offline" on any news card to persist it locally via AsyncStorage; `menu-offline-news` entry in Profile opens the list; remove individually or clear all.

## Phase 4 — Explore polish + Parcha scanner (Oct 2026) ✅ Shipped

### Explore map
- **Pin-preview snap**: bottom sheet is now capped at a single ~55% snap when a property is selected, with `topInset` so the top chrome (location pill, search, Buy/Rent/Sell, chip row) is always visible. Tapping a pin auto-snaps to this middle position.
- **"Back to listings"** pill remains a prominent brandTertiary chip with large hitSlop; no longer overlapped.
- **"View on map"** CTA added at the top of each property's description.

### Category sub-filters
- A secondary chip row appears below the main category chips when a category is selected:
  - **Apartment / Villa** → BHK quick-pills (1+, 2+, 3+, 4+)
  - **Residential Plot / Agricultural Land / Commercial** → area buckets (<100, 100–500, 500–2 K, 2 K+ sq yd)
  - Shared **price buckets** (<₹50 L, ₹50 L–1 Cr, ₹1–3 Cr, ₹3 Cr+)
  - Row is hidden when 'All' is selected; `subfilter-clear` resets everything; switching categories auto-resets sub-filters.

### Parcha scanner (Market)
- **`scan-parcha-cta`** banner on the Market materials home opens `/market/scan-parcha`.
- Camera view (via `expo-camera`) with capture framing guide and gallery fallback.
- Image uploads to object storage, then **`POST /api/materials/scan-parcha`** sends it to Emergent LLM (gpt-4o vision) which extracts `{name, quantity, unit, brand, raw}` items.
- Backend matches each extracted item against the materials catalogue and **picks the cheapest vendor** per line; unmatched items are shown separately.
- One-tap **"Add all to cart"** pushes everything into the existing Zustand materials cart. Scan history is stored in `parcha_scans` collection.
- Added iOS `NSCameraUsageDescription` + Android `android.permission.CAMERA` to `app.json`.



