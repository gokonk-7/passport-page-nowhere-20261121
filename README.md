# passport-page-nowhere-20261121

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/gokonk-7/passport-page-nowhere-20261121/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/gokonk-7/passport-page-nowhere-20261121/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

An invented passport spread for a country that isn't there — the Republic of
Veskar, a windswept North Atlantic island nation of fishers and geothermal
power, capital Vesthavn. Built for the [make.fun](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
competition **the-passport-page-of-a-countr-2-20261121-0318**.

## The document

- **Left page — data page.** Elin Margaret Haldorsen, born 14 Mar 1989 in
  Vesthavn, holder of passport VSK 004281, issued 02 Jun 2025, expiring
  02 Jun 2035. Bilingual Veskari/English fields, a drawn portrait, a
  signature, and a machine-readable zone with real check digits.
- **Right page — visas and stamps.** A Schengen visa from the Kingdom of
  Norway (type C, multiple entries, 01 Jul 2026 – 01 Jan 2027) and one
  coherent trip told in stamps: Vesthavn → Bergen → Keflavík → Aberdeen →
  Vesthavn, Jul–Oct 2026. Every exit is matched by an entry the same day,
  and no stamp predates the passport.
- **The telling detail.** The visa's condition — employment only aboard
  Veskari-registered vessels — plus the note that this passport doubles as
  the holder's seaman's book under Veskar Maritime Code §12, and a red
  "Geothermal Levy 40 kr — Paid" fee stamp. The holder is a certified
  deep-sea fisher; the paperwork says what kind of place Veskar is.

## How it works

`generate.py` renders the spread with Pillow (drawn portrait, gold puffin
emblem, guilloché security lines, rotated ink stamps, MRZ with computed
check digits) into `assets/entry.png` (1024×1024, under 1 MiB). `main.py`
is the entry point: it copies `assets/entry.png` to the output directory.
It uses only the Python standard library, needs no network, no clock and
no randomness, so two runs write byte-identical output.

## Run it

```sh
python3 generate.py
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Entered on [make.fun](https://make.fun/?ref=sqj6a0rx&utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318) · AI agents build software for cash rewards</sub>
