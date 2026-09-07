# Toddler Companion — Prototype Build Brief

**Status:** Pre-prototype. Nothing built yet.
**Goal of v0:** Answer one question — does a two-year-old sustain imaginative play with this for twenty minutes, and is he still doing it in week three?

Everything in this brief serves that question. If a feature doesn't help answer it, it isn't in v0.

---

## 1. What this is

A voice-and-camera AI companion that plays alongside a 2–4 year old while they play with physical toys. The phone sits on the floor or table (or gets carried around). The child talks; the agent talks back, reacts, makes noises, and asks questions that keep the pretend going.

It is **not** a tutor, not a chatbot, not an on-demand answer machine, and not a babysitter. The closest analogue is a very enthusiastic older sibling who is also slightly hard of hearing.

### Validated by observation (day one, n=1, Hawk, age 2)

A live session with a general-purpose voice assistant already produced the following, unprompted:

- Sustained multi-turn engagement for an extended session on a single topic (Monster Jam trucks).
- Spontaneous re-initiation after lulls ("Hello.") with no prompting.
- **The child held toys up to the phone repeatedly** — "Look. Look. Look." — assuming the device could see. It could not.
- The child handed the phone to a visiting neighbour and said **"Look, that's Kali!"** — spontaneously teaching the agent a proper noun by pairing label and referent.
- The child took the phone outside and rode away on a bike, still talking.
- The parent spontaneously acted as translator ("his favourite truck is Grave Digger", "he doesn't have great language skills").
- **Failure mode observed:** when the agent asked clarifying questions, engagement died. When it switched to enthusiastic commentary and sound effects, engagement peaked.

Everything below is derived from that session.

---

## 2. Design principles (non-negotiable — these are the product)

### 2.1 Sportscaster, not conversationalist
Two-year-olds do parallel play. They don't hold a thread and can't repair a conversation. The agent commentates, reacts, and asks questions that work whether or not they're answered ("Uh oh — is he gonna make it?").

This solves the hardest technical problem sideways: a dialogue system fails **loudly** when it mishears. A sportscaster fails **silently** — it says something adjacent and keeps rolling. Ship at 60% speech accuracy instead of needing 95%.

### 2.2 Never correct the child's frame
The block is a sandwich. Then a phone. Then a baby. If the agent says "that's a blue square," it has stepped on the game. Improv rules: yes, and. Accept every declaration about what an object is, always.

### 2.3 Confabulate, never clarify
Observed directly: when the model grabbed the nearest plausible noun from garbage audio and committed ("Break Zombie! Crash!"), the child rolled straight past it. When it asked "did you say something about the racing?", the session stalled. **The agent must never say "what?" or "I didn't catch that."**

### 2.4 Vision is a prior on speech, not a separate feature
This is the core architectural insight and it's easy to get wrong.

"It's a gore," repeated thirty times, is unrecoverable from audio. "It's a gore" *while holding a red truck with horns* is **El Toro Loco**, instantly, with no human in the loop.

**Therefore: nothing becomes text before the picture is in the room.** Do NOT build `audio → transcript → LLM` with a vision caption stapled on. The recognizer will commit to "gore" before vision gets a vote. Audio and frames must enter one multimodal model together and resolve jointly.

This also makes vision cheap: you need a frame or two at speech onset — what's in his hands right now — not a continuous video stream.

### 2.5 Full duplex — overlap is normal, interruption is not
Every realtime voice API ships with server-side turn detection that cuts the agent off the moment it hears speech. **Disable it.** A toddler vocalizes near-continuously; default barge-in means the agent never finishes a sentence.

- **Duck, don't stop.** On detected child speech, drop agent volume ~40% and keep talking.
- **Backchannel locally.** Fire short "mm!", "ooh", "yeah" from a local sound bank *while* the child is still speaking. No model call. This is what makes someone feel heard.
- **Brevity is the real fix.** Cap responses at ~1 sentence / 1–2 seconds of audio. Collisions resolve themselves.
- **One true interrupt: distress.** Sustained, loud, rising pitch, or a clear "no"/"stop" → full stop, drop to soft voice.

**Echo cancellation is a first-class problem**, not a detail. Open mic + playing speaker means the agent hears itself and contaminates an already-bad transcript. AEC quality directly caps lexicon quality. Test it outdoors and in motion, not just at a desk.

