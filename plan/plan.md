# InfraJagat — Engineering Handbook

A map-first, mobile-first real-estate discovery and intelligence app for India, pairing every property with a locality valuation range, a government DLC benchmark and the infrastructure being built around it.
It is Zillow's clarity, Airbnb's map interaction and Zomato's category depth, adapted for how Indians actually buy, rent, book and build homes.

## Who it's for

- **Serious end-buyers and investors** researching a Tier-2 Indian city — people who want median asking price, government valuation, price trend, lifestyle score and incoming infrastructure before committing crores.
- **Working brokers, developers and land aggregators** who need a distribution surface with WhatsApp-native leads, tiered verification and a professional profile that appreciates as they earn reviews.
- **Home-project decision makers** (owners building, interiors, rental move-in) who need architects, contractors, materials and move-in services in one place.
- **Ancillary professionals** — JDA / land-use liaison, registry agents, property lawyers, RERA consultants and home-loan advisors — who currently rely on word of mouth for leads.

First user is an Indian, aged 22–45, comfortable on WhatsApp, researching property in Jaipur.

## Core features and experience

### Brand & shell

- Name **InfraJagat**, tagline **Know Before You Buy.**
- Five bottom tabs: **Explore · Agents · News · Market · Saved**.
- Palette locked to Ivory background, Deep Navy display type, Terracotta primary action.
- Indian number formatting across the app (`₹72 L`, `₹1.85 Cr`, `12,500/sq yd`).
- WhatsApp is the default contact rail; Call is the fallback; Email appears only on Contact-us.
- Heat gradient (green → yellow → red) is used in exactly one place — the Explore price heatmap.

### Onboarding (`/onboarding`)

- Form: name, 10-digit mobile, free-text city / town / village, required **profession** chip (Buyer, Investor, Seller, Broker, Developer, Architect, Contractor, Loan Advisor, Lawyer, Other).
- No password. Submits to `/otp`.

### OTP verification (`/otp`)

- 4-digit input with per-box focus progression and a `Verify & continue` CTA.
- MVP accepts **0000** only, with a visible hint chip.
- Resend OTP with countdown, Change number returns to onboarding, back arrow to onboarding.
- Only after correct OTP does the client call `POST /api/auth/onboard` and persist the user.
- Scaffold for Phase 2 — swap the client-side `MOCK_OTP` for a server endpoint without touching the UI.

### Explore (map-first home tab, `/explore`)

Top chrome:

- Greeting pill `Hi, {firstName}` + ☰ profile button + `+ List` CTA.
- Search bar for locality / project / road.
- **Buy / Rent / Book** segmented control (3 chips).
- Horizontal category chip row — All · Apartments · Villas · Plots · Agricultural Land · Commercial · Industrial.
- Heat toggle chip that flips the map into a price heatmap.

Main view:

- Native: `react-native-maps` with OSM tiles + custom price pins; a `Circle` overlay per locality when Heat is on; a floating heat legend.
- Web: list-first fallback that renders the same pins as a cloud with the heatmap grid.

Draggable bottom sheet (`@gorhom/bottom-sheet`, snap points 22% / 55% / 92%):

- Header switches context:
   - Nothing selected: `{N} properties` on the left, `Map / List` toggle on the right.
   - A pin is selected: `← Back to listings` + `SELECTED` kicker. Map/List toggle hides.
- Map view (default): Trending localities horizontal strip + full property list.
- List view: Airbnb-style curated feed with these sections:
   - **Trending areas** sorted by YoY asking-price movement, each row showing median ₹/sq yd, DLC rate, YoY % and lifestyle score.
   - **Best Deals** — properties asking at least 5% under the InfraValue midpoint.
   - **Verified Spotlight** — verified-only grid.
   - **Under ₹50 L**, **Plots under ₹80 L**, **Ready to Move**, **All properties**.
- Pin preview (when a pin is tapped):
   - Hero image, big price, `Below InfraValue` deal ribbon when applicable.
   - InfraValue range vs Government DLC row.
   - Verified pill, type pill.
   - **Heart button** (`pin-preview-like`) that saves/unsaves via `POST /api/saved/toggle`.
   - "Listed by" mini card: agent avatar, name, firm, RERA line, inline WhatsApp + Call.
   - `View full details` CTA → `/property/{id}`.
   - **Similar Properties** horizontal slider; each card has a **Show on map** chip that deep-links to `/explore?highlight={id}`.

### Property detail (`/property/[id]`)

