# Frontier Operating Model Research: 企業戦略・事業経済設計（01）

Generated: 2026-05-13 JST  
Scope: 01  
Unit: 企業戦略・事業経済設計  
Method: RESEARCH.md の「公開情報限定」「意思決定システムとして再構成」「Clone Spec 生成」「A/B/C/D 信頼度分離」に準拠

---

## 0. スコープとレイヤー正規化

ユーザー指定の対象レイヤーは `01`、主なサブテーマは「経営目的・事業目的・事業戦略・市場戦略・顧客戦略・収益/価格/原価/利益構造・KPI・OKR」である。本レポートでは、提示されたサブテーマを次の 12 レイヤーに正規化した。

| Layer ID | Layer Name | Decision Object | 主な成果物 |
|---:|---|---|---|
| 01.01 | 経営目的 | 企業全体として、誰に何の価値を、どの時間軸・制約下で創るか | Mission / Purpose / Principles / Stakeholder boundary |
| 01.02 | 事業目的 | 特定事業が、どの顧客・利用者・パートナーのどの Job を解くか | Business purpose / Value proposition / Customer promise |
| 01.03 | 事業戦略 | どの事業領域・能力・資産・投資配分で勝つか | Strategy map / Segment strategy / Resource allocation thesis |
| 01.04 | 市場戦略 | どの市場・地域・カテゴリ・チャネルを優先するか | TAM/SAM/SOM, geographic/category plan, competitive positioning |
| 01.05 | 顧客戦略 | どの顧客群を、どの体験・信頼・関係性で獲得・維持するか | Customer segmentation, lifecycle, trust/retention model |
| 01.06 | 収益構造 | どの価値単位から、どの収益源・認識方法・ミックスで売上を作るか | Revenue model, revenue recognition, revenue mix, leading metrics |
| 01.07 | 価格構造 | どの価値単位を、どの価格階層・料金式・割引・契約で課金するか | Pricing architecture, tiers, fees, discount policy |
| 01.08 | 原価構造 | 価値提供に必要な変動費・固定費・資本費・運転資本をどう制御するか | Cost driver map, COGS/Opex/Capex model, unit cost model |
| 01.09 | 利益構造 | 売上・原価・投資・資本配分をどう利益・キャッシュに変換するか | Segment P&L, margin model, free cash flow logic |
| 01.10 | KPI設計 | 経営・事業判断に使う指標をどう定義・計算・統制するか | KPI dictionary, metric hierarchy, reconciliation rules |
| 01.11 | OKR設計 | 目的と測定可能な成果を、どの周期・透明性・評価ルールで運用するか | Objectives, Key Results, scoring, cadence, public alignment |
| 01.12 | 事業経済統合設計 | 目的→顧客→市場→収益→価格→原価→利益→KPI/OKR を単一の経済モデルに接続するか | Business economic equation, unit economics, capital allocation loop |

---

## 1. 調査方法

### 1.1 Source Priority

RESEARCH.md の方針に従い、経営・事業レイヤーでは T1 の 10-K / Annual Report / MD&A / 監査済み財務、T2 の価格表・プロダクト仕様・公式メトリクス、T0/T3 の標準・公式運用文書を優先した。求人票、メディア記事、二次解説は補助扱いとし、本版では主要主張の根拠には使っていない。

| Tier | 本レポートでの使い方 | 採用例 |
|---|---|---|
| T1 | 経営目的、事業、収益構造、セグメント、リスク、MD&A の直接証拠 | Amazon 10-K, Microsoft Annual Report, Apple 10-K, Alphabet 10-K, Netflix 10-K, Airbnb 10-K, Costco 10-K |
| T2 | 価格・顧客・KPI と実際のプロダクト/経済設計の接続 | Netflix 料金レンジ、Airbnb GBV/Nights and Seats、Costco membership metrics |
| T0/T3 | KPI/OKR/ERM の規範・運用モデル | IFRS Management Commentary, SEC MD&A KPI guidance, COSO ERM, Google re:Work OKR, Atlassian OKR, IBM OKR |

### 1.2 Evidence Confidence

| Confidence | 意味 | 採用ルール |
|---|---|---|
| A | 一次情報または公式文書で直接確認 | Clone Spec の中核に採用 |
| B | 複数の独立公開情報から整合的に推定 | 中核に採用。ただし推定であることを明記 |
| C | 状況証拠として合理的だが direct proof がない | 補助仮説として隔離 |
| D | 仮説 | 実装前の追加調査対象 |
| X | 反証または不適格 | 不採用 |

---

## 2. Executive Synthesis

01 の先端パターンは、単なる「経営戦略文書」ではなく、**企業目的から事業経済までを一貫して管理する意思決定システム**である。トップ企業は、経営目的を抽象的な理念で終わらせず、事業セグメント、顧客群、価格、原価、利益、キャッシュ、KPI、OKR へ落とし込む。

### 2.1 共通する Frontier Pattern

1. **Purpose is translated into economic control.**  
   Amazon は顧客中心・発明・オペレーショナルエクセレンス・長期思考を経営原則として掲げ、その下でセグメント、顧客群、キャッシュフロー、原価管理を接続している [S01]。Microsoft は mission、AI、クラウド、3 つの事業 ambition、セグメント別収益/営業利益を接続している [S02]。

2. **Segment architecture is the resource-allocation interface.**  
   Amazon は North America / International / AWS、Microsoft は Productivity and Business Processes / Intelligent Cloud / More Personal Computing、Alphabet は Google Services / Google Cloud / Other Bets で、経営判断と財務報告の単位を接続している [S01][S02][S05]。

3. **Customer strategy is an economic design, not a marketing slogan.**  
   Costco は低価格・限定 SKU・高回転・会員制を一体化し、会費、更新率、粗利率、在庫回転を経済設計として管理する [S04]。Airbnb は hosts と guests の二面市場を、Nights and Seats Booked、GBV、service fee、trust/safety friction で管理する [S07]。

4. **Revenue, price, cost, and profit are managed as coupled variables.**  
   Netflix は会員課金、広告付きプラン、国別価格レンジ、コンテンツ償却、営業利益率を接続する [S06]。Alphabet は広告収益、Google Cloud、TAC、データセンター/技術インフラ、セグメント営業利益を接続する [S05]。

5. **KPI must be management-used, defined, and reconciled.**  
   IFRS Management Commentary は、重要な performance measures は経営者が progress/prospects 評価に使うもので、定義・計算・変更理由・非 IFRS 指標の説明/調整が必要だとする [S09]。SEC も MD&A の KPI/metrics について、投資家が理解できる定義・計算・利用理由・比較可能性を要求する方向のガイダンスを出している [S10]。

6. **OKR is a cadence and learning system, not a personnel-rating system.**  
   Google re:Work は OKR を公開・測定可能・野心的な目標設定として運用し、sweet spot を 60–70% とし、低い grade は評価対象ではなくデータとみなす [S12]。Atlassian と IBM も、Objectives を定性的、Key Results を測定可能な成果として分離し、少数の KR と定期レビューを推奨する [S13][S14]。

---

## 3. Frontier Exemplars Scorecard

スコアは RESEARCH.md の軸（Performance / Adoption / Artifact Richness / Peer Validation / Recency / Transferability / Failure Evidence）を 100 点換算した調査上の相対評価である。数値は公開証拠密度と移植可能性の評価であり、企業価値や業績順位を意味しない。

| Rank | Exemplar | Score | 01 で強い根拠 | 主な Evidence |
|---:|---|---:|---|---|
| 1 | Amazon | 94 | 顧客中心、長期思考、セグメント、FCF、原価・運転資本・価格変更を一体管理 | [S01] |
| 2 | Microsoft | 91 | Mission、AI/Cloud 戦略、3 ambition、セグメント別収益/営業利益、CODM 指標 | [S02] |
| 3 | Costco | 88 | 低価格、限定 SKU、高回転、会員制、低粗利、更新率を一体化 | [S04] |
| 4 | Alphabet | 87 | 情報アクセス mission、AI full-stack、広告/Cloud/Other Bets、TAC、セグメント営業利益 | [S05] |
| 5 | Apple | 86 | 統合型製品/サービス、設計・エコシステム、地域/製品カテゴリ、Services 高粗利 | [S03] |
| 6 | Netflix | 83 | 会員課金、広告、国別価格、コンテンツ償却、営業利益率と revenue focus | [S06] |
| 7 | Airbnb | 82 | 二面市場、GBV、Nights and Seats、service fee、trust/safety friction | [S07] |
| 8 | Salesforce | 76 | Subscription / support, RPO/cRPO, recurring-revenue management | [S08] |

---

## 4. Evidence Map

| Claim ID | Layer(s) | Claim | Evidence | Confidence |
|---|---|---|---|---|
| C-001 | 01.01, 01.03, 01.12 | 先端企業は経営目的を mission/principles として明文化し、事業セグメント・顧客群・資本配分へ接続する | Amazon, Microsoft, Alphabet | A |
| C-002 | 01.02, 01.05 | 事業目的は顧客群と Job に翻訳される。消費者、企業、開発者、seller、host/guest、member など顧客単位が経済単位になる | Amazon, Airbnb, Netflix, Costco | A |
| C-003 | 01.03, 01.09, 01.12 | セグメントは報告単位であると同時に、経営者が resource allocation と performance assessment に使う単位である | Microsoft, Alphabet, Netflix, Amazon | A |
| C-004 | 01.04 | 市場戦略は地域、カテゴリ、チャネル、価格帯、規制/供給制約を含む portfolio choice として設計される | Apple, Netflix, Costco, Airbnb | B |
| C-005 | 01.05 | 顧客戦略は retention/trust/experience metric を持つ。会員更新率、GBV、Nights/Seats、customer experience levers が直接の管理対象になる | Costco, Airbnb, Amazon | A |
| C-006 | 01.06 | 収益構造は単一売上ではなく、product/service、subscription、ads、marketplace fee、membership fee、cloud consumption の mix として設計される | Amazon, Alphabet, Apple, Netflix, Airbnb, Costco | A |
| C-007 | 01.07 | 価格構造は価格表だけでなく、価格変更、契約期間、地域/機能/広告有無/手数料率/会員制を含む設計問題である | Netflix, Airbnb, Costco, Amazon | A |
| C-008 | 01.08 | 原価構造は variable/fixed cost、TAC、content amortization、AI/Cloud infrastructure、inventory/warehouse economics の分解で管理される | Amazon, Alphabet, Netflix, Microsoft, Costco | A |
| C-009 | 01.09 | 利益構造は営業利益率・セグメント営業利益・FCF・粗利率を組み合わせて、短期利益と長期投資のトレードオフを管理する | Amazon, Microsoft, Alphabet, Netflix, Apple | A |
| C-010 | 01.10 | KPI は management-used、定義済み、計算方法明示、変更理由明示、非 GAAP/非 IFRS 指標の説明・調整が必要 | IFRS, SEC, Airbnb, Amazon | A |
| C-011 | 01.11 | OKR は野心的で公開され、Objective と Key Results を分離し、少数の測定可能な KR と定期レビューで運用する | Google re:Work, Atlassian, IBM | A |
| C-012 | 01.12 | 01.01–01.11 を統合するには、Purpose → Customer value → Revenue unit → Price → Cost drivers → Margin/FCF → KPI/OKR という economic equation が必要 | Cross-source synthesis | B |

