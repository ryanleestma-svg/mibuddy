# Unit economics

Answers §5.2 and open question #1: *cost per session at realistic toddler duty
cycle.* The tunable model is [`cost-model.xlsx`](cost-model.xlsx); this file
explains what it says and why.

## Baseline assumptions

| | |
|---|---|
| Sessions per day | 2 |
| Minutes per session | 20 |
| Sessions per month | 60 |
| Child speech duty cycle | 35% of session (mic gated by local VAD) |
| Agent responses per session | 45 × 1.5s ≈ 1.1 min of speech |
| Frames per session | 45 (one at each speech onset — **not** continuous) |
| Context replay multiplier | 4× (accumulated context reprocessed per response) |
| Cached input rate | 25% of full price |

Retail target $10/month at 70% gross margin → **COGS budget $3.00/month.**

## Result at baseline

| | $/session | $/month | vs $3 budget | Break-even retail @70% |
|---|---|---|---|---|
| `gpt-realtime-2.1` | $0.54 | **$32.15** | 10.7× over | $107/mo |
| `gpt-realtime-2.1-mini` | $0.17 | **$10.05** | 3.3× over | $33/mo |
| `gemini-3.1-flash-live` | $0.06 | **$3.50** | 1.2× over | $12/mo |

**At baseline assumptions, none of them fit a $10/month product.** The flagship
is dead on arrival. Mini needs ~$33/month retail. Gemini is the only one close to
affordable — and it's the one whose terms prohibit this use entirely.

That is the finding §5.2 asked for, and it is worse than "model this before
writing code" implies. The brief's instinct was right.

## But the prototype is not the product — and this is the important part

Sixty sessions a month on mini is **$10/month of API spend.** To answer the only
question v0 asks — does Hawk sustain play for twenty minutes, and is he still
doing it in week three — that is nothing. It's a rounding error against the value
of the answer.

**The economics problem bites at scale, not at n=1.** There is no reason to delay
building. There is every reason not to sign anyone up.

## What actually moves the number

Sensitivity, in order of leverage:

1. **Context replay multiplier (4× assumed).** Dominates everything. It is a
   guess and could plausibly be 1.5× or 8× — a range that spans "viable product"
   to "unshippable." **Instrument this in the first prototype session:** log
   actual billed input tokens per response and back out the real multiplier.
   Every other number here is noise until you know this one.
2. **Duty cycle (35% assumed).** Halving it roughly halves input cost. Local VAD
   discipline is worth real money.
3. **Sessions per day.** The brief already wants hard session caps (§2.7).
4. **Agent verbosity.** Output tokens are 2× the input rate per minute and the
   agent is *designed* to be terse. Already optimised.

At the assumed 4× replay, **no combination in the sensitivity grid gets under
budget** — even 15% duty cycle at one session/day is $3.76/month. Duty cycle and
session count alone cannot save this. Drop replay to 2× and the same lean case
lands at $3.14/month, essentially at budget.

**So the replay multiplier is the whole ballgame, and it is the one number in
this model that is pure guesswork.** Everything else is a second-order lever.

## The rare alignment holds, and it's quantifiable

§5.2 claims the cost mitigations and the design principles point the same
direction. They do, and the model puts numbers on it:

| Mitigation | Effect in this model |
|---|---|
| Frames at speech onset, not continuous | 45 frames vs ~1,200 at 1fps — **27× reduction** |
| Local VAD gates the mic | Bills 7 of 20 wall-clock minutes |
| Short responses (~1 sentence) | 1.1 min of output per 20-min session |
| Local backchannel sound bank | Free — zero model calls, zero latency |
| Hard session caps | Linear control on the whole bill |

Without these the product is unbuildable at any price. With them it is merely
expensive. The design was load-bearing on economics before anyone modelled it.

## Recommendation

1. **Build the prototype now on `gpt-realtime-2.1-mini`.** $10/month for n=1 is
   not a decision that needs a spreadsheet.
2. **Instrument context replay from session one.** It is the number that decides
   whether this is a business, and no amount of desk research will produce it.
3. **Do not commit to a $10/month price point.** On current numbers the honest
   price is $20–35/month, or the product needs a materially cheaper stack than
   exists today under usable terms.
4. **Re-run this model against measured data after week one.** Every input here
   is a guess except the published prices.