- Hero gallery, big price, type/area/bedrooms/facing/road width/source/dimensions.
- **InfraValue™** block with range, confidence (High / Medium / Low), methodology disclaimer.
- Side-by-side **Asking price · InfraValue · Government DLC** compare row.
- Save heart in header + title bar.
- `Listed by` card (agent name/firm/RERA/phone, verified check, tap routes to `/agent/{id}` when a broker/developer; synthetic owner card when source is Owner).
- Locality row with median ₹/sq yd + YoY, taps through to `/locality/{id}`.
- **Similar properties** horizontal slider, each with a per-item **Show on map** chip.
- Bottom bar: **WhatsApp (prefilled)** + **Call {firstName}**.
- Every visit is silently added to Recently Viewed via `@/src/utils/history`.

### Locality intelligence (`/locality/[id]`)

- Hero image, city, tagline.
- Metric cards: median asking price, government DLC rate, listings count, 1-year price movement.
- **InfraValue estimated range** card with methodology.
- **Neighbourhood Lifestyle Score** card — walkability, schools, hospitals, connectivity, safety; coloured bars + overall-score pill.
- **Price history chart** (6 years, SVG) toggleable between Listing · Est. Range · Government rate.
- **Government vs Market** compare strip.
- **Infrastructure timeline** — metro, road, airport, industrial, hospital, university, SEZ, commercial-hub projects with status + distance.
- **Hyperlocal news** list.
- Live listings grid.
- Save heart in header + Follow locality button.

### Agents (`/agents`)

- Search bar + category grid (7 role categories).
- Top-rated carousel at the top (sorted by rating × reviews).
- Full agent list with filters: Verified · Featured · Area.
- Each card shows avatar, verified check, **Bronze / Silver / Gold** tier pill, rating, review count, firm, specialties.

### Agent category (`/agent-category/[id]`)

- Category header + sort controls (Top rated / Most reviews / Most experienced).
- List of agents in the category with tier badges.

### Agent detail (`/agent/[id]`)

- Avatar, name, firm, verified + big **Gold/Silver/Bronze verified agent** badge, category chip.
- Rating · Reviews · Years-experience stats row.
- RERA ID, coverage areas, specialties, languages, about.
- Recent listings strip (for brokers / land aggregators).
- Bottom bar: **WhatsApp + Call + Send enquiry** sheet (name/mobile/message → `POST /api/agents/{id}/enquiries`).

### News (`/news`)

- Sticky header `InfraJagat News` + category chips (All · Infrastructure · Government · Land · Development · Industrial · Commercial · Residential).
- Pull-to-refresh.
- Each card: headline, 60-word summary, locality chip, date, source. Tapping a locality chip routes to `/locality/{id}`.

### Market — construction ecosystem (`/market`)

- Header + search bar.
- Six lifecycle group tiles with icons: **Design · Build · Materials · Interiors · Move In · Maintenance**.
- Group drilldown shows categories grid with supplier counts.
- Featured suppliers horizontal strip.

### Market category (`/market-category/[id]`)

- Supplier list with sort (Top rated / Most reviews) + verified-only filter.
- Each supplier card: logo, name, tagline, rating, coverage, verified check, starting price pill.

### Supplier detail (`/supplier/[id]`)

- Hero, rating, verified, starting price, coverage, about, offerings pills.
- **Reviews section** — star + text, submitted via `POST /market/suppliers/{id}/reviews`.
- Bottom bar: **WhatsApp + Call + Request Quote** sheet (`POST /market/quote-requests`).

### Saved (`/saved`)

- Segmented tabs: **Properties · Localities**.
- **Properties tab** — saved property cards with a Compare-mode toggle.
   - In Compare mode each card gets a checkbox; the user picks 2–4 and taps `Compare` → routes to `/compare?ids=...`.
- **Localities tab** — followed localities.
- Both tabs pull-to-refresh.

### Compare (`/compare?ids=`)

- Side-by-side table (2–4 columns) with thumbnails and rows: Price · Area · Price/unit · Bedrooms · Facing · Locality · InfraValue · Govt DLC · Verified · and a smart `% under / over InfraValue` delta chip.

### List property wizard (`/list-property`)

Seven-step wizard with progress bar:

1. Property type
2. Location (locality + map pin)
3. Details (area, unit, bedrooms, facing, road width, description)
4. Price
5. Photos (upload to Emergent Object Storage via `POST /api/upload`)
6. Ownership / Seller type (Owner · Broker · Developer)
7. Contact + preview + submit → `POST /api/properties`, listing marked `Verification Pending`.