---

## 5. Pattern Library

| Pattern ID | Pattern | Layer Scope | Description | Preconditions | Trade-offs | Confidence |
|---|---|---|---|---|---|---|
| P-01 | Mission-to-Economics Traceability | 01 | 経営目的を顧客・セグメント・収益・原価・利益指標まで trace する | Mission、segment、P&L、KPI dictionary が存在 | 短期収益最大化だけでは purpose と矛盾する可能性 | A |
| P-02 | Segment as Decision Boundary | 01.03, 01.06, 01.09, 01.12 | セグメントを resource allocation と performance assessment の単位にする | セグメント別売上/利益/投資データ | 顧客横断シナジーが見えにくくなる | A |
| P-03 | Customer-Economics Coupling | 01.02, 01.05, 01.06, 01.07 | 顧客体験・信頼・維持率を revenue unit と価格に接続する | 顧客群ごとの metric と pricing unit | CAC/LTV の過度な単純化 | B |
| P-04 | Price-Cost Pairing | 01.07, 01.08, 01.09 | 価格変更を cost driver と margin impact と同時に審査する | Cost driver map、price ladder、gross margin data | 価格を低く保つ戦略では短期 margin が犠牲になる | A |
| P-05 | KPI Governance | 01.10, 01.12 | 指標の定義・計算・所有者・利用場面・変更履歴を管理する | KPI dictionary、source of truth | 指標が多すぎると意思決定が遅くなる | A |
| P-06 | OKR as Learning Cadence | 01.11, 01.12 | OKR を評価制度ではなく alignment/learning/review の周期として使う | Transparent OKR board、quarterly review | 報酬評価と混ぜると stretch が消える | A |
| P-07 | Cash-Conversion Strategy | 01.08, 01.09, 01.12 | 営業利益だけでなく FCF、Capex、運転資本、契約コミットメントを統合管理する | Cash flow statement, Capex plan, working capital metrics | 高成長期は FCF が短期的に低下する | B |

---

# 6. Clone Specs by Layer

以下は 01 の各レイヤーについて、RESEARCH.md の Clone Spec テンプレートを圧縮適用した実装可能仕様である。

---

## 01.01 経営目的

### Definition
企業全体として、誰に何の価値を、どの時間軸・制約・原則の下で創るかを定義するレイヤー。経営目的は mission statement ではなく、事業選択、資源配分、顧客・社会・株主への価値創出、リスク許容度、長期/短期トレードオフを制御する意思決定ルールである。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Amazon | 顧客中心、発明、オペレーショナルエクセレンス、長期思考を経営原則として開示し、FCF・原価・顧客体験へ接続 | [S01] |
| Microsoft | mission、AI の民主化、クラウドの規模経済、3 ambition を annual report と segment reporting に接続 | [S02] |
| Alphabet | 情報アクセス mission と AI full-stack investment を、Search/YouTube/Cloud/Other Bets の portfolio に接続 | [S05] |
| Costco | 低価格・高品質・会員価値を、限定 SKU、高回転、低粗利という経済構造に接続 | [S04] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 経営目的は customer promise と long-term investment を同時に制御する | Amazon, Microsoft | direct | A |
| mission はセグメント別の投資・利益・顧客成果へ翻訳される必要がある | Microsoft, Alphabet, Amazon | direct | A |
| 目的が価格・原価・利益設計と接続しない場合、実装不能な slogan になる | Cross-source synthesis | inferred | B |

### Core Philosophy
経営目的は「何を最大化するか」ではなく、「何を犠牲にし、何を守るか」を決める上位制約である。Frontier 企業は、顧客価値・信頼・長期投資・経済性を同一の意思決定系に置く。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 顧客群、長期市場機会、技術/供給制約、競争環境、資本市場制約、規制/社会的期待 |
| Decision Object | 企業が守る価値創出原則と、許容する経済トレードオフ |
| Criteria | 顧客価値、長期持続性、信頼、収益/利益/FCF への接続、セグメント整合性 |
| Priorities | 1. 顧客価値、2. 長期 compounding、3. 再投資可能な経済性、4. 測定可能性 |
| Prohibitions | generic purpose、短期 EPS だけの目的化、顧客価値と価格/原価設計の切断 |
| Exceptions | 危機対応、法令・安全・信頼リスク、資本制約による投資抑制 |
| Owners | CEO、CFO、CSO、取締役会、事業責任者 |
| Cadence | 年次戦略レビュー、四半期事業レビュー、重要投資・撤退判断時 |

### Operating Model
- 役割: CEO が目的と原則を保持し、CFO が経済整合性、CSO が戦略整合性、事業責任者が execution へ翻訳する。
- プロセス: Mission → Strategic priorities → Segment strategy → Economic model → KPI/OKR の cascade を年次で更新する。
- 会議体: Annual strategy offsite、Quarterly Business Review、Capital Allocation Committee。
- 成果物: Purpose statement、Principles、Strategic thesis、Capital allocation thesis、KPI tree。

### Technical / Business Specification
- 経営目的は 5 文以内で定義し、各文に対応する測定可能な business outcome を 1–3 個置く。
- 各 strategic initiative は、どの purpose element に貢献するかを明記する。
- 目的ごとに「守る制約」と「許容する犠牲」を明文化する。例: 低価格を守るため短期粗利率を犠牲にする、AI infrastructure 投資で短期 gross margin を犠牲にする。

### Metrics
Mission-linked revenue share、customer trust metric、NPS/retention、strategic initiative ROI、segment operating income、FCF、capital allocation adherence、purpose-to-KPI traceability rate。

### Failure Modes
- Mission が slogans に留まり、価格・原価・投資判断に影響しない。
- 顧客価値と株主価値が別々の資料で管理され、トレードオフが不可視になる。
- 経営目的が毎年変わり、事業ポートフォリオの一貫性が崩れる。

### Anti-patterns
- “世界を良くする” のような抽象目的だけで、顧客・市場・収益単位がない。
- Purpose を PR 部門の文書に閉じる。
- KPI と OKR に purpose への trace がない。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | Mission なし、または founder の暗黙知 |
| 1 | 宣言 | Mission はあるが、事業/経済との接続なし |
| 2 | 文書化 | 目的と戦略テーマが文書化される |
| 3 | 標準化 | 目的がセグメント・KPI・投資判断に接続 |
| 4 | 計測 | purpose-to-KPI trace と capital allocation がレビューされる |
| 5 | 自律改善 | 目的・戦略・経済性のズレを四半期単位で検知/修正 |

### Clone Implementation Guide
1. CEO/CFO/CSO で目的文を 5 文以内に再定義する。
2. 各目的文に顧客成果、経済成果、リスク制約を紐づける。
3. 全 strategic initiative に purpose tag を付ける。
4. QBR で purpose/KPI/economics のズレをレビューする。

### Confidence & Unknowns
- A: 主要 exemplar の mission/strategy/segment/economics は一次情報で確認済み。
- B: purpose-to-economic-control という抽象パターンは複数企業の合成。
- Unknown: 各社の内部 offsite、board review、OKR cascade の具体運用は公開情報だけでは限定的。

---

## 01.02 事業目的

### Definition
個別事業が、どの顧客・利用者・パートナーのどの問題を、なぜ自社が解くべきかを定義するレイヤー。事業目的は revenue stream の前段であり、顧客単位、価値単位、信頼単位、使用単位を特定する。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Airbnb | hosts と guests の二面市場を明示し、booking value と nights/seats を事業目的の測定単位にする | [S07] |
| Netflix | members への entertainment value と subscription monetization を明確に接続 | [S06] |
| Amazon | consumers, sellers, developers, enterprises, creators, advertisers など複数顧客群を事業群ごとに定義 | [S01] |
| Costco | members に低価格・限定品揃え・高品質を提供する warehouse model | [S04] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 事業目的は顧客群の明確化から始まる | Airbnb, Amazon, Costco | direct | A |
| marketplace/subscription/membership では、顧客価値の単位が revenue metric と直結する | Airbnb, Netflix, Costco | direct | A |
| 顧客群を曖昧にすると価格・原価・KPI が設計できない | Cross-source synthesis | inferred | B |

### Core Philosophy
事業目的は「何を売るか」ではなく「誰のどの成果を、どの繰り返し可能な価値単位で改善するか」を決める。Frontier 企業は customer set と economic unit を同時に定義する。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 顧客セグメント、Job-to-be-done、代替手段、利用頻度、価値の発生単位、信頼/安全要求 |
| Decision Object | 事業が解く顧客問題と、成功を示す利用/取引/維持 metric |
| Criteria | 顧客の重要課題、繰り返し利用可能性、収益化可能性、供給/需要の拡張性、信頼コスト |
| Priorities | 明確な顧客群、明確な価値単位、事業固有の leading metric |
| Prohibitions | “全顧客向け” の曖昧目的、売上カテゴリだけで顧客価値を定義すること |
| Exceptions | プラットフォーム事業では複数顧客群を同時に持つ。ただし各群の価値指標を分ける |
| Owners | 事業責任者、Product GM、Revenue lead、Customer/Market research lead |
| Cadence | 年次事業計画、主要 product/market expansion、pricing change 前 |

### Operating Model
- 事業目的レビューでは、顧客、価値単位、収益単位、原価単位を同時に確認する。
- 二面市場では demand side と supply side の目的を分け、摩擦・信頼・流動性を別々に管理する。
- Subscription/membership では acquisition より retention/renewal と利用価値を中心に置く。

