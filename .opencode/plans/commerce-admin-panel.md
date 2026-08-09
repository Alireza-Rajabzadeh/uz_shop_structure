# Commerce Admin Panel — Process Log

Goal: Add **order, wishlist, preorder, cart** to the admin panel (read-only lists + detail views).
Requires new backend admin APIs (currently customer-only) plus admin panel UI.

## Repos / order of commits
1. `back/` — backend admin API endpoints + tests (commit on master)
2. `admin_panel/` — sidebar, permissions, i18n, services, pages, components (commit on master)
3. Top-level — update submodule pointers + commit (master)

## Status legend
- [x] done
- [ ] pending
- [~] in progress

---

## Step 1 — Progress log + plan doc
- [~] Create this file
- [ ] Verify clean git state on master for all repos

## Step 2 — Backend: Order admin endpoints
- [ ] `OrderService.list_orders_admin(filters)` — compact filterable query
- [ ] `OrderService.get_order_admin(order_id)` — rich `_order_payload`
- [ ] Admin views: `AdminOrderList`, `AdminOrderDetail`, `AdminOrderStatusList`
- [ ] Query serializer (filters: status, search, created_from/to, ordering)
- [ ] URLs: `admin/orders`, `admin/orders/<id>`, `admin/statuses`

## Step 3 — Backend: Wishlist admin endpoints
- [ ] Admin views: `AdminWishlistList`, `AdminWishlistDetail`
- [ ] Filters: customer search, product_id, created_from/to, ordering
- [ ] URLs: `admin/wishlists`, `admin/wishlists/<id>`

## Step 4 — Backend: Preorder admin endpoints
- [ ] Admin views: `AdminPreOrderList`, `AdminPreOrderDetail` (mirror wishlist)
- [ ] URLs: `admin/preorders`, `admin/preorders/<id>`

## Step 5 — Backend: Cart admin endpoints
- [ ] `CartService.cart_payload_admin(cart)` — reuse describe_existing payload
- [ ] Admin views: `AdminCartList`, `AdminCartDetail`
- [ ] Filters: customer search, created_from/to, ordering
- [ ] URLs: `admin/carts`, `admin/carts/<id>`

## Step 6 — Backend: admin API tests (all 4 domains)
- [ ] Admin list access + paginated envelope
- [ ] Filter behavior
- [ ] 404 on missing detail
- [ ] Customer-token rejection (401/403)

## Step 7 — Backend: check + tests + commit back/
- [ ] `python manage.py check`
- [ ] Focused test suites
- [ ] `git diff --check`
- [ ] Commit on master (back)

## Step 8 — Admin: permissions map + sidebar + icons
- [ ] `permissionMap.ts`: routePermissionMap + getRoutePermission regexes + sidebarPermissionMap
- [ ] `AppSidebar.tsx`: Commerce group with 4 sub-items
- [ ] 4 new SVG icons in `src/icons/` + export

## Step 9 — Admin: i18n keys (en + fa)
- [ ] sidebar.commerce/orders/wishlist/preorders/carts
- [ ] domain keys: title, columns, filters, detail

## Step 10 — Admin: services
- [ ] `order.service.ts`, `wishlist.service.ts`, `preorder.service.ts`, `cart.service.ts`

## Step 11 — Admin: Orders pages + components
- [ ] `/orders` list page + `OrderList` component
- [ ] `/orders/[id]` detail page + detail component

## Step 12 — Admin: Wishlist pages + components
- [ ] `/wishlist` list page + `WishlistList` component

## Step 13 — Admin: Preorder pages + components
- [ ] `/preorders` list page + `PreOrderList` component

## Step 14 — Admin: Cart pages + components
- [ ] `/carts` list page + `CartList` component
- [ ] `/carts/[id]` detail page + detail component

## Step 15 — Admin: typecheck/lint/build + commit admin_panel/
- [ ] `npx tsc --noEmit`
- [ ] `npm run lint`
- [ ] Commit on master (admin_panel)

## Step 16 — Top-level: submodule pointers + commit
- [x] Commit submodule pointer updates on master

---

## Completion

All steps complete. Commits:
- `back/` → `4e1a36c` feat(admin): add read-only admin APIs for order, wishlist, preorder, cart
- `admin_panel/` → `97f9632` feat(commerce): add order, wishlist, preorder and cart admin pages
- top-level → `a2d35dd` feat(commerce): add order, wishlist, preorder and cart admin APIs and pages

Note: submodule commits are local; push `back`, `admin_panel`, then the top-level repo.

## Notes / decisions
- Admin endpoints are GET-only (read-only), following `domains/customer/admin_views.py` pattern:
  `AdminJWTAuthentication` + `AdminModelPermissions` + `model` + `api_response` + `PageNumberPagination`.
- Wishlist/Preorder are list-only in the UI (rows link to customer + product pages).
  Order and Cart get detail pages.
- Response envelope everywhere: `{ success, message, data, errors }`, money as strings.