### Profile / Menu (`/profile`)

- User card: initials avatar, name, mobile, profession + city pills.
- Stats row: Saved · Following · Enquiries · Listings (powered by `GET /api/user/{uid}/activity`).
- Grouped sections:
   - **Account** — History (`/history`) · Enquiries & orders (`/orders`) · Subscriptions (`/subscriptions`)
   - **Business** — Work with us / Become an agent (`/become-agent`) · List with us (`/list-property`)
   - **Help** — Contact us (`/contact-us`) · About
   - Sign out (clears AsyncStorage).

### Subscriptions (`/subscriptions`)

- Free / Pro / Business tier cards with feature lists.
- "Coming soon" buttons — payments gated to Phase 2.

### History (`/history`)

- Recently-viewed properties pulled from AsyncStorage (`history_v1`, FIFO, max ~20).
- Property cards + Clear history CTA.

### Enquiries & orders (`/orders`)

- Two-tab screen: Agent enquiries + Supplier quote requests.
- Each entry shows the agent/supplier avatar, firm/name, submitted date, status pill.

### Become an agent (`/become-agent`)

- Structured application form: name, mobile, firm, role chips (Broker / Developer / Land Aggregator / JDA Liaison / Registry Agent / Loan Advisor / Lawyer / RERA Consultant), city, RERA ID, notes.
- Submits to `POST /api/agents/{ag-01}/enquiries` with role in the message (admin workflow is Phase 2).

### Contact us (`/contact-us`)

- WhatsApp / Call / Email tiles.
- Common help topics list.

## User flow

- **First-time buyer.** Opens app → onboards (name/mobile/city/profession) → **OTP screen** → enters `0000` → lands on Explore in Buy mode → sees Jaipur price map → flips **Heat** → spots a green cell → taps a pin → pin preview shows price + **Below InfraValue** ribbon → taps heart to save → taps **View full details** → reads locality intelligence, lifestyle score, price history → taps **WhatsApp** on the Listed-by card → chat opens with the agent, listing prefilled.
- **Rental seeker.** Explore → flips **Rent** → sees six rentals with monthly prices → taps a pin → saves → opens Saved tab.
- **Pre-launch booker.** Explore → flips **Book** → sees six pre-launch / under-construction projects → opens one → taps WhatsApp to request the booking kit.
- **Comparison shopper.** Saves 3 properties across sessions → opens **Saved** → turns on Compare mode → picks all three → opens `/compare?ids=...` → reviews InfraValue deltas → picks one → WhatsApps the agent.
- **Locality-first researcher.** Opens **News** → reads a Ring Road story → taps the locality chip → reviews lifestyle score + infrastructure timeline → follows the locality.
- **Home builder.** Opens **Market** → Build group → Contractors → opens a supplier → reads reviews → leaves a star + note → taps **Request Quote**.
- **Working broker.** Onboards with profession Broker → ☰ → **Work with us** → submits firm + RERA + coverage → list properties → receives WhatsApp enquiries which land in Enquiries & orders.

## UI/UX feel

- Premium PropTech aesthetic — the opposite of a cluttered Indian portal.
- Large readable numbers, generous whitespace, subtle shadows, minimal borders.
- Thumb-friendly 44×48 pt targets, bottom-sheet with physical gestures.
- Pin preview, Lifestyle Score, Agent-tier badges and the Below-InfraValue ribbon are the only coloured rewards — each carries real information.
- Heart, WhatsApp and Call are rendered as full icons at thumb height.
- Entire app uses tokens from `src/theme.ts`; no hex literals except for third-party brand colours (WhatsApp green).

## Tech architecture

### Frontend

- **Expo SDK** (React Native + TypeScript) with **expo-router** file-based navigation.
- Tabs under `app/(tabs)/`, modal/stack routes under `app/`.
- `@gorhom/bottom-sheet` v5 with `BottomSheetView` + `BottomSheetScrollView` children and `enableDynamicSizing={false}` (required for iOS).
- `react-native-maps` with the default provider → OSM tiles. `Marker`, `Circle` overlays. Web fallback: hand-rolled pin cloud + heat-grid.
- `react-native-reanimated`, `react-native-gesture-handler`, `react-native-safe-area-context`.
- `@react-native-vector-icons/ionicons` for all icons.
- `expo-image` for images, `expo-image-picker` for list-property uploads, `expo-blur` for sheet accents.
- `react-native-svg` for the custom price-history chart.
- `@tanstack/react-query` for data fetching; `@react-native-async-storage/async-storage` for user + history.
- Theme tokens live in `src/theme.ts`; `useTheme()` for light/dark awareness.
- Shared utilities under `src/utils/`:
   - `format.ts` → `formatINR`, `indianComma`, `formatRange`
   - `heat.ts` → `heatColor`, `heatLabel`
   - `tier.ts` → `tierColor`, `tierBgColor`
   - `history.ts` → `addHistory`, `listHistory`, `clearHistory`
   - `contact.ts` → `openWhatsApp`, `openTel`