### Technical / Business Specification
- Business purpose statement は `Customer / Job / Value Unit / Revenue Unit / Constraint` の形式で書く。
- 例: `Guests and hosts / trusted short-term stay transaction / nights booked and GBV / service fee / trust and safety friction`。
- 各事業目的に 1 つの north-star usage metric と 3–5 個の guardrail metric を設定する。

### Metrics
Customer segment growth、usage unit、transaction value、retention/renewal、conversion、trust/safety incidents、revenue per value unit、gross margin per value unit。

### Failure Modes
- 事業目的が「売上成長」だけになり、顧客価値と value unit が未定義。
- Marketplace で一方の顧客群だけを最適化し、もう一方の供給/需要が壊れる。
- Subscription で会員数だけを追い、価値・利用・解約理由を見ない。

### Anti-patterns
- 顧客群を personas だけで定義し、経済単位に変換しない。
- 価値単位と課金単位が別々に設計される。
- trust/safety/friction を growth の副作用として後回しにする。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 事業目的が売上目標だけ |
| 1 | 顧客記述 | 顧客像はあるが value unit がない |
| 2 | Value Unit 定義 | 顧客成果と利用単位を定義 |
| 3 | 経済接続 | 利用単位が収益/原価/KPI に接続 |
| 4 | Segment 最適化 | 顧客群ごとの retention/unit economics を管理 |
| 5 | 自律改善 | 顧客価値と経済性の変化を継続的に再設計 |

### Clone Implementation Guide
1. 各事業について `Customer / Job / Value Unit / Revenue Unit / Trust Constraint` を 1 行で定義する。
2. 顧客群が複数ある場合は群ごとに価値単位を分ける。
3. 既存 KPI を価値単位に紐づけ、紐づかない KPI を棚卸しする。

### Confidence & Unknowns
- A: Airbnb、Costco、Netflix、Amazon の顧客群・事業単位は一次情報で確認済み。
- B: value-unit-based business purpose は複数企業の合成パターン。
- Unknown: 各社の非公開 customer research や internal segmentation の詳細。

---

## 01.03 事業戦略

### Definition
どの事業領域、能力、資産、セグメント、投資配分を通じて勝つかを決めるレイヤー。事業戦略は単なる成長テーマではなく、資本・人材・技術・営業・チャネル・M&A・撤退判断を制御する resource allocation logic である。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Microsoft | 3 ambition と segment reporting を接続し、AI/cloud investment と営業利益を同じ報告体系で管理 | [S02] |
| Alphabet | AI full-stack、Google Services、Google Cloud、Other Bets を portfolio として管理 | [S05] |
| Amazon | Retail/marketplace/advertising/AWS を segment と顧客群で分け、投資・FCF・原価を管理 | [S01] |
| Apple | ハードウェア、ソフトウェア、サービスを統合設計し、product/service mix と gross margin を管理 | [S03] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 事業戦略の公開観測面は segment reporting と MD&A に強く現れる | Amazon, Microsoft, Alphabet | direct | A |
| 戦略単位は必ずしも法人組織図ではなく、経営者が資源配分に使う事業境界である | Microsoft, Alphabet, Netflix | direct | A |
| AI/Cloud/Services のような横断技術はセグメント strategy と capital allocation の両方に影響する | Microsoft, Alphabet, Apple | direct/inferred | B |

### Core Philosophy
事業戦略は「どこで戦うか」と「何を再投資エンジンにするか」を同時に決める。Frontier 企業は、セグメントを外部報告用ラベルではなく、経営資源配分の単位として扱う。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 市場成長率、競争優位、顧客セグメント、技術/データ/ブランド資産、資本制約、リスク |
| Decision Object | 事業ポートフォリオ、セグメント境界、投資/撤退/拡張方針 |
| Criteria | 優位性の持続性、収益成長、margin potential、cash conversion、capability fit、option value |
| Priorities | 1. 既存優位の compounding、2. 高成長 adjacent market、3. 長期 option、4. portfolio risk balance |
| Prohibitions | セグメント別経済性なしの事業拡張、目的と整合しない diversification |
| Exceptions | 戦略的技術投資、規制/信頼対応、defensive investment |
| Owners | CEO、CFO、CSO、Segment GM、Corporate Development、Board |
| Cadence | 年次 portfolio review、四半期 segment review、M&A/撤退/大型 Capex 時 |

### Operating Model
- セグメントごとに growth, margin, cash, strategic option value を評価する。
- 事業戦略レビューでは、新規投資を既存セグメント、隣接セグメント、長期 option に分類する。
- CODM/経営会議が見る指標と外部報告セグメントを可能な限り整合させる。

### Technical / Business Specification
- 各セグメントに `strategic role` を付ける。例: cash engine、growth engine、option portfolio、platform enabler。
- Segment strategy sheet は以下を必須にする: customer set、market boundary、differentiation、revenue model、cost model、profit/cash profile、major risks、investment ask。
- 事業ポートフォリオは 2x2 の単純分類ではなく、`current profit / future option / capability leverage / capital intensity` で評価する。

### Metrics
Segment revenue growth、segment operating income/margin、gross margin、capital intensity、FCF contribution、R&D/Capex allocation、customer/usage growth、strategic option milestones。

### Failure Modes
- 戦略が成長市場リストになり、勝ち筋・資本制約・原価構造が定義されない。
- セグメントが外部報告上の区分だけになり、内部資源配分とズレる。
- 長期 option と既存 cash engine の評価尺度を混同する。

### Anti-patterns
- どの事業も「成長投資」と呼び、撤退基準がない。
- 一時的な市場トレンドを core strategy と誤認する。
- 事業責任者が revenue のみ、CFO が cost のみを管理し、統合 P&L owner がいない。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 事業戦略が個別案件の集合 |
| 1 | テーマ化 | 成長テーマはあるが経済モデルなし |
| 2 | セグメント化 | 事業単位と基本 P&L を定義 |
| 3 | 資源配分 | セグメント別投資/利益/リスクで判断 |
| 4 | Portfolio 管理 | cash engine/growth/option を分ける |
| 5 | 動的再配分 | 四半期で戦略仮説と資源配分を更新 |

### Clone Implementation Guide
1. 全事業を segment / sub-segment / initiative に分解する。
2. 各セグメントの strategic role と economic profile を定義する。
3. 年次 budget ではなく、戦略仮説ごとの capital allocation table を作る。
4. 事業撤退/縮小基準を先に決める。

### Confidence & Unknowns
- A: セグメント開示と経営者評価指標の関係は複数一次情報で確認。
- B: strategic role 分類は公開情報から抽象化した移植用仕様。
- Unknown: 実際の社内 capital committee、M&A hurdle rate、内部 ROI 閾値。

---

## 01.04 市場戦略

### Definition
どの市場、地域、カテゴリ、顧客層、チャネル、価格帯、規制環境を優先するかを決めるレイヤー。市場戦略は TAM の大きさだけではなく、自社の勝ち筋、供給能力、原価構造、チャネル到達性、ローカル規制/文化制約を含む。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Apple | 地域別・製品カテゴリ別の売上/粗利を開示し、統合製品・サービス ecosystem で市場を設計 | [S03] |
| Netflix | 地域別 streaming revenue と国別価格レンジ、広告付きプランを組み合わせる | [S06] |
| Costco | 倉庫型小売を地域・物件・会員基盤・商品回転に接続 | [S04] |
| Airbnb | 国際的 marketplace を地域、host/guest 供給、trust/safety friction で管理 | [S07] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 市場戦略は地域・カテゴリ・チャネルの組み合わせで観測できる | Apple, Netflix, Costco | direct | A |
| Marketplace/retail/subscription では市場拡大が供給・信頼・価格の制約を伴う | Airbnb, Costco, Netflix | direct/inferred | B |
| 市場優先順位は segment economics と接続されなければならない | Apple, Microsoft, Alphabet | inferred | B |

### Core Philosophy
市場戦略は「大きい市場を狙う」ではなく、「自社の価値単位が高い再現性で成立する市場を選ぶ」ことである。Frontier 企業は、地域・カテゴリ・価格帯・チャネルを経済モデルの制約として扱う。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | TAM/SAM/SOM、競争密度、規制、供給制約、物流/インフラ、価格感度、チャネル、ブランド適合性 |
| Decision Object | 優先市場、参入順序、撤退/保留市場、ローカル化要件 |
| Criteria | 顧客価値適合、unit economics、供給可能性、規制/信頼リスク、チャネル効率、戦略的 option value |
| Priorities | 1. 既存能力の leverage、2. 高い unit economics、3. 学習価値、4. リスク制御 |
| Prohibitions | TAM だけで参入、地域別 cost-to-serve 無視、価格ローカライズなし |
| Exceptions | 戦略的防衛市場、規制対応市場、長期 option 市場 |
| Owners | CSO、Regional GM、Product/Market lead、Finance、Legal/Policy |
| Cadence | 年次 market prioritization、四半期 geography/category review、参入/撤退時 |

### Operating Model
- 市場候補ごとに `market attractiveness / ability to win / economic fit / risk` を採点する。
- 地域別/カテゴリ別の価格・原価・チャネル・規制要件を 1 枚の market entry memo に統合する。
- 参入後は KPI を global aggregate ではなく market cohort でレビューする。

### Technical / Business Specification
- Market Strategy Card: `market definition`, `target customer`, `entry wedge`, `price localization`, `cost-to-serve`, `channel`, `regulatory constraints`, `success metric`, `exit criteria`。
- 参入基準: target margin、payback、供給充足率、顧客獲得効率、trust/safety readiness。
- 既存市場の深耕と新市場の探索を別 budget bucket にする。

### Metrics
Market revenue growth、market gross margin、CAC/payback、retention by market、channel conversion、cost-to-serve、supply liquidity、regulatory incident count、market-level operating income。

### Failure Modes
- 高 TAM 市場に入るが、価格・供給・規制・チャネルが合わない。
- 地域別 economics を見ず、global average で黒字に見せる。
- 参入後の撤退基準がなく、低採算市場が固定費化する。

### Anti-patterns
- 市場を国名だけで定義する。
- 顧客・価格・チャネル・原価を別々の資料で管理する。
- ローカル競争・規制・信頼コストを後から足す。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 市場選択が場当たり |
| 1 | TAM 重視 | TAM と競合情報だけで判断 |
| 2 | Entry Memo | 市場参入メモを作る |
| 3 | Unit Economics | 市場別 revenue/cost/margin を管理 |
| 4 | Portfolio | 市場を grow/hold/exit/option に分類 |
| 5 | Dynamic Market System | 市場別学習を価格・商品・供給へ自動反映 |

