# mibuddy

A voice-and-camera AI companion that plays alongside a 2–4 year old while they
play with physical toys. Not a tutor, not a chatbot, not a babysitter.

**Status: pre-prototype. No code yet — deliberately.**

The full design brief is in [`docs/build-brief.md`](docs/build-brief.md). Read it
before writing anything; the product lives in the design principles, not the code.

## The one question v0 answers

> Does a two-year-old sustain imaginative play with this for twenty minutes,
> and is he still doing it in week three?

If a feature doesn't help answer that, it isn't in v0.

## Two gating items before any code

Both are called out in the brief and neither is a coding task:

1. **Unit economics** (§5.2) — cost per session at a realistic toddler duty
   cycle. Realtime multimodal APIs are priced for short business interactions,
   not forty minutes a day of jabber. This is a spreadsheet, and it may reshape
   the design.
2. **Provider terms** (§5.5) — Anthropic, OpenAI and Google all restrict
   child-directed products and require adult users. Needs a written answer from
   a provider's enterprise team before committing to a stack.

## Non-negotiables, in one line each

- **Sportscaster, not conversationalist** — commentate, don't converse.
- **Never correct the child's frame** — the block is a sandwich if he says so.
- **Confabulate, never clarify** — never "what?", never "say that again".
- **Vision is a prior on speech** — audio and frames enter one multimodal model
  together. Nothing becomes text before the picture is in the room.
- **Full duplex** — duck, don't stop. Server-side turn detection off.
- **Sub-2s voice-to-voice** — an architecture decision, not an optimization.
- **Do not optimize for engagement** — design it to end around 15–20 minutes.

## Build order

Strictly sequential (§6): the loop → the face → the lexicon → speaker identity →
parent routing. Everything in the "explicitly NOT in v0" list stays out.

## Privacy posture

Video never leaves the device. Store the label the child gave, never a face
template. COPPA governs everything; Illinois BIPA carries statutory damages.
