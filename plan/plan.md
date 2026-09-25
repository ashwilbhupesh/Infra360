# InfraLocal — Know Before You Buy

InfraLocal is a map-first, mobile-first real-estate discovery and intelligence app for India that pairs every property with a locality-level valuation range, a government DLC benchmark, and the infrastructure being built around it.
It is Zillow's clarity, Airbnb's map interaction and Zomato's category depth, adapted for how Indians actually buy, rent and build homes.

## Who it's for

- **Serious end-buyers and investors** researching a locality in a Tier-2 Indian city — people who want to know median asking price, government valuation, price trend, lifestyle score and what infrastructure is coming before they commit crores.
- **Working brokers, developers and land aggregators** who need a distribution surface with WhatsApp-native leads, tiered verification and a professional profile that appreciates as they earn reviews.
- **Home-project decision makers** (owners planning a build, interiors, rental move-in) who need architects, contractors, cement, steel, packers and AMC providers in one place.
- **Ancillary professionals** — JDA / land-use liaison, registry agents, property lawyers, RERA consultants and home-loan advisors — who currently rely on word of mouth for leads.

The first user is an Indian, aged 22–45, comfortable on WhatsApp, researching property in Jaipur.

## Core features and experience

**Explore (the map-first home tab)**
A single tab that behaves like Zillow's search map. Sticky top: greeting with the buyer's name, a menu button that opens the profile, a "List" call to action, a search bar, a Buy / Rent segmented toggle and category chips (Apartment, Villa, Plot, Land, Commercial). A Heat toggle turns the map into a green-to-red price heatmap by locality. A bottom sheet drags up over the map with a Map / List view toggle. In List view the sheet becomes an Airbnb-style curated feed: Trending Areas in the city with YoY movement, lifestyle score and confidence pill; Best Deals below InfraValue; Verified Spotlight; Under 50 Lakh; Plots under 80 Lakh; Ready to Move; all listings.

**Pin preview (tap a price on the map)**
The sheet snaps up and shows a rich in-app preview: hero photo, big price, a "Below InfraValue" ribbon when the ask is under the estimated midpoint, InfraValue range vs government DLC side by side, a "Listed by" mini card with agent avatar, firm, RERA and inline WhatsApp + Call buttons, a horizontal Similar Properties slider (each with its own "Show on map" chip that jumps back to Explore with that property highlighted), and a prominent "View full details" button.

**Property detail**
Full-screen gallery, price, ownership type, area, dimensions, facing, road width, source. InfraValue™ block with confidence label (High / Medium / Low) and disclaimer, side-by-side comparison of asking price, InfraValue and government DLC, a Similar Properties strip with per-item "Show on map", a locality link, and a bottom bar with WhatsApp + Call. Every visit is silently added to the buyer's Recently Viewed history.

**Locality intelligence page**
Hero image, city, tagline. Metric cards: median asking price, government DLC rate, listings count, 1-year price movement. InfraValue estimated range with methodology. A signature **Neighbourhood Lifestyle Score** card with walkability, schools, hospitals, connectivity, safety and an overall score badge. A price history chart (6 years, toggleable between listing price, estimated range and government rate). Government vs Market comparison strip. Infrastructure timeline listing metro, road, airport, industrial, hospital, university projects with status and distance. Hyperlocal news and the locality's live listings.

**Agents tab**
Directory of brokers, land aggregators, JDA / land-use liaison, registry & stamp duty agents, property lawyers, home-loan advisors and RERA consultants. Search, category grid, top-rated list. Each agent has a **Bronze / Silver / Gold verification tier** derived from RERA + reviews + rating + experience — buyers spot the strongest agent instantly. Detail page shows tier badge, RERA ID, coverage areas, specialties, languages, recent listings, and a bottom bar with WhatsApp + Call + Send-enquiry sheet.

**News tab**
Inshorts-style hyperlocal property feed with category chips (Infrastructure, Government, Land, Development, Industrial, Commercial, Residential). Each card links back to its locality.

