# Design system: Arterion EF Console

A recreation of a clean medical-AI landing page, in royal blue and white. Every claim and number on the page comes from this project's own README and metrics.

## Structure
1. Floating navigation: logo mark, pill tabs, status, sign-in, Get Started
2. Hero: badge, serif headline (italic gradient second line), lead, two calls to action, check-badges, motif line
3. Features: six cards with gradient icon tiles
4. Process: four numbered steps joined by a rail that fills as you scroll
5. Analyze: the working tool
6. Evidence: dark section with an italic claim and a glass panel of held-out metric bars
7. Call to action and footer

## Tokens
| Token | Value |
|---|---|
| `--brand-1` | `#1e40af` |
| `--brand-2` | `#2563eb` |
| `--brand-3` | `#3b82f6` |
| `--bright` | `#93c5fd` |
| `--ink` | `#0f172a` |
| `--muted` | `#64748b` |
| `--bg` | `#f8fafc` |
| `--soft` | `#eff6ff` |
| `--dark-1` | `#0b1530` |
| `--dark-2` | `#1e3a8a` |

## Type
Headlines: 'Playfair Display'. Body: 'Poppins'. Numbers: 'JetBrains Mono'.

## Motion
- **Motion (framer-motion engine, vanilla build):** hero entrance on a spring, button hover and press springs, count-ups.
- **GSAP + ScrollTrigger:** read-progress bar, hero parallax, heading and card reveals, a scrubbed rail that connects the steps, metric bars that grow once in view.
- **Reduced motion:** all animation is skipped and bars and counters show their final values.

## Accessibility
Skip link, labelled landmarks, visible focus rings, text contrast of at least 4.5:1 on buttons, and a keyboard-operable mobile menu.
