---
name: futbin-cli
description: Use cli-web-futbin to answer questions about EA FC Ultimate Team players, prices, player comparison, SBCs, evolutions, config, market data, popular/trending players, newly released cards, price history, finding cheap deals, market analysis, undervalued players, cross-platform arbitrage, trading signals, version comparisons, and trading strategies. Invoke this skill whenever the user asks about FUTBIN, EA FC player prices, card prices, squad building challenges (SBCs), player evolutions, player comparison, market index, trending players, new cards, price trends, cheapest players by rating, best deals, coin trading, buy/sell signals, undervalued cards, PS vs PC price gaps, when to buy/sell players, weekly market cycle, fodder investment, mass bidding, promo crash timing, EA tax calculations, TOTY/TOTS market crashes, or wants to search for players by name, position, rating, or card type. Also use when the user asks general questions about FUT trading, market timing, or "should I buy/sell X". Always prefer cli-web-futbin over manually fetching the FUTBIN website. Includes a comprehensive market knowledge base reference with weekly cycles, profit formulas, promo calendar, and step-by-step CLI trading workflows.
---

# cli-web-futbin

CLI for [FUTBIN](https://www.futbin.com/) — EA FC Ultimate Team player database.
Installed at: `cli-web-futbin` (run `cli-web-futbin --help` to verify).

## Quick Start

```bash
# Search by name
cli-web-futbin players search --name "Mbappe" --json

# List with filters
cli-web-futbin players list --position ST --cheapest --json

# Compare two players
cli-web-futbin players compare 40 42 --json

# Market index
cli-web-futbin market index --json

# Popular/trending players
cli-web-futbin market popular --limit 20 --json

# Newly released cards
cli-web-futbin market latest --json

# Cheapest players by rating (for SBCs/trading)
cli-web-futbin market cheapest --rating-min 88 --json

# Price analysis + buy/sell signal
cli-web-futbin market analyze 40 --json

# Find undervalued players (bulk scan)
cli-web-futbin market scan --rating-min 85 --rating-max 89 --json

# Cross-platform arbitrage (PS vs PC price gaps)
cli-web-futbin market arbitrage --rating-min 88 --min-gap 5 --json

# All versions of a player compared with value score
cli-web-futbin players versions --name "Haaland" --json

# Price history & trends
cli-web-futbin players price-history 40 --json

# SBCs
cli-web-futbin sbc list --json

# Evolutions
cli-web-futbin evolutions list --json
```

Always use `--json` when you need to parse or display data programmatically.

---

## Commands

### `players search`

Searches by player name. Uses the FUTBIN JSON API — fast, returns ratings and prices.

```bash
cli-web-futbin players search --name "Salah" --json
cli-web-futbin players search --name "Ronaldo" --year 25 --json
cli-web-futbin players search --name "Mbappe" --evolutions --json
```

**Options:** `--name` (required), `--year` (default 26), `--evolutions` (include evo cards)

**Output fields:** `id`, `name`, `rating`, `position`, `version`, `club`, `nation`, `year`, `ps_price`, `xbox_price`, `url`, `stats` (empty `{}` in search — use `players get` for full stats)

---

### `players list`

Browse/filter the full player database. Supports comprehensive filters.

```bash
# Cheapest gold rare strikers
cli-web-futbin players list --position ST --version gold_rare --cheapest --json

# Top rated CAMs rated 85+, page 2
cli-web-futbin players list --position CAM --rating-min 85 --page 2 --json

# TOTY players under 500K
cli-web-futbin players list --version toty --max-price 500000 --cheapest --page 1 --json

# 5-star skill players
cli-web-futbin players list --min-skills 5 --json
```

**Filter options:**

| Option | Description | Example values |
|--------|-------------|----------------|
| `--position` | Position | `GK CB LB RB CAM CM CDM RM LM ST RW LW` |
| `--rating-min` | Min overall (40-99) | `85` |
| `--rating-max` | Max overall (40-99) | `99` |
| `--version` | Card type | `gold_rare gold_if toty fut_birthday icons heroes silver bronze` (see full list below) |
| `--min-price` | Min price in coins | `50000` |
| `--max-price` | Max price in coins | `500000` |
| `--cheapest` | Sort cheapest first | flag |
| `--platform` | Price platform | `ps` (default) or `pc` |
| `--min-skills` | Min skill stars | `1`–`5` |
| `--min-wf` | Min weak foot stars | `1`–`5` |
| `--gender` | Gender | `men` or `women` |
| `--league` | League ID (numeric) | `13` (Premier League) |
| `--nation` | Nation ID (numeric) | |
| `--club` | Club ID (numeric) | |
| `--page` | Page number | `1` (default) |
| `--year` | Game year | `26` (default, falls back to config) |

**Common `--version` values:**
`gold_rare`, `gold_if`, `gold_nr`, `silver_rare`, `bronze`, `toty`, `toty_icon`,
`fut_birthday`, `fut_birthday_hero`, `icons`, `heroes`, `non_icons`,
`flashback`, `moments`, `showdown`, `thunderstruck`, `unbreakables`,
`winter_wildcards`, `future_stars`, `world_tour`, `potm_pl`, `potm_bundesliga`

---

### `players get`

Full detail for a specific player by ID (get the ID from `players search`).

```bash
cli-web-futbin players get 40 --json
```

**Output fields:** name, rating, position, version, club, nation, ps_price, xbox_price, stats (pac/sho/pas/dri/def/phy), skill_moves, weak_foot, height, foot, trend (e.g., "0.17% (-12K)"), price_range (min/max EA listing bounds), ps_bin_listings (array of current BIN prices), pc_bin_listings

The extended fields (skill_moves, weak_foot, trend, price_range, bin_listings) are only populated from the detail page scrape, not from list/search results.

---

### `players compare`

Side-by-side comparison of two players.

```bash
cli-web-futbin players compare 40 42 --json
```

**Output fields:** per-player: name, rating, position, stats (pac/sho/pas/dri/def/phy), ps_price, xbox_price

---

### `players price-history`

Price history and trends for a player. Shows current, lowest, highest, and recent trend.

```bash
cli-web-futbin players price-history 40 --json
cli-web-futbin players price-history 40 --year 25 --json
```

**Output fields:** `player_id`, `player_name`, `ps_prices` (array of [timestamp_ms, price]), `pc_prices`, `ps_current`, `ps_min`, `ps_max`, `pc_current`, `pc_min`, `pc_max`, `data_points`

---

### `market index`

EA FC market price tracker. Shows all rating tier indices, or detail for a specific tier.

```bash
cli-web-futbin market index --json                     # all tiers overview
cli-web-futbin market index --rating 83 --json          # detail: current/open/low/high for 83-rated
cli-web-futbin market index --rating 100 --json         # overall index 100
cli-web-futbin market index --rating icons --json       # icons index
```

**Options:** `--rating` (81, 82, 83, 84, 85, 86, 100, icons)

**Detail output:** `current`, `change_pct`, `open`, `lowest`, `highest`

---

### `market popular`

Trending/most-viewed players on FUTBIN.

```bash
cli-web-futbin market popular --json
cli-web-futbin market popular --limit 50 --json
```

**Options:** `--limit` (number of players, default 30, max 250)

**Output fields:** Same as `players list` — `id`, `name`, `rating`, `position`, `ps_price`, `xbox_price`, `stats`

---

### `market latest`

Newly released player cards.

```bash
cli-web-futbin market latest --json
cli-web-futbin market latest --page 2 --json
```

**Options:** `--page` (page number, default 1)

---

### `market cheapest`

Find cheapest players by rating — best value for SBCs and trading.

```bash
cli-web-futbin market cheapest --rating-min 88 --json
cli-web-futbin market cheapest --rating-min 85 --rating-max 87 --max-price 10000 --json
cli-web-futbin market cheapest --rating-min 90 --platform pc --json
```

**Options:** `--rating-min` (default 83), `--rating-max` (default 99), `--max-price`, `--platform` (ps/pc), `--page`

---

### `market movers`

Biggest price risers or fallers — spot momentum and crash opportunities.

```bash
cli-web-futbin market movers --json                    # biggest risers
cli-web-futbin market movers --fallers --json           # biggest fallers
cli-web-futbin market movers --rating-min 85 --json     # only 85+ rated
```

**Options:** `--fallers` (show fallers instead of risers), `--rating-min` (default 80), `--min-price` (default 1000), `--max-price` (default 15M), `--platform` (ps/pc), `--page`

**Tip:** Adjust `--min-price` and `--rating-min` to control noise. Use `--min-price 200` for bronze/silver movers, or `--min-price 50000 --rating-min 85` for high-end market only.

---

### `market fodder`

SBC fodder prices — cheapest player at each rating tier (81-99). Essential for SBC cost planning.

```bash
cli-web-futbin market fodder --json
cli-web-futbin market fodder --rating-min 85 --json     # only 85+ tiers
cli-web-futbin market fodder --rating-min 88 --rating-max 91 --json
```

**Options:** `--rating-min`, `--rating-max`

**Output fields:** `rating`, `cheapest_price`, `players` (array of {id, name, position, price})

---

### `sbc list` / `sbc get`

Squad Building Challenges.

```bash
cli-web-futbin sbc list --json
cli-web-futbin sbc list --category "League SBC" --json
cli-web-futbin sbc get 665 --json
```

**Options:** `--category TEXT` (filter by SBC category), `--year INTEGER` (game year)

**Output fields:** `id`, `name`, `expires`, `cost_ps`, `cost_xbox`, `repeatable`, `reward`

---

### `evolutions list` / `evolutions get`

Player evolution paths.

```bash
cli-web-futbin evolutions list --json
cli-web-futbin evolutions list --expiring --json   # expiring soon
cli-web-futbin evolutions list --category "Lengthy" --json
cli-web-futbin evolutions get 666 --json
```

**Options:** `--category TEXT`, `--expiring` (show expiring soon), `--year INTEGER`

---

### `config`

Persistent configuration (year, platform, etc.).

```bash
cli-web-futbin config set year 26       # Set game year
cli-web-futbin config set platform ps   # Set price platform
cli-web-futbin config get year          # Get a setting
cli-web-futbin config show --json       # Show all settings
cli-web-futbin config reset             # Reset to defaults
```

When `--year` is omitted on other commands, it falls back to the value set in config.

---

### `market analyze`

Deep price analysis for a single player — trend, buy/sell signal, platform gap.

```bash
cli-web-futbin market analyze 40 --json
cli-web-futbin market analyze 67 --year 26 --json
```

**Output fields per platform (ps/pc):** `current`, `min`, `max`, `avg_30d`, `price_position_pct` (0%=floor, 100%=ceiling), `vs_avg_30d_pct` (negative=below avg=undervalued), `trend_7d`, `trend_30d`, `volatility_30d`, `signal` (BUY/SELL/HOLD)

**Signal logic:** BUY if >10% below 30d avg with stable/rising 7d trend. SELL if >15% above 30d avg with falling 7d trend. HOLD otherwise.

Also includes `platform_gap_pct` — cross-platform price difference %.

---

### `market scan`

Bulk undervalue detection — scans players by rating and flags those trading below their 30-day average.

```bash
cli-web-futbin market scan --rating-min 85 --rating-max 89 --json
cli-web-futbin market scan --rating-min 88 --limit 10 --threshold 15 --json
cli-web-futbin market scan --rating-min 84 --rating-max 86 --platform pc --json
```

**Options:** `--rating-min` (default 84), `--rating-max` (default 90), `--limit` (default 20), `--threshold` (default 10 — min % below avg to flag), `--platform`, `--json`

**Output fields:** `id`, `name`, `position`, `rating`, `version`, `current_price`, `avg_30d`, `vs_avg_30d_pct`, `trend_7d`, `signal`

Note: Makes one request per player for price history — uses Rich progress bar. Rate-limited at 0.5s/request.

---

### `market arbitrage`

Find cross-platform price gaps — identifies players where PS and PC prices diverge significantly.

```bash
cli-web-futbin market arbitrage --rating-min 88 --rating-max 92 --min-gap 5 --json
cli-web-futbin market arbitrage --rating-min 85 --min-gap 10 --json
```

**Options:** `--rating-min` (default 85), `--rating-max` (default 92), `--min-gap` (default 5 — minimum gap % to show), `--page`, `--json`

**Output fields:** `id`, `name`, `position`, `rating`, `version`, `ps_price`, `pc_price`, `gap_pct`, `gap_coins`, `cheaper_on` (ps/pc)

---

### `players versions`

All versions of a player compared — with value score (stats per 1K coins).

```bash
cli-web-futbin players versions --name "Haaland" --json
cli-web-futbin players versions --name "Mbappe" --year 26 --json
```

**Options:** `--name` (required), `--year`, `--json`

**Output fields:** Standard player fields + `total_stats` (pac+sho+pas+dri+def+phy), `value_score` (total_stats / price_in_thousands — higher = better value)

Fetches up to 10 versions with Rich progress bar. Sorted by rating descending.

---

## Agent Patterns

```bash
# What's Mbappe's current PS price?
cli-web-futbin players search --name "Mbappe" --json | python -c "import json,sys; p=json.load(sys.stdin)[0]; print(p['name'], p['ps_price'])"

# Compare two players (now includes value metrics)
cli-web-futbin players compare 40 42 --json

# Find cheapest gold rare CAM rated 85+
cli-web-futbin players list --position CAM --version gold_rare --rating-min 85 --cheapest --json

# Get player detail
cli-web-futbin players get 40 --json

# SBCs with cost under 100K (PS)
cli-web-futbin sbc list --json | python -c "import json,sys; [print(s['name'], s['cost_ps']) for s in json.load(sys.stdin) if s.get('cost_ps') and s['cost_ps'] < 100000]"

# Get all active evolutions
cli-web-futbin evolutions list --json

# What's trending right now?
cli-web-futbin market popular --limit 10 --json

# What new cards just dropped?
cli-web-futbin market latest --json

# Cheapest 88+ rated players for SBCs
cli-web-futbin market cheapest --rating-min 88 --json

# Is Mbappe at a good price to buy?
cli-web-futbin market analyze 40 --json

# Find deals: cheapest 90+ rated under 50K
cli-web-futbin market cheapest --rating-min 90 --max-price 50000 --json
```

---

## Market Knowledge Base

For in-depth trading intelligence — weekly price cycles, EA tax formulas, promo crash calendar, fodder investment rules, mass bidding strategy, and step-by-step CLI workflows — read the reference file:

**Read `references/market-knowledge-base.md`** when the user asks about:
- When to buy or sell players
- Market timing, weekly cycles, best days to trade
- Promo schedules, market crashes, TOTY/TOTS/Black Friday impact
- Fodder investment strategies
- Mass bidding techniques
- EA tax calculations and profit margins
- Step-by-step trading workflows

Quick reference (details in the reference file):
- **Best buy days:** Wednesday (midweek crash), Thursday AM (rewards flood), Sunday night (post-WL sell-off)
- **Best sell days:** Friday (WL demand), Saturday (peak prices)
- **EA tax:** 5% on all sales. Break-even = Buy Price / 0.95. Min margin: 10-15%
- **Fodder sweet spot:** 84-87 rated. Buy when no SBCs active, sell when popular SBC drops
- **Signal guide:** BUY = >10% below 30d avg + stable trend. SELL = >15% above avg + falling trend

---

## Trading Strategies

### 1. Buy the Dip — Find undervalued players

```bash
# Scan for players trading >10% below their 30-day average
cli-web-futbin market scan --rating-min 85 --rating-max 89 --threshold 10 --json

# Deep analysis on a specific player before buying
cli-web-futbin market analyze <player_id> --json
# Look for: signal=BUY, price_position_pct < 15%, trend_7d positive
```

### 2. SBC Fodder Trading — Buy cheap fodder before SBC drops

```bash
# Check current fodder prices at each tier
cli-web-futbin market fodder --json

# Find the absolute cheapest 85-rated players
cli-web-futbin market cheapest --rating-min 85 --rating-max 85 --json

# When SBC drops, fodder prices spike — check movers to confirm
cli-web-futbin market movers --rating-min 84 --min-price 1000 --max-price 20000 --json
```

### 3. Cross-Platform Arbitrage — Exploit PS/PC price gaps

```bash
# Find players with >10% price gap between platforms
cli-web-futbin market arbitrage --rating-min 88 --min-gap 10 --json

# Verify with deep analysis (check liquidity/trend context)
cli-web-futbin market analyze <player_id> --json
```

### 4. Version Value Hunting — Best bang for your coins

```bash
# Compare all versions of a player to find the best value
cli-web-futbin players versions --name "Salah" --json
# Look for: highest value_score (stats per 1K coins)

# Compare two specific versions head-to-head
cli-web-futbin players compare <base_id> <special_id> --json
# Check value.value_winner and coins_per_stat
```

### 5. Market Crash Detection — Spot opportunities after events

```bash
# Check which high-rated players are crashing
cli-web-futbin market movers --fallers --rating-min 88 --min-price 10000 --json

# Cross-reference with market index to see if it's market-wide
cli-web-futbin market index --json

# Drill into specific tier
cli-web-futbin market index --rating 88 --json
```

### 6. Trending Player Flip — Buy what's getting attention

```bash
# See what's trending on FUTBIN right now
cli-web-futbin market popular --limit 30 --json

# Check if trending players are still cheap (analyze before spike)
cli-web-futbin market analyze <trending_player_id> --json
# Buy if: signal=BUY or HOLD, price_position_pct < 30%
```

---

## Notes

- Prices are in EA FC coins
- Year 26 = EA FC 26 (current default); use `--year 25` for last year's cards. `--year` falls back to config value if omitted
- Errors: `--json` mode returns structured JSON errors `{"error": true, "code": "...", "message": "..."}`
- Rate limiting: 0.5s delay between requests
- `players list` scrapes HTML — may show limited data in some fields
- `players search` uses the JSON API — more reliable for name/rating/price data