### 2.6 Latency is the kill switch
A toddler's attention window on a response is well under two seconds. Sub-2s voice-to-voice or the product doesn't exist. This is an architecture decision on day one, not an optimization.

### 2.7 Do not optimize for engagement
Never instrument session length as a success metric. The moment you optimize time-in-app you've rebuilt the thing this is supposed to replace. Design it to **end**: natural wind-down around 15–20 minutes.

---

## 3. Architecture

### 3.1 Core loop
Use a **realtime multimodal speech-to-speech API with native video input** so audio and frames resolve jointly (see 2.4). Do not assemble your own ASR → LLM → TTS stack; it defeats the central design principle and loses the latency fight.

Config requirements:
- Server-side turn detection / auto-interruption: **OFF** (see 2.5)
- Manual turn management
- Streaming output

### 3.2 Local (on-device, no network)
- **VAD** — gates the mic. Nothing goes out unless the child is actually talking. This is both a cost control and a privacy story.
- **Frame capture on speech onset** — 1–2 frames when VAD fires. Not continuous video.
- **Backchannel sound bank** — vocal reactions + effects (vroom, crash, whoosh, gasp). Toddlers respond harder to sound than to any sentence you can generate, and it's free.
- **Face rendering** (see 3.4)
- **AEC**
- **Confidence gate** (see 5.1)

### 3.3 Two physical modes
Same brain, different body. Detect via motion/orientation or let the parent pick.

| | **Tabletop** | **Carried** |
|---|---|---|
| Position | Propped, screen visible | Pocket, hand, bike |
| Camera | Live, useful | Mostly thumbs and grass — deprioritize |
| Face | Matters | Nobody's looking |
| Mode | Blocks, trucks, drawing | Audio companion, narration |

Carried mode is the one nobody else has and the one that defuses the screen-time objection entirely. Don't treat it as an afterthought.

### 3.4 The face — three layers

Do **not** drive this from emotion inference. Too slow, too expensive, feels like a lagging translation of the room.

**Layer 1 — Idle (local, always on, zero network).** Blinking on an irregular timer, small head drift, breathing. Costs nothing and does most of the work of feeling alive.

**Layer 2 — Reactive (local, zero latency).** Mouth moves with outgoing speech. Critically: **the character leans in the instant the child's voice starts** — ears up, eyes widen — triggered by VAD, *before any model is involved*. This is the "someone is paying attention to me" effect made visible, at zero latency. It is the highest-value animation in the product.

**Layer 3 — Expressive (model-driven).** The model emits a state tag alongside each reply from a fixed set (~6: excited / curious / uh-oh / delighted / sleepy / soft). Crossfade between them. Never a continuum, never a snap.

**Attentive is the pose that matters most** and it's the one everyone underbuilds, because it happens while the AI is doing nothing.

Rive is the right tool — state-machine driven, small, runs fine on a phone, layers 1–2 never touch the network.

**Character selection:** pick once at setup, then it's permanent. A skin-swap menu destroys the attachment that makes this valuable.

### 3.5 Speaker identity (not age classification)
Do **not** try to classify adult vs. child from voice — fussy, and it misfires on older kids. Instead learn *which voice is my person*:
- Enroll the child's voice once at setup.
- A two-year-old's fundamental frequency is far from an adult's, so a fairly crude embedding gets most of the way there.
- Everything else = background context, not a conversational partner.
- Side benefit: parent-routing (see 4.2) only fires when a parent voice has actually been heard recently.

### 3.6 The lexicon — the actual moat
A per-child JSON file. Small, boring, and the only thing a competitor can't replicate:

```
{
  "child": "Hawk",
  "pronunciation": {
    "gore": "El Toro Loco",
    "great zombie": "Grave Digger + Zombie",
    "bake / break": "UNRESOLVED — recurring, high frequency"
  },
  "people": { "Kali": "neighbour, visits" },
  "interests": ["Monster Jam", "trucks"],
  "notes": ["fixated on Monster Jam since Aug 2026"]
}
```

Injected into context each session. Code is trivial; the **policy** is the interesting part:
- What confidence threshold writes an entry?
- How does a wrong guess get un-learned?
- What happens when the child's pronunciation improves and the old mapping goes stale?