**Market tab**
Zomato-style directory covering the full home lifecycle: Design → Build → Materials → Interiors → Move In → Maintenance. Six groups × ~24 categories × supplier listings with rating, verified badge, offerings, starting price and coverage. Supplier detail page carries a Reviews section (star + text, community-driven), WhatsApp + Call + Request Quote flow.

**Saved tab**
Saved properties + followed localities. A Compare mode lets the buyer pick 2–4 properties and open a side-by-side table showing price, area, price per unit, InfraValue, DLC, verification, and a smart "% under / over InfraValue" delta chip.

**List property flow**
7-step wizard: Type → Location (with map pin) → Details → Price → Photos → Ownership / Seller type → Preview → Submit. New listings mark as "Verification pending."

**Profile / Menu**
Reached via the ☰ icon on Explore. User card with initials avatar, mobile, profession and city pills. Four quick stats: Saved, Following, Enquiries, Listings. Grouped sections: Account (History · Enquiries & orders · Subscriptions), Business (Work with us — become an agent · List with us), Help (Contact us — WhatsApp / Call / Email · About). Sign out at the bottom.

**Onboarding**
Name + 10-digit mobile + free-text city / town / village + a profession chip (Buyer, Investor, Seller, Broker, Developer, Architect, Contractor, Loan Advisor, Lawyer, Other). No OTP, no password — kept intentionally light to remove friction.

## User flow

- **First-time buyer.** Opens the app → onboards with name / mobile / city / profession → lands on Explore in Buy mode → sees Jaipur's price map with pins → toggles Heat, spots value pockets → taps a pin → pin preview shows price and Below-InfraValue badge → taps "View full details" → reads locality intelligence, lifestyle score, price history → taps WhatsApp on the "Listed by" card → chat opens with the agent, listing prefilled.
- **Rental seeker.** Explore → flips Buy / Rent toggle → sees six Jaipur rentals with monthly prices → taps a rental → same preview + WhatsApp path.
- **Comparison shopper.** Saves 3 properties over a few sessions → opens Saved tab → enters Compare mode → picks all three → sees side-by-side table with InfraValue deltas → picks one → contacts on WhatsApp.
- **Locality-first researcher.** Opens News tab → reads "Ring Road extension" story → taps the locality link → reviews lifestyle score + infrastructure timeline → follows the locality → saves the search.
- **Home builder.** Opens Market tab → picks Contractors → filters top-rated verified → opens a supplier → reads reviews → taps Request Quote → agent WhatsApps back.
- **Working broker.** Onboards with profession Broker → opens Profile → taps Work with us → submits firm + RERA + coverage → gets verified → publishes listings, receives WhatsApp enquiries in Enquiries & orders inbox.

## UI/UX feel

- Premium, minimal PropTech aesthetic — the opposite of a cluttered Indian portal.
- Ivory background, deep-navy display type, terracotta primary action, muted borders. No gaudy gradients, no cheap card shadows.
- Indian number formatting throughout (72 Lakh, 1.85 Cr, 12,500/sq yd).
- Large readable prices, generous whitespace, subtle typography weight changes.
- Every interactive element is thumb-friendly and reachable in one hand.
- WhatsApp is the default contact rail — one tap, prefilled message, native app opens on the phone.
- Airbnb-style bottom sheet: draggable, three snap points, list feels physical.
- Heatmap uses a controlled green → yellow → red gradient; nowhere else in the app.
- Tier badges (Bronze / Silver / Gold), verified checks, and lifestyle score pills are the only permitted colour rewards — they carry real information.

## Implementation phases

### Phase 1 — Public MVP for Jaipur (built now)

The complete discovery, intelligence and lead-capture experience described above, seeded with realistic Jaipur demo data across seven localities, ~30 sale listings, six rentals, seven agent categories with 13 agents, six lifecycle groups with 24 supplier categories, infrastructure projects, news items and government DLC benchmarks. Free onboarding, no payments, WhatsApp / Call CTAs everywhere. Ready to hand-invite to agents and developers so they populate their own listings.