### Clone Implementation Guide
1. 主要市場を地理・カテゴリ・顧客群で再定義する。
2. 各市場の price/cost/channel/regulation を同じテンプレートで比較する。
3. 市場別 P&L と撤退基準を設定する。

### Confidence & Unknowns
- A: 地域/カテゴリ/セグメント売上の公開事実。
- B: 市場選択ルールは複数企業からの抽象化。
- Unknown: 各社の内部 TAM、market entry hurdle、地域別 CAC。

---

## 01.05 顧客戦略

### Definition
どの顧客群に対し、どの獲得・維持・信頼・体験・関係性モデルで価値を届けるかを決めるレイヤー。顧客戦略は CRM やマーケティング施策ではなく、顧客価値と経済性を接続する設計である。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Amazon | 品揃え、価格、利便性、Prime、seller/enterprise/developer 顧客群を統合 | [S01] |
| Costco | 会員制と renewal rate を中心に、低価格・高回転・限定 SKU を顧客価値に接続 | [S04] |
| Airbnb | hosts/guests の trust, safety, fraud, friction を marketplace 成長の制約として扱う | [S07] |
| Netflix | membership value、recommendation、pricing、content investment を顧客維持に接続 | [S06] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 顧客戦略は acquisition だけではなく retention/renewal/trust を含む | Costco, Airbnb, Netflix | direct | A |
| 顧客体験の改善は売上成長・FCF・原価効率と結合する | Amazon, Costco | direct/inferred | B |
| 二面市場では両側の顧客戦略を別々に設計する必要がある | Airbnb | direct | A |

### Core Philosophy
顧客戦略は「売り方」ではなく「顧客が再度選ぶ理由を経済的に再現する仕組み」である。Frontier 企業は顧客価値指標と revenue/margin 指標を同じレビューで見る。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 顧客セグメント、獲得経路、利用/購買頻度、解約理由、信頼/安全要求、価格感度、サポートコスト |
| Decision Object | 顧客ポートフォリオ、獲得/維持/拡張施策、体験投資、trust controls |
| Criteria | LTV、retention、usage depth、trust, cost-to-serve、strategic customer value |
| Priorities | 1. 継続利用、2. 信頼、3. 価値体験、4. 収益化、5. 獲得効率 |
| Prohibitions | CAC だけの最適化、high-value customer と high-cost customer の混同 |
| Exceptions | 新規市場立ち上げ時は短期 CAC/payback が悪化しうる。ただし exit criteria を持つ |
| Owners | Chief Customer/Revenue/Product Officer、Marketing、Customer Success、Trust/Safety、Finance |
| Cadence | Monthly customer review、quarterly cohort review、pricing/product change 前 |

### Operating Model
- 顧客 cohort ごとに acquisition, activation, retention, expansion, support cost をレビューする。
- Trust/safety/support は growth の後処理ではなく、顧客戦略の制約として扱う。
- 価格変更は customer lifetime value と churn risk を同時に評価する。

### Technical / Business Specification
- Customer Strategy Sheet: `segment`, `job`, `promise`, `value metric`, `acquisition path`, `retention mechanism`, `price sensitivity`, `cost-to-serve`, `trust risk`。
- 各顧客群に leading metric、lagging metric、guardrail metric を定義する。
- Marketplace では supply-side と demand-side の liquidity/quality/trust 指標を分ける。

### Metrics
Retention/renewal rate、LTV/CAC、NPS、active customers/members、repeat purchase、usage frequency、churn、trust/safety incidents、support cost per customer、revenue per customer、gross margin per customer。

### Failure Modes
- 成長指標が新規獲得に偏り、更新率/継続利用/信頼を見ない。
- 顧客群別の cost-to-serve が不明で、不採算顧客が拡大する。
- Trust/safety issue が顧客獲得を相殺する。

### Anti-patterns
- 全顧客を同じ LTV/CAC で評価する。
- 顧客の “声” を施策リストにし、経済モデルに接続しない。
- 顧客体験 metric と finance metric を別会議で扱う。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 顧客戦略が広告/営業施策だけ |
| 1 | Segment | 顧客セグメントを定義 |
| 2 | Lifecycle | acquisition/retention を計測 |
| 3 | Economics | 顧客別 LTV/CAC/cost-to-serve を管理 |
| 4 | Trust & Guardrail | trust/safety/support を経済制約に含める |
| 5 | Adaptive Customer System | cohort 学習で価格・商品・体験を継続更新 |

### Clone Implementation Guide
1. 顧客群ごとに value metric と revenue metric を分けて記述する。
2. 顧客レビューを growth, retention, trust, margin の 4 軸にする。
3. CAC/LTV に加えて cost-to-serve と trust incidents を必ず含める。

### Confidence & Unknowns
- A: Costco の renewal、Airbnb の marketplace metric、Netflix の subscription model は一次情報で確認。
- B: 顧客戦略を unit economics に接続する仕様は合成。
- Unknown: 各社の詳細 cohort、内部 LTV/CAC、support cost。

---

## 01.06 収益構造

### Definition
どの顧客価値から、どの収益源、収益認識、収益ミックス、成長 driver、leading indicator で売上を作るかを決めるレイヤー。収益構造は売上高の表ではなく、価値単位・課金単位・認識単位・成長単位の設計である。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Amazon | product sales、third-party seller services、advertising、subscription、AWS など複数 revenue stream を組み合わせる | [S01] |
| Alphabet | advertising が主要収益源で、Google Cloud/Subscriptions/Platforms/Devices/Other Bets と組み合わせる | [S05] |
| Netflix | monthly membership fee と advertising-supported tier を管理し、revenue と operating margin を主要 focus にする | [S06] |
| Airbnb | service fee を booking value に対する percentage として得る marketplace model | [S07] |
| Costco | merchandise net sales と membership fee revenue を組み合わせる warehouse membership model | [S04] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 収益構造は収益源ミックスと顧客/価値単位ごとの driver で分解する必要がある | Amazon, Alphabet, Costco | direct | A |
| Subscription/membership/marketplace では認識タイミングと利用/取引 metric が重要 | Netflix, Airbnb, Costco | direct | A |
| 単一 revenue metric だけでは事業の持続性を判断できない | Cross-source synthesis | inferred | B |

### Core Philosophy
収益は「売上」ではなく「顧客価値がどの単位で現金化されるか」である。Frontier 企業は revenue source ごとに growth driver、recognition、margin profile、risk を分ける。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 顧客価値単位、利用/取引頻度、契約期間、支払いタイミング、返金/キャンセル、広告/手数料/購読/販売の混在 |
| Decision Object | Revenue stream、recognition rule、revenue mix、growth driver、leading metric |
| Criteria | 顧客価値との整合、予測可能性、gross margin、cash timing、scalability、risk |
| Priorities | 1. Recurring/retained revenue、2. high-margin scalable stream、3. cash conversion、4. defensibility |
| Prohibitions | revenue stream の混同、one-time と recurring の未分離、metric 定義なしの成長報告 |
| Exceptions | 新規事業では traction metric を revenue より先行させる。ただし収益化仮説を持つ |
| Owners | CFO、Revenue Operations、Segment GM、Accounting、Pricing Lead |
| Cadence | 月次 close、四半期 revenue mix review、年次 model redesign |

### Operating Model
- Revenue stream ごとに owner、認識ルール、leading metric、margin profile を定義する。
- Revenue growth は price / volume / mix / FX / usage / renewal / new customers に分解する。
- Non-GAAP や operational metrics は定義・計算方法・変更履歴を KPI dictionary に格納する。

### Technical / Business Specification
- Revenue Model Table の必須列: `stream`, `customer`, `value unit`, `pricing unit`, `recognition`, `leading metric`, `gross margin`, `cash timing`, `risks`。
- Marketplace では GBV と revenue を明確に分ける。
- Subscription では paid membership、ARPU、churn、plan mix を分ける。
- Membership retail では membership fee revenue と merchandise margin を分ける。

### Metrics
Revenue growth、revenue mix、ARR/MRR、GBV、take-rate proxy、paid members、membership fee revenue、ad impressions/clicks/CPC/CPM、cloud consumption、RPO/cRPO、deferred revenue、gross margin by stream。

### Failure Modes
- Gross revenue と net revenue、GMV/GBV と revenue を混同する。
- 高成長だが低 margin / low cash conversion stream が過大評価される。
- 認識基準・返金・キャンセル・契約期間を無視して KPI を作る。

### Anti-patterns
- 売上だけを KPI にし、stream mix を見ない。
- 一時的な price increase を core revenue growth と誤認する。
- Marketplace の流通総額を売上と同等に扱う。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 売上総額だけを管理 |
| 1 | Stream 分解 | 収益源別売上を管理 |
| 2 | Recognition | 認識・契約・支払を整理 |
| 3 | Driver 分解 | price/volume/mix/usage/renewal を分解 |
| 4 | Profit/Cash 接続 | revenue stream ごとに margin/cash を管理 |
| 5 | Dynamic Revenue System | revenue mix と顧客/価格/原価を統合最適化 |

### Clone Implementation Guide
1. 全 revenue stream を value unit と pricing unit で再分類する。
2. Revenue growth を price, volume, mix, retention, new customer, FX に分解する。
3. KPI dictionary に revenue metric の定義・認識・所有者を登録する。

### Confidence & Unknowns
- A: 主要 exemplar の revenue stream と metric は一次情報で確認。
- B: revenue model table は移植用仕様。
- Unknown: 各社の内部 pricing elasticity、stream-level margin の詳細。

---

## 01.07 価格構造

### Definition
顧客価値単位をどの課金単位、価格階層、割引、契約、手数料、地域/機能差、価格変更ルールで monetization するかを決めるレイヤー。価格構造は finance と sales の後処理ではなく、顧客戦略・収益構造・原価構造を接続する design layer である。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Netflix | 国別・機能別・広告有無による価格レンジと subscription revenue を管理 | [S06] |
| Airbnb | booking value に対する service fee と marketplace friction を設計 | [S07] |
| Costco | 低価格を中心にし、価格権限を短期利益最大化に従属させない model | [S04] |
| Amazon | 小売価格、subscription、seller service fee、AWS price changes/long-term commitments を組み合わせる | [S01] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 価格構造は plan/tier/fee/region/contract を含む多変数設計である | Netflix, Airbnb, Amazon | direct | A |
| 低価格戦略は高回転・低粗利・membership economics とセットで成立する | Costco | direct | A |
| 価格変更は顧客維持、需要、原価、margin への影響を同時評価すべき | Netflix, Amazon, Costco | inferred | B |

