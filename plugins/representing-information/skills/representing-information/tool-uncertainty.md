# Showing Uncertainty

Two questions get conflated and have different answers: **in what form** to show uncertainty, and
**whether** to show it. The literature answers the first with an uncomfortable finding — the
near-universal default is the one form shown to distort judgement — and the second against the
folklore.

## The move
- **Never default to a bare bar plus error bar.** Correll & Gleicher measured a **within-the-bar
  bias**: values inside the bar's filled region are judged more probable than values the same
  distance outside it, so the same interval reads asymmetrically. Gradient and violin encodings
  aligned judgement better with the statistics.
- **Pick for the reader's task, not for the statistic you happen to have.** Kale, Kay & Hullman
  found **the display best supporting unbiased effect-size estimation is not the one best supporting
  decisions**, and that **adding a mean marker biases readers toward discounting the spread** — so
  "should I mark the mean?" is a real decision with a known cost, not a free clarification.
- **Match the interval to the question.** Confidence interval for precision of an estimate;
  prediction or distributional forms where the question is about an individual outcome. Showing CIs
  where prediction intervals belong makes readers overestimate effects and pay more (Hofman et al.).
- **Show it as a range, never as a hedge.** van der Bles et al. (five experiments, including a BBC
  News field experiment, n=5,780): numeric uncertainty cost a small amount of trust in the number
  and essentially none in the source. Kerr et al. (N=10,519) located the harm precisely — **vague
  verbal statements that uncertainty exists damage trust in both number and source; numeric ranges
  do not.** Disclosure is not the risk; vagueness is.

## The forms, and what each is good for
- **Quantile dotplots and CDFs** — countable discrete outcomes. Fernandes et al. found they produced
  better real transit decisions than a textual interval or a continuous density, with dotplots best
  for a general public. The strongest result available for a non-expert deciding under uncertainty.
- **Hypothetical outcome plots** — animated draws, letting readers count instead of decoding an
  interval. Hullman et al. found HOPs beat error bars and violins **for judging the reliability of
  an ordering**; for a single distribution all three were comparable. Narrower than the enthusiasm
  suggests, and the costs are structural: motion excludes some readers, several assistive paths, and
  every printed or forwarded artefact.
- **Gradient and violin** — better than a bar-plus-error-bar for probability judgements about values.

## Apply it — risk framing
Format does not change how fast an answer arrives; it changes **which answer competent people give**.

- **Natural frequencies over conditional probabilities.** Given a positive mammography as
  conditional probabilities, about 60% of gynaecologists put the positive predictive value at
  81–90%; the true answer is about 10%. Recast as counts out of a thousand women, **87% got it
  right** — same figures, same doctors, minutes apart. Natural frequencies work because the base
  rate stays inside the numbers instead of having to be reinstated.
- **Absolute alongside relative.** A Cochrane review found the asymmetry reliably: relative risk
  reduction makes an intervention look bigger and raises willingness to take it; absolute risk and
  number-needed-to-treat do not inflate. **"Risk cut by 50%" with no base rate** is technically true
  at any base rate — four in ten to two in ten, or four in a million to two in a million — and is
  the commonest way a chart misleads without lying. Put the base rate in the visible channel.
- **Hold the denominator constant** across every comparison. One in eight here, 12.5% there, 125 per
  thousand overhead: each conversion correct, the set unreadable.
- **Numeracy does not exempt anyone.** Below-median numeracy predicted framing susceptibility even
  within a high-numeracy sample, and the clearest demonstration used specialists reading figures
  from their own field.
- **Choose the framing before you know which way it favours you.** Deciding the format after seeing
  which version flatters is where format selection becomes persuasion — see `tool-honesty.md`.
- **When nothing can be distinguished, say that in the title.** The honest null is a finding.

## Failure modes
- **The reflex error bar** — reached for because the tool produces it and the discipline expects it.
- **Hedging instead of quantifying** — "approximately", "indicative only". The move the evidence says costs trust.
- **Silent substitution of inferential for outcome uncertainty** — precision about a mean, where the reader is asking about one person.
- **Picking the display from the statistic** — having a CI and therefore drawing an interval.
- **Motion without checking the occasion** — a HOP in a document that will be printed is an absent uncertainty display.
- **"Uncertainty paralyses decision-makers"** — asserted far more often than demonstrated; the trust evidence points the other way.

## Depth
`representing-information/uncertainty-and-honesty/showing-uncertainty.md` and `risk-framing.md` in
an optional source corpus (when available). Caveat: the HOP and quantile-dotplot literature is
dominated by crowdworker samples on low-stakes tasks; none of it tested high-stakes, time-pressured
or adversarial settings. The disclosure findings are the best-powered material here.