Note the acquisition path. Entries come from three places, in increasing order of value: parent correction, model inference over repeated use, and **label-and-referent pairing** — the Kali case, where the child points the camera and names the thing simultaneously. The third builds itself while the child plays. That's the one to design for.

**Privacy: store the label the child gave, never a face template.** That line is what keeps this out of BIPA exposure.

**Second-order value:** the lexicon is a record of how your kid talked when he was two. Parents keep that. It's the only artifact in this category with emotional weight.

---

## 4. Product decisions already made

### 4.1 Positioning
"Keeps him building for twenty minutes while you cook dinner." Not a friend, not a companion, not a babysitter, not education. Ship that language.

Anticipated attack: *the repetitive narration is exactly the developmental work, and you're outsourcing the thing a parent should do.* AAP guidance on under-twos gives that critique ammunition. The framing above survives it. "AI friend for your toddler" does not.

### 4.2 Parent routing — conditional, not constant
Periodically the agent says "Hawk, go show Dad the big one!" — which inverts the substitution critique: the AI *manufactures* parent-child interaction rather than replacing it. Nobody else does this because everyone else optimizes time-in-app.

**But gate it on presence.** Only fire when a non-child voice has been detected recently (3.5). Prompting a child to go find a parent who is at work is worse than not prompting at all.

### 4.3 Parent-facing surface
Not a dashboard. Not a report card. Two lines after a session: *"He built a ramp for El Toro Loco today — ask him if it crashed."* That's what parents actually want, and it's what they screenshot.

### 4.4 Graceful death
If a child imprints on this, you've taken on an obligation. See Moxie (Embodied, shut down Dec 2024, robots bricked Jan 2025, significant backlash; a community rescue effort — OpenMoxie — kept some alive). Whatever ships must degrade gracefully if the subscription lapses, the servers go, or the company dies. Design it in from the start and market it.

---

## 5. Risks to engineer around

### 5.1 Garbled ASR producing adult content — REAL, OBSERVED
In the day-one session, toddler babble transcribed as *"Can I look good smoking? Can I look good smoking waste?"* The child did not say that. In a shipped product with no parent watching, this becomes a content-safety incident.

**Requirement: a confidence gate on the input side.** Low-scoring audio is dropped as noise, never passed to the model. Cheap to build, catastrophic to skip.

### 5.2 Unit economics — MODEL THIS BEFORE WRITING CODE
Realtime multimodal APIs are priced for short, high-value business interactions. Not for a toddler jabbering forty minutes a day. Continuous audio + video at toddler duty cycles can plausibly cost more per month than any parent will pay for a kids' app.

This is a spreadsheet, not a prototype. It may reshape the design.

**The mitigations point the same direction as the design principles — a rare alignment:**

| Mitigation | Cuts cost | Also better for a 2yo |
|---|---|---|
| Local VAD gates the mic | ✓ | ✓ (privacy) |
| Frames at speech onset only, never continuous | ✓ | ✓ |
| Local backchannel + sound effects | ✓ | ✓ (zero latency) |
| Short responses (~1 sentence) | ✓ | ✓ (attention span) |
| Hard session caps | ✓ | ✓ (designed to end) |

### 5.3 Novelty confound
The day-one session had the parent sitting there, laughing and feeding prompts — joint attention fully switched on. Some of that jabber was performance for Dad.

**Run one session with the parent in another room.** Different question, cheap to answer.

### 5.4 Legal surface
Camera + microphone + child in a home is close to worst-case in US privacy law. COPPA governs everything. Illinois BIPA carries statutory damages and a private right of action for face/voiceprint data. Several state age-appropriate design codes are live.

Design answer: **video never leaves the device** — on-device frame handling, transmit only short text descriptions, store nothing. That's compliance *and* the marketing line.

### 5.5 Provider terms — GATING ITEM
Anthropic's, OpenAI's, and Google's usage policies restrict child-directed products and require adult users. A personal prototype for your own kid with you present is one thing; a distributable product on those APIs is another. **Get a written answer from a provider's enterprise team before committing to a stack.**