### Core Philosophy
価格は「顧客に何を約束し、どの原価構造で利益を残すか」の境界条件である。Frontier 企業は、価格を revenue lever としてだけでなく、顧客信頼・競争優位・原価吸収・利用促進の lever として扱う。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | Value unit、顧客 willingness-to-pay、競争価格、cost-to-serve、plan feature、地域、契約期間、elasticity |
| Decision Object | Price ladder、plan/tier、fee rate、discount、promotion、price-change rule |
| Criteria | 顧客価値との整合、収益性、維持率、競争優位、簡潔性、公平性、法令/契約制約 |
| Priorities | 1. Value alignment、2. Retention/trust、3. Margin adequacy、4. Simplicity、5. Strategic positioning |
| Prohibitions | コスト無視の値下げ、顧客価値無視の値上げ、例外割引の乱発、価格表と実売価格の乖離 |
| Exceptions | 新市場 launch、strategic account、在庫/需給調整、regulatory/tax change |
| Owners | Pricing Lead、CFO、Revenue Ops、Product、Sales、Legal |
| Cadence | 四半期 pricing review、価格変更前、主要原価変動時、競争環境変化時 |

### Operating Model
- 価格変更は `customer impact / revenue impact / margin impact / churn risk / trust risk` の 5 軸で審査する。
- Plan/tier の追加は、顧客価値の差分と operational complexity の差分を比較する。
- 割引は例外ではなく policy として owner、上限、承認、期間、測定指標を持つ。

### Technical / Business Specification
- Pricing Architecture Document: `pricing unit`, `tier`, `included value`, `overage/fee`, `discount authority`, `contract term`, `renewal rule`, `migration rule`, `margin floor`。
- 価格テストには cohort、gross margin、churn、support contact、trust signal を含める。
- B2B では list price、net price、discount reason、renewal uplift、contract commitment を分ける。

### Metrics
ARPU、price realization、discount rate、gross margin by tier、churn after price change、upgrade/downgrade rate、fee take-rate proxy、price elasticity、renewal uplift、net revenue retention。

### Failure Modes
- 価格が複雑化し、顧客が価値差を理解できない。
- 割引権限が分散し、gross margin と信頼が毀損する。
- 価格変更が revenue だけで判断され、解約・信頼・サポート負荷が悪化する。

### Anti-patterns
- 価格表を作るが、価格変更ルールと承認者がない。
- 低価格戦略なのに原価/在庫/回転の設計がない。
- Usage pricing を導入するが、顧客の予測可能性を設計しない。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 価格は都度決定 |
| 1 | List Price | 価格表のみ存在 |
| 2 | Tier/Discount | 階層と割引ルールを定義 |
| 3 | Margin Control | 価格と原価/margin を接続 |
| 4 | Customer Impact | churn/trust/usage と価格を統合管理 |
| 5 | Adaptive Pricing Governance | 市場・原価・顧客反応で価格体系を継続更新 |

### Clone Implementation Guide
1. 価格を SKU/顧客/地域/契約/割引/費用単位で棚卸しする。
2. 各価格の value unit と cost-to-serve を紐づける。
3. 価格変更 approval memo を標準化する。

### Confidence & Unknowns
- A: Netflix pricing range、Airbnb fee model、Costco low-price model は一次情報で確認。
- B: 価格変更審査仕様は合成。
- Unknown: 各社の内部 elasticity、割引承認基準、A/B pricing 実験結果。

---

## 01.08 原価構造

### Definition
価値提供に必要な直接費、変動費、固定費、技術インフラ、コンテンツ/在庫/物流、販売費、サポート費、資本支出、運転資本をどう分解・制御するかを決めるレイヤー。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Amazon | 変動費・固定費・在庫回転・履行費・技術/インフラ投資・FCF を統合 | [S01] |
| Costco | 限定 SKU、高販売量、迅速な在庫回転、効率的物流により低粗利 model を成立 | [S04] |
| Alphabet | TAC、データセンター、technical infrastructure、広告/Cloud cost を分解 | [S05] |
| Netflix | コンテンツ償却、content acquisition/production、technology/development、marketing を管理 | [S06] |
| Microsoft | AI/cloud infrastructure 投資が gross margin と capex に影響することを開示 | [S02] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 原価構造は変動費・固定費・資本費・運転資本に分解する必要がある | Amazon, Alphabet, Netflix | direct | A |
| 低価格戦略は原価/在庫/物流効率と一体で設計される | Costco | direct | A |
| AI/cloud/content-heavy business では Capex や償却が利益構造を大きく左右する | Microsoft, Alphabet, Netflix | direct | A |

### Core Philosophy
原価は削減対象ではなく、顧客価値をどの operational system で生むかの構造である。Frontier 企業は、原価を line item ではなく、価値単位ごとの driver として管理する。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | Value unit、delivery model、supplier/partner cost、inventory、infrastructure、content/data、labor、support、capex |
| Decision Object | Cost driver map、unit cost、fixed/variable split、capital intensity、cost-control rule |
| Criteria | 顧客価値維持、gross margin、scale leverage、quality/reliability、cash impact、strategic control |
| Priorities | 1. Unit economics、2. Quality/reliability、3. Scale efficiency、4. Working capital、5. Optionality |
| Prohibitions | コスト削減で顧客価値や信頼を毀損、fixed cost の隠れ増加、Capex を margin 外で無視 |
| Exceptions | 戦略的先行投資、安全/信頼投資、規制対応、供給安定化投資 |
| Owners | CFO、COO、CTO/Infrastructure、Supply Chain、Segment GM、FP&A |
| Cadence | 月次 cost review、四半期 unit economics review、Capex/contract approval 時 |

### Operating Model
- Cost driver を value unit に紐づける。例: order、booking、streaming hour、ad impression、cloud usage、member。
- Fixed cost は capacity utilization と組み合わせて管理する。
- Capex/contract commitments は P&L だけでなく FCF と liquidity に接続する。

### Technical / Business Specification
- Cost Model Table: `value unit`, `variable cost`, `semi-variable cost`, `fixed cost`, `capex`, `working capital`, `quality risk`, `owner`, `levers`。
- Cost initiative は削減額だけでなく、顧客価値、SLA/quality、trust、growth impact を記載する。
- Gross margin review と operating expense review を revenue stream 別に分ける。

### Metrics
COGS/revenue、gross margin、unit cost、fulfillment cost、TAC rate、content amortization/revenue、infrastructure cost per usage、inventory turnover、capex/revenue、FCF conversion、operating expense ratio。

### Failure Modes
- 売上成長に伴い隠れ固定費が増え、scale leverage が出ない。
- 原価削減が品質・信頼・顧客体験を毀損する。
- Capex-heavy growth を P&L だけで評価し、FCF/資本効率を見ない。

### Anti-patterns
- 原価を勘定科目別にしか見ず、顧客価値単位に紐づけない。
- インフラ/コンテンツ/在庫投資を戦略投資として一括りにし、回収仮説を持たない。
- procurement savings を顧客体験や品質指標なしに評価する。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 原価を月次実績で見るだけ |
| 1 | 勘定科目管理 | COGS/Opex を分ける |
| 2 | Driver Map | 原価 driver を特定 |
| 3 | Unit Cost | value unit ごとに unit cost を管理 |
| 4 | Capital/Cash 接続 | Capex/working capital/FCF と連携 |
| 5 | Adaptive Cost System | usage/品質/需要変動で原価構造を継続最適化 |

### Clone Implementation Guide
1. 主要価値単位ごとに variable/fixed/capex/working capital を分解する。
2. 原価削減施策に customer/trust/quality guardrail を付ける。
3. Cost review を revenue stream と segment P&L に接続する。

### Confidence & Unknowns
- A: Amazon、Costco、Alphabet、Netflix、Microsoft の原価/投資開示。
- B: value-unit cost model は移植用合成仕様。
- Unknown: 各社の内部 unit cost、supplier contract、capacity model。

---

## 01.09 利益構造

### Definition
収益、価格、原価、投資、資本支出、運転資本をどのように粗利、営業利益、セグメント利益、FCF、資本効率へ変換するかを決めるレイヤー。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Amazon | Operating income、FCF、顧客体験投資、在庫/Capex を一体的に説明 | [S01] |
| Microsoft | Segment revenue/gross margin/operating income と AI/cloud infrastructure 投資の影響を開示 | [S02] |
| Netflix | Revenue と operating margin を primary focus とし、コンテンツ償却を含む利益構造を管理 | [S06] |
| Alphabet | Segment operating income、TAC、infrastructure cost、ads/Cloud/Other Bets を接続 | [S05] |
| Apple | Products/Services の gross margin mix を開示し、Services 高粗利が全体 margin に影響 | [S03] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 利益構造は segment operating income/margin を中心に観測できる | Microsoft, Alphabet, Netflix | direct | A |
| FCF は operating cash flow、Capex、working capital を通じて経営判断に関係する | Amazon | direct | A |
| 製品/サービス mix は gross margin と利益構造を大きく変える | Apple, Amazon, Microsoft | direct | A |

### Core Philosophy
利益構造は「利益率を上げる」ではなく、「どの価値単位がどの期間で cash と reinvestment capacity を生むか」を設計することである。Frontier 企業は短期 margin と長期投資を同じ portfolio 上で管理する。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | Revenue mix、gross margin、opex、capex、working capital、segment strategy、growth stage、risk |
| Decision Object | Margin target、segment profit role、reinvestment level、FCF/capital allocation rule |
| Criteria | Sustainable margin、growth trade-off、cash conversion、capital efficiency、strategic option value |
| Priorities | 1. Sustainable profitability、2. Reinvestment capacity、3. Segment-specific logic、4. FCF resilience |
| Prohibitions | 一律 margin target、growth と profit の未分離、Capex/working capital 無視 |
| Exceptions | 新規成長事業、AI/Cloud/Infrastructure 先行投資、規制/信頼投資 |
| Owners | CFO、CEO、Segment GM、FP&A、Capital Allocation Committee |
| Cadence | 月次 P&L review、四半期 segment review、年次 capital allocation |

### Operating Model
- 利益構造は product/service/segment/customer/maturity stage ごとに分ける。
- 営業利益率だけでなく gross margin, contribution margin, FCF, capex intensity を併記する。
- 新規投資には profit path と kill/scale criteria を設定する。