- Shared components under `src/components/`: `property-card`, `locality-card`, `price-chart`, `pin-preview`, `explore-list-view`.

### Backend

- **FastAPI** (Python) + **motor** (async MongoDB driver) + **Pydantic**.
- Single `api_router` prefixed `/api`.
- Idempotent `seed_if_needed` on startup; backfill ensures legacy records get `listing_type: "Buy"`.
- `pick_lister(prop)` deterministically maps a property id to an agent so every property has a "Listed by" card.
- `with_lifestyle(locality)` and `with_tier(agent)` enrich responses on the way out.
- Object storage via Emergent proxy (`init_storage` + `put_object` + `get_object`); property photos round-trip through `/api/upload` and `/api/files/{path}`.
- Universal LLM key provisioned at `EMERGENT_LLM_KEY` for future AI features; not yet exercised.

### Data model (MongoDB collections, `_id` always stripped on egress)

- **users** `{ id, name, mobile (unique), area, profession, created_at }`
- **localities** `{ id, name, city, state, lat, lng, image, tagline, median_price_per_sq_yd, govt_dlc_per_sq_yd, estimated_range_low, estimated_range_high, yoy_change_pct, confidence, is_demo }` (lifestyle computed via `enrich.with_lifestyle`)
- **properties** `{ id, locality_id, locality_name, city, state, title, type, listing_type: "Buy"|"Rent"|"Book", price, area, area_unit, price_per_unit, bedrooms, facing, road_width_ft, lat, lng, address, verified, verification_status?, source: "Owner"|"Broker"|"Developer", images, listed_at, is_demo, owner_user_id? }`
- **price_history** `{ locality_id, series: [{year, listing, govt, est_low, est_high}] }`
- **infrastructure** `{ id, name, type, status, expected_completion, distance_km, source, source_url?, locality_ids: [] }`
- **news** `{ id, title, summary, locality_id, category, date, source, image? }`
- **saved** `{ user_id, property_id, created_at }`
- **follows** `{ user_id, locality_id, created_at }`
- **market_groups** `{ id, name, subtitle, icon }`
- **market_categories** `{ id, group_id, name, image }` (`suppliers_count` enriched at read)
- **suppliers** `{ id, category_id, name, tagline, city, area, rating, reviews, verified, featured, offerings: [], starting_price?, phone, whatsapp?, image, about }`
- **supplier_reviews** `{ id, supplier_id, user_id?, name, rating (1-5), text?, created_at }`
- **quote_requests** `{ id, supplier_id, user_id?, name, mobile, message?, status, created_at }`
- **agent_categories** `{ id, name, icon }` (`agents_count` enriched at read)
- **agents** `{ id, category_id, name, firm?, city, area, rating, reviews, verified, featured, years_exp, languages: [], specialties: [], coverage: [], rera_id?, phone, whatsapp?, image, about }` (`tier` computed via `enrich.with_tier`)
- **agent_enquiries** `{ id, agent_id, user_id?, name, mobile, message?, status, created_at }`

### REST API — complete endpoint list

Health
- `GET /api/health`

Auth
- `POST /api/auth/onboard` — body `{name, mobile, area?, profession?}` → `{user}` (upserts on mobile; preserves profession when omitted)
- `GET /api/auth/me?user_id=`

Localities
- `GET /api/localities` — array with lifestyle
- `GET /api/localities/{loc_id}` — detail + `price_history`, `infrastructure`, `news`, `properties_count`, `lifestyle`

Properties
- `GET /api/properties` — filters `type`, `listing_type`, `locality_id`, `min_price`, `max_price`, `bedrooms`, `verified_only`, `source`, `q`, `limit`
- `GET /api/properties/{pid}` — attaches `locality`, `infravalue {low, high, confidence}`, `govt_value`, `lister`
- `GET /api/properties/{pid}/similar?limit=6` — same type + listing_type, price ±60%, same-locality first
- `POST /api/properties` — body `PropertyIn`; new listings default `verified=false`, `verification_status="Verification Pending"`

