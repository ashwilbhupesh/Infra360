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
- **Explore (tab)** — hero, search, category chips, "Explore on Map" CTA, trending localities, featured properties, InfraLocal News CTA, InfraValue explainer.
- **Map (tab)** — native: react-native-maps + price pins + bottom sheet of swipeable cards; web fallback: filters + cluster + list.
- **Market (tab)** — Zomato-style construction ecosystem directory: 6 lifecycle groups (Design → Build → Materials → Interiors → Move In → Maintenance), 24 categories, ~26 suppliers with rating, verified badge, offerings, starting price, quote request bottom sheet.
- **Saved (tab)** — Saved properties + followed localities + sign-out.
- **News** — Inshorts-style category feed (accessed via Explore CTA).
- **Property Detail** — hero, price, InfraValue vs Govt DLC comparison, details, locality link.
- **Locality Detail** — hero, metric cards, InfraValue range, price history chart, Govt vs Market compare, infrastructure timeline, news, listings.
- **List Property** — 7-step wizard with photo upload.
- **Market Category** — sortable supplier list with rating / reviews / verified filters.
- **Supplier Detail** — hero, rating, offerings, starting price, About; Call + Request Quote CTAs; quote submission bottom sheet.

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
- `GET /api/market/groups` (with categories + supplier counts)
- `GET /api/market/categories?group_id=`
- `GET /api/market/suppliers?category_id=&group_id=&q=&featured_only=&verified_only=&city=`
- `GET /api/market/suppliers/{id}` (with attached category)
- `POST /api/market/quote-requests`