### Phase 2 — Broker & developer operating layer + monetisation

Turn on the paid side and give power users a real workspace.

- Featured listings — brokers pay per listing per month for top placement in their locality and category.
- Lead-based pricing — WhatsApp click and enquiry submission events are counted, invoiced monthly, priced by locality demand.
- Agent + developer subscription tiers — Bronze / Silver / Gold with progressive perks: unlimited listings, priority routing, analytics, verified badge, featured banner in the locality page.
- Supplier lead-gen on the Market tab — Zomato-style paid categories with monthly plans and pay-per-quote-request tiers.
- Verification system — Document-Verified badge on listings once title / khasra / RERA docs are uploaded; a review workflow for the internal team.
- Saved-search alerts — the promise made by the Free tier: "Plots in Ajmer Road under 80 Lakh" pings you the moment a matching listing appears.
- Locality compare — same side-by-side model as property compare but for localities.
- Home-loan instant quote — inline EMI + eligibility estimate on every property card, with a partner CTA.
- Analytics dashboard — for agents and developers, showing listing views, WhatsApp clicks, saves and enquiries.

### Phase 3 — Real-world data ingestion & advanced intelligence

Replace demo data with defensible datasets and let the differentiation become the moat.

- Government DLC / circle-rate ingestion via state portals; kept fresh with a light scraping + curation pipeline until an API partnership is signed.
- RERA project registry ingestion for developers and new-launch projects.
- GIS layers overlaid on the map: JDA / municipal boundaries, land-use classification, master-plan zones.
- Transaction indicators from state registration portals where public.
- Off-market whispers — a private feed of verified-broker off-market listings unlocked only for profession-verified users.
- AI-backed InfraValue upgrade — swap the current locality-median heuristic for a learned model trained on the ingested transaction and listing data.
- Multi-language UI — Hindi first, then regional languages as new cities come online.
- City-by-city expansion — Ajmer, Udaipur, Kota next, each launched with seeded locality intelligence + at least ten verified agents before opening to the public.

## Assumptions

- **Auth stays lightweight for launch.** Name + mobile + city + profession, no OTP, no password. Fraud is deferred to Phase 2 verification.
- **Map provider.** OpenStreetMap tiles via react-native-maps. No Google or Mapbox key required. Sufficient for city-level detail.
- **Web preview is a companion, not the product.** The interactive map, native pins, bottom-sheet gestures and WhatsApp deep links are only fully alive in Expo Go or a native build.
- **Rentals stay in the same tab as Buy.** Segmented toggle inside Explore, not a separate top-level tab.
- **Compare lives inside Saved.** No dedicated Compare tab.
- **WhatsApp is the default lead channel** for every property, agent and supplier. Call is the fallback. Email is only in Contact-us.
- **Nothing is removed from the current MVP before public launch.** Market, Compare, Heatmap, Rentals and the full agent directory all stay in v1.
- **All prices, DLC values, lifestyle scores, YoY movements and news items are labelled demo data** until real datasets replace them. Nowhere in the UI is fabricated data presented as verified government information.
- **First city is Jaipur.** No multi-city switcher in Phase 1; the Explore hero implies "Jaipur".
- **No payments in Phase 1.** Subscription screen shows Free / Pro / Business tiers with a "coming soon" state so the roadmap is visible without collecting money.
- **Push notifications are out of scope for Phase 1.** Saved-search alerts are a Phase 2 feature.
- **Storage.** Property photos and any uploads go to the managed object store; nothing base64-encoded into the database.
- **A profession value is required at onboarding.** It is stored and used later for personalising the feed and gating off-market content in Phase 3.
- **Data provenance in Phase 3** starts with broker- and user-submitted listings; government DLC and RERA come in over time; no dependency on a third-party data partnership before public launch.
- **The InfraLocal name, "Know Before You Buy." tagline, and the ivory / deep-navy / terracotta palette are locked** and shouldn't be revisited without an explicit brand review.