Infrastructure, News
- `GET /api/infrastructure?locality_id=`
- `GET /api/news?locality_id=&category=&limit=50`

Saves, Follows
- `POST /api/saved/toggle` `{user_id, property_id}` → `{saved}`
- `GET /api/saved?user_id=`
- `POST /api/follows/toggle` `{user_id, locality_id}` → `{following}`
- `GET /api/follows?user_id=`

Uploads
- `POST /api/upload` multipart `file`, optional `user_id` → `{storage_path, url}`
- `GET /api/files/{path:path}`

Market
- `GET /api/market/groups` — groups with nested categories + `suppliers_count`
- `GET /api/market/categories?group_id=`
- `GET /api/market/suppliers?category_id=&group_id=&q=&featured_only=&verified_only=&city=`
- `GET /api/market/suppliers/{sid}` — supplier + attached `category`
- `POST /api/market/quote-requests` `{supplier_id, user_id?, name, mobile, message?}`
- `GET /api/market/suppliers/{sid}/reviews`
- `POST /api/market/suppliers/{sid}/reviews` `{user_id?, name, rating (1-5), text?}`

Heatmap
- `GET /api/heatmap` → `{min, max, points: [{id, name, lat, lng, median_price_per_sq_yd, govt_dlc_per_sq_yd, intensity}]}`

Agents
- `GET /api/agent-categories`
- `GET /api/agents?category_id=&q=&verified_only=&featured_only=&area=`
- `GET /api/agents/{aid}` — with `category`, `recent_listings` for brokers/land aggregators, computed `tier`
- `POST /api/agents/{aid}/enquiries` `{user_id?, name, mobile, message?}`

Compare
- `GET /api/compare?ids=p1,p2,p3,p4` — up to 4 properties, each fully enriched

User activity
- `GET /api/user/{uid}/activity` → `{saved, follows, my_listings, quote_requests, agent_enquiries}` with embedded property / locality / supplier / agent snapshots

### Derived intelligence rules

- **InfraValue estimate** = `locality.estimated_range_low..high × area` (unit-converted; `sq ft ÷ 9 ≈ sq yd`). Confidence inherits the locality's confidence label.
- **Government value** = `locality.govt_dlc_per_sq_yd × area` (unit-converted).
- **Below InfraValue ribbon** when asking price is ≥ 5% under the InfraValue midpoint.
- **Agent tier** (`enrich.with_tier`):
   - Gold → verified + RERA + reviews ≥ 100
   - Silver → verified + (RERA or reviews ≥ 50)
   - Bronze → verified
   - Unverified → otherwise
- **Lifestyle overall** = `round(mean(walkability, schools, hospitals, connectivity, safety))`.
- **Lister picker** — Owners get a synthetic contact derived from the property id; Broker/Developer listings get a deterministic broker from the `acat-broker` category (hash by pid).
- **Similar properties** — same `type`, same `listing_type`, price within ±60% of the subject; same-locality first, then global, deduped.

### Seed data (demo, labelled)

- 7 Jaipur localities: Ajmer Road, Jagatpura, Tonk Road, Vaishali Nagar, Mansarovar, Sikar Road, Sirsi Road.
- 42 properties — 30 Buy + 6 Rent + 6 Book (pre-launch / under-construction / plotted-township projects).
- Price history: 6 years per locality.
- 7 infrastructure projects spanning Metro, Road, Highway, Airport, Industrial, Hospital, Commercial Hub.
- Hyperlocal news items distributed across localities and categories.
- 7 agent categories × 13 agents (Property Brokers, Land Aggregators, JDA / Land-Use Liaison, Registry & Stamp Duty, Property Lawyers, Home Loan Advisors, RERA Consultants).
- 6 market groups × 24 categories × 26 suppliers across Design → Maintenance.

### Environment & infrastructure

- `MONGO_URL`, `DB_NAME` — local MongoDB in preview; production per deploy.
- `EMERGENT_LLM_KEY` — Emergent Universal Key (LLM + managed Object Storage).
- `INTEGRATION_PROXY_URL` — Emergent integrations proxy (default `https://integrations.emergentagent.com`).
- Backend binds `0.0.0.0:8001`; ingress routes `/api/*` to it.
- Frontend reads `EXPO_PUBLIC_BACKEND_URL` for every API call.
- Supervisor manages `backend` and `expo` services.
- Yarn is the package manager, pinned to the Expo SDK via `yarn expo install`.