### Technical / Business Specification
- Profit Model Table: `segment`, `revenue stream`, `gross margin`, `opex`, `operating income`, `capex`, `working capital`, `FCF impact`, `strategic role`。
- Segment P&L は direct cost と allocated cost の区分を明記する。
- Profitability review は `current profit`, `future option`, `risk hedge`, `platform enabler` を分ける。

### Metrics
Gross margin、operating margin、segment operating income、contribution margin、FCF、FCF conversion、ROIC、capex/revenue、payback、cash conversion cycle、profit per customer/value unit。

### Failure Modes
- 利益率を一律に求め、成長事業や infrastructure-heavy 事業を誤評価する。
- 売上成長と利益成長の差分を revenue mix/cost mix に分解できない。
- FCF 悪化の原因が growth investment か inefficiency か分からない。

### Anti-patterns
- “黒字/赤字” だけで事業を評価する。
- セグメント利益を allocation で操作し、実態の unit economics を見ない。
- 短期 margin 改善のために顧客価値・技術基盤・信頼投資を削る。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 会社全体の利益だけを管理 |
| 1 | P&L | 基本 P&L を管理 |
| 2 | Segment Profit | セグメント別利益を管理 |
| 3 | Unit Profit | 顧客/価値単位別利益を管理 |
| 4 | Cash/Capital | FCF/Capex/ROIC と接続 |
| 5 | Portfolio Profit System | 成長・収益・option・risk を動的配分 |

### Clone Implementation Guide
1. セグメント別 P&L に gross margin、opex、capex、FCF impact を追加する。
2. 新規事業と成熟事業に別々の margin/cash hurdle を設定する。
3. 価格変更・原価施策・投資案件を profit model に通す。

### Confidence & Unknowns
- A: segment profit、gross margin、FCF の公開開示。
- B: profit role 分類は移植用合成仕様。
- Unknown: 内部 contribution margin、allocation rule、ROIC hurdle。

---

## 01.10 KPI設計

### Definition
経営・事業判断に使う指標を、どの定義、計算方法、所有者、利用場面、変更履歴、調整ルール、監査性で管理するかを決めるレイヤー。KPI は dashboard item ではなく、意思決定と説明責任の contract である。

### Frontier Exemplars / Standards

| Exemplar / Standard | 選定理由 | Evidence |
|---|---|---|
| IFRS Management Commentary | 重要な measures/indicators は経営者が performance/prospects 評価に使うもので、定義・変更説明・非 IFRS 調整を要求 | [S09] |
| SEC MD&A KPI Guidance | KPI/metrics の説明、定義、計算、利用理由、比較可能性への開示期待を示す | [S10] |
| Airbnb | Nights and Seats Booked、GBV、Adjusted EBITDA、FCF など主要 business metrics を定義 | [S07] |
| Amazon | FCF など non-GAAP measure の reconciliation と limitations を明示 | [S01] |
| Microsoft / Netflix / Alphabet | CODM が performance/resource allocation に使う指標を開示 | [S02][S05][S06] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| KPI は management-used であることが重要 | IFRS, SEC, Microsoft, Netflix | direct | A |
| KPI は定義、計算方法、変更、調整、限界を明示すべき | IFRS, SEC, Amazon, Airbnb | direct | A |
| KPI は目的・戦略・経済構造に接続しなければ管理行動を歪める | Cross-source synthesis | inferred | B |

### Core Philosophy
KPI は「測れるもの」ではなく「経営が意思決定に使い、投資家・社員・顧客に説明できるもの」である。Frontier では KPI dictionary が strategy、P&L、operating cadence の接続点になる。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 経営目的、事業目的、segment strategy、revenue/cost/profit model、顧客 lifecycle、リスク |
| Decision Object | KPI set、definition、calculation、owner、source of truth、review cadence、retirement rule |
| Criteria | Decision relevance、management-use、causality、comparability、auditability、leading/lagging balance |
| Priorities | 1. 意思決定に使う、2. 定義が一貫、3. 操作されにくい、4. 先行/遅行を組み合わせる |
| Prohibitions | vanity metrics、定義のない KPI、毎期変わる KPI、non-GAAP reconciliation なし |
| Exceptions | 新規事業では learning metric を使う。ただし revenue/profit path と紐づける |
| Owners | CFO/FP&A、Data/Analytics、Strategy、Segment GM、Accounting/Internal Audit |
| Cadence | 月次 KPI review、四半期 KPI governance、年次 KPI dictionary refresh |

### Operating Model
- KPI は `North-star / Driver / Guardrail / Diagnostic` に分類する。
- KPI 変更時は変更理由、旧定義との比較、影響範囲、owner approval を記録する。
- 非 GAAP/非 IFRS 指標や operational metric は、定義、計算式、reconciliation、limitations を記載する。

### Technical / Business Specification
- KPI Dictionary 必須列: `metric_name`, `purpose`, `definition`, `formula`, `source_system`, `owner`, `review_cadence`, `decision_use`, `segment/customer applicability`, `guardrail`, `change_log`, `confidence`。
- Dashboard は KPI dictionary から生成し、未登録 KPI を表示しない。
- KPI は OKR の KR と紐づくが、すべての KPI が OKR になるわけではない。

### Metrics
KPI definition coverage、dashboard-to-dictionary consistency、metric owner coverage、data freshness、metric change count、orphan KPI count、decision-use frequency、reconciliation completion、audit exception count。

### Failure Modes
- 指標数が増えすぎ、意思決定に使われない。
- 同じ KPI が部署ごとに異なる定義で使われる。
- 指標が goal 化され、顧客価値や利益構造を歪める。
- 非 GAAP/調整指標の説明が不足し、外部説明責任が弱い。

### Anti-patterns
- KPI を dashboard から逆算して作る。
- KPI owner がいない。
- KPI の変更履歴がなく、前年比較できない。
- OKR の KR に activity metric を置く。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 指標が散在 |
| 1 | Dashboard | dashboard はあるが定義が曖昧 |
| 2 | Dictionary | KPI 定義・所有者を登録 |
| 3 | Governance | 変更・reconciliation・review cadence を管理 |
| 4 | Decision Link | KPI が戦略/投資/事業レビューに直接使われる |
| 5 | Metric Operating System | KPI の有効性を継続検証し、歪みを検知 |

### Clone Implementation Guide
1. 既存 dashboard の全指標を棚卸しし、decision-use がないものを削除候補にする。
2. KPI dictionary を作成し、owner と source system を割り当てる。
3. North-star、driver、guardrail、diagnostic に分類する。
4. OKR の KR は KPI dictionary から選ぶ。

### Confidence & Unknowns
- A: IFRS/SEC/企業開示の KPI 仕様。
- B: KPI dictionary の運用仕様は合成だが、一次情報の要件と整合。
- Unknown: 各社の内部 metric review、data governance tooling。

---

## 01.11 OKR設計

### Definition
経営目的・事業戦略を、野心的な Objective と測定可能な Key Results に分解し、透明性、周期、採点、レビュー、学習を通じて組織を整列させるレイヤー。OKR はタスク管理でも人事評価でもなく、戦略実行と学習の cadence である。

### Frontier Exemplars / Standards

| Exemplar / Standard | 選定理由 | Evidence |
|---|---|---|
| Google re:Work | OKR を公開・測定可能・野心的・60–70% sweet spot・評価制度ではない仕組みとして説明 | [S12] |
| Atlassian | 1–3 objectives、3–5 key results、annual/quarterly/monthly cadence を推奨 | [S13] |
| IBM | Objectives を qualitative、Key Results を measurable outcomes とし、2–4 KR を推奨 | [S14] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| OKR は Objective と測定可能な Key Results を分ける | Google, Atlassian, IBM | direct | A |
| OKR は stretch goal として運用し、人事評価や task list と混同しない | Google | direct | A |
| 少数の objectives/KRs と定期レビューが運用上重要 | Atlassian, IBM, Google | direct | A |

### Core Philosophy
OKR は「達成率 100% を狙う予算目標」ではなく、戦略上の学習仮説を組織全体に公開し、進捗とズレを短周期で検出する仕組みである。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 経営目的、戦略優先順位、KPI dictionary、事業課題、リソース制約、前期 learning |
| Decision Object | Objective、Key Results、owner、cadence、scoring、review rule |
| Criteria | Strategic relevance、measurability、stretch、clarity、owner accountability、cross-team alignment |
| Priorities | 1. 少数集中、2. 測定可能な成果、3. 公開性、4. learning、5. 評価制度からの分離 |
| Prohibitions | task list、KPI の羅列、報酬評価との直結、too many OKRs、活動量 KR |
| Exceptions | Compliance/safety 目標は stretch ではなく 100% 達成の guardrail にする |
| Owners | CEO/Executive team、Strategy/People Ops、Team lead、KPI owner |
| Cadence | 年次 strategic OKR、四半期 team OKR、月次 check-in、四半期 grading/retro |

### Operating Model
- 年次で company OKR、四半期で business/team OKR を設定する。
- KR は KPI dictionary に登録済み metric を優先する。
- OKR grade は評価ではなく学習ログとし、未達時は原因を capability/resource/strategy/market に分類する。
- Compliance/safety/trust は OKR ではなく guardrail KPI として別管理する。

### Technical / Business Specification
- OKR Record 必須列: `objective`, `why_now`, `key_result`, `metric_source`, `baseline`, `target`, `owner`, `confidence`, `dependencies`, `check_in_cadence`, `score`, `learning`。
- Objective は 1 文、KR は 3–5 個以下、KR は outcome metric に限定する。
- scoring: 0.0–1.0。0.6–0.7 を stretch sweet spot として扱い、1.0 常態化は目標が保守的である signal とする。

### Metrics
OKR completion score、check-in completion、KR measurability rate、orphan OKR count、strategic priority coverage、cross-team dependency resolution、learning quality、KR sourced from KPI dictionary rate。

### Failure Modes
- OKR が業務タスク一覧になる。
- 100% 達成前提になり、挑戦的目標が消える。
- 人事評価と直結し、KR が保守的になる。
- KR の metric source が不明で、レビュー不能になる。

### Anti-patterns
- Objective が数値、KR が施策名。
- 全部署が 10 個以上の OKR を持つ。
- OKR と KPI が別体系で整合しない。
- 未達を punishment として扱う。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 目標が個人/部署別で不統一 |
| 1 | Goal List | 目標はあるが KR が活動指標 |
| 2 | OKR Format | Objective/KR 形式を導入 |
| 3 | Cadence | 四半期設定・月次 check-in・grading を実施 |
| 4 | Strategic Alignment | Company → business → team OKR が接続 |
| 5 | Learning System | OKR 結果から戦略・KPI・資源配分を更新 |

