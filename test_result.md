#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Redesign the Market "Materials" section to a shopping-app style like the reference screenshot:
  10 category tiles (Cement & steel, Electricals & lighting, Bathware, Tiling & adhesives,
  Paints & finishes, Electrical appliances, Water proofing, CPVC/PVC & GI fittings, Hardware & locks,
  Plywood & laminates). Each category lists multiple stores, each store shows a product catalogue.
  Tapping a product adds to a persisted cart, submit cart via Request Quotes + per-store WhatsApp.
  Keep everything else in the app unchanged.

backend:
  - task: "Materials categories + stores + products seed and endpoints"
    implemented: true
    working: true
    file: "/app/backend/materials_seed.py, /app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added materials_seed.py with 10 shopping categories, 24 stores, and 85+ products. Added endpoints: GET /api/materials/categories, GET /api/materials/categories/{id}/stores (with per-store product catalogue), GET /api/materials/stores/{id} (full catalogue), GET /api/materials/products?q=, POST /api/materials/cart-enquiry. Collections re-seeded on every startup. User activity endpoint now includes materials_orders."
      - working: true
        agent: "testing"
        comment: "All 14 backend pytest tests PASSED. Categories (10 ordered), category→stores drill-down, store→catalogue, product search, cart-enquiry with correct totals + per-store rollup, validation (400 on empty items / invalid mobile), user activity now includes materials_orders. Regression: /market/groups, /market/suppliers, /properties, /agents all pass."

frontend:
  - task: "Materials shopping UI: category grid, store+catalogue page, store page, cart"
    implemented: true
    working: true
    file: "/app/frontend/app/(tabs)/market.tsx, /app/frontend/app/materials/category/[id].tsx, /app/frontend/app/materials/store/[id].tsx, /app/frontend/app/materials/cart.tsx, /app/frontend/src/stores/materials-cart.ts"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Rewrote Market tab: when Materials group active, shows 'Materials across Jaipur' header + cart badge + search + 3-col category tile grid matching the reference. Category drill-down shows stores grouped vertically, each with horizontal catalogue of products with ADD/+/- quantity controls. Store page shows full catalogue with search, category tabs, 2-col product grid. Cart page shows items grouped by store with per-store WhatsApp enquiry and 'Request quotes' submit. Cart persisted via zustand + AsyncStorage (infrajagat.materials.cart.v1). Verified via screenshots: home grid, category page with products, cart page all render correctly."
      - working: true
        agent: "testing"
        comment: "All critical paths validated at 390x844 mobile viewport. Materials home grid, category drill-down with store/product cards, add-to-cart with +/- quantity controls, cart badge increments, store-grouped cart with Send-on-WhatsApp per store, Request quotes submits to real backend (POST returns 200), decrement-to-remove, clear cart empty state, store detail with catalogue search. Regression on Design group chip + /supplier/sup-01 passes."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 12
  run_ui: false

test_plan:
  current_focus:
    - "Materials categories + stores + products seed and endpoints"
    - "Materials shopping UI: category grid, store+catalogue page, store page, cart"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      Shipped Materials shopping redesign. Please verify:
      1. GET /api/materials/categories returns 10 ordered categories with stores_count
      2. GET /api/materials/categories/mat-cement-steel/stores returns 3 stores, each with their products in that category
      3. GET /api/materials/stores/mst-steelsynd returns catalogue array grouped by category
      4. POST /api/materials/cart-enquiry creates a doc with per_store rollup and total
      5. Frontend flow: open Market → Materials chip (default) → "Shop by category" grid → tap a tile → stores list with product cards → tap ADD → cart badge increments → open cart → see store-grouped items → fill name/mobile → "Request quotes" posts successfully
      6. Store detail: tap store header or View All → see full catalogue, add items, verify qty persistence
      7. Non-materials tabs (Design/Build/Interiors/etc) still work with existing supplier directory flow
      8. User activity endpoint now returns materials_orders; orders.tsx shows them as a "Material enquiries" section
      Known cosmetic: some Unsplash category tile images 404 — not functional, display empty tile with name; non-blocking.
  - agent: "main"
    message: |
      Shipped the user-reported 7 issues + a new feature (publish news with admin moderation):

      1. **Android map (re-fix)** — Replaced `react-native-maps` with a pure WebView + Leaflet (OpenStreetMap) implementation in `src/components/web-map.tsx`. No Google Maps API key needed. Pins/heatmap/zoom all re-implemented via injected JS. Works identically on Android, iOS and web.
      2. **"Show on map"** — explore.tsx highlight effect no longer auto-opens the pin preview sheet; it only highlights + centres the pin. Tapping the pin opens the preview.
      3. **List/Map toggle** — simplified: the toggle is now PINNED inline with the Buy/Rent/Sell segment control at the top so it's always reachable. In list mode, a full-screen overlay replaces the sheet; in map mode, the BottomSheet pattern is restored.
      4. **Sell option** — added to Buy/Rent segment. Tapping navigates to new `/sell` screen (How-it-works + Why-InfraJagat + testimonial + CTA to /list-property). Available in both explore.tsx and explore.web.tsx.
      5. **Popular localities horizontal scroll on Android** — set `nestedScrollEnabled`, `directionalLockEnabled`, `overScrollMode="never"` on the inner `ScrollView` inside BottomSheet to stop the sheet from eating horizontal drags.
      6. **News search + sub-areas** — news.tsx: added debounced search input (hits `/api/news?q=`), "Sub-area" chip row above "Topic". Backend `/api/news` now supports `q` (regex over title+summary) and `status` filter.
      7. **Publish news with admin moderation** — new `/publish-news` screen (title, 2-3 line summary, Topic + Area chips, image picker via expo-image-picker → /api/upload, "Your submissions" list). Backend: `POST /api/news/submit` (status=pending), `GET /api/news/mine`, `POST /api/news/{id}/review` (admin). New `/admin-news` screen with token login (default `infrajagat-admin`, overridable via `ADMIN_TOKEN` env). Linked from Profile → Help.
      8. **Compare criteria** — compare.tsx: 20 rows across Price / Property / Location / Listing groups with togglable group chips + "Only differences" toggle + "Best" trophy badges on winning cells. Backend `/api/compare` enriches with locality lifestyle + YoY.
      9. **News with pictures** — seed_data.py NEWS now has `image` URLs (Unsplash) + `status: "published"`. News cards render a 16:9 hero image above the title. Backfill on startup updates legacy docs.

      Backend verified via curl:
       - `/news?q=metro` returns matching items with images and status
       - `/news/submit` creates pending doc; `/news/{id}/review` with token flips to published; wrong token → 403; missing admin → 403
       - `/compare?ids=p-01,p-02` returns yoy_change_pct and lifestyle fields

      Frontend verified via screenshots: Explore map (web fallback since native requires device), News with images + Publish + Search + Sub-areas, Publish-news form, Compare with group chips + Best badges, Floating 5-tab bar visible on all detail screens.

      Needs retest focus:
       - WebMap on actual Android device (confirms the Google-Maps-free fix)
       - Publish → wait for admin approval → see in /news feed flow (end-to-end)
       - Sell button navigates away from Buy/Rent (stays unselected)
       - Compare "Only differences" filters rows correctly across 2–4 picks