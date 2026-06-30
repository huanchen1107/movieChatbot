# Movie Database

> **100 movies** scraped from `https://ssr1.scrape.center` | avg score 8.97 | 22 categories | SQLite-powered

A full-stack movie data platform: SSR scraper, SQLite database, sklearn-powered ranking, FastAPI server with Gemini AI chatbot, and Excel export with embedded posters.

---

## Architecture

```
ssr1.scrape.center
       |
  crawler.py          -- scrape 100 movies + download posters
       |
  output/movie.db     -- SQLite database (shared source of truth)
       |
  db.py               -- shared module: schema, load, save, search
       |
  +----+----+----+
  |    |    |    |
  |    |    |    +-- chatbot.py   -- CLI chatbot (sklearn Jaccard ranking)
  |    |    |
  |    |    +------- movie_rank.py -- K-Means clustering analysis
  |    |
  |    +------------ server.py    -- FastAPI + Gemini AI + Web UI
  |                   |
  |              index.html       -- frontend (search, chat, settings)
  |
  +----------------- README.md    -- this file + movie table
                     output/movies.xlsx -- Excel with embedded posters
                     output/posters/    -- 100 poster JPGs
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install requests beautifulsoup4 openpyxl Pillow scikit-learn fastapi uvicorn google-genai
```

### 2. Scrape movies + download posters

```bash
python crawler.py
```

Outputs:
- `output/movie.db` — SQLite database
- `output/movies.csv` — CSV export
- `output/movies.xlsx` — Excel with embedded poster thumbnails
- `output/posters/` — 100 poster images

### 3. Launch the web server

```bash
python server.py
# Open http://localhost:8000
```

The web UI features:
- Search bar + clickable category tags for filtering
- Movie card grid with posters
- Chat panel (bottom-right): basic commands or Gemini AI mode
- Settings gear icon: users can input their own Gemini API key
- Swagger API docs at `/docs`

### 4. CLI chatbot (optional)

```bash
python chatbot.py
```

Commands: `top 5`, `search 肖申克`, `rank 动画, 冒险`, `like 霸王别姬`, `info 3`, `stats`, `cats`, `help`

### 5. Sklearn analysis (optional)

```bash
python movie_rank.py
```

Prints K-Means clusters of genres and Jaccard similarity rankings.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| GET | `/docs` | Swagger API docs |
| GET | `/api/search?q=` | Search by name/country/category |
| GET | `/api/rank?categories=` | Jaccard-similarity ranking |
| GET | `/api/top?n=` | Top N by score |
| GET | `/api/movie/{id}` | Movie detail |
| GET | `/api/similar/{id}` | 10 similar movies |
| GET | `/api/categories` | Category list with counts |
| GET | `/api/stats` | Database statistics |
| POST | `/api/chat` | Basic rule-based chatbot |
| POST | `/api/chat/gemini` | Gemini AI chatbot |
| GET | `/api/chat/gemini/status` | Gemini availability |

---

## Database Schema

```sql
CREATE TABLE movies (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    categories   TEXT NOT NULL,    -- '剧情 / 爱情'
    country      TEXT,             -- '美国'
    duration     TEXT,             -- '142 分钟'
    release_date TEXT,             -- '1994-09-10 上映'
    score        REAL,             -- 9.5
    cover        TEXT,             -- poster URL
    poster_file  TEXT              -- local poster path
);
```

---

## File Index

| File | Purpose |
|------|---------|
| `crawler.py` | Scrape SSR pages, download posters, write SQLite + CSV + Excel |
| `db.py` | Shared SQLite module (schema, CRUD, search) |
| `server.py` | FastAPI app with REST API + Gemini AI + inline Web UI |
| `index.html` | Frontend: search, chat, Gemini settings (gear icon) |
| `chatbot.py` | CLI chatbot with sklearn Jaccard ranking |
| `movie_rank.py` | K-Means clustering + Jaccard analysis |
| `output/movie.db` | SQLite database (100 movies) |
| `output/movies.csv` | CSV export |
| `output/movies.xlsx` | Excel with embedded posters |
| `output/posters/` | 100 poster JPGs |
| `page1.html` | Raw page 1 HTML (for reference) |
| `.env` | Gemini API key (server-side fallback) |