### Clone Implementation Guide
1. Company OKR を 3 個以下に絞る。
2. KR は KPI dictionary から選ぶ。
3. 人事評価と OKR score を分離する。
4. 四半期末に score だけでなく learning memo を必須化する。

### Confidence & Unknowns
- A: OKR の基本運用は Google/Atlassian/IBM の公式文書で確認。
- B: KPI dictionary との統合は 01.10 との合成仕様。
- Unknown: 各社の内部 OKR tooling、報酬制度との実際の分離度。

---

## 01.12 事業経済統合設計

### Definition
01.01–01.11 を単一の business economic equation に接続し、目的、顧客価値、市場、収益、価格、原価、利益、キャッシュ、KPI、OKR を一貫して運用するレイヤー。これは単なる財務モデルではなく、戦略実行の制御システムである。

### Frontier Exemplars

| Exemplar | 選定理由 | Evidence |
|---|---|---|
| Amazon | 顧客体験、価格、品揃え、原価、在庫、Capex、FCF を長期思考に接続 | [S01] |
| Microsoft | Mission、AI/cloud strategy、segment economics、CODM 指標、infrastructure investment を接続 | [S02] |
| Alphabet | Mission、AI full-stack、ads/Cloud/Other Bets、TAC、segment operating income、capex/commitments を接続 | [S05] |
| Costco | 顧客価値、会員制、低価格、限定 SKU、高回転、低粗利、更新率を一つの経済設計に接続 | [S04] |
| Netflix | 会員価値、価格、コンテンツ投資、revenue、operating margin を接続 | [S06] |

### Evidence Map

| Claim | Source | Directness | Confidence |
|---|---|---|---|
| 01.01–01.11 は個別ではなく、purpose-to-economics の連鎖として設計されるべき | Amazon, Microsoft, Costco | direct/inferred | B |
| Segment economics と KPI/OKR を接続しないと、戦略実行は dashboard と財務計画に分断される | Microsoft, Alphabet, IFRS/SEC | inferred | B |
| Capital-intensive strategy では P&L, FCF, Capex, contract commitments を統合して見る必要がある | Amazon, Microsoft, Alphabet | direct | A |

### Core Philosophy
企業戦略・事業経済設計の最終形は、目的から利益までを貫く `economic equation` である。Frontier では、全レイヤーが以下の式に接続される。

```text
Purpose
→ Customer / Job / Value Unit
→ Market / Segment Choice
→ Revenue Unit × Price Architecture
→ Cost Drivers + Capital Intensity
→ Gross Margin / Operating Margin / FCF
→ KPI Dictionary
→ OKR Cadence
→ Strategy / Resource Allocation Update
```

### Decision Model

| Field | Specification |
|---|---|
| Inputs | 01.01–01.11 の全成果物、P&L、Cash Flow、Capex、KPI dictionary、OKR score、market/customer data |
| Decision Object | 統合事業経済モデル、資源配分、成長/利益/投資トレードオフ、戦略更新 |
| Criteria | Purpose fit、customer value、segment economics、cash conversion、capital efficiency、risk/option balance |
| Priorities | 1. Traceability、2. Economic coherence、3. Decision velocity、4. Risk guardrails、5. Learning loop |
| Prohibitions | 目的・KPI・OKR・予算・P&L の分断、短期 revenue だけの最適化、Capex/FCF 無視 |
| Exceptions | 新規事業探索、規制・安全・信頼投資、戦略的防衛投資 |
| Owners | CEO、CFO、CSO、COO、Segment GM、Data/FP&A、Strategy Office |
| Cadence | 月次 operating review、四半期 business review、年次 strategy/capital allocation review |

### Operating Model
- 1 つの integrated operating review に、顧客・収益・価格・原価・利益・KPI・OKR を統合する。
- すべての重要戦略案件は business economic equation を持つ。
- OKR の review 結果は KPI dictionary と事業経済モデルに戻し、次四半期の資源配分に反映する。

### Technical / Business Specification

#### 統合モデルの必須コンポーネント

| Component | Required Fields |
|---|---|
| Purpose Link | purpose element, strategic priority, owner |
| Customer Economics | customer segment, value unit, retention, trust/safety, cost-to-serve |
| Market Economics | market/category/geography, TAM/SAM, entry thesis, local price/cost |
| Revenue Model | stream, recognition, growth driver, leading metric |
| Pricing Model | tier/fee, discount, contract, price-change rule |
| Cost Model | variable, fixed, capex, working capital, quality guardrail |
| Profit Model | gross margin, operating margin, segment income, FCF, ROIC |
| KPI Governance | metric definition, owner, source, reconciliation, change log |
| OKR Cadence | objective, KR, baseline, target, score, learning |
| Risk/Exception | strategic risk, trust/safety, regulatory, capacity, exit criteria |

#### Minimum Business Economic Equation

```text
Segment Profitability =
  Σ(Customer Cohort × Value Unit Volume × Realized Price × Revenue Recognition)
- Σ(Value Unit Volume × Variable Cost)
- Allocated Fixed Operating Cost
- Strategic Investment / Opex
± Working Capital / Cash Timing Effects
- Required Capital / Depreciation or Amortization Effects
```

#### Minimum Review Questions

1. 目的と事業目的はまだ有効か。
2. 顧客価値単位は成長しているか。
3. 収益成長は price / volume / mix / retention / FX のどれか。
4. 原価増は顧客価値投資か、非効率か。
5. 利益率低下は戦略的投資か、構造劣化か。
6. KPI は実際に意思決定に使われたか。
7. OKR 未達は market、strategy、execution、capability、resource のどれか。
8. 次四半期に資源配分を変えるべきか。

### Metrics
Purpose-to-KPI traceability、strategic initiative ROI、segment growth/margin/FCF、customer value unit growth、revenue mix quality、gross margin variance、unit cost variance、Capex efficiency、OKR learning quality、resource reallocation rate、guardrail breach count。

### Failure Modes
- 事業計画、KPI、OKR、予算が別々に作られ、相互矛盾する。
- 成長率だけを評価し、原価/Capex/FCF を無視する。
- OKR が戦略学習に戻らず、四半期ごとの儀式になる。
- セグメント P&L があるが、顧客価値単位や pricing unit と接続していない。

### Anti-patterns
- 統合モデルを CFO だけが管理し、事業責任者が使わない。
- KPI dictionary なしに OKR を作る。
- 戦略案件の approval が narrative だけで、economic equation がない。
- 例外投資に期限・仮説・学習指標・撤退条件がない。

### Maturity Model
| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | 戦略、予算、KPI、OKR が分断 |
| 1 | 財務計画 | P&L はあるが purpose/customer linkage がない |
| 2 | Layer 接続 | 01.01–01.11 の成果物を個別作成 |
| 3 | Integrated Review | 顧客・収益・原価・利益・KPI/OKR を同じ会議でレビュー |
| 4 | Dynamic Allocation | KPI/OKR 学習に基づき資源配分を変更 |
| 5 | Frontier Operating System | 目的・市場・顧客・経済性・資源配分が継続的に自己補正 |

### Clone Implementation Guide
1. 01.01–01.11 の成果物を 1 枚の economic equation map に統合する。
2. 各 strategic initiative に business economic equation を添付する。
3. QBR を `customer → revenue → price → cost → profit → KPI → OKR → allocation` の順に再設計する。
4. OKR score と KPI variance を、翌四半期の資源配分ルールに接続する。

### Confidence & Unknowns
- A: P&L/segment/FCF/capex/metric の公開証拠。
- B: 統合モデルは複数 exemplar の合成仕様。
- Unknown: 各社の内部 integrated operating review、allocation algorithm、OKR-to-budget linkage。

---

## 7. 統合 Implementation Guide

### 7.1 30/60/90 Day Plan

| Phase | Goal | Actions | Deliverables |
|---|---|---|---|
| 0–30 days | Baseline | 01 の layer registry を作成。既存 mission、戦略、顧客、収益、価格、原価、利益、KPI、OKR 文書を棚卸し | Current-state map, source catalog, KPI inventory |
| 31–60 days | Economic Model | 事業別に value unit、revenue unit、cost driver、profit model を定義。KPI dictionary v1 を作成 | Revenue/cost/profit model, KPI dictionary, segment scorecard |
| 61–90 days | Operating Cadence | QBR/MBR を統合レビューに変更。OKR を KPI dictionary に接続。価格/投資/撤退 approval memo を標準化 | Integrated operating review, OKR board, approval templates |

### 7.2 Required Roles

| Role | Responsibility |
|---|---|
| CEO | Purpose、strategic priorities、trade-off の最終所有者 |
| CFO / FP&A | revenue/cost/profit/cash/KPI governance の所有者 |
| CSO / Strategy Office | layer registry、portfolio strategy、market strategy、resource allocation synthesis |
| Segment GM | 事業目的、顧客価値、segment P&L、OKR の owner |
| Product / Pricing Lead | value unit、pricing architecture、customer experience economics |
| Data / Analytics | KPI dictionary、source of truth、dashboard governance |
| People / Strategy Ops | OKR cadence、transparency、grading/learning process |

### 7.3 Governance Artifacts

1. Purpose-to-Economics Map
2. Segment Strategy Sheet
3. Market Entry / Exit Memo
4. Customer Economics Sheet
5. Revenue Model Table
6. Pricing Architecture Document
7. Cost Driver Map
8. Segment Profit / FCF Model
9. KPI Dictionary
10. OKR Board and Learning Log
11. Integrated QBR Pack
12. Capital Allocation Decision Memo

---

## 8. Validation Queries

以下は、再調査・反証・鮮度確認のための検索クエリ束である。

