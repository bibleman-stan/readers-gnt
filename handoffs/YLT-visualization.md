# YLT Visualization Layer — Conversation Handoff

Verbatim conversation from 2026-04-10 exploring whether a toggleable YLT English layer belongs in the GNT Reader.

---

## Stan:

let's revisit whether adding anything else to the gnt reader makes sense - for example, hovering over a word revealing the english gloss? and/or something more "logos like" in terms of having a "turn on/turn off" layer that would give a fairly literal rendering of the text into english on an atomic thought by atomic thought basis? this to me seems like a potential value-added not at odds with the objectives of the key researcher demographic, some of whom are fluent in greek but maybe some of whom are not/are rusty, etc. thoughts? give me pros and cons analysis

## Claude:

Good instinct to revisit this — these are fundamentally different from the morpheme reader. Let me think through each.

### 1. Hover Glosses (word-level)

**Pros:**
- Keeps the reading flow — you only see a gloss when you need it, then it disappears
- Zero visual noise in default state; the colometric layout stays pristine
- Directly serves the "rusty Greek" reader who can follow 80% but hits a wall on a rare word
- Low implementation cost — you already have MorphGNT lemmas in the repo and could generate a frequency-based gloss table
- This is a *reading aid*, not an analysis tool — it helps people stay in the text rather than leaving to look something up

