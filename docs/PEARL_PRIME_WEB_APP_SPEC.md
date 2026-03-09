# Pearl Prime — Web App UI & Branding Specification

Developer-ready spec: product brief plus implementation guardrails (accessibility, mobile, content config, performance, i18n, brand assets).

---

## 1. Application Name & Branding

The web application is branded **Pearl Prime.**

**Brand presentation:**
- Display the **pearl_prime_icon.png** icon.
- The icon appears **to the left of the text "Pearl Prime."**
- The brand is placed in the **top navigation bar** of the app.

Example header layout:
```
[pearl_prime_icon.png]  Pearl Prime
```

**Brand identity:** calm, uplifting, spiritual, modern and clean.

---

## 2. Visual Design Theme

**Background:** Primary background color **Light Blue**, suggested tone `#EAF6FF`.

**Accent colors:**
- **White** for panels, cards, UI sections, menu bars.
- **Dark gray / navy** for text.

Example:
- background: light blue (`#EAF6FF`)
- cards: white
- text: dark gray / navy

**Design style:** peaceful, minimalist, modern spiritual technology, readable and uncluttered.

---

## 3. Bottom Animated Text Ticker

A **horizontal scrolling ticker** runs across the **bottom of the screen**.

**Animation:** Stock-market style; text moves **right → left** continuously; smooth, constant speed; infinite loop.

**Languages:** English, Chinese, Japanese (may rotate or mix).

**English ticker content** (see also §12 — content lives in config):
- Spread wisdom to every heart.
- Offer hope to the weary.
- Let the truth shine everywhere.
- Guide spirits toward freedom.
- Carry compassion to the world.
- Lift hearts with words.
- Awaken the light within all.
- Share words of healing.
- Open paths to inner peace.
- Plant seeds of awakening.
- Bring clarity to the confused.
- Let wisdom flow to all beings.

**Behavior:** Sentences appear sequentially; when the final sentence finishes, loop again; spacing allows comfortable reading.

---

## 4. Left Side Vertical Word Runner

A **vertical scrolling message column** on the **left side of the screen**.

**Animation:** Text moves **bottom → top**; continuous smooth scrolling; infinite loop (meditation-quotes / news-feed style).

**Message content** (see §12 — content in config):
- Books that inspire courage
- Books that awaken wisdom
- Stories that open hearts
- Stories that reveal truth
- Teachings that guide the path
- Teachings that bring clarity
- Exercises that calm the mind
- Exercises that restore balance
- Practices that nurture peace
- Practices that build resilience
- Words that uplift the spirit
- Words that spark transformation

**Display:** Each phrase appears individually, rises upward, may fade slightly near the top; new phrases from the bottom — continuous vertical flow of inspiration.

---

## 5. Layout Overview

```
-----------------------------------------------------
| Pearl Prime logo + icon                           |
-----------------------------------------------------

| LEFT MESSAGE COLUMN |     MAIN CONTENT AREA       |
|                     |                             |
| Books that inspire  |                             |
| courage             |                             |
|                     |                             |
| (vertical scroll)   |                             |
|                     |                             |
-----------------------------------------------------
| horizontal ticker scrolling messages              |
-----------------------------------------------------
```

---

## 6. Motion & Animation Guidelines

Animations should feel **calm, smooth, not distracting, meditative.**

**Speed suggestions:**
- **Horizontal ticker:** ~40–60 seconds per full loop.
- **Vertical message column:** ~1 phrase every 3–5 seconds.

---

## 7. Typography

**Primary font:** Clean sans serif — e.g. **Inter**, **Open Sans**, or **Lato**.

Text should feel **readable, calm, elegant.**

---

## 8. Optional Enhancements

- **Language rotation:** Ticker alternates between English, Chinese, Japanese.
- **Subtle glow:** Important words (e.g. wisdom, peace, awakening, clarity) may gently brighten.

---

## 9. Design Goals

The interface should communicate **wisdom, peace, compassion, spiritual guidance** — like a **modern digital temple of knowledge** where teachings flow continuously across the screen.

---

## 10. Accessibility

- **Reduced motion:** When the user has `prefers-reduced-motion: reduce`, **pause or significantly slow** both tickers (horizontal and vertical). Do not rely on motion for critical information.
- **Contrast:** Ensure **WCAG 2.1** contrast (at least 4.5:1 for normal text) on:
  - Text on light blue background (`#EAF6FF`)
  - Text on white cards/panels  
  Use **dark gray or navy** text as specified in §2 to meet contrast.

---

## 11. Mobile / Responsive

- **Left vertical runner:** On viewports **below 768px**, **hide or collapse** the left message column so the main content has full width.
- **Bottom ticker:** Remain **single line** with overflow hidden; no layout shift or wrapping that breaks the ticker strip.
- Define a single breakpoint (e.g. 768px) and document it in the implementation.

---

## 12. Content Safety

- **Ticker and runner phrases must not be hardcoded** in app code.
- Store them in **config/JSON** (or YAML) so copy can be edited **without code deploy**.
- **Canonical path:** `config/pearl_prime/ticker_phrases.json` (see repo for schema).
- Structure: `ticker` and `runner` objects with locale keys (`en`, `zh`, `ja`) and arrays of strings. The app loads this at runtime (or at build time for static export).

---

## 13. Performance

- Use **CSS `transform: translate3d()`** for ticker and runner animations to leverage compositing and avoid layout thrash.
- Prefer **CSS `@keyframes`** and duplicated content for infinite scroll where possible; **avoid JS timers** (e.g. `setInterval`) for the primary scroll loop if a pure-CSS infinite loop is feasible.
- If JS is used for timing, use `requestAnimationFrame` and still apply movement via `transform`, not `left`/`top`.

---

## 14. I18n Typography

- For **Chinese and Japanese** text, use a **CJK font fallback stack** to avoid system defaults that may render poorly.
- **Recommended stack:**  
  `"Noto Sans SC", "Noto Sans JP", "Noto Sans TC", system-ui, sans-serif`  
  (or equivalent: SC = Simplified Chinese, JP = Japanese, TC = Traditional Chinese.)
- Load Noto Sans via font link (e.g. Google Fonts) when CJK locales are used.

---

## 15. Brand Asset Spec

- **Icon:** `pearl_prime_icon.png`
  - **Display size:** 28px height (width scale proportionally).
  - **Gap between icon and text:** 10px.
  - **Header bar height:** 56px (minimum).
- **Source path in repo:** `PhoenixControl/Assets.xcassets/AppIcon.appiconset/pearl_prime_icon.png`. For the web app, copy to `pearl_prime_web/assets/` (or equivalent) so the app is self-contained.

---

## Implementation Reference

- **Starter implementation:** `pearl_prime_web/` — `index.html`, `styles.css`, `app.js`.
- **Content config:** `config/pearl_prime/ticker_phrases.json`.
