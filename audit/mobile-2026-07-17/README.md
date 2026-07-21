# Amulet mobile audit — 2026-07-17

Viewport reviewed: 390 × 844 px, compared with 1440 × 1000 px desktop.

## Verdict

The mobile page preserves the content and visual language, but loses the desktop composition. The main causes are the absolutely positioned hero screenshot, inconsistent device widths between sections, and long single-column sections without enough visual pacing.

## Findings

1. Hero — poor
   - The device is right-aligned rather than centered (`right: 4px`, `width: 58vw`).
   - Its 1320:2868 aspect ratio makes it taller than the remaining hero space, while the hero clips overflow. The bottom of the phone is cut off.
   - The headline and phone compete instead of forming one composition.

2. Deck / practice — needs work
   - Text, explanation, and three dense rows appear before the image, delaying the visual payoff.
   - The device width is capped at 270 px, visibly smaller than the 320 px feature devices.
   - The section is long and text-heavy at 390 px.

3. Patterns and meanings — mixed
   - The screens themselves are centered.
   - Their 82vw width is inconsistent with the deck screen and hero.
   - Large headings plus generous vertical padding make the page feel slower and less editorial than desktop.

4. Privacy and closing — acceptable, but flat
   - The one-column privacy list is readable but loses the 2×2 rhythm of desktop.
   - Repeated full-width dividers make the lower half visually monotonous.

## Accessibility risks visible from screenshots/code

- `--faint` has an estimated 2.59:1 contrast ratio on the page background, too low for 12 px labels and metadata.
- Header and footer links render around 12 px and do not visibly provide a 44 px tap target.
- Screenshot review cannot confirm keyboard behavior, screen-reader order, text zoom resilience, or actual touch-target hit areas.

## Recommended order

1. Rebuild the mobile hero as a normal-flow two-part composition and remove clipping.
2. Create one shared mobile device width and centering rule.
3. Move the deck image closer to its introduction; shorten or regroup supporting copy.
4. Tighten mobile section padding and heading sizes.
5. Increase faint-text contrast and interactive hit areas.