**Cons:**
- Mobile: hover doesn't exist, so you'd need tap-to-reveal, which is clunkier
- Gloss quality matters — a bad one-word gloss for a theologically loaded term could mislead more than help (e.g., δικαιοσύνη → "righteousness" is fine, but σάρξ → "flesh" flattens Paul's whole argument)
- You need a curated lexicon, not just an auto-generated one — or at minimum, editorial review of the glosses
- Adds a JS event layer and a data dependency (gloss JSON) to what's currently pure static HTML

**Verdict:** This is a natural fit. It's the digital equivalent of a vocabulary footnote in a printed reader's edition — Mounce's reader, UBS reader, they all do this. It doesn't change what the site *is*.

### 2. Toggle-able English Sense-Line Rendering

**Pros:**
- This is where your colometric structure becomes a *unique advantage* — no one else can offer a sense-line-aligned English rendering because no one else has sense lines
- It's genuinely useful for the intermediate reader: see the Greek line, see what it means, keep going
- Toggle on/off preserves the clean default state
- It reinforces the colometric pedagogy — the reader *sees* that each line is an atomic thought because the English confirms it
- Could attract a wider audience (seminary students, pastors prepping sermons, devotional readers with some Greek)

**Cons:**
- **Translation is editorial.** Every English line is an interpretive decision. Who writes them? You're no longer just formatting the SBLGNT — you're producing a translation, even if "fairly literal." This is a different scholarly claim with different accountability
- **Maintenance scope doubles.** 27 books of aligned English text that needs to track your colometric breaks. Every time you re-break a Greek line, the English has to be updated
- **Which English?** If you write your own, it's a massive undertaking. If you pull from an existing translation (ESV, NASB, etc.), you hit copyright walls and the line breaks won't align with yours
- **Risk of becoming a parallel Bible.** The moment there's English on screen, some users will just read the English. You've inadvertently built a bilingual reader, which is a different product
- **Scholarly perception:** "Reading edition with optional English interlinear" sounds closer to a student crib than a scholarly tool

### The Spectrum

| Feature | Changes product identity? | Reading aid or analysis tool? | Implementation cost |
|---------|--------------------------|-------------------------------|-------------------|
| Hover glosses | No | Reading aid | Low-medium |
| Sense-line English toggle | Yes, meaningfully | Reading aid, but also a translation | High |

### My Take

**Hover glosses: yes, do it.** It's table stakes for a digital reader's edition. Every printed reader's edition has vocabulary helps. The digital version should too, and hover/tap is more elegant than footnotes.

**Sense-line English: not yet, and maybe not here.** The translation problem is real — it's either a massive editorial undertaking or a copyright issue. And it shifts the site's identity from "Greek reading edition" toward "bilingual parallel text." If you do pursue it eventually, it might work better as a separate toggle-able layer in the morpheme reader site, where the expectations are already "analysis + helps."

The one exception: if you could auto-generate a *gloss-level* rendering (not a real translation, but a word-order-following rough crib like an interlinear), that's less editorially fraught. But it's also less useful and more ugly.

What's your read on the translation question — would you want to write your own, or were you thinking of aligning an existing one?

---

## Stan:

what (if any) translations are in the public use space that might be of use? if it's just a matter of splitting the YLT for example, maybe the cost is actually not as steep?

## Claude:

Here's what's available, ranked by how well they'd align to Greek clause structure:

### Public Domain NT Translations

| Translation | Year | Literalness | Greek word-order fidelity | Digital availability |
|---|---|---|---|---|
| **YLT** (Young's Literal) | 1898 | Extreme | Best of any English translation | OSIS XML, USFM on eBible.org/GitHub |
| **ASV** | 1901 | Very high | Close | USFM, OSIS on eBible.org |
| **Darby** | 1890 | Very high | Close | eBible.org, GitHub |
| **KJV** | 1769 | High | Moderate — reshapes clauses for English rhythm | Everywhere |
| **WEB** (World English Bible) | 2000+ | Moderate-high | Moderate — smooths Greek structures | USFM on eBible.org, explicitly PD |

### The YLT Case

You're right that YLT changes the cost calculation significantly. Young *intentionally* preserved Greek clause structure, tense distinctions, even word order where English tolerates it. That means:

- Your colometric line breaks will often correspond to natural break points in the YLT text
- A script could do the initial alignment: split YLT verse text at the same clause boundaries you've already identified in the Greek
- The hand-editing pass would be *refinement*, not *translation from scratch*

A rough pipeline: verse-match YLT to SBLGNT by reference → within each verse, align YLT clause segments to your colometric lines → hand-review for places where Young restructured.

### The Remaining Cost

It's not zero though:

- **YLT is 1898 English.** "Hath," "doth," "ye," etc. Some users will find this charming; others will find it a barrier. The WEB exists partly to solve this problem
- **Alignment isn't 1:1.** Even YLT rearranges some clauses. You'd need a review pass per chapter, and some lines will need manual splitting/joining
- **Your colometric breaks are finer-grained than verses.** The automation gets you to verse-level, but splitting within verses still requires editorial judgment about where the English maps to each colon

### Revised Verdict

With YLT or ASV as the source, this drops from "massive editorial undertaking" to "medium scripting project + editorial review pass." Maybe 60% automatable, 40% hand-refinement. That's a meaningfully different proposition than writing a translation.

The question becomes: does a toggleable YLT/ASV layer underneath each Greek sense-line serve your target reader, or does archaic English undercut the whole thing? WEB solves the language problem but aligns less cleanly.

Want me to pull down one of these (YLT for Galatians, say) and do a test alignment against your colometric breaks so we can see how close the automated match actually gets?

---

## Stan:

the whole point would be to have a hidden-by-default layer that could be those "crib" notes you mentioned when assessing the value/impact of our colometric result set; give me a mock up of acts 9:1-3 and let me see what it looks like/my first impressions in terms of "we really can just break ylt to match our breaks" or not

## Claude:

*(Claude produced a mockup alignment of Acts 9:1-3 with YLT split to match colometric breaks. The first attempt over-split the lines — Stan sent a screenshot of the actual rendering and corrected the error.)*

---

## Stan:

*(screenshot of actual Acts 9:1-3 rendering)*

what are you looking at? you're not accurately describing my line breaks

## Claude:

You're right, I apologize. I over-split the lines in my mockup. Looking at the actual text file and your screenshot:

*(Claude acknowledged the line count discrepancy — the actual text file shows:)*

**9:1** — 2 lines:
```
Ὁ δὲ Σαῦλος ἔτι ἐμπνέων ἀπειλῆς καὶ φόνου εἰς τοὺς μαθητὰς τοῦ κυρίου,
προσελθὼν τῷ ἀρχιερεῖ
```

**9:2** — 3 lines:
```
ᾐτήσατο παρʼ αὐτοῦ ἐπιστολὰς εἰς Δαμασκὸν πρὸς τὰς συναγωγάς
ὅπως ἐάν τινας εὕρῃ τῆς ὁδοῦ ὄντας,
ἄνδρας τε καὶ γυναῖκας, δεδεμένους ἀγάγῃ εἰς Ἰερουσαλήμ.
```

**9:3** — 3 lines:
```
ἐν δὲ τῷ πορεύεσθαι
ἐγένετο αὐτὸν ἐγγίζειν τῇ Δαμασκῷ,
ἐξαίφνης τε αὐτὸν περιήστραψεν φῶς ἐκ τοῦ οὐρανοῦ,
```

---

## Stan:

i guess i'm now thinking that a might be a solid option, and that you could even HIDE the greek and leave the "re-worked" YLT as the only visible text; this would open up the project to a broader audience, both scholarly (DH, statisticians, etc.) who don't have Greek, or the layperson who'd like to see a text that proposes to better convey the atomic thoughts/possibly more genuine breaks intended by the author

## Claude:

That's a genuinely important realization. You've just redefined what the project *is*.

Up to now the colometric edition has been: "a better way to read the Greek." But what you're describing is: **the colometric structure itself is the scholarly contribution, and the Greek is just one way to view it.** The sense-line breaks are a claim about discourse structure — about where Luke (or Paul, or John) put the seams in their thinking. That claim is legible in any language.

A "colometric YLT" would be a unique artifact. Nobody has done this. You'd have:

- **Greek mode** — what you have now, for Greek readers
- **English mode** — the same colometric structure rendered in YLT, for anyone
- **Interleaved mode** — both, for learners and comparativists

Three views of one underlying data structure: your line breaks.

### What this changes strategically

**Audience goes from hundreds to thousands.** Seminary students, pastors, DH researchers, literary scholars interested in oral performance, translation theorists — none of them need Greek to see and evaluate your colometric proposals.

**The scholarly argument becomes self-demonstrating.** Instead of writing a paper that *describes* your colometric principles, you ship a site that *shows* them. A reader can toggle to English and immediately see "oh, each line really is one thought."

**YLT's woodenness becomes a feature, not a bug.** The archaic English doesn't matter because nobody's reading it *as literature* — they're reading it as a structural diagram that happens to use English words. "Having gone to the chief priest" is actually *better* than a smooth modern translation here because it preserves the participial structure that motivated your line break.

### What to watch out for

**You're now making two claims, not one.** Claim 1: these line breaks reflect the Greek discourse structure. Claim 2: this YLT splitting accurately represents those breaks in English. Claim 2 is editorial work that can be wrong independently of claim 1. A bad YLT split could undermine confidence in the Greek colometry.

**YLT is still a translation.** Where Young departed from Greek clause order (and he does sometimes), your English lines will misrepresent the structure you're claiming. You'd need to flag or hand-edit those cases.

**Scope creep risk is real again** — but it's a *different* risk than the morpheme reader. This isn't bolting on a foreign feature. This is the same feature (colometric structure) rendered in a second language. It's more like internationalization than feature creep.

### The minimal version

A toggle in the settings panel: **Greek / English / Both**. The data is just a second text file per chapter (`acts-09-ylt.txt`) with the same line count as the Greek. Build pipeline reads both, emits both wrapped in a class, CSS shows/hides. Extremely simple implementation.

---

## Open Questions

1. **Go/no-go decision** — Stan has not yet committed to this. The conversation ended with a proposal to think through the data pipeline.
2. **YLT alignment quality** — No rigorous test has been done. Need to actually split YLT for a full chapter against colometric breaks and assess the match rate.
3. **Display mode** — Interleaved (option A) with three modes (Greek / English / Both) is the current leading design. Side-by-side rejected. Hover/tap-per-line still viable as alternative.
4. **YLT source** — Need to acquire machine-readable YLT (eBible.org USFM is the likely source) and write a splitting script.
5. **Editorial review workflow** — How does Stan review/approve the YLT splits? Same as colometric editing (text files, one line per colon)?
