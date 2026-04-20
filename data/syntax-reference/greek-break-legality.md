# Greek Break Legality — Layer 1

**Layer 1** documents syntactic constraints on line breaks that hold for any Koine Greek edition, independent of editorial sense-line choices. A validator matches each row against parsed token data; a verdict of `REQUIRED-MERGE` or `REQUIRED-BREAK` flags a hard syntactic violation. `PERMITTED-EITHER` rows pass to Layer 3 editorial rules in `private/01-method/colometry-canon.md`.

Parse data sources: Macula-Greek (`github.com/Clear-Bible/macula-greek`, CC-BY 4.0) and MorphGNT (`github.com/morphgnt/sblgnt`, CC-BY-SA). Use dependency and POS fields; token position within line is the check surface.

---

| Syntactic signature | Legality verdict | Grammar reference | Brief note |
|---|---|---|---|
| `CCONJ (καί, δέ, ἀλλά, γάρ, οὖν) at line end` | `REQUIRED-MERGE` | BDF §442; Smyth §2834 | Coordinating conjunction must stay with the clause it introduces |
| `CCONJ (δέ, γάρ, οὖν, μέν, τε, ἄν) at line start` | `REQUIRED-MERGE` | BDF §442; Smyth §2834 | Postpositives are second-position; line-initial placement is ill-formed |
| `DET at line end (any case/gender/number of ὁ, ἡ, τό)` | `REQUIRED-MERGE` | BDF §249; Wallace §215 | Article must immediately precede or frame its noun phrase |
| `DET + N split across line boundary` | `REQUIRED-MERGE` | BDF §249; Smyth §1118 | Article and its noun are a single syntactic unit |
| `PART (οὐ, οὐκ, οὐχ, μή) at line end` | `REQUIRED-MERGE` | BDF §426; Smyth §2693 | Negative particle must attach to the word it negates |
| `PART (οὐδέ, μηδέ) at line end` | `REQUIRED-MERGE` | BDF §445.3; Smyth §2765 | Negative correlative must precede its constituent |
| `PART (οὐκέτι, μηκέτι, μήποτε) at line end` | `REQUIRED-MERGE` | BDF §426; Wallace §667 | Compound negative adverb must attach to its verbal head |
| `AUX (εἰμί finite) + VERB (participle) split across line` | `REQUIRED-MERGE` | BDF §352–353; Wallace §647–649 | Periphrastic construction is a single verbal unit |
| `AUX (μέλλω) + VERB (infinitive) split across line` | `REQUIRED-MERGE` | BDF §356; Wallace §647 | Auxiliated infinitive is a single verbal unit |
| `AUX (ἄρχομαι) + VERB (infinitive) split across line` | `REQUIRED-MERGE` | BDF §392; Smyth §2002 | Phasal auxiliary and infinitive are a single verbal unit |
| `ADP at line end (any preposition governing a following NP)` | `REQUIRED-MERGE` | BDF §203; Smyth §1636 | Preposition and its object form an inseparable syntactic unit |
| `ADP + NP split across line boundary` | `REQUIRED-MERGE` | BDF §203; Smyth §1636 | Prepositional phrase must be contiguous |
| `Vocative multi-word unit split across line` | `REQUIRED-MERGE` | BDF §146; Smyth §1283 | Multi-word vocative address is a single illocutionary unit |
| `Crasis token (e.g., κἀγώ, κἀκεῖ) at line boundary forcing morpheme split` | `REQUIRED-MERGE` | BDF §18; Smyth §68 | Crasis is a single orthographic and prosodic word |
| `Interrogative particle (ἆρα, οὐχί, μήτι) at line end separated from governing verb` | `REQUIRED-MERGE` | BDF §440; Smyth §2651 | Interrogative particle scopes over the clause it introduces |
| `Fixed phrase split: εἰς τὸν αἰῶνα` | `REQUIRED-MERGE` | BDF §217.3; BDAG s.v. αἰών | Formulaic prepositional phrase; internal break destroys the idiom |
| `Fixed phrase split: ἐν αὐτῷ / ἐν αὐτοῖς (idiomatic locative)` | `REQUIRED-MERGE` | BDF §220; BDAG s.v. ἐν | Formulaic locative; internal break is syntactically inadmissible |
| `Governing noun + immediately adjacent dependent genitive (short adnominal)` | `PERMITTED-EITHER` | BDF §162; Wallace §78–79 | Grammar permits both; break decision belongs to Layer 3 |
| `Subject pronoun + finite verb (same clause, adjacent tokens)` | `PERMITTED-EITHER` | Smyth §937; BDF §277 | Explicit pronoun subject is not bound to verb by Greek syntax |
| `Participial phrase (non-gen-abs) immediately following its head noun` | `PERMITTED-EITHER` | BDF §412; Smyth §2050 | Attachment is semantic, not syntactic; Layer 3 decides |
| `Relative clause introduced by ὅς immediately following its antecedent` | `PERMITTED-EITHER` | BDF §293; Smyth §2555 | Break before relative clause is syntactically legal; Layer 3 decides |
| `Subordinate clause introduced by ἵνα, ὥστε, ὅτι, ὅταν, εἰ, ἐάν` | `PERMITTED-EITHER` | BDF §369, 391, 442; Smyth §2200 | Connector at line start is syntactically well-formed; Layer 3 decides |
| `Genitive absolute (gen noun/pronoun + gen participle, syntactically detached)` | `PERMITTED-EITHER` | BDF §423; Wallace §654–655 | Syntactically independent; Layer 3 mandates its own line |
| `Infinitival complement to main verb (no AUX)` | `PERMITTED-EITHER` | BDF §390; Smyth §1966 | Complement infinitive is a full clause boundary; Layer 3 decides |
