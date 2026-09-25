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
- Simple name + mobile + area of interest. No OTP. User stored in AsyncStorage.

## Screens
- **Onboarding** — name/mobile/area chips.
- **Explore (tab)** — hero, search, category chips, "Explore on Map" CTA, trending localities, featured properties, InfraLocal News CTA, InfraValue explainer. Header shows quick-access **Saved** heart icon.
- **Map (tab)** — native: react-native-maps + price pins + bottom sheet of swipeable cards + **Price Heatmap toggle** (Circle overlays). Web fallback: filters + heat-cell grid legend + list.
- **Agents (tab)** — Discovery of brokers, land aggregators, JDA / land-use liaison, registry agents, property lawyers, home-loan advisors, RERA consultants. Category grid + top-rated list + search.
- **Market (tab)** — Zomato-style construction ecosystem directory (Design → Build → Materials → Interiors → Move In → Maintenance).
- **Saved** — Saved properties + followed localities + **Compare mode** (select 2–4 properties → side-by-side table). Accessed from Explore header.
- **News** — Inshorts-style category feed (accessed via Explore CTA).
- **Property Detail** — hero, price, InfraValue vs Govt DLC comparison, details, **"Listed by" card** (agent name, firm, RERA, phone), locality link. Bottom bar: **WhatsApp + Call**.
- **Agent Detail** — avatar, verified badge, RERA ID, rating/reviews/years, specialties, coverage, languages, recent listings; Bottom bar: **WhatsApp + Call + Send enquiry** sheet.
- **Supplier Detail** — hero, rating, offerings, starting price, **Reviews section** (write + list), Call + Request Quote CTAs; Bottom bar: **WhatsApp + Call + Quote**.
- **Compare** — side-by-side table for up to 4 properties (price, area, InfraValue, DLC, delta chip, verification).
- **Locality Detail** — hero, metric cards, InfraValue range, price history chart, Govt vs Market compare, infrastructure timeline, news, listings.
- **List Property** — 7-step wizard with photo upload.

## Data
- Seeded 7 Jaipur localities, ~30 properties, 7 infrastructure projects, 7 news items — all clearly demo.

## Key API
- `POST /api/auth/onboard`
- `GET /api/localities`, `GET /api/localities/{id}` (includes price_history + infra + news)
- `GET /api/properties?type=&locality_id=&q=&verified_only=`
- `GET /api/properties/{id}` (includes infravalue estimate + govt_value + **lister**)
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
