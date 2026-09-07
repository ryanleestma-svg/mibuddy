# Provider capability matrix

Answers open question #2 (§9): *which realtime provider actually supports native
video in + manual turn management + acceptable latency.*

Researched 2026-09-07. Realtime APIs move fast — re-verify before committing.

## The three hard requirements

From the brief, these are non-negotiable and they disqualify most of the market:

1. **Frames and audio resolve in one model** (§2.4). Not ASR → LLM → TTS with a
   caption stapled on.
2. **Server-side turn detection can be turned OFF** (§2.5), with manual turn
   control, so the agent is never barge-in interrupted.
3. **Sub-2s voice-to-voice** (§2.6).

## Matrix

| | **OpenAI Realtime** (`gpt-realtime-2.1`, `-mini`) | **Gemini Live** (`gemini-3.1-flash-live-preview`) | **Nova Sonic / Hume EVI / Cartesia etc.** |
|---|---|---|---|
| Speech-to-speech, single model | Yes | Yes | Yes |
| **Image/frame input in session** | **Yes** — images supported alongside audio in a Realtime session | **Yes** — native, `send_realtime_input(video=Blob(mime_type="image/jpeg"))` | **No** — audio only |
| **Disable server VAD** | **Yes** — `turn_detection: null`, then manual `response.create` | **Yes** — `realtimeInputConfig.automaticActivityDetection.disabled`, manual `activityStart`/`activityEnd` | Varies / audio-only anyway |
| Latency | Sub-second typical | Sub-second typical | 100–300ms (best in class, but no vision) |
| Audio price (per 1M tokens) | $32 in / $64 out; **mini $10 / $20** | **$3 in / $12 out** | n/a |
| Session limits | Standard websocket session | **audio+video capped at 2 min** uncompressed; ~10 min connection; needs context compression + session resumption | — |
| **Under-18 terms** | **Permitted with conditions** — under-13 personal data requires Zero Data Retention enabled, plus COPPA compliance and safeguards | **Prohibited** — terms bar use in a service "directed towards or likely to be accessed by individuals under the age of 18" | Varies |
| ZDR on the realtime endpoint | **Yes, subject to approval** (enterprise sales, not self-serve) | n/a | Varies |

## Finding 1 — the §2.4 / §3.1 tension dissolves, and not the way I expected

I flagged that "native video in" might have an empty shortlist. It doesn't, but
the more useful observation is that **the brief doesn't actually need video.**

§2.4 says it plainly: *"you need a frame or two at speech onset — what's in his
hands right now — not a continuous video stream."* That is **image input into a
realtime audio session**, which is a much easier requirement than video
streaming, and both providers do it.

So "don't assemble your own stack" and "sub-2s" do not collide. Both survive.
The constraint that actually bites is somewhere else entirely.

## Finding 2 — the real conflict is legal vs. economic, and it's a genuine bind

The two providers fail on opposite axes:

- **Gemini Live is ~5–10× cheaper** and has the better vision path, but its terms
  contain a flat prohibition on services likely to be accessed by under-18s.
  There is no documented carve-out, no safeguards-based exception, no enterprise
  path published. It is a wall, not a hurdle.
- **OpenAI is the only documented legal path** — under-13 data is permitted with
  ZDR + COPPA compliance + safeguards, and ZDR *is* available on the realtime
  endpoint. But it is the expensive one, and ZDR requires enterprise approval
  rather than a self-serve toggle.

**The provider that is legally viable is the expensive one. The cheap one is
prohibited.** That is the actual shape of §5.5, and it is worse than the brief
assumed — the brief treats provider terms as a question to ask; it is really a
constraint that removes the cheapest option outright.

## Finding 3 — Gemini's 2-minute audio+video session cap

Easy to miss and it directly contradicts a 15–20 minute session. Extending it
requires context-window compression plus session resumption across ~10-minute
connection lifetimes. That is real engineering, on top of a provider whose terms
already rule it out for a shipped product.

## Recommendation

**Prototype on OpenAI Realtime (`gpt-realtime-2.1-mini`), not Gemini.**

- It is the only stack with a documented route to a legal shipped product, so
  prototyping on it means the prototype is on the path rather than a throwaway.
- Mini is ~3× cheaper than flagship and the sportscaster design is deliberately
  undemanding — one sentence, big energy. This is not a task that needs the
  frontier model. Test mini first and only move up if the character falls flat.
- Image-at-speech-onset is supported, which is exactly the §2.4 pattern.
- Building on Gemini now means either throwing the code away or shipping in
  breach of terms. Neither is acceptable for something you point at your kid.

**Caveat to verify before committing:** ZDR approval is enterprise sales, not a
toggle. A personal prototype with a parent present is a different posture than a
distributable product — but confirm in writing, per §5.5. That conversation
should start now, because it gates distribution, not prototyping.

## Sources

- [OpenAI Realtime: gpt-realtime and image input](https://openai.com/index/introducing-gpt-realtime/)
- [OpenAI Realtime VAD guide](https://developers.openai.com/api/docs/guides/realtime-vad)
- [OpenAI under-18 API guidance](https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance)
- [OpenAI usage policies](https://openai.com/policies/usage-policies/)
- [OpenAI zero data retention](https://openai.com/index/offering-zero-data-retention-for-frontier-models/)
- [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data)
- [Gemini Live API capabilities](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- [Gemini Live session management](https://ai.google.dev/gemini-api/docs/live-session)
- [Gemini API additional terms](https://ai.google.dev/gemini-api/terms)
- [Firebase AI Logic: Live API limits](https://firebase.google.com/docs/ai-logic/live-api/limits-and-specs)
- [OpenAI Realtime pricing, measured](https://hackernoon.com/openai-realtime-api-pricing-in-2026-real-world-data-from-4000-measured-sessions)