### Known constraints (today)

- OTP is mocked at `0000`; no SMS provider wired.
- Payments are not wired; subscriptions screen renders "coming soon".
- Push notifications are not wired.
- Map interactivity (pins, heat circles) is native-only; the web preview renders a list fallback.
- No multi-city switcher; the Explore hero implies Jaipur.
- Admin panel is not shipped; verification is a flag on the record.

## Implementation phases

### Phase 1 — Public MVP for Jaipur (shipped now)

Everything described above: discovery, intelligence, lead capture, Buy / Rent / Book listings, Agents directory with tier badges, Market construction ecosystem with reviews, Saved + Compare, 7-step List Property wizard, Profile with Work-with-us / Subscriptions / History / Enquiries / Contact-us. Free, no payments, no OTP SMS. Ready to hand-invite agents and developers to populate real listings.

### Phase 2 — Broker & developer operating layer + monetisation (not yet built)

- Real SMS OTP (Twilio / MSG91 / Karix); keep client-side `MOCK_OTP` fallback.
- Payments live for Pro / Business subscriptions (Stripe or Razorpay).
- Featured listings — brokers pay per listing per month for top placement.
- Lead-based pricing — WhatsApp click + enquiry events priced by locality demand.
- Developer sponsored projects on the locality page and Explore Book tab.
- Document-Verified badge via a review workflow (title / khasra / RERA uploads).
- Saved-search alerts + push notifications ("Plots in Ajmer Road under 80 Lakh").
- **Locality Compare** (mirrors property Compare).
- Home-loan instant quote on every property card.
- Agent / developer analytics dashboard (views, WhatsApp clicks, saves, enquiries).
- Supplier lead-gen monetisation on the Market tab.
- Admin dashboard — moderate listings, verify agents, manage categories, publish news.

### Phase 3 — Real-world data ingestion & advanced intelligence (not yet built)

- Government DLC / circle-rate ingestion via state portals.
- RERA project registry ingestion for developers and new launches.
- GIS layers (JDA / municipal boundaries, land-use classification, master-plan zones).
- Transaction indicators from state registration portals where public.
- Off-market whispers — a private feed of verified-broker off-market listings unlocked only for profession-verified users.
- AI-backed InfraValue — swap the heuristic for a learned model trained on ingested transaction + listing data; the Emergent LLM key is already wired.
- Multi-language UI, starting with Hindi.
- City-by-city expansion — Ajmer, Udaipur, Kota next, each with seeded intelligence + ten verified agents before public launch.

## Assumptions

- Auth stays lightweight for launch: name + mobile + city + profession + mock OTP (`0000`). No password, no social auth, no device binding. Real SMS deferred to Phase 2.
- Map provider is OpenStreetMap tiles via `react-native-maps`. No Google / Mapbox key.
- Web preview is a companion, not the product. Native-only behaviours (interactive map, pin gestures, bottom-sheet physics, WhatsApp deep links, camera uploads) are only fully alive in Expo Go or a native build.
- Rentals and Book stay inside the same Explore tab as Buy, flipped via a segmented control.
- Compare lives inside the Saved tab.
- WhatsApp is the default lead channel for every property, agent and supplier.
- All prices, DLC values, lifestyle scores, YoY movements, news items and agent/supplier records are **demo data** until real datasets replace them. Nothing fabricated is presented as verified government information.
- First city is Jaipur; the Explore hero implies "Jaipur" and there is no multi-city switcher.
- No payments in Phase 1; the Subscriptions screen shows tiers with "coming soon".
- Push notifications are out of scope for Phase 1.
- Property photos and listing uploads go to Emergent Object Storage; nothing base64-encoded in the database.
- Profession is required at onboarding; it personalises the feed and gates Phase-3 off-market content.
- Admin / moderation flows are Phase 2; v1 ships with `verified` as a flag seeded on each demo record.
- Data provenance in Phase 3 starts with broker- and user-submitted listings; government DLC and RERA come in over time. No dependency on a third-party data partnership before public launch.
- The InfraJagat name, **Know Before You Buy.** tagline and the Ivory / Deep-Navy / Terracotta palette are locked and should not be revisited without an explicit brand review. **InfraValue™** is the estimation-method trademark and intentionally stays as-is even after the InfraLocal → InfraJagat rename.
