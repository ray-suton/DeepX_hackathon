# Design System — Paladin

## Product Context
- **What this is:** A manufacturer-facing web app that lets AI chip vendors simulate how a prospect's inference workload would likely perform on their hardware before shipping physical evaluation boards.
- **Who it's for:** Solutions engineers, field engineers, technical sales teams, and hardware evaluation stakeholders on the customer side.
- **Space/industry:** AI infrastructure, semiconductor tooling, inference performance analysis.
- **Project type:** Web app / dashboard.

## Research Synthesis

### What the category is doing
- Developer and infra dashboards converge on quiet neutral surfaces, metric cards, line or bar charts, and sparse accent color.
- Strong dashboard systems use composable charts and clear hierarchy instead of dense visual decoration.
- The category has an obvious monoculture problem: too many products borrow the same soft SaaS look, which makes serious tools feel generic.

### What to keep
- Familiar left-nav plus report-canvas app structure.
- Strong metric hierarchy with summary first, breakdown second.
- Sparse, intentional accent color usage.

### Where to break from the category
- Most AI and dashboard products chase “future” with purple gradients and generic glow. Paladin should feel like instrumentation, not marketing.
- Most infra dashboards hide assumptions in tooltips or settings. Paladin should surface confidence and assumptions as first-class trust UI.

### Design thesis
Paladin should feel like a calibrated lab console: precise, industrial, credible, and a little sharp. Not playful. Not corporate sludge. A tool you trust to evaluate expensive hardware decisions.

## Aesthetic Direction
- **Direction:** Industrial / utilitarian with editorial restraint.
- **Decoration level:** Intentional.
- **Mood:** Crisp, technical, and grounded. The interface should feel like it belongs in a hardware lab or reliability war room, but with enough refinement that it still reads as a modern product.
- **Reference posture:** Borrow the clarity of serious data tools, but avoid their generic “template dashboard” softness.

## Typography
- **Display/Hero:** `Satoshi` — confident without feeling startup-generic, good for report headings and score callouts.
- **Body:** `Instrument Sans` — clean, compact, and legible under dense dashboard conditions.
- **UI/Labels:** `Instrument Sans` — keeps controls and metadata consistent.
- **Data/Tables:** `IBM Plex Mono` — use for hardware specs, batch sizes, precision labels, throughput values, and any value where tabular rhythm matters.
- **Code:** `IBM Plex Mono`
- **Loading:** Google Fonts or Bunny Fonts for `Satoshi`, `Instrument Sans`, and `IBM Plex Mono`.
- **Scale:**
  - Display XL: `56px / 3.5rem`
  - Display L: `40px / 2.5rem`
  - Section title: `28px / 1.75rem`
  - Card title: `18px / 1.125rem`
  - Body: `15px / 0.9375rem`
  - Small UI/meta: `12px / 0.75rem`
  - Mono metric: `14px / 0.875rem`

## Color
- **Approach:** Restrained with one sharp warm accent and one technical signal accent.
- **Primary:** `#FF6A3D` — signal orange, used for primary actions, active states, and DeepX highlight moments.
- **Secondary:** `#B6FF5C` — acid green, reserved for efficiency wins, “best perf/watt,” and positive signal markers.
- **Neutrals:**
  - `#0F1113` app background
  - `#171A1D` elevated background
  - `#1F2428` card surface
  - `#31383E` border / gridline
  - `#66707A` muted text
  - `#C8D0D7` primary text on dark surfaces
  - `#F3F1EB` warm light surface for printable/report sections if needed
- **Semantic:**
  - Success: `#7DFFB3`
  - Warning: `#FFB84D`
  - Error: `#FF6B6B`
  - Info: `#6FC7FF`
- **Dark mode:** Native dark-first design. Keep saturation controlled. Avoid glowing neon surfaces; use accent color on edges, numbers, badges, and focused actions only.

## Spacing
- **Base unit:** `8px`
- **Density:** Comfortable but disciplined.
- **Scale:** `2xs(4) xs(8) sm(12) md(16) lg(24) xl(32) 2xl(48) 3xl(64)`

## Layout
- **Approach:** Hybrid, dashboard shell with an editorial report canvas.
- **Grid:** `12-column` content grid on desktop, `8-column` on tablet, single column on mobile.
- **Max content width:** `1440px`
- **Border radius:**
  - small controls: `6px`
  - cards: `10px`
  - modals / panels: `14px`
  - pills: `9999px`
- **Composition rules:**
  - Left rail for navigation and simulation setup.
  - Main canvas for report output.
  - Top of report shows the decision headline first: what won, under which assumptions.
  - Charts come after the answer, not before it.
  - Assumptions and confidence must be visible in the top viewport, not buried at the bottom.

## Motion
- **Approach:** Minimal-functional.
- **Easing:** enter `ease-out`, exit `ease-in`, move `ease-in-out`
- **Duration:** micro `80ms`, short `180ms`, medium `280ms`, long `420ms`
- **Rules:**
  - Animate panel reveals and chart loading states.
  - Do not animate numeric counters aggressively.
  - No decorative floating motion or blob-driven effects.

## Component Direction

### Navigation
- Narrow dark sidebar with strong section labels.
- Hardware profiles and saved runs should feel operational, not consumer-friendly.

### Inputs
- Inputs should look instrument-grade: sharp edges, clear labels, visible units.
- Precision, batch size, and model metadata belong in a setup panel that feels compact and explicit.

### Cards
- Summary cards should use large numeric hierarchy and mono sub-metrics.
- One card may be visually “pinned” as recommended, but only if the assumptions justify it.

### Charts
- Use dark plot backgrounds with quiet gridlines and very selective color.
- Do not color every series loudly. Use orange for DeepX, steel blue or muted gray for baselines, acid green only for efficiency highlights.

### Trust UI
- Confidence and assumptions are not footnotes.
- Treat them as a first-class module with status-badge treatment and compact explanatory copy.

## Safe Choices
- Familiar dashboard navigation and report layout so users instantly know how to operate it.
- Neutral surface hierarchy so charts and metrics stay readable.
- Conservative motion and compact controls because this is a serious infrastructure tool.

## Risks
- **Signal orange as the primary accent:** This is bolder than most infra dashboards, but it makes the product feel like hardware instrumentation instead of generic SaaS.
- **Mono for key data surfaces:** Using `IBM Plex Mono` on specs and metric detail adds credibility and rhythm, but overuse would make the app feel too terminal-like, so keep it scoped.
- **Dark-first industrial palette:** Dark dashboards are common, but this one should feel steel-and-graphite rather than neon cyberpunk. The risk is looking too severe; the warm orange prevents that.

## UI Principles
- Lead with the answer, then show the evidence.
- Confidence should sit next to performance, not behind it.
- Every accent color must carry meaning.
- The product should look expensive enough to support a hardware sales conversation.
- If a panel does not help a user decide “should I evaluate this chip?”, it does not earn the space.

## Suggested First Screens
- Simulation setup dashboard
- Comparison report view
- Saved reports / export history

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-08 | Adopted an industrial dashboard system with dark graphite surfaces, signal orange highlight, and mono data accents | Fits the product's trust-heavy semiconductor tooling use case and avoids generic AI dashboard aesthetics |
