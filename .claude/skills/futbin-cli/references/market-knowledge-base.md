# EA FC 26 Market Knowledge Base

Complete trading intelligence for the Ultimate Team transfer market. Every strategy includes the exact `cli-web-futbin` commands to execute it.

## Table of Contents

1. [Weekly Market Cycle](#weekly-market-cycle)
2. [EA Tax & Profit Formula](#ea-tax--profit-formula)
3. [FC 26 Promo Calendar & Crash Windows](#fc-26-promo-calendar--crash-windows)
4. [Fodder Investment Rules](#fodder-investment-rules)
5. [Mass Bidding Strategy](#mass-bidding-strategy)
6. [CLI Trading Workflows](#cli-trading-workflows)

---

## Weekly Market Cycle

The UT transfer market follows a predictable weekly rhythm driven by game modes (FUT Champions, Division Rivals, Squad Battles) and reward distribution times. Understanding this cycle is the single most important factor for consistent profits.

| Day | What happens | Action | Why |
|-----|-------------|--------|-----|
| **Monday** | Slow market, low activity. WL over, most players done for the week. | **BUY** — prices stable/low | Fewer buyers = less demand = lower prices |
| **Tuesday** | Continued low activity. Content drops at 6PM but rarely market-moving. | **BUY** — accumulate targets | Supply still high from weekend pack openings |
| **Wednesday** | Midweek crash — FUT Champions squads get sold off as players rebuild. | **BUY** — best window of the week | Biggest supply dump of the week meets lowest demand |
| **Thursday AM** | Division Rivals rewards drop — market floods with new pack pulls. | **BUY** the initial dip | New supply temporarily depresses prices 5-10% |
| **Thursday PM** | Prices recover as players use reward coins to buy Weekend League squads. | **HOLD** or start listing | Demand picks up, prices stabilize then rise |
| **Friday** | Weekend League demand peaks. New promo/content at 6PM can cause panic selling. | **SELL** — prime window | Buyers have coins from rewards + urgency to complete squads |
| **Saturday** | Late Weekend League squad additions. Prices at weekly high for meta cards. | **SELL** — peak prices | Maximum demand, minimum patience = buyers pay premium |
| **Sunday** | Squad Battles rewards + FUT Champs sell-offs. Panic selling late night. | **BUY** late evening | Post-WL sell-off floods supply, prices crater |

### CLI commands to exploit the weekly cycle

```bash
# Wednesday/Thursday morning — find your buy targets
cli-web-futbin market scan --rating-min 85 --rating-max 89 --threshold 10 --json

# Thursday — check which players crashed most from reward packs
cli-web-futbin market movers --fallers --rating-min 84 --min-price 2000 --json

# Friday — verify your holds have risen before selling
cli-web-futbin market analyze <player_id> --json
# Sell if: trend_7d positive AND vs_avg_30d_pct > 5%

# Sunday night — check for post-WL crash buys
cli-web-futbin market movers --fallers --rating-min 86 --min-price 5000 --max-price 100000 --json
```

---

## EA Tax & Profit Formula

Every transfer market sale incurs a 5% EA tax. This is non-negotiable and applies to all platforms.

### Core formulas

| Concept | Formula | Example |
|---------|---------|---------|
| **Tax amount** | `Sale Price × 0.05` | 100K sale → 5K tax |
| **Net return** | `Sale Price × 0.95` | 100K sale → 95K return |
| **Break-even sell price** | `Buy Price / 0.95` | Bought at 10K → must sell at 10,527+ |
| **Profit** | `(Sell × 0.95) - Buy` | Buy 10K, sell 15K → 14,250 - 10,000 = 4,250 profit |
| **Profit margin %** | `((Sell × 0.95) - Buy) / Buy × 100` | 4,250 / 10,000 = 42.5% |

### Minimum viable margins by price tier

The 5% tax means you need larger price gaps to profit on expensive cards:

| Card price | Min sell price for profit | Tax cost | Notes |
|-----------|-------------------------|----------|-------|
| 1K-5K | +200 coins over buy | 50-250 | High volume needed, 10-15% margin minimum |
| 5K-20K | +1K over buy | 250-1K | Sweet spot for mass bidding |
| 20K-100K | +3-5K over buy | 1K-5K | Good for meta player flips |
| 100K-500K | +10-20K over buy | 5K-25K | Single flip can be very profitable |
| 500K+ | +50K+ over buy | 25K+ | High risk — 3% market fluctuation + tax can wipe profits |

### New card release pricing trap

When a card is first released (especially during promos), its price is artificially inflated by hype and low supply. A TOTY card that launches at 10M might settle to 3M within 2 weeks. This is NOT an indication the card is "undervalued" at 3M — the 10M was the anomaly.

When analyzing a recently released card:
- **Ignore the first 7-14 days of price history** — launch prices are noise, not signal
- **The "historic max" is misleading** for new cards — don't use price_position_pct on cards less than 2 weeks old
- **Wait for stabilization** — a card needs ~2 weeks of flat-ish prices to establish a true trading range
- **Check `market latest`** — if the card appeared recently, treat all analysis with caution

```bash
# Check if a card is newly released before trusting analysis
cli-web-futbin market latest --json
# If the player appears in latest, their price history is too short for reliable signals

# For new cards, use price_range instead of price_history for context
cli-web-futbin players get <id> --json
# The price_range.min shows EA's floor — if current price is near it, card might be settling
```

### CLI commands for profit calculation

```bash
# Check a player's current price vs 30d average to estimate margin
cli-web-futbin market analyze <player_id> --json
# If vs_avg_30d_pct is -15%, the card is 15% below average
# After 5% tax, that's still ~10% profit if it reverts to mean

# Find cards with enough margin to overcome tax
cli-web-futbin market scan --rating-min 84 --threshold 15 --json
# threshold 15 means only show players 15%+ below avg — enough margin after tax
```

---

## FC 26 Promo Calendar & Crash Windows

Promos cause market crashes because EA releases special packs that flood the market with supply. Knowing the schedule lets you sell BEFORE crashes and buy DURING them.

### Major promos (confirmed FC 26 dates)

| Promo | Dates | Market impact | Strategy |
|-------|-------|--------------|----------|
| **TOTY** | Jan 16 - Feb | Biggest crash of the year. All meta cards lose 30-50% value. | Sell meta cards by Jan 10. Buy during Jan 22-30 window. |
| **Future Stars** | Feb (expected) | Moderate crash. Young player meta cards drop. | Buy promising young cards after initial crash settles. |
| **FUT Birthday** | Mar 6-20 | Icon SBCs spike fodder temporarily, then crash. | Sell fodder BEFORE Mar 6. Buy special cards during promo. |
| **Fantasy FC** | Feb 20 - May 29 | Long-running, gradual shifts. Live items upgrade. | Track live items — buy early, sell on upgrades. |
| **Festival of Football** | Mar 20-27 | World Cup 2026 warmup. National team demand rises. | Stockpile key nation players beforehand. |
| **TOTS** | May-Jun (expected) | Second biggest crash. 90+ rated cards become common. | Sell all high-rated cards before TOTS. Market bottom during. |
| **Shapeshifters** | Jun 12 - Jul 10 | Position changes create new meta. Out-of-position demand. | Buy cheap versions of shifted players before hype. |
| **World Cup Path to Glory** | Jun 26 - Jul 24 | National team upgradable cards. Country progression drives price. | Invest in strong-nation base cards early. |
| **Futties** | Jul 10 - Aug 14 | End-of-cycle super cards. Market at annual low. | Buy anything you want to try. Prices don't matter anymore. |
| **Black Friday** | Late Nov | Short but intense. Hourly pack drops, lightning rounds. | Sell everything Wed before. Buy cheap Thursday-Friday. |

### Pre-crash preparation checklist

```bash
# 1. Check your high-value holds — are they near historic highs?
cli-web-futbin market analyze <player_id> --json
# If price_position_pct > 60%, consider selling before crash

# 2. Monitor market index for early signs of sell-off
cli-web-futbin market index --json
# Falling indices across all tiers = crash starting

# 3. Check fodder tiers — are they inflated?
cli-web-futbin market fodder --rating-min 84 --json
# If 84-rated > 5K, they're inflated — sell before promo

# 4. During crash — find the deepest dips
cli-web-futbin market movers --fallers --rating-min 88 --min-price 10000 --json
cli-web-futbin market scan --rating-min 86 --rating-max 90 --threshold 20 --json
```

---

## Fodder Investment Rules

Fodder trading is the safest and most consistent money-maker in UT. "Fodder" means high-rated cards (83-91) used primarily as SBC fuel, not for gameplay.

### The fodder cycle

```
No active SBCs → Fodder prices LOW → BUY
    ↓
Popular SBC released (Icon, POTM, etc.) → Fodder demand SPIKES → SELL
    ↓
Promo starts → Pack opening floods supply → Fodder CRASHES → BUY again
```

### Investment tiers (safest to riskiest)

| Rating | Typical price range | Risk level | Notes |
|--------|-------------------|------------|-------|
| 83 | 700-2K | Very low | Massive supply, small margins, high volume |
| 84 | 1K-4K | Low | Best risk/reward ratio for beginners |
| 85 | 2K-8K | Low | Consistent demand from mid-tier SBCs |
| 86 | 3K-12K | Medium | Good margins, moderate supply |
| 87 | 4K-15K | Medium | Higher margins, less liquid |
| 88+ | 5K-30K+ | Higher | Big margins but slower to sell, more volatile |

### Golden rules

1. **Buy 84-87 rated** — safest investment tier with consistent SBC demand
2. **Buy when no active SBCs** — supply high, demand low, prices at floor
3. **Sell when popular SBC drops** — Icon SBCs, POTM, Upgrade SBCs spike demand
4. **Sell BEFORE promo starts** — pack openings crash fodder within hours
5. **Never hold fodder through TOTY or TOTS** — pack spam destroys fodder prices for weeks
6. **Diversify across ratings** — don't put all coins in one tier

### CLI fodder workflow

```bash
# Step 1: Check current fodder prices across tiers
cli-web-futbin market fodder --json

# Step 2: Compare to market index to see if fodder is cheap or inflated
cli-web-futbin market index --rating 84 --json
cli-web-futbin market index --rating 85 --json
# If index is near "lowest" → fodder is cheap → BUY
# If index is near "highest" → fodder is inflated → SELL or HOLD

# Step 3: Find the cheapest cards at your target rating
cli-web-futbin market cheapest --rating-min 84 --rating-max 84 --json
cli-web-futbin market cheapest --rating-min 85 --rating-max 85 --json

# Step 4: When SBC drops, check if fodder is rising
cli-web-futbin market movers --rating-min 83 --min-price 500 --max-price 20000 --json
# If your ratings are in the risers list → SELL NOW

# Step 5: Verify specific card price before selling
cli-web-futbin market analyze <player_id> --json
# Sell if: vs_avg_30d_pct > 10% (above average = inflated)
```

---

## Mass Bidding Strategy

Mass bidding means placing 50-100+ bids at once, slightly below market price, winning ~30-40% of them, and relisting at BIN for profit. It's the most scalable trading method.

### Target profile

| Parameter | Value | Why |
|-----------|-------|-----|
| Price range | 2K-10K | Enough margin after tax, high enough volume |
| Rating range | 83-86 | Consistent demand, not too volatile |
| Card type | Gold Rare, meta players | Buyers want them for squads or SBCs |
| Bid discount | 10-20% below BIN | Aggressive enough to win, conservative enough to profit |

### Profit math example

| Scenario | Values |
|----------|--------|
| Lowest BIN | 5,000 |
| Your bid | 4,200 (16% below BIN) |
| Relist at | 4,900 (just under BIN) |
| After 5% tax | 4,655 |
| **Profit per card** | **455 coins** |
| Win rate (50 bids) | ~18 wins |
| **Total profit** | **~8,190 coins per round** |

### CLI commands for mass bidding research

```bash
# Find mass bidding targets — cheapest meta cards in the sweet spot
cli-web-futbin market cheapest --rating-min 83 --rating-max 86 --min-price 2000 --max-price 10000 --json

# Check which cards are popular (high demand = faster sell)
cli-web-futbin market popular --limit 50 --json

# Verify a specific target has enough margin
cli-web-futbin market analyze <player_id> --json
# Good target: volatility_30d < 15% (stable price) AND price_position_pct < 40%

# Track your results with movers
cli-web-futbin market movers --rating-min 83 --min-price 2000 --max-price 10000 --json
```

---

## CLI Trading Workflows

Complete step-by-step recipes for common trading scenarios.

### Daily Trading Routine (10 minutes)

Run this every day to spot opportunities:

```bash
# 1. Market health check — is the market up or down today?
cli-web-futbin market index --json

# 2. What's moving? Check biggest risers and fallers
cli-web-futbin market movers --rating-min 84 --min-price 2000 --json
cli-web-futbin market movers --fallers --rating-min 84 --min-price 2000 --json

# 3. Any new cards dropped? (could shift meta or create investment opportunities)
cli-web-futbin market latest --json

# 4. What's trending? (hype often precedes price spikes)
cli-web-futbin market popular --limit 20 --json

# 5. Check fodder tiers for SBC investment timing
cli-web-futbin market fodder --rating-min 84 --rating-max 88 --json

# 6. Quick scan for undervalued cards in your target range
cli-web-futbin market scan --rating-min 85 --rating-max 89 --limit 10 --json
```

### Pre-Promo Preparation (run 3-5 days before any major promo)

```bash
# 1. Sell check — analyze all your high-value holds
cli-web-futbin market analyze <player_id> --json
# Sell if: price_position_pct > 40% (near recent highs)
# Sell if: trend_30d negative (already declining)

# 2. Check market indices — is the market already deflating?
cli-web-futbin market index --json
# Falling indices = players already selling ahead of promo

# 3. Identify post-crash buy targets (research now, buy during crash)
cli-web-futbin players versions --name "Mbappe" --json
cli-web-futbin players versions --name "Haaland" --json
# Note which versions have best value_score — buy those during crash

# 4. Check fodder — sell if inflated
cli-web-futbin market fodder --json
cli-web-futbin market index --rating 85 --json
# If 85-rated index near "highest" → SELL ALL FODDER NOW

# 5. Check cross-platform gaps — arbitrage opportunities spike pre-promo
cli-web-futbin market arbitrage --rating-min 88 --min-gap 10 --json
```

### Post-Crash Recovery Buying (run during/after a promo crash)

```bash
# 1. How deep is the crash? Check index vs normal levels
cli-web-futbin market index --json
# Compare "current" to "open" — large negative change = deep crash

# 2. Find the biggest fallers — these are your buy candidates
cli-web-futbin market movers --fallers --rating-min 87 --min-price 5000 --json

# 3. Deep analysis on top candidates — look for oversold signals
cli-web-futbin market analyze <player_id> --json
# BUY signals: price_position_pct < 10%, vs_avg_30d_pct < -20%, trend_7d starting to stabilize

# 4. Scan for bulk undervalued cards
cli-web-futbin market scan --rating-min 86 --rating-max 90 --threshold 15 --limit 20 --json
# Buy any with signal=BUY

# 5. Check fodder — crashes are prime fodder buying time
cli-web-futbin market fodder --json
# If 84-rated < 1.5K and 85-rated < 3K → load up, they'll rebound
```

### Fodder Cycle Trading (the bread-and-butter strategy)

```bash
# PHASE 1: IDENTIFY (is fodder cheap right now?)
cli-web-futbin market fodder --json
cli-web-futbin market index --rating 84 --json
cli-web-futbin market index --rating 85 --json
# If indices near "lowest" → proceed to Phase 2

# PHASE 2: BUY (accumulate cheap fodder)
cli-web-futbin market cheapest --rating-min 84 --rating-max 84 --max-price 2000 --json
cli-web-futbin market cheapest --rating-min 85 --rating-max 85 --max-price 4000 --json
cli-web-futbin market cheapest --rating-min 86 --rating-max 86 --max-price 6000 --json
# Buy the cheapest at each tier — diversify across ratings

# PHASE 3: MONITOR (wait for SBC to spike demand)
cli-web-futbin sbc list --json
# Check daily — when a popular SBC drops (Icon, POTM, Upgrade), proceed to Phase 4

# PHASE 4: SELL (fodder is spiking)
cli-web-futbin market movers --rating-min 83 --min-price 500 --max-price 20000 --json
# If your ratings are rising → sell immediately
cli-web-futbin market analyze <player_id> --json
# Confirm: vs_avg_30d_pct > 10% → sell at inflated price
# Don't wait for the absolute peak — sell when you're 10-20% up
```

---

## Signal Interpretation Guide

The `market analyze` command returns a `signal` field. Here's how to interpret it in different contexts:

| Signal | Meaning | When to act | When to ignore |
|--------|---------|------------|---------------|
| **BUY** | >10% below 30d avg, 7d trend stable/rising | Strong buy if you understand why it dipped (crash, new card released) | Ignore if the card is being replaced by a better version (permanent decline) |
| **SELL** | >15% above 30d avg, 7d trend falling | Sell if you're holding for profit. The bubble is deflating. | Ignore if a major SBC just dropped and demand is still rising |
| **HOLD** | Near average, no strong signal either way | Wait for a clearer signal. Check again in 1-2 days. | Act anyway if you have time-sensitive info (promo coming, SBC expiring) |

### Combining signals with context

The signal alone isn't enough. Always combine with:
1. **Weekly cycle** — Is it Wednesday (buy day) or Friday (sell day)?
2. **Promo calendar** — Is a crash coming that will push prices lower?
3. **SBC activity** — Did a new SBC just drop that needs this rating?
4. **Market index** — Is the whole market moving, or just this card?

```bash
# Full decision workflow for any card:
cli-web-futbin market analyze <id> --json     # Signal + trends
cli-web-futbin market index --json             # Market-wide context
cli-web-futbin sbc list --json                 # Active SBC demand
cli-web-futbin market movers --json            # What else is moving?
```
