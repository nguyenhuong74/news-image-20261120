# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/nguyenhuong74/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/nguyenhuong74/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The World in One Page — Friday 20 November 2026

A newspaper front page summing up Friday 20 November 2026's world news — Russia's biggest missile and drone barrage of the war, with two missiles and a drone landing in Poland; Myanmar calling the World Court's genocide ruling unfair as Britain expels its defence attaché; Anthropic sliding about 10% on its second day as Asia heads for its worst week since 2020; COP31 reaching its Friday deadline with fossil-fuel language stripped from the draft; a Houthi missile damaging Riyadh's tallest tower; and the EU and Britain meeting again in Brussels — drawn in code as one 1024x1024 PNG with the Python standard library.

## How it works

`main.py` draws the whole front page programmatically: a hand-written 5x7 bitmap font for all text, simple geometric pictograms (a Kyiv skyline under a missile barrage, tipped scales of justice, a falling chart, a crossed-out smokestack, a cracked skyscraper, the EU and British flags), and a PNG encoder built from `zlib` + `struct`. No network, no time, no randomness, no dependencies — the grader runs it twice and both runs write byte-identical `entry.png` files.

Stories covered: Russia firing more than 400 drones and 110 missiles, 27 of them ballistic, at Ukraine overnight, killing eight and wounding 28, while two missiles and a drone came down in Poland, which Warsaw called a deliberate provocation and NATO a violation; Myanmar rejecting the International Court of Justice's genocide ruling as unfair, a day after the court found it guilty 9–6, as Britain expels its defence attaché and calls for an urgent UN Security Council session; Anthropic falling about 10% to $87 on its second day of trading, towards its $83 offer price, with the Nikkei down 5.1% and the Kospi down 5.2% as Asia heads for its worst week since 2020; COP31 in Antalya reaching its Friday deadline with all fossil-fuel language stripped from the draft deal, while the text admits for the first time that the 1.5°C limit will be overshot; Saudi civil defence confirming a Houthi missile damaged the PIF Tower in Riyadh, blowing out windows across seven to eight floors, with no injuries; and the European Union and Britain holding their second summit since the reset, Prime Minister Andy Burnham meeting António Costa and Ursula von der Leyen. The briefs strip adds GTA VI's $3.79 billion day-one sales, the biggest entertainment launch ever; 34 suspected gang members killed in a police operation in Haiti; and Fiona the hippo dying at Cincinnati Zoo aged nine after swallowing a visitor's hat.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB), byte-identical on every run.

---

<sub>Entered on [make.fun](https://make.fun/?ref=6nfavmbn&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