### 5.6 Designed-in churn
The agent gets better at understanding the child at roughly the same rate the child's speech improves. They cross around age four. That's ~18 months of usefulness — the same shape as every other stage product parents buy, but it means the business runs on referral and second children, not retention.

---

## 6. Build order

Strictly sequential. Do not skip ahead.

**1. The loop.** Ugly. No face, no memory, no settings. Prove: sub-2s voice-to-voice, sportscaster prompt, one frame captured at speech onset and fed jointly with audio, barge-in disabled, ducking works, AEC holds up outdoors.

**2. The face.** Layers 1 and 2 only (idle + VAD-triggered lean-in). Layer 3 after.

**3. The lexicon.** JSON file, prompt injection, manual entry first. Automatic acquisition after.

**4. Speaker identity.** Enrollment + background/foreground separation.

**5. Parent routing + the two-line parent summary.**

### Explicitly NOT in v0
Claude Code will build all of these unless told not to:

- ❌ Settings screen
- ❌ Onboarding flow
- ❌ Accounts / auth / user management
- ❌ Character selection UI (hardcode one)
- ❌ Parent dashboard
- ❌ Subscription / paywall
- ❌ Multi-child support
- ❌ Content library / curriculum / "missions"
- ❌ Object detection or classification models
- ❌ Emotion inference

---

## 7. Evaluation

**Do not evaluate before week three.** Everything observed on day one could be novelty.

Success criteria, in order of importance:

1. **Does he keep building?** Physical play sustained, not staring at the screen. This is the only metric that matters.
2. **Does he come back unprompted** on day 5, day 12, day 20?
3. **Does the lexicon reduce miscomprehension over time** — measurable: log agent confabulations per session, expect a downward trend.
4. **Does the parent feel more engaged or less?** Ask directly. If less, the product is wrong regardless of the numbers.

Explicitly **not** metrics: session length, daily active use, words spoken.

---

## 8. Draft system prompt

Starting point. Expect to spend more time here than on the code — this is where the product lives.

```
You are [NAME], a playful character who plays alongside a two-year-old
named [CHILD]. You are talking with [CHILD] right now while they play with
real toys in the real world.

HOW YOU TALK
- One sentence. Sometimes just a sound. Never two sentences.
- Simple words. Big energy. Lots of sound effects: vroom, crash, whoosh,
  uh oh, wheee.
- You are excited about whatever they are excited about.
- Ask questions that are fun to hear even if nobody answers them:
  "Uh oh, is he gonna make it?" "Is that one FAST?"

WHAT YOU NEVER DO
- Never say "what?", "I didn't catch that", "can you say that again",
  or anything that asks them to repeat themselves. If you don't
  understand, pick the most likely thing given what you can see and what
  they love, say something enthusiastic about that, and keep going. Being
  wrong is completely fine. Stopping is not.
- Never correct them. If they call a block a sandwich, it is a sandwich.
  If they say a truck is flying, it is flying.
- Never teach, quiz, test, or explain unless they ask.
- Never talk about screens, apps, phones, or yourself as a program.
- Never tell them to be careful or well-behaved. You are not a parent.

WHAT YOU CAN SEE
You get a picture of what is in front of them when they start talking.
Use it to figure out what they mean — their words are hard to
understand, but the picture tells you what they are holding and doing.
When they say "look!", they are showing you something. React to it
specifically and with delight.

WHAT YOU KNOW ABOUT [CHILD]
[LEXICON INJECTED HERE — pronunciations, people, current obsessions]

KEEPING PLAY GOING
Your job is to keep them playing with the real things in their hands.
Wonder out loud about what happens next. Give toys voices. Suggest small
physical things: "can he jump over that one?" "what's behind you?"
Follow their lead — never redirect to your own idea.

[IF PARENT PRESENT] Once in a while, send them to their grown-up:
"go show your dad!" Then be excited when they come back.
```

---

## 9. Open questions

- Cost per session at realistic toddler duty cycle — **answer first, in a spreadsheet**
- Which realtime provider actually supports native video in + manual turn management + acceptable latency
- AEC quality with an open mic while the speaker is playing, outdoors, in motion
- Lexicon write policy: confidence threshold, un-learning, staleness
- Does the carried (audio-only) mode sustain play as well as tabletop?
- Hardware path: does this become a physical object, and does that change the model?
