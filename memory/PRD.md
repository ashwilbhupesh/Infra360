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
- **Explore (tab)** — hero, search, category chips, "Explore on Map" CTA, trending localities, featured properties, InfraValue explainer.
- **Map (tab)** — native: react-native-maps + price pins + bottom sheet of swipeable cards; web fallback: filters + cluster + list.
- **News (tab)** — Inshorts-style category feed.
- **Saved (tab)** — Saved properties + followed localities + sign-out.
- **Property Detail** — hero, price, InfraValue vs Govt DLC comparison, details, locality link.
- **Locality Detail** — hero, metric cards, InfraValue range, price history chart (listing / est. range / govt), Govt vs Market compare, infrastructure timeline, news, listings.
- **List Property** — 7-step wizard (Type → Location → Details → Price → Photos → Seller → Preview).

## Data
- Seeded 7 Jaipur localities, ~30 properties, 7 infrastructure projects, 7 news items — all clearly demo.

## Key API
- `POST /api/auth/onboard`
- `GET /api/localities`, `GET /api/localities/{id}` (includes price_history + infra + news)
- `GET /api/properties?type=&locality_id=&q=&verified_only=`
- `GET /api/properties/{id}` (includes infravalue estimate + govt_value)
- `POST /api/properties`
- `GET /api/infrastructure`, `GET /api/news`
- `POST /api/saved/toggle`, `GET /api/saved`
- `POST /api/follows/toggle`, `GET /api/follows`
- `POST /api/upload`, `GET /api/files/{path}`
