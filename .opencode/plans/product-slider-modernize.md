# Modernize ProductSlider - smaller & sleeker on desktop

## Changes needed

### 1. `components/product/ProductCard.tsx`

**a) Card widths (shows more items):**
```
min-w-[48%] sm:min-w-[40%] md:min-w-[22%] lg:min-w-[16%] xl:min-w-[12%]
→ min-w-[48%] sm:min-w-[35%] md:min-w-[18%] lg:min-w-[13%] xl:min-w-[9%]
```

**b) Image padding:** `p-1.5` → `p-1`

**c) Discount badge:** `top-2 -right-2 w-11 px-3 text-[11px]` → `top-1.5 -right-1.5 w-9 px-2 text-[10px]`

**d) Wishlist button:** `h-7 w-7` `size={14}` → `h-6 w-6` `size={12}`, `top-2 left-2` → `top-1.5 left-1.5`

**e) Add-to-cart button:** `h-10 w-10 group-hover:w-20` `ShoppingBag size={18}` → `h-8 w-8 group-hover:w-16` `ShoppingBag size={14}`, `bottom-15` → `bottom-12`, text `bottom-2.5` → `bottom-2`, text `text-xs`

**f) Content padding:** `px-2 pb-2 min-h-18` → `px-1.5 pb-1.5 min-h-14`

**g) Title:** `text-sm min-h-[36px]` → `text-xs min-h-[28px]`

**h) Price margin:** `pt-1.5` → `pt-1`

**i) Skeleton:** match reduced padding/sizes

### 2. `components/slider/parts/SliderArrow.tsx`

**a) Size:** `h-20 w-10` → `h-14 w-8`

**b) Hover reveal:** add `opacity-0 group-hover:opacity-100 transition-opacity duration-300` so arrows only show on hover (cleaner look)

### 3. `components/slider/ProductSlider.tsx`

**a) Section padding:** `px-5 py-2` → `px-3 py-2`

**b) Header margin:** `mb-5` → `mb-3`

**c) Title size:** `text-lg md:text-xl` → `text-base md:text-lg`

**d) Gap between cards:** `gap-1` → `gap-0.5`