```text
# 10-K / Annual Report / MD&A
site:sec.gov/Archives/edgar "10-K" "business" "segments" "operating income" "free cash flow"
site:sec.gov/Archives/edgar "10-K" "risk factors" "pricing" "gross margin"
site:sec.gov/Archives/edgar "10-K" "key business metrics" "gross booking value"
site:sec.gov/Archives/edgar "10-K" "membership fee revenue" "renewal rate"
site:sec.gov/Archives/edgar "10-K" "traffic acquisition costs" "operating income"

# Company canonical
site:ir.aboutamazon.com "annual report" "free cash flow" "customer"
site:microsoft.com/investor "annual report" "segment" "operating income" "AI"
site:abc.xyz/investor "annual report" "traffic acquisition costs" "Google Cloud"
site:investor.netflix.net "10-K" "operating margin" "monthly membership fees"
site:investor.airbnb.com "10-K" "gross booking value" "nights and seats booked"
site:investor.costco.com "10-K" "membership fee revenue" "renewal rate"

# KPI / OKR normative
site:sec.gov "MD&A" "key performance indicators" "metrics"
site:ifrs.org "management commentary" "performance measures" "indicators"
site:rework.withgoogle.com "OKRs" "60" "70" "grade"
site:atlassian.com "OKR" "key results" "monthly"
site:ibm.com "OKRs" "objectives" "key results"

# Failure / contradiction
"Amazon" "free cash flow" "capital expenditures" "risk factors"
"Costco" "low gross margin" "membership renewal" "risk factors"
"Netflix" "operating margin" "content amortization" "risk factors"
"Airbnb" "trust and safety" "friction" "risk factors"
"Alphabet" "traffic acquisition costs" "operating margin" "risk factors"
"OKR" "performance evaluation" "anti-pattern"
```

---

## 9. QA Report

| Check | Result | Notes |
|---|---|---|
| Coverage | Pass | 01 すべてに Clone Spec を作成 |
| T1/T0/T2 Evidence | Pass | 企業レイヤーは 10-K/Annual Report、KPI/OKR は IFRS/SEC/公式ガイドで補強 |
| Critical Claims | Pass with caveat | 中核 claim は A/B。内部運用の詳細は Unknown に隔離 |
| Recency | Pass | 2025/2026 期の公開開示を中心に使用 |
| Exceptions | Partial | 公開情報上の例外は限定的。内部 exception approval は Unknown |
| Failure Modes | Pass | 各レイヤーに failure modes と anti-patterns を記載 |
| Provenance | Pass | Source Catalog と Evidence Map を付与 |
| Output Integrity | Pass | Clone Spec 必須要素を圧縮形式で網羅 |

---

## 10. Source Catalog

| Source ID | Entity | Title / Type | Tier | Key facts used | Locator |
|---|---|---|---|---|---|
| S01 | Amazon | 2025 Form 10-K / SEC filing | T1 | customer-centric purpose, principles, segments, customer groups, FCF focus, variable/fixed costs, net sales by segment, FCF reconciliation | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm |
| S02 | Microsoft | 2025 Annual Report | T1 | mission, AI/cloud strategy, three ambitions, reportable segments, segment revenue/operating income, CODM resource allocation, AI infrastructure margin pressure | https://www.microsoft.com/investor/reports/ar25/index.html |
| S03 | Apple | 2025 Form 10-K / SEC filing | T1 | integrated products/services, geographic management, competitive factors, product/service gross margin, services revenue growth | https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm |
| S04 | Costco | 2025 Form 10-K / SEC filing | T1 | membership warehouse model, low prices, limited selection, high volume, rapid inventory turnover, membership fee revenue, renewal rates, gross margin | https://www.sec.gov/Archives/edgar/data/909832/000090983225000101/cost-20250831.htm |
| S05 | Alphabet | 2025 Form 10-K / SEC filing | T1 | mission, AI full-stack, advertising revenue dependence, TAC, Google Services/Cloud/Other Bets, segment operating income, capex/commitments | https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm |
| S06 | Netflix | 2025 Form 10-K / SEC filing | T1/T2 | monthly membership fees, pricing ranges, advertising-supported plans, revenue and operating margin focus, content amortization, single operating segment | https://www.sec.gov/Archives/edgar/data/1065280/000106528026000034/nflx-20251231.htm |
| S07 | Airbnb | 2025 Form 10-K / SEC filing | T1/T2 | two-sided marketplace, hosts/guests, Nights and Seats Booked, GBV, service fees, trust/safety/fraud friction, adjusted metrics | https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm |
| S08 | Salesforce | FY2026 investor release / SEC filing | T1/T2 | subscription/support revenue, RPO/cRPO, recurring-revenue management caveats | https://investor.salesforce.com/news/news-details/2026/Salesforce-Delivers-Record-Fourth-Quarter-Fiscal-2026-Results/default.aspx |
| S09 | IFRS Foundation | Management Commentary Practice Statement / IFRS source | T0 | performance measures should reflect critical success factors, management-used indicators, definition/change/reconciliation expectations | https://www.ifrs.org/content/dam/ifrs/publications/html-standards/english/2023/issued/ps1.html |
| S10 | U.S. SEC | Commission Guidance on MD&A and Key Performance Indicators | T0/T1 | KPI/metrics disclosure guidance for MD&A, definitions, calculation, usefulness, comparability | https://www.sec.gov/rules-regulations/2020/01/commission-guidance-managements-discussion-analysis-financial-condition-results-operations |
| S11 | COSO | Enterprise Risk Management—Integrating with Strategy and Performance | T0 | strategy/performance/risk integration and mission/vision/strategic goals connection | https://www.coso.org/guidance-erm |
| S12 | Google re:Work | Set goals with OKRs | T3 | ambitious objectives, measurable KRs, transparency, 60–70% sweet spot, grades as data, not performance evaluation | https://rework.withgoogle.com/intl/en/guides/set-goals-with-okrs |
| S13 | Atlassian | OKRs Play | T3 | 1–3 objectives, 3–5 key results, monthly/quarterly/annual cadence | https://www.atlassian.com/team-playbook/plays/okrs |
| S14 | IBM | What are OKRs? | T3 | qualitative objectives, measurable key results, recommended KR count, avoid activity-based KRs | https://www.ibm.com/think/topics/okrs |

---

## 11. Machine-Readable Layer Registry Capsule

```yaml
layer_registry:
  - layer_id: "01.01"
    layer_name_ja: "経営目的"
    cluster: "企業戦略・事業経済設計"
    decision_object: "企業が守る価値創出原則と経済トレードオフ"
    owner_roles: [CEO, CFO, CSO, Board]
    default_metrics: [purpose_to_kpi_traceability, customer_trust, segment_operating_income, FCF]
  - layer_id: "01.02"
    layer_name_ja: "事業目的"
    decision_object: "顧客群・Job・価値単位・収益単位"
    owner_roles: [Segment GM, Product GM, Revenue Lead]
    default_metrics: [value_unit_growth, retention, revenue_per_value_unit, gross_margin_per_value_unit]
  - layer_id: "01.03"
    layer_name_ja: "事業戦略"
    decision_object: "事業ポートフォリオと資源配分"
    owner_roles: [CEO, CFO, CSO, Segment GM]
    default_metrics: [segment_revenue_growth, segment_operating_income, capital_intensity, option_milestones]
  - layer_id: "01.04"
    layer_name_ja: "市場戦略"
    decision_object: "市場・地域・カテゴリ・チャネル優先順位"
    owner_roles: [CSO, Regional GM, Product Market Lead]
    default_metrics: [market_revenue_growth, market_gross_margin, CAC_payback, market_operating_income]
  - layer_id: "01.05"
    layer_name_ja: "顧客戦略"
    decision_object: "顧客群別の獲得・維持・信頼・体験設計"
    owner_roles: [Customer Officer, Revenue Lead, Product Lead, Trust Safety]
    default_metrics: [retention, renewal_rate, LTV_CAC, trust_incidents, cost_to_serve]
  - layer_id: "01.06"
    layer_name_ja: "収益構造"
    decision_object: "収益源・認識・ミックス・成長 driver"
    owner_roles: [CFO, Revenue Ops, Accounting, Segment GM]
    default_metrics: [revenue_growth, revenue_mix, ARR_MRR, GBV, RPO, gross_margin_by_stream]
  - layer_id: "01.07"
    layer_name_ja: "価格構造"
    decision_object: "価格階層・手数料・割引・契約・価格変更ルール"
    owner_roles: [Pricing Lead, CFO, Product, Sales]
    default_metrics: [ARPU, price_realization, discount_rate, churn_after_price_change, gross_margin_by_tier]
  - layer_id: "01.08"
    layer_name_ja: "原価構造"
    decision_object: "変動費・固定費・資本費・運転資本の driver map"
    owner_roles: [CFO, COO, CTO, Supply Chain, FP&A]
    default_metrics: [unit_cost, gross_margin, TAC_rate, content_amortization, capex_revenue, FCF_conversion]
  - layer_id: "01.09"
    layer_name_ja: "利益構造"
    decision_object: "margin・segment profit・FCF・資本効率の設計"
    owner_roles: [CFO, CEO, Segment GM, FP&A]
    default_metrics: [operating_margin, segment_operating_income, contribution_margin, FCF, ROIC]
  - layer_id: "01.10"
    layer_name_ja: "KPI設計"
    decision_object: "指標の定義・計算・所有者・利用場面・変更統制"
    owner_roles: [CFO, FP&A, Data Analytics, Internal Audit]
    default_metrics: [definition_coverage, source_consistency, owner_coverage, orphan_kpi_count]
  - layer_id: "01.11"
    layer_name_ja: "OKR設計"
    decision_object: "Objective・Key Results・scoring・cadence・learning"
    owner_roles: [Executive Team, Strategy Ops, People Ops, Team Leads]
    default_metrics: [okr_score, checkin_completion, kr_measurability, learning_quality]
  - layer_id: "01.12"
    layer_name_ja: "事業経済統合設計"
    decision_object: "PurposeからOKRまでの統合 business economic equation"
    owner_roles: [CEO, CFO, CSO, COO, Segment GM]
    default_metrics: [purpose_to_kpi_traceability, segment_FCF, resource_reallocation_rate, guardrail_breach_count]
```

---

## 12. Notes on Limitations

- 本レポートは公開情報限定で作成しており、非公開の board materials、pricing committee、internal OKR system、customer cohort data、unit economics detail は対象外である。
- 企業の 10-K/Annual Report は企業自身の開示であり、内部意思決定プロセスのすべてを直接示すものではない。したがって、内部運用・承認権限・具体閾値は Unknown として隔離した。
- 価格・原価・KPI の詳細は企業によって開示粒度が異なる。抽象化された Clone Spec は移植用モデルであり、個社ベンチマークの完全な複製ではない。
- 2026-05-13 時点で確認できた公開情報を用いた。今後の 10-K、年次報告、価格表、公式 KPI/OKR ガイド更新により再検証が必要である。