---

## Movie Table

| # | Poster | Name | Categories | Country | Duration | Release Date | Score |
|---|--------|------|------------|---------|----------|--------------|-------|
| 1 | <img src="output/posters/1.jpg" width="80"> | 霸王别姬 - Farewell My Concubine | 剧情 / 爱情 | 中国内地、中国香港 | 171 分钟 | 1993-07-26 上映 | 9.5 |
| 2 | <img src="output/posters/2.jpg" width="80"> | 这个杀手不太冷 - Léon | 剧情 / 动作 / 犯罪 | 法国 | 110 分钟 | 1994-09-14 上映 | 9.5 |
| 3 | <img src="output/posters/3.jpg" width="80"> | 肖申克的救赎 - The Shawshank Redemption | 剧情 / 犯罪 | 美国 | 142 分钟 | 1994-09-10 上映 | 9.5 |
| 4 | <img src="output/posters/4.jpg" width="80"> | 泰坦尼克号 - Titanic | 剧情 / 爱情 / 灾难 | 美国 | 194 分钟 | 1998-04-03 上映 | 9.5 |
| 5 | <img src="output/posters/5.jpg" width="80"> | 罗马假日 - Roman Holiday | 剧情 / 喜剧 / 爱情 | 美国 | 118 分钟 | 1953-08-20 上映 | 9.5 |
| 6 | <img src="output/posters/6.jpg" width="80"> | 唐伯虎点秋香 - Flirting Scholar | 喜剧 / 爱情 / 古装 | 中国香港 | 102 分钟 | 1993-07-01 上映 | 9.5 |
| 7 | <img src="output/posters/7.jpg" width="80"> | 乱世佳人 - Gone with the Wind | 剧情 / 爱情 / 历史 / 战争 | 美国 | 238 分钟 | 1939-12-15 上映 | 9.5 |
| 8 | <img src="output/posters/8.jpg" width="80"> | 喜剧之王 - The King of Comedy | 剧情 / 喜剧 / 爱情 | 中国香港 | 85 分钟 | 1999-02-13 上映 | 9.5 |
| 9 | <img src="output/posters/9.jpg" width="80"> | 楚门的世界 - The Truman Show | 剧情 / 科幻 | 美国 | 103 分钟 |  | 9.0 |
| 10 | <img src="output/posters/10.jpg" width="80"> | 狮子王 - The Lion King | 动画 / 歌舞 / 冒险 | 美国 | 89 分钟 | 1995-07-15 上映 | 9.0 |
| 11 | <img src="output/posters/11.jpg" width="80"> | V字仇杀队 - V for Vendetta | 剧情 / 动作 / 科幻 / 惊悚 | 美国、英国、德国 | 132 分钟 | 2005-12-11 上映 | 8.9 |
| 12 | <img src="output/posters/12.jpg" width="80"> | 少年派的奇幻漂流 - Life of Pi | 剧情 / 奇幻 / 冒险 | 美国、中国台湾、英国、加拿大 | 127 分钟 | 2012-11-22 上映 | 8.9 |
| 13 | <img src="output/posters/13.jpg" width="80"> | 美丽心灵 - A Beautiful Mind | 剧情 / 传记 | 美国 | 135 分钟 | 2001-12-13 上映 | 8.8 |
| 14 | <img src="output/posters/14.jpg" width="80"> | 初恋这件小事 - สิ่งเล็กเล็กที่เรียกว่า...รัก | 喜剧 / 爱情 | 泰国 | 118 分钟 | 2012-06-05 上映 | 8.9 |
| 15 | <img src="output/posters/15.jpg" width="80"> | 借东西的小人阿莉埃蒂 - 借りぐらしのアリエッティ | 动画 / 奇幻 / 冒险 | 日本 | 94 分钟 | 2010-07-17 上映 | 8.8 |
| 16 | <img src="output/posters/16.jpg" width="80"> | 一一 - Yi yi: A One and a Two | 剧情 / 爱情 / 家庭 | 中国台湾、日本 | 173 分钟 | 2000-05-15 上映 | 8.8 |
| 17 | <img src="output/posters/17.jpg" width="80"> | 美丽人生 - La vita è bella | 战争 / 剧情 / 爱情 | 意大利 | 116 分钟 | 2020-01-03 上映 | 9.1 |
| 18 | <img src="output/posters/18.jpg" width="80"> | 海上钢琴师 - La leggenda del pianista sull'oceano | 剧情 / 爱情 / 音乐 | 意大利 | 126 分钟 | 2019-11-15 上映 | 9.1 |
| 19 | <img src="output/posters/19.jpg" width="80"> | 千与千寻 - 千と千尋の神隠し | 动画 / 冒险 / 奇幻 / 家庭 | 日本 | 125 分钟 | 2019-06-21 上映 | 9.1 |
| 20 | <img src="output/posters/20.jpg" width="80"> | 迁徙的鸟 - The Travelling Birds | 纪录片 | 法国、德国、意大利、西班牙、瑞士 | 98 分钟 | 2001-12-12 上映 | 9.1 |
| 21 | <img src="output/posters/21.jpg" width="80"> | 黄金三镖客 - Il buono, il brutto, il cattivo. | 西部 / 冒险 | 意大利、西班牙、西德 | 161 分钟 | 1966-12-23 上映 | 9.1 |
| 22 | <img src="output/posters/22.jpg" width="80"> | 海洋 - Océans | 纪录片 | 法国、瑞士、西班牙、美国、阿联酋 | 104 分钟 | 2011-08-12 上映 | 9.1 |
| 23 | <img src="output/posters/23.jpg" width="80"> | 我爱你 - 그대를 사랑합니다 | 剧情 / 爱情 | 韩国 | 118 分钟 | 2011-02-17 上映 | 9.1 |
| 24 | <img src="output/posters/24.jpg" width="80"> | 阿飞正传 - Days of Being Wild | 剧情 / 爱情 / 犯罪 | 中国香港 | 94 分钟 | 2018-06-25 上映 | 9.1 |
| 36 | <img src="output/posters/36.jpg" width="80"> | 7号房的礼物 - 7번방의 선물 | 剧情 / 喜剧 / 家庭 | 韩国 | 127 分钟 | 2013-01-23 上映 | 8.8 |
| 25 | <img src="output/posters/25.jpg" width="80"> | 爱·回家 - 집으로... | 剧情 / 家庭 | 韩国 | 80 分钟 | 2002-04-05 上映 | 9.1 |
| 26 | <img src="output/posters/26.jpg" width="80"> | 龙猫 - となりのトトロ | 动画 / 冒险 / 奇幻 / 家庭 | 日本 | 86 分钟 | 2018-12-14 上映 | 9.1 |
| 27 | <img src="output/posters/27.jpg" width="80"> | 七武士 - 七人の侍 | 剧情 / 动作 / 冒险 | 日本 | 207 分钟 | 1954-04-26 上映 | 8.8 |
| 28 | <img src="output/posters/28.jpg" width="80"> | 美国往事 - Once Upon a Time in America | 剧情 / 犯罪 | 意大利、美国 | 229 分钟 | 2015-04-23 上映 | 8.8 |
| 29 | <img src="output/posters/29.jpg" width="80"> | 完美的世界 - A Perfect World | 剧情 / 犯罪 | 美国 | 138 分钟 | 1993-11-24 上映 | 8.8 |
| 30 | <img src="output/posters/30.jpg" width="80"> | 上帝之城 - Cidade de Deus | 剧情 / 犯罪 | 巴西、法国 | 130 分钟 |  | 8.8 |
| 31 | <img src="output/posters/31.jpg" width="80"> | 辩护人 - 변호인 | 剧情 | 韩国 | 127 分钟 | 2013-12-18 上映 | 8.8 |
| 32 | <img src="output/posters/32.jpg" width="80"> | 忠犬八公物语 - ハチ公物語 | 剧情 | 日本 | 107 分钟 | 1987-08-01 上映 | 8.8 |
| 33 | <img src="output/posters/33.jpg" width="80"> | 海豚湾 - The Cove | 纪录片 | 美国 | 92 分钟 | 2009-07-31 上映 | 8.8 |
| 34 | <img src="output/posters/34.jpg" width="80"> | 英雄本色 - A Better Tomorrow | 剧情 / 动作 / 犯罪 | 中国香港 | 95 分钟 | 2017-11-17 上映 | 8.8 |
| 35 | <img src="output/posters/35.jpg" width="80"> | 恐怖直播 - 더 테러 라이브 | 剧情 / 悬疑 / 犯罪 | 韩国 | 97 分钟 | 2013-07-31 上映 | 8.8 |
| 37 | <img src="output/posters/37.jpg" width="80"> | 窃听风暴 - Das Leben der Anderen | 剧情 / 悬疑 | 德国 | 137 分钟 | 2006-03-23 上映 | 8.8 |
| 38 | <img src="output/posters/38.jpg" width="80"> | 时空恋旅人 - About Time | 喜剧 / 爱情 / 奇幻 | 英国 | 123 分钟 | 2013-09-04 上映 | 8.8 |
| 39 | <img src="output/posters/39.jpg" width="80"> | 穿条纹睡衣的男孩 - The Boy in the Striped Pajamas | 剧情 / 战争 | 英国、美国 | 94 分钟 | 2008-08-28 上映 | 8.8 |
| 40 | <img src="output/posters/40.jpg" width="80"> | 教父 - The Godfather | 剧情 / 犯罪 | 美国 | 175 分钟 | 2015-04-18 上映 | 8.8 |
| 41 | <img src="output/posters/41.jpg" width="80"> | 萤火之森 - 蛍火の杜へ | 剧情 / 爱情 / 动画 / 奇幻 | 日本 | 45 分钟 | 2011-09-17 上映 | 8.8 |
| 42 | <img src="output/posters/42.jpg" width="80"> | 素媛 - 소원 | 剧情 | 韩国 | 123 分钟 | 2013-10-02 上映 | 8.8 |
| 43 | <img src="output/posters/43.jpg" width="80"> | 小鞋子 - بچههای آسمان | 剧情 / 家庭 | 伊朗 | 89 分钟 |  | 8.8 |
| 44 | <img src="output/posters/44.jpg" width="80"> | 熔炉 - 도가니 | 剧情 | 韩国 | 125 分钟 | 2011-09-22 上映 | 8.8 |
| 45 | <img src="output/posters/45.jpg" width="80"> | 大话西游之大圣娶亲 - A Chinese Odyssey Part Two - Cinderella | 喜剧 / 爱情 / 奇幻 | 中国香港、中国大陆 | 110 分钟 | 2014-10-24 上映 | 8.9 |
| 46 | <img src="output/posters/46.jpg" width="80"> | 新龙门客栈 - New Dragon Gate Inn | 动作 / 爱情 / 武侠 / 古装 | 中国香港、中国大陆 | 88 分钟 | 2012-02-24 上映 | 8.9 |
| 47 | <img src="output/posters/47.jpg" width="80"> | 触不可及 - Intouchables | 剧情 / 喜剧 | 法国 | 112 分钟 | 2011-11-02 上映 | 8.9 |
| 48 | <img src="output/posters/48.jpg" width="80"> | 钢琴家 - The Pianist | 剧情 / 音乐 / 传记 / 历史 / 战争 | 法国、德国、英国、波兰 | 150 分钟 | 2002-05-24 上映 | 8.9 |
| 49 | <img src="output/posters/49.jpg" width="80"> | 本杰明·巴顿奇事 - The Curious Case of Benjamin Button | 剧情 / 爱情 / 奇幻 | 美国 | 166 分钟 | 2008-12-25 上映 | 8.9 |
| 50 | <img src="output/posters/50.jpg" width="80"> | 倩女幽魂 - A Chinese Ghost Story | 爱情 / 奇幻 / 武侠 / 古装 | 中国香港 | 98 分钟 | 2011-04-30 上映 | 8.9 |
| 51 | <img src="output/posters/51.jpg" width="80"> | 哈利·波特与死亡圣器（下） - Harry Potter and the Deathly Hallows: Part 2 | 剧情 / 悬疑 / 奇幻 / 冒险 | 英国、美国 | 130 分钟 | 2011-08-04 上映 | 8.9 |
| 52 | <img src="output/posters/52.jpg" width="80"> | 甜蜜蜜 - Comrades: Almost a Love Story | 剧情 / 爱情 | 中国香港 | 118 分钟 | 2015-02-13 上映 | 8.9 |
| 53 | <img src="output/posters/53.jpg" width="80"> | 蝙蝠侠：黑暗骑士崛起 - The Dark Knight Rises | 剧情 / 动作 / 科幻 / 惊悚 / 犯罪 | 美国、英国 | 165 分钟 | 2012-08-27 上映 | 8.9 |
| 54 | <img src="output/posters/54.jpg" width="80"> | 鬼子来了 - Devils on the Doorstep | 剧情 / 战争 | 中国大陆 | 139 分钟 | 2000-05-13 上映 | 8.8 |
| 55 | <img src="output/posters/55.jpg" width="80"> | 无敌破坏王 - Wreck-It Ralph | 喜剧 / 动画 / 奇幻 / 冒险 | 美国 | 101 分钟 | 2012-11-06 上映 | 8.8 |
| 56 | <img src="output/posters/56.jpg" width="80"> | 致命魔术 - The Prestige | 剧情 / 悬疑 / 惊悚 | 美国、英国 | 130 分钟 | 2006-10-17 上映 | 8.8 |
| 57 | <img src="output/posters/57.jpg" width="80"> | 神偷奶爸 - Despicable Me | 喜剧 / 动画 / 冒险 | 美国、法国 | 95 分钟 | 2010-06-20 上映 | 8.8 |
| 58 | <img src="output/posters/58.jpg" width="80"> | 断背山 - Brokeback Mountain | 剧情 / 爱情 / 家庭 | 美国、加拿大 | 134 分钟 | 2005-09-02 上映 | 8.8 |
| 59 | <img src="output/posters/59.jpg" width="80"> | 怦然心动 - Flipped | 剧情 / 喜剧 / 爱情 | 美国 | 90 分钟 | 2010-07-26 上映 | 8.8 |
| 60 | <img src="output/posters/60.jpg" width="80"> | 驯龙高手 - How to Train Your Dragon | 喜剧 / 动画 / 奇幻 / 冒险 | 美国 | 98 分钟 | 2010-05-14 上映 | 8.8 |
| 61 | <img src="output/posters/61.jpg" width="80"> | 飞屋环游记 - Up | 剧情 / 喜剧 / 动画 / 冒险 | 美国 | 96 分钟 | 2009-08-04 上映 | 8.8 |
| 62 | <img src="output/posters/62.jpg" width="80"> | 黑客帝国3：矩阵革命 - The Matrix Revolutions | 动作 / 科幻 | 美国、澳大利亚 | 129 分钟 | 2003-11-05 上映 | 8.8 |
| 63 | <img src="output/posters/63.jpg" width="80"> | 速度与激情5 - Fast Five | 动作 / 犯罪 | 美国 | 130 分钟 | 2011-05-12 上映 | 8.9 |
| 64 | <img src="output/posters/64.jpg" width="80"> | 勇敢的心 - Braveheart | 剧情 / 动作 / 传记 / 历史 / 战争 | 美国 | 177 分钟 | 1995-05-18 上映 | 8.9 |
| 65 | <img src="output/posters/65.jpg" width="80"> | 三傻大闹宝莱坞 - 3 Idiots | 剧情 / 喜剧 / 爱情 / 歌舞 | 印度 | 171 分钟 | 2011-12-08 上映 | 8.9 |
| 66 | <img src="output/posters/66.jpg" width="80"> | 闻香识女人 - Scent of a Woman | 剧情 | 美国 | 157 分钟 | 1992-12-23 上映 | 8.9 |
| 67 | <img src="output/posters/67.jpg" width="80"> | 末代皇帝 - The Last Emperor | 剧情 / 传记 / 历史 | 英国、意大利、中国大陆、法国、美国 | 163 分钟 | 1987-10-23 上映 | 8.9 |
| 68 | <img src="output/posters/68.jpg" width="80"> | 风之谷 - 風の谷のナウシカ | 动画 / 奇幻 / 冒险 | 日本 | 117 分钟 |  | 8.9 |
| 69 | <img src="output/posters/69.jpg" width="80"> | 大话西游之月光宝盒 - A Chinese Odyssey | 喜剧 / 爱情 / 奇幻 / 古装 | 中国香港、中国大陆 | 87 分钟 | 2014-10-24 上映 | 8.9 |
| 70 | <img src="output/posters/70.jpg" width="80"> | 放牛班的春天 - Les choristes | 剧情 / 音乐 | 法国、德国、瑞士 | 97 分钟 | 2004-10-16 上映 | 8.9 |
| 71 | <img src="output/posters/71.jpg" width="80"> | 当幸福来敲门 - The Pursuit of Happyness | 剧情 / 家庭 / 传记 | 美国 | 117 分钟 | 2008-01-17 上映 | 8.9 |
| 72 | <img src="output/posters/72.jpg" width="80"> | 幽灵公主 - もののけ姫 | 动画 / 奇幻 / 冒险 | 日本 | 134 分钟 | 1998-05-01 上映 | 8.9 |
| 73 | <img src="output/posters/73.jpg" width="80"> | 十二怒汉 - 12 Angry Men | 剧情 | 美国 | 96 分钟 | 1957-04-13 上映 | 8.9 |
| 74 | <img src="output/posters/74.jpg" width="80"> | 搏击俱乐部 - Fight Club | 剧情 / 动作 / 悬疑 / 惊悚 | 美国、德国 | 139 分钟 | 1999-09-10 上映 | 8.9 |
| 75 | <img src="output/posters/75.jpg" width="80"> | 疯狂原始人 - The Croods | 喜剧 / 动画 / 冒险 | 美国 | 98 分钟 | 2013-04-20 上映 | 8.9 |
| 76 | <img src="output/posters/76.jpg" width="80"> | 阿凡达 - Avatar | 动作 / 科幻 / 冒险 | 美国、英国 | 162 分钟 | 2010-01-04 上映 | 8.9 |
| 77 | <img src="output/posters/77.jpg" width="80"> | 哈尔的移动城堡 - ハウルの動く城 | 动画 / 奇幻 / 冒险 | 日本 | 119 分钟 | 2004-09-05 上映 | 8.9 |
| 78 | <img src="output/posters/78.jpg" width="80"> | 盗梦空间 - Inception | 剧情 / 科幻 / 悬疑 / 冒险 | 美国、英国 | 148 分钟 | 2010-09-01 上映 | 8.9 |
| 79 | <img src="output/posters/79.jpg" width="80"> | 忠犬八公的故事 - Hachi: A Dog's Tale | 剧情 | 美国、英国 | 93 分钟 | 2009-06-13 上映 | 8.9 |
| 80 | <img src="output/posters/80.jpg" width="80"> | 拯救大兵瑞恩 - Saving Private Ryan | 剧情 / 历史 / 战争 | 美国 | 169 分钟 | 1998-11-13 上映 | 8.9 |
| 81 | <img src="output/posters/81.jpg" width="80"> | 活着 - To Live | 剧情 / 家庭 / 历史 | 中国大陆、中国香港 | 132 分钟 | 1994-05-17 上映 | 9.0 |
| 82 | <img src="output/posters/82.jpg" width="80"> | 机器人总动员 - WALL·E | 喜剧 / 科幻 / 动画 | 美国 | 98 分钟 | 2008-06-27 上映 | 9.0 |
| 83 | <img src="output/posters/83.jpg" width="80"> | 天堂电影院 - Nuovo Cinema Paradiso | 剧情 / 爱情 | 意大利、法国 | 155 分钟 | 1988-11-17 上映 | 9.0 |
| 84 | <img src="output/posters/84.jpg" width="80"> | 指环王2：双塔奇兵 - The Lord of the Rings: The Two Towers | 剧情 / 动作 / 奇幻 / 冒险 | 美国、新西兰 | 179 分钟 | 2003-04-25 上映 | 9.0 |
| 85 | <img src="output/posters/85.jpg" width="80"> | 指环王1：护戒使者 - The Lord of the Rings: The Fellowship of the Ring | 剧情 / 动作 / 奇幻 / 冒险 | 新西兰、美国 | 178 分钟 | 2002-04-04 上映 | 9.0 |
| 86 | <img src="output/posters/86.jpg" width="80"> | 射雕英雄传之东成西就 - The Eagle Shooting Heroes | 喜剧 / 奇幻 / 武侠 / 古装 | 中国香港 | 113 分钟 | 1993-02-05 上映 | 9.0 |
| 87 | <img src="output/posters/87.jpg" width="80"> | 蝙蝠侠：黑暗骑士 - The Dark Knight | 剧情 / 动作 / 科幻 / 惊悚 / 犯罪 | 美国、英国 | 152 分钟 | 2008-07-14 上映 | 9.0 |
| 88 | <img src="output/posters/88.jpg" width="80"> | 无间道 - Infernal Affairs | 剧情 / 悬疑 / 犯罪 | 中国香港 | 101 分钟 | 2003-09-05 上映 | 9.0 |
| 89 | <img src="output/posters/89.jpg" width="80"> | 教父2 - The Godfather: Part Ⅱ | 剧情 / 犯罪 | 美国 | 202 分钟 | 1974-12-12 上映 | 9.0 |
| 90 | <img src="output/posters/90.jpg" width="80"> | 加勒比海盗 - Pirates of the Caribbean: The Curse of the Black Pearl | 动作 / 奇幻 / 冒险 | 美国 | 143 分钟 | 2003-11-21 上映 | 9.0 |
| 91 | <img src="output/posters/91.jpg" width="80"> | 哈利·波特与魔法石 - Harry Potter and the Sorcerer's Stone | 奇幻 / 冒险 | 美国、英国 | 152 分钟 | 2002-01-26 上映 | 9.0 |
| 92 | <img src="output/posters/92.jpg" width="80"> | 指环王3：王者无敌 - The Lord of the Rings: The Return of the King | 剧情 / 动作 / 奇幻 / 冒险 | 美国、新西兰 | 201 分钟 | 2004-03-15 上映 | 9.0 |
| 93 | <img src="output/posters/93.jpg" width="80"> | 黑客帝国 - The Matrix | 动作 / 科幻 | 美国、澳大利亚 | 136 分钟 | 2000-01-14 上映 | 9.0 |
| 94 | <img src="output/posters/94.jpg" width="80"> | 剪刀手爱德华 - Edward Scissorhands | 剧情 / 爱情 / 奇幻 | 美国 | 105 分钟 | 1990-12-06 上映 | 9.0 |
| 95 | <img src="output/posters/95.jpg" width="80"> | 春光乍泄 - Happy Together | 剧情 / 爱情 | 中国香港、日本、韩国 | 96 分钟 | 1997-05-17 上映 | 9.0 |
| 96 | <img src="output/posters/96.jpg" width="80"> | 大闹天宫 - The Monkey King | 动画 / 奇幻 | 中国大陆 | 114 分钟 | 1965-12-31 上映 | 9.0 |
| 97 | <img src="output/posters/97.jpg" width="80"> | 天空之城 - 天空の城ラピュタ | 动画 / 奇幻 / 冒险 | 日本 | 125 分钟 | 1992-05-01 上映 | 9.0 |
| 98 | <img src="output/posters/98.jpg" width="80"> | 音乐之声 - The Sound of Music | 剧情 / 爱情 / 歌舞 / 传记 | 美国 | 174 分钟 | 1965-03-02 上映 | 9.0 |
| 99 | <img src="output/posters/99.jpg" width="80"> | 辛德勒的名单 - Schindler's List | 剧情 / 历史 / 战争 | 美国 | 195 分钟 | 1993-11-30 上映 | 9.5 |
| 100 | <img src="output/posters/100.jpg" width="80"> | 魂断蓝桥 - Waterloo Bridge | 剧情 / 爱情 / 战争 | 美国 | 108 分钟 | 1940-05-17 上映 | 9.5 |
