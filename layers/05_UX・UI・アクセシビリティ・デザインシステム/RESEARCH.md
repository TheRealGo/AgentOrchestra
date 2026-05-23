# Frontier Operating Model Research: UX・UI・アクセシビリティ・デザインシステム（05）

Generated: 2026-05-13 JST  
Scope: 05 / UX設計・情報設計・画面遷移・UI・インタラクション・アクセシビリティ・多言語化・デザインシステム・コンポーネント・スタイル  
Method: `RESEARCH.md` の実行プロトコルに従い、公開情報のみを対象に、標準・公式設計ガイド・公式デザインシステム・公式法規制/政策資料・公開コミュニティ仕様を横断した。主要 claim は A/B 信頼度を中核にし、C/D は unknowns に分離した。

---

## 0. 調査方針

このクラスターは、単なる画面制作ではなく「ユーザーが目的を達成できる状態を、どの証拠・制約・標準・再利用資産で継続的に保証するか」を決める意思決定システムである。したがって、候補は有名度ではなく、公開成果物の厚み、標準性、運用可能性、アクセシビリティの検証可能性、コンポーネント/トークン化の再現性で評価した。

本レポートのソース階層は次の通り。

- **T0 規範的一次情報**: WCAG 2.2、WAI-ARIA、Using ARIA、W3C i18n、DTCG 2025.10、ISO 9241-210/11。
- **T2 実行可能成果物**: GOV.UK Design System、USWDS、Carbon、Fluent、Material Design、Apple HIG、Polaris 等のコンポーネント/トークン/コード/ガイド。
- **T3 公式運用文書**: GOV.UK Service Manual、USWDS accessibility process、GOV.UK pattern contribution、Carbon accessibility guidance。
- **T4/T5 履歴・外部検証**: EU/US accessibility regulation、Section 508、EN 301 549、Design Tokens CG stable release、Open UI CG。
- **T6 補助**: NN/g usability heuristics、IA/tree testing 等。T6 は実務パターンの補助根拠として使用し、単独で中核 claim にはしない。

---

## 1. Layer Registry

| Layer ID | Layer Name | Decision Object | Decision Question | 主な出力成果物 | Owner Roles | 主要 Metrics |
|---|---|---|---|---|---|---|
| 05.01 | UX設計 | ユーザー目標・業務目標・利用文脈を統合した体験仮説と検証計画 | どのユーザー/状況/目的に対し、どのタスク成功条件・検証方法・改善サイクルで体験を成立させるか | UX principles, journey map, research plan, prototype, usability report, success metrics | Head of UX, Product Designer, User Researcher, Product Manager | task success, time-on-task, error rate, satisfaction, support contact rate |
| 05.02 | 情報設計 | 情報・機能・コンテンツの分類、階層、ラベル、導線 | どの情報構造なら、利用者が迷わず発見・理解・完了できるか | IA map, taxonomy, navigation model, content model, tree/card-sort results | Information Architect, Content Designer, UX Researcher | findability, tree-test success, search success, navigation abandonment |
| 05.03 | 画面遷移 | 画面/状態/タスクステップ間の遷移、戻る/中断/再開、進捗、焦点移動 | どの状態遷移なら、利用者が現在地・次アクション・完了条件を常に理解できるか | flow diagram, state machine, transition rules, progress model, focus rules | UX Designer, Interaction Designer, Frontend Lead | funnel completion, focus loss defects, backtrack rate, abandonment |
| 05.04 | UI設計 | 画面上の情報密度、レイアウト、視覚階層、コントロール配置、レスポンシブ挙動 | どのUI構造・視覚規則・標準コンポーネントで認知負荷を下げ、一貫性を保つか | wireframe, high-fidelity UI, responsive layout, visual hierarchy spec | Product Designer, UI Designer, Design System Designer | component reuse, design QA pass, contrast pass, visual consistency |
| 05.05 | インタラクション設計 | 入力、フィードバック、状態、エラー、キーボード/タッチ/支援技術操作 | どの操作モデルなら、全入力モードで安全・予測可能・可逆にタスクを実行できるか | interaction spec, event/state matrix, keyboard map, error/undo rules | Interaction Designer, Frontend Engineer, Accessibility Specialist | keyboard coverage, interaction defects, error recovery success, latency |
| 05.06 | アクセシビリティ | 法規制・標準・支援技術・利用者多様性を満たす製品品質ゲート | どのアクセシビリティ基準を採用し、どの検査・責任・例外管理で継続的に保証するか | accessibility policy, WCAG matrix, ACR/VPAT, audit report, remediation backlog | Accessibility Lead, QA Lead, Design System Owner, Legal/Compliance | WCAG pass, critical a11y defects, screen reader pass, keyboard pass, audit SLA |
| 05.07 | 多言語化・国際化 | 言語、文字、方向、地域形式、翻訳、文化差に耐えるUI/コンテンツ構造 | どのi18n/l10nアーキテクチャなら、言語追加時にレイアウト・意味・操作が破綻しないか | locale matrix, string inventory, translation workflow, RTL spec, formatting rules | Localization PM, Content Designer, Frontend Engineer, i18n Lead | untranslated strings, RTL defects, locale formatting defects, release lag |
| 05.08 | デザインシステム | 再利用可能な原則・コンポーネント・トークン・ガイド・コード・運用統治 | 何を共通資産化し、どの採用/貢献/版管理/品質ゲートでプロダクト群へ配布するか | design system site, contribution model, roadmap, release notes, governance rules | Design System Lead, DesignOps, Frontend Platform Lead | adoption, duplicate components, contribution lead time, breaking changes |
| 05.09 | コンポーネント設計 | UI部品の anatomy、状態、props/API、アクセシビリティ、テスト、使用条件 | どのコンポーネント契約なら、再利用しても挙動・見た目・アクセシビリティが崩れないか | component spec, Storybook, prop table, state matrix, a11y test cases | Component Designer, Frontend Engineer, Accessibility Engineer | component coverage, a11y pass per component, prop misuse, visual regression |
| 05.10 | スタイル・トークン設計 | 色、タイポグラフィ、余白、形状、影、モーション、テーマの値体系 | どのトークン階層・命名・変換・テーマ規則で、ブランドと可用性を全プラットフォームへ同期するか | token files, theme definitions, style dictionary, typography/color/spacing scales | Design Token Owner, Brand Designer, Frontend Platform Engineer | hard-coded value count, token adoption, contrast violations, theme drift |

---

## 2. Source Catalog

| ID | Entity | Source | Tier | Evidence Type | Relevance |
|---|---|---|---|---|---|
| S01 | User-provided `RESEARCH.md` | Frontier Operating Model Research 運用プレイブック | T0 internal instruction | research protocol | Clone Spec fields, evidence model, confidence model, QA method |
| S02 | ISO | ISO 9241-210:2019 Human-centred design for interactive systems — https://www.iso.org/standard/77520.html | T0 | standard | HCD lifecycle requirements/recommendations; current confirmed version |
| S03 | ISO | ISO 9241-11:2018 Usability: Definitions and concepts — https://www.iso.org/standard/63500.html | T0 | standard | Usability as outcome of use; design/evaluation framework |
| S04 | W3C/WAI | WCAG 2.2 — https://www.w3.org/TR/WCAG22/ | T0 | standard | Accessibility success criteria; conformance basis |
| S05 | W3C/WAI | WCAG 2 Overview — https://www.w3.org/WAI/standards-guidelines/wcag/ | T0 | standard overview | Four principles, levels A/AA/AAA, latest WCAG chronology |
| S06 | W3C/WAI | What’s New in WCAG 2.2 — https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/ | T0 | standard update | New success criteria: focus, drag, target size, help, redundant entry, auth |
| S07 | W3C/WAI | WAI-ARIA 1.2 — https://www.w3.org/TR/wai-aria-1.2/ | T0 | technical spec | Roles/states/properties for advanced/custom UI |
| S08 | W3C/WAI | ARIA Authoring Practices Guide — https://www.w3.org/WAI/ARIA/apg/ | T0/T3 | patterns/examples | Accessible widget patterns, keyboard behavior, examples |
| S09 | W3C/WAI | Using ARIA — https://www.w3.org/TR/using-aria/ | T0/T3 | guidance | Native HTML first, keyboard operability, no hidden focusable controls |
| S10 | W3C/WAI | ARIA in HTML — https://www.w3.org/TR/html-aria/ | T0 | technical spec | ARIA/HTML conformance and native semantics constraints |
| S11 | W3C i18n | Internationalization techniques for authoring HTML — https://www.w3.org/International/techniques/authoring-html | T0 | guidance | Encoding, language, direction, authoring techniques |
| S12 | W3C i18n | Internationalization Quick Tips — https://www.w3.org/International/quicktips/ | T0/T3 | guidance | Directionality, validation, international web design concepts |
| S13 | W3C i18n | About W3C Internationalization — https://www.w3.org/International/i18n-drafts/nav/about | T0/T3 | guidance | i18n requirements and techniques resources |
| S14 | W3C/WAI | Making Content Usable for People with Cognitive and Learning Disabilities — https://www.w3.org/TR/coga-usable/ | T0/T3 | supplemental guidance | Cognitive accessibility patterns beyond WCAG conformance |
| S15 | UK Government | GOV.UK Service Standard — https://www.gov.uk/service-manual/service-standard | T3 | official operating standard | Understand users, simple service, common components/patterns |
| S16 | UK Government | GOV.UK User Research — https://www.gov.uk/service-manual/user-research | T3 | operating guide | Research planning, phases, recruitment, methods |
| S17 | UK Government | GOV.UK Design System — https://design-system.service.gov.uk/ | T2/T3 | design system | Styles, components, patterns, governance, roadmap, release notes |
| S18 | UK Government | GOV.UK Using/adapting/creating patterns — https://www.gov.uk/service-manual/design/using-adapting-and-creating-patterns | T3 | operating guide | Evidence-based patterns; contribute findings back |
| S19 | UK Government | GOV.UK Writing for user interfaces — https://www.gov.uk/service-manual/design/writing-for-user-interfaces | T3 | content/UI guidance | Accessible link text, labels/legends, headings, microcopy |
| S20 | US Government | USWDS home — https://designsystem.digital.gov/ | T2/T3 | design system | Federal design system; components, patterns, tokens |
| S21 | US Government | USWDS Design Tokens — https://designsystem.digital.gov/design-tokens/ | T2/T3 | token guidance | Tokenized palettes and helper functions/mixins |
| S22 | US Government | USWDS Accessibility — https://designsystem.digital.gov/documentation/accessibility/ | T2/T3 | operating guide | Component testing with screen readers, keyboard, zoom, aXe/pa11y, audits |
| S23 | Section508.gov | Accessible Design Using USWDS — https://www.section508.gov/develop/accessible-design-using-uswds/ | T3/T5 | government guidance | Accessible/mobile-friendly government websites; compliance from start |
| S24 | IBM | Carbon Design System — https://carbondesignsystem.com/ | T2/T3 | design system | Open source code, design tools, resources, HIG, community |
| S25 | IBM | Carbon Accessibility — https://carbondesignsystem.com/guidelines/accessibility/overview/ | T2/T3 | accessibility guidance | WCAG AA, Section 508, European standards basis; screen reader testing |
| S26 | IBM | Carbon Spacing — https://carbondesignsystem.com/elements/spacing/overview/ | T2 | token spec | 2/4/8 spacing scale, tokens, stack/layout rules |
| S27 | IBM | Carbon Color Tokens — https://carbondesignsystem.com/elements/color/tokens/ | T2 | token spec | Core/component color tokens, semantic roles, focus/support tokens |
| S28 | Microsoft | Fluent 2 Design Tokens — https://fluent2.microsoft.design/design-tokens | T2 | token spec | Global/alias tokens, theming, high-contrast/dark/light support |
| S29 | Microsoft | Fluent UI — https://developer.microsoft.com/en-us/fluentui | T2 | component library | Open source components with accessibility, i18n, performance included |
| S30 | Google | Material Design 3 — https://m3.material.io/ | T2 | design system | Guidelines, components, tools, Material 3 / M3 Expressive |
| S31 | Google | Material 3 Design Tokens — https://m3.material.io/foundations/design-tokens | T2 | token guidance | UI building blocks and systematic design values |
| S32 | Google | Material 3 Transitions — https://m3.material.io/styles/motion/transitions | T2 | motion guidance | Transition patterns for motion implementation |
| S33 | Apple | Human Interface Guidelines — https://developer.apple.com/design/human-interface-guidelines | T2/T3 | platform guide | Apple platform design guidance/best practices |
| S34 | Apple | HIG Accessibility — https://developer.apple.com/design/human-interface-guidelines/accessibility | T2/T3 | accessibility guide | Accessible interface guidance across Apple apps/games |
| S35 | DTCG | Design Tokens Technical Reports 2025.10 — https://www.designtokens.org/tr/2025.10/ | T0/T4 | community specification | Token definition, candidate recommendation, implementation intent |
| S36 | DTCG | Stable version announcement 2025.10 — https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/ | T4 | release/status | Vendor-neutral, production-ready token format; theming, multi-brand, interoperability |
| S37 | Open UI | Open UI Home — https://open-ui.org/ | T0/T4 | community spec/research | Component anatomy, states, behaviors, accessibility requirements |
| S38 | W3C | Open UI Community Group — https://www.w3.org/community/open-ui/ | T4 | community group | Interoperability for design systems/frameworks/web platform |
| S39 | DOJ/ADA.gov | ADA Title II web/mobile rule fact sheet — https://www.ada.gov/resources/2024-03-08-web-rule/ | T1/T5 | regulation/guidance | US public entity web/app accessibility requirements and updated compliance dates |
| S40 | European Commission | European Accessibility Act — https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-accessibility-act-eaa_en | T1/T5 | regulation overview | EU-wide accessibility requirements for selected products/services |
| S41 | AccessibleEU | EAA effective date — https://accessible-eu-centre.ec.europa.eu/content-corner/news/eaa-comes-effect-june-2025-are-you-ready-2025-01-31_en | T5 | regulation timing | EAA approved in 2019; came into effect 2025-06-28 |
| S42 | Section508.gov | Applicability & Conformance — https://www.section508.gov/develop/applicability-conformance/ | T1/T5 | compliance guidance | Revised 508 and WCAG 2.0 A/AA conformance constraints |
| S43 | European Commission | EN 301 549 standards/harmonisation — https://digital-strategy.ec.europa.eu/en/policies/web-accessibility-directive-standards-and-harmonisation | T1/T5 | compliance guidance | EN 301 549 v3.2.1 based on WCAG 2.1; WCAG 2.2 not automatically legal baseline |
| S44 | Nielsen Norman Group | 10 Usability Heuristics — https://www.nngroup.com/articles/ten-usability-heuristics/ | T6 | heuristic guidance | Visibility, real-world match, control, consistency, error prevention |
| S45 | Nielsen Norman Group | IA Study Guide — https://www.nngroup.com/articles/ia-study-guide/ | T6 | research guide | IA, navigation, card sorting/tree testing resources |
| S46 | Nielsen Norman Group | Tree testing — https://www.nngroup.com/videos/tree-testing/ | T6 | research method | Tree testing as IA/navigation evaluation method |

---

## 3. Frontier Candidate Scores

Scale: Performance 25 / Adoption 15 / Artifact Richness 20 / Peer Validation 15 / Recency 10 / Transferability 10 / Failure Evidence 5. Scores are normalized to 100 and based only on public evidence.

| Candidate | Relevant Layers | Score | Why it is frontier-grade | Main Limitations |
|---|---:|---:|---|---|
| W3C/WAI WCAG 2.2 + WAI-ARIA + APG | 05.05, 05.06, 05.09 | 96 | Normative accessibility standard, testable success criteria, ARIA semantics, widget examples, broad policy reuse | WCAG conformance alone does not cover every user need; ARIA misuse can create failures |
| ISO 9241-210/11 | 05.01 | 91 | Current ISO standards for HCD and usability; defines design/evaluation framing | Paywalled full text; method details are abstract |
| GOV.UK Service Manual + Design System | 05.01, 05.02, 05.03, 05.08, 05.09 | 94 | Public service standard, user research, evidence-based patterns, accessible components, contribution model, latest release notes | UK public-service context; some service-specific policy dependencies |
| USWDS | 05.04, 05.06, 05.08, 05.09, 05.10 | 91 | Federal design system with components, patterns, tokens, explicit accessibility testing process | US government context; legal baselines differ from commercial/global products |
| IBM Carbon | 05.04, 05.06, 05.08, 05.09, 05.10 | 89 | Open-source system with design tools, code libraries, accessibility checklist, tokenized spacing/color | Enterprise/B2B bias; some ecosystem content depends on IBM product context |
| Microsoft Fluent 2 / Fluent UI | 05.04, 05.05, 05.08, 05.09, 05.10 | 85 | Tokens, theming, high contrast/dark/light support, open-source components with accessibility/i18n claims | Public docs reveal less governance detail than GOV.UK/USWDS |
| Material Design 3 | 05.03, 05.04, 05.05, 05.08, 05.10 | 85 | Broad adoption, open-source code, adaptive components, motion/transitions/tokens | JS-heavy docs; platform-specific implementation details require Android/Web docs |
| Apple Human Interface Guidelines | 05.03, 05.04, 05.05, 05.06, 05.07 | 82 | Platform-native interface conventions, accessibility and component guidance | Less open source; parsed public evidence is thinner |
| DTCG Design Tokens 2025.10 | 05.08, 05.10 | 83 | First stable vendor-neutral token format, cross-tool interoperability, theming/multi-brand/color support | Community spec, not W3C Recommendation; implementation ecosystem still maturing |
| Open UI | 05.09 | 78 | Component anatomy/states/behavior/accessibility research for web-platform interoperability | Community group, not final web standard; frontier as direction-setting evidence |
| NN/g heuristics / IA / tree testing | 05.01, 05.02, 05.05 | 76 | Widely adopted UX heuristics and IA research methods | T6補助。標準・公式運用文書での裏取りが必要 |

---

## 4. Cluster Evidence Graph Summary

| Claim ID | Claim | Evidence | Confidence | Notes |
|---|---|---|---|---|
| C-UX-01 | UX quality should be managed as an outcome of use, not as subjective “ease of use” alone. | S02, S03, S15, S16 | A | ISO 9241-11 frames usability as outcome; GOV.UK requires user-needs research and testing. |
| C-UX-02 | Frontier UX processes use frequent user research, prototypes, and shared findings to drive product decisions. | S15, S16, S18, S44 | B | Direct GOV.UK evidence plus heuristic support. |
| C-IA-01 | IA must separate underlying structure from visible navigation and validate with user research such as card sorting/tree testing. | S15, S16, S45, S46 | B | Strong practice pattern; T6 method backed by official research process. |
| C-FLOW-01 | Screen transitions should preserve orientation, progress, reversibility, and focus visibility. | S04, S06, S08, S32, S44 | A/B | Accessibility and usability evidence converge. |
| C-INT-01 | Custom interactive controls require semantic roles/states/properties plus keyboard-equivalent behavior. | S07, S08, S09, S10 | A | Direct W3C evidence. |
| C-A11Y-01 | WCAG 2.2 is the recommended current technical baseline, but legal baselines differ by jurisdiction. | S04, S05, S39, S40, S41, S42, S43 | A | W3C recommends current WCAG; Section 508/EN 301 549/ADA/EAA vary. |
| C-I18N-01 | Internationalization must be designed into authoring, encoding, language, directionality, and validation from the start. | S11, S12, S13 | A | Direct W3C i18n evidence. |
| C-DS-01 | Design systems reduce duplicated work by packaging styles, components, patterns, code, guidance, and governance. | S17, S18, S20, S24 | A/B | Official GOV.UK/USWDS/Carbon evidence. |
| C-CMP-01 | Components are contracts: anatomy, state, behavior, keyboard support, accessible name, tokens, and tests must be specified together. | S08, S09, S20, S22, S24, S37 | A/B | Direct W3C + design-system evidence. |
| C-TOK-01 | Design tokens should be a single source of truth for styles and should support theming and cross-platform transformation. | S21, S26, S27, S28, S35, S36 | A/B | DTCG stable spec plus USWDS/Carbon/Fluent token systems. |

---

## 5. Cross-layer Pattern Library

| Pattern ID | Pattern | Applies to | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P01 | Outcome-first UX | 05.01–05.05 | Start from user goals, context of use, and measurable task outcomes; design artifacts are hypotheses until tested. | Research access, task analytics, prototype capability | Slower than opinion-driven UI; requires synthesis discipline | A |
| P02 | Accessibility as quality gate | 05.04–05.10 | Accessibility is embedded in component design, code review, QA, and release gates, not a final audit. | Standards target, test matrix, accountable owners | Manual testing cost; legal baselines vary | A |
| P03 | Native semantics first | 05.05, 05.06, 05.09 | Use native HTML/platform controls before ARIA/custom controls; custom widgets must implement keyboard and semantic behavior. | Engineering literacy, component tests | May constrain visual customization; reduces maintenance risk | A |
| P04 | Evidence-based patterns | 05.01–05.09 | Reuse patterns that have research, guidance, and coded examples; adapt only when user research shows mismatch. | Pattern library, contribution process | Governance overhead; avoids local reinvention | A/B |
| P05 | Component as contract | 05.08–05.10 | Specify each component by anatomy, variants, states, events, tokens, content rules, accessibility, and tests. | Storybook/docs, prop API, design spec | Up-front design work; fewer downstream inconsistencies | B |
| P06 | Tokens as source of truth | 05.04, 05.08, 05.10 | Replace hard-coded visual values with named design tokens and semantic aliases; produce platform outputs from token source. | Token governance, build pipeline | Token proliferation risk; needs naming discipline | A/B |
| P07 | Motion for orientation | 05.03, 05.05, 05.10 | Motion/transitions should help users perceive state change and hierarchy, not merely decorate. | Reduced-motion support, state model | Overuse harms accessibility and performance | B |
| P08 | Locale as variant, not afterthought | 05.02, 05.04, 05.07, 05.10 | Treat language, direction, expansion, date/number/currency, content availability, and typography as design variants. | i18n architecture, translation workflow | Early complexity; avoids costly retrofit | A |
| P09 | Public governance loop | 05.08, 05.09 | Mature systems publish roadmap, releases, contribution paths, accessibility posture, and deprecation/migration notes. | Maintainers, review board, versioning | Requires operational capacity | B |
| P10 | Testable evidence over style preference | 05 | Design decisions must map to user evidence, standard criteria, coded behavior, or measurable product outcomes. | Metrics and evidence capture | Reduces arbitrary creativity; increases replicability | A/B |

---

# 6. Clone Specs by Layer

## Clone Spec 05.01 — UX設計

### Definition
UX設計は、ユーザーの目的、利用文脈、制約、行動、期待、業務成果を統合し、製品・サービスの体験仮説、タスクフロー、検証方法、改善サイクルを決めるレイヤーである。

### Frontier Exemplars
- **ISO 9241-210/11**: 人間中心設計の原則と活動、ユーザビリティの評価概念を標準化している [S02][S03]。
- **GOV.UK Service Manual / Service Standard**: ユーザー理解、シンプルなサービス、全員が使えること、成功指標公開を標準として扱う [S15][S16]。
- **NN/g usability heuristics**: 視認可能な状態、現実世界との一致、ユーザー制御、標準・一貫性、エラー予防などの実務ヒューリスティックを提供する [S44]。
- **USWDS / Carbon**: アクセシブルで一貫したUIをUX品質の一部として運用している [S20][S22][S24][S25]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| UXは「利用結果」として効果・効率・満足を評価すべき | S03 | standard | direct | A |
| HCDはライフサイクル全体でユーザー・要件・人間工学・ユーザビリティ知識を適用する | S02 | standard | direct | A |
| サービスはユーザーニーズを理解し、シンプルで、実ユーザーで頻繁に検証する | S15, S16 | official process | direct | A |
| 状態可視化、現実世界との一致、エラー予防はUX設計の横断的基準 | S44 | heuristic | near_direct | B |

### Core Philosophy
先端UXは「画面を良くする」ではなく、「利用者が現実の制約下で目的を達成できる確率を高める」活動である。デザイン案は仮説であり、ユーザー調査、行動データ、タスク成功、アクセシビリティ検証、プロダクト成果により採否を決める。

### Decision Model
- 入力: ユーザーセグメント、利用文脈、業務/政策/事業目的、既存行動データ、サポートログ、失敗タスク、アクセシビリティ要求。
- 判断基準: ユーザー目的への適合、タスク成功率、認知負荷、リスク/エラー低減、アクセシビリティ、実装可能性、学習容易性。
- 優先順位: 1) ユーザーが完了できること、2) 重大エラーを避けること、3) 初回利用でも理解できること、4) 再利用・拡張しやすいこと。
- 禁止事項: 社内用語をUI言語にする、単一ペルソナ前提にする、調査なしに複雑なフローを確定する、アクセシビリティを最終工程に送る。
- 例外条件: 法規制・安全・詐欺防止などでユーザー負荷が必要な場合。ただし理由・リスク・軽減策を明文化する。
- 承認者: Product Manager、UX Lead、User Research Lead、Accessibility Lead、Domain Owner。
- 見直し頻度: discovery/alpha/beta/live の各フェーズ、主要リリース前、主要UX指標悪化時、法規制/標準改定時。

### Operating Model
- 役割: Product Designer、User Researcher、Content Designer、Accessibility Specialist、Product Manager、Data Analyst。
- プロセス: research question設定 → 仮説/プロトタイプ → usability test → evidence synthesis → design decision log → implementation QA → post-release measurement。
- 会議体: weekly research playback、design critique、accessibility review、metrics review。
- レビュー: 重要フローは実ユーザーで検証し、アクセシビリティとコンテンツレビューを通す。
- 監査: リリースごとにUX指標と重大UX defectを確認。
- ツール: prototype tool、research repository、analytics、session replay（適法範囲）、a11y test、design system。
- 成果物: user needs、journey map、prototype、usability findings、decision log、UX success metrics。

### Technical / Business Specification
- すべての主要ユーザージャーニーに「ユーザー目的」「入口」「完了定義」「失敗条件」「代替チャネル」「測定イベント」を付ける。
- タスク成功は最低限 `success / partial / fail / abandoned / error-assisted` で分類する。
- リサーチ成果は個人メモではなく、チームの意思決定に接続する research repository / decision log に残す。
- 新規主要フローは、実装前に low/high fidelity prototype のいずれかで検証する。
- アクセシビリティ要求を persona や user story の別枠ではなく、各タスクの制約として扱う。

### Metrics
- Task completion rate、time-on-task、first-time success、error rate、abandonment、support contact rate、CSAT/SUS/SEQ、accessibility defect count、research finding adoption rate。

### Failure Modes
- 調査が意思決定に接続せず、調査報告書だけが残る。
- 社内ドメインモデルや組織都合がUI構造になる。
- 視覚的完成度をUX品質と誤認する。
- アクセシビリティ・多言語・例外ケースを後工程に送って設計をやり直す。

### Anti-patterns
- “デザインレビュー”が好みの議論だけになる。
- ユーザーが成功するまでの支援や失敗回復を設計しない。
- 指標がページビューやクリックだけで、タスク完了を測らない。
- ユーザー調査を1回限りの validation として扱う。

### Maturity Model
- Level 0: UX決定が個人の経験・好み依存。
- Level 1: 主要画面だけワイヤーフレーム化。
- Level 2: 調査計画とユーザビリティテストが文書化。
- Level 3: 主要フローが計測・検証・アクセシビリティレビュー対象。
- Level 4: UX decision log と research repository が運用され、設計変更に証拠が紐づく。
- Level 5: UX成果が事業KPI・品質KPI・アクセシビリティKPIと統合され、自律改善される。

### Clone Implementation Guide
1. 主要ユーザージャーニーを10件以内に絞り、各ジャーニーの完了定義と失敗条件を記述する。  
2. 週次 research playback を固定化し、調査結果を backlog / roadmap / design system へ接続する。  
3. 各フローのUX KPIを `task success + error + abandonment + support contact` で定義する。  
4. リリースゲートに accessibility / content / usability の3レビューを追加する。  
5. 意思決定ログに「採用案・却下案・根拠・残リスク」を残す。

### Confidence & Unknowns
- 確度A: HCD/ユーザビリティの標準、GOV.UK/USWDSの公式運用、WCAG基準。
- 確度B: NN/gヒューリスティックを用いたUX判断基準。
- 確度C: 具体的な組織内承認会議・レビュー権限は各組織で非公開のため推定。
- 不明点: 個別企業の内部UX review board、実際の指標閾値、失敗時の escalations。

### Validation Queries
- `site:gov.uk/service-manual "user research" "share findings"`
- `site:iso.org "ISO 9241-210" "current"`
- `"UX" "usability testing" "failure" "design system"`

---

## Clone Spec 05.02 — 情報設計

### Definition
情報設計は、ユーザーが必要な情報・機能・手続きに到達し、理解し、次の行動へ進むための分類、階層、ラベル、検索、ナビゲーション、コンテンツモデルを決めるレイヤーである。

### Frontier Exemplars
- **GOV.UK Service Manual / Design System**: サービスの命名、構造化、パターン、コンテンツ設計を公式に扱う [S15][S17][S18][S19]。
- **USWDS patterns**: 効果的で inclusive なユーザー体験を作るパターンガイダンスを公開する [S20]。
- **NN/g IA resources**: IAとナビゲーションの分離、card sorting/tree testing などを整理している [S45][S46]。
- **W3C COGA/WCAG**: 明確な目的、段階、ナビゲーション、理解可能性をアクセシビリティ側から補強する [S04][S06][S14]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| IAはナビゲーションだけでなく、分類・構造・ラベル・検索行動を含む | S45 | research guide | near_direct | B |
| パターンは既存の調査・経験から再利用し、必要なら適応/新規作成し貢献する | S18 | official process | direct | A |
| UIリンクや見出しはスクリーンリーダー単体でも意味が通る必要がある | S19, S04 | official guidance/standard | direct | A |
| 進捗・現在地・目的の明確化は認知アクセシビリティにも重要 | S14, S06 | standard/supplement | direct | A/B |

### Core Philosophy
先端の情報設計は「組織が知っている分類」ではなく「ユーザーが目的達成のために探索・判断できる構造」を作る。見えるナビゲーションは、基礎となる情報モデルの表現の一つにすぎない。

### Decision Model
- 入力: ユーザーの言語、検索語、上位タスク、既存コンテンツ、規制/手続き、サポート問い合わせ、サイト内検索ログ、ユーザーテスト結果。
- 判断基準: findability、理解容易性、用語の自然さ、階層の浅さ/深さ、再利用性、アクセシビリティ、コンテンツ維持可能性。
- 優先順位: 1) ユーザー語彙、2) タスク起点、3) 予測可能な構造、4) スクリーンリーダー/検索でも意味が通るラベル。
- 禁止事項: 組織図・内部システム名・法務分類をそのままナビゲーションにする、`click here` のような文脈依存リンク、重複カテゴリ乱立。
- 例外条件: 法的名称を表示する必要がある場合。ただし平易な説明・別名・検索導線を補う。
- 承認者: Information Architect、Content Design Lead、UX Research Lead、Service Owner。
- 見直し頻度: 新規機能追加、コンテンツ増加、検索失敗率/問い合わせ増加、ユーザー調査でカテゴリ誤認が出た時。

### Operating Model
- 役割: Information Architect、Content Designer、UX Researcher、Service Designer、Analytics Lead。
- プロセス: content inventory → top-task analysis → card sort/tree test → IA proposal → prototype navigation → usability/accessibility validation → content governance。
- 会議体: content design review、IA critique、taxonomy council（大規模組織の場合）。
- レビュー: 主要導線は screen reader link list、heading structure、search result snippet で検査する。
- 成果物: taxonomy、navigation map、content model、link text rules、heading hierarchy、redirect/alias table。

### Technical / Business Specification
- 全ページに単一目的の H1 と、ページ目的を反映した title を設定する。
- 重要リンクはリンクテキスト単体で目的を理解できるようにする。
- IA変更時は tree test または usability test により上位タスクの到達率を検証する。
- コンテンツモデルに `owner / review_date / source_of_truth / locale / status / redirect` を持たせる。
- 検索・ナビゲーション・FAQ・サポート問い合わせを同じ分類モデルで分析する。

### Metrics
- Tree-test success、first-click success、search zero-result rate、time to content、breadcrumb/backtrack rate、content duplication、link ambiguity defects、support contact due to findability。

### Failure Modes
- ナビゲーションは綺麗だが、基礎IAが重複・矛盾している。
- 一つのカテゴリに多すぎる内容を詰め、ユーザーが選べない。
- ラベルが内部用語・略語・法務用語中心になる。
- 多言語化時に階層や用語が崩れる。

### Anti-patterns
- 3-click rule のような俗説を絶対規則にする。
- フッターや検索でIAの失敗を隠す。
- ナビゲーションテストなしにメニューを増減する。
- ページ単位で所有者が違い、分類ルールがない。

### Maturity Model
- Level 0: コンテンツが追加順・部署順に並ぶ。
- Level 1: メニューとページ一覧だけがある。
- Level 2: タクソノミー、ページ目的、リンク/見出しルールがある。
- Level 3: card sort/tree test/search analytics で検証する。
- Level 4: IA変更がデータ・調査・アクセシビリティに基づき承認される。
- Level 5: コンテンツモデル、検索、パーソナライズ、ローカライズが統合される。

### Clone Implementation Guide
1. 上位20タスクと既存コンテンツを棚卸しする。  
2. カテゴリ案を3案以内に作り、tree test で比較する。  
3. リンクテキスト、H1/title、パンくず、検索同義語のルールを定義する。  
4. コンテンツモデルに owner/review_date/status を追加する。  
5. 月次で search zero-result と support問い合わせをIA改善に接続する。

### Confidence & Unknowns
- 確度A: GOV.UK の pattern/content guidance、WCAG/W3C の明確な見出し・リンク・ナビゲーション要件。
- 確度B: NN/g IA/tree testing 実務の採用。
- 確度C: 大規模組織での taxonomy council 等の会議体は公開情報からの一般化。
- 不明点: 各企業の内部検索ログ、カテゴリ別成功率、実際のIAガバナンス体制。

### Validation Queries
- `site:gov.uk/service-manual/design "structuring" "service"`
- `"tree testing" "information architecture" "navigation" "case study"`
- `site:designsystem.digital.gov "patterns" "inclusive user experiences"`

---

## Clone Spec 05.03 — 画面遷移

### Definition
画面遷移は、ユーザーがタスクを進める際のページ/ビュー/モーダル/状態/ステップ間の移動、戻る・中断・再開、進捗、アニメーション、フォーカス移動を決めるレイヤーである。

### Frontier Exemplars
- **Material Design motion/transitions**: 画面間変化をパターン化し、状態変化の理解を支援する [S32]。
- **Apple HIG navigation/components**: プラットフォーム慣習に沿ったナビゲーション/遷移を扱う [S33]。
- **GOV.UK service patterns**: ユーザーがサービスを開始・入力・確認・完了するための公的パターンを提供する [S17][S18]。
- **WCAG 2.2 / APG**: フォーカス可視性、ドラッグ代替、ターゲットサイズ、キーボード操作、ウィジェット遷移を標準化する [S04][S06][S08]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| 遷移は現在地・次の行動・完了条件を理解させる必要がある | S06, S14, S44 | standard/supplement/heuristic | near_direct | B |
| キーボードフォーカスは遷移後も見えている必要がある | S04, S06, S09 | standard/guidance | direct | A |
| ウィザード/フォーム系は段階、エラー、戻る、再入力回避を設計する | S06, S18, S19 | standard/official guidance | direct | A/B |
| motion は状態変化や階層理解を支援する設計対象である | S32, S30 | official design guidance | near_direct | B |

### Core Philosophy
遷移の目的は「動きを見せる」ことではなく、ユーザーのメンタルモデルを保護することである。現在地、完了/未完了、戻れる範囲、入力保持、フォーカス位置、エラー回復を一貫して制御する。

### Decision Model
- 入力: タスクフロー、画面状態、非同期処理、データ保存条件、戻る/中断/再開、エラー、デバイスサイズ、支援技術要件。
- 判断基準: orientation、continuity、reversibility、focus safety、state persistence、reduced motion、latency tolerance。
- 優先順位: 1) タスク完了、2) 迷子防止、3) 入力損失防止、4) エラー回復、5) ブランド/情緒表現。
- 禁止事項: 戻る操作で入力が消える、モーダル閉鎖後のフォーカス先不定、アニメーションだけで状態変化を伝える、進捗を曖昧にする。
- 例外条件: セキュリティ・決済・認証などで戻る/再送信を制限する場合。警告と回復手段を用意する。
- 承認者: UX Lead、Interaction Designer、Frontend Lead、Accessibility Specialist、Security/Compliance（必要時）。
- 見直し頻度: 新規タスクフロー、マルチステップ追加、モーダル/ダイアログ追加、入力喪失/離脱率増加時。

### Operating Model
- 役割: Interaction Designer、Product Designer、Frontend Engineer、Accessibility Engineer、QA。
- プロセス: journey state map → flow/state machine → prototype → focus/motion/keyboard QA → analytics instrumentation → post-release funnel review。
- 会議体: flow review、frontend accessibility pairing、release QA。
- レビュー: フォーカス順、戻る操作、リロード、中断再開、エラー時遷移、reduced motion、深いリンクを検証する。
- 成果物: screen flow、state transition table、focus management rules、animation spec、progress model。

### Technical / Business Specification
- 各遷移に `from_state / trigger / to_state / data_persistence / focus_target / announcement / allowed_back / error_recovery` を定義する。
- モーダル/ダイアログは開閉時フォーカス、escape、背景操作、スクリーンリーダー告知を仕様化する。
- ステップ型フォームは progress indicator、保存/戻る/再入力回避、エラー時の誘導を定義する。
- motion は reduced motion 対応と、情報伝達を色・位置・テキストでも補う。
- 非同期遷移は loading、success、error、retry、timeout を状態として持つ。

### Metrics
- Funnel completion、step abandonment、backtrack rate、input loss incidents、focus trap defects、screen-reader announcement defects、motion-related complaints、task recovery time。

### Failure Modes
- 戻ると入力が消え、再入力を要求する。
- フォーカスがページ先頭/不可視要素へ飛ぶ。
- 遷移の意味がアニメーションだけで伝達される。
- 非同期処理中にユーザーが状態を理解できない。
- セッション切れ・決済失敗・認証失敗後の復帰導線がない。

### Anti-patterns
- “かっこいい” motion を orientation より優先する。
- 画面一覧だけで flow/state を仕様化しない。
- エラー遷移を happy path 実装後に考える。
- モーダルを画面遷移の代替として乱用する。

### Maturity Model
- Level 0: 画面ごとの静的デザインのみ。
- Level 1: 基本フロー図はあるが例外状態がない。
- Level 2: 戻る/エラー/保存/フォーカスが仕様化。
- Level 3: state transition table と QA checklist がある。
- Level 4: funnel analytics と UX defect が遷移改善に接続。
- Level 5: 状態機械・計測・アクセシビリティ・モーションが設計システム化される。

### Clone Implementation Guide
1. 主要タスクごとに state transition table を作る。  
2. 遷移ごとに focus target と data persistence を必須項目にする。  
3. modal/dialog/wizard/async loading の標準パターンをコンポーネント化する。  
4. QAに keyboard-only、screen reader、browser back、reload、timeout を含める。  
5. funnel analytics を step/state 単位で計測する。

### Confidence & Unknowns
- 確度A: WCAG/WAI-ARIA/APG のフォーカス・キーボード・状態要件。
- 確度B: Material/Apple/GOV.UK から抽出した motion/navigation/progress の先端パターン。
- 確度C: 具体的なアニメーション閾値や企業内 motion governance は公開情報のみでは限定的。
- 不明点: 各プラットフォームの内部 motion review、ユーザー実験結果、遷移KPI閾値。

### Validation Queries
- `site:m3.material.io "transitions" "motion" "patterns"`
- `site:w3.org/WAI/ARIA/apg "dialog" "keyboard interaction"`
- `"focus management" "modal" "accessibility" "defect"`

---

## Clone Spec 05.04 — UI設計

### Definition
UI設計は、画面上の情報、操作、視覚階層、レイアウト、レスポンシブ/アダプティブ挙動、表示密度、コンポーネント選択を決めるレイヤーである。

### Frontier Exemplars
- **Material Design 3**: ガイドライン、コンポーネント、ツール、adaptive design、tokens、motion を持つ [S30][S31][S32]。
- **Apple HIG**: Apple プラットフォーム上の一貫した操作・コンポーネント・アクセシビリティ設計を扱う [S33][S34]。
- **USWDS / GOV.UK / Carbon / Fluent**: 公開デザインシステムとしてレイアウト・タイポグラフィ・色・コンポーネント・アクセシビリティを結合する [S17][S20][S24][S28]。
- **WCAG 2.2**: UIの可読性、操作可能性、理解可能性、堅牢性を最低品質ゲートとして規定する [S04][S05][S06]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| UIは見た目だけでなく、アクセシブルで再利用可能なコンポーネント/スタイルで構築する | S17, S20, S24, S25 | design system | direct | A/B |
| 一貫したトークン/スタイルはデザイナーと開発者のコミュニケーション粒度を下げる | S21, S28 | token guidance | direct | A |
| UIは幅広いデバイスと入力・支援技術で利用可能にする必要がある | S04, S06, S22, S23 | standard/process | direct | A |
| platform HIG は利用者の既存期待に沿う UIを作る根拠になる | S33, S44 | official platform guide/heuristic | near_direct | B |

### Core Philosophy
先端UIは「ブランド表現」と「利用可能性」を分離しない。視覚階層、情報密度、コンポーネント、余白、色、フォーカス、状態は、全てタスク理解と品質保証の対象である。

### Decision Model
- 入力: 画面目的、情報優先度、ユーザー端末、入力モード、コンポーネント候補、ブランド/スタイル制約、アクセシビリティ基準。
- 判断基準: clarity、consistency、recognition、responsiveness、contrast、touch/keyboard usability、component reuse、implementation cost。
- 優先順位: 1) 読める/理解できる、2) 操作できる、3) 一貫している、4) 標準コンポーネントを使う、5) ブランド差別化。
- 禁止事項: 色だけで状態を表す、非標準のカスタムUIを安易に作る、視覚密度をKPI目的だけで上げる、フォーカス状態を削る。
- 例外条件: 独自ブランド体験や新規操作が必要な場合。ただし usability/a11y test と component spec を追加する。
- 承認者: UI/Visual Design Lead、Design System Lead、Accessibility Lead、Frontend Lead、Brand Owner。
- 見直し頻度: design system release、brand refresh、major feature、accessibility defects、responsive breakpoints変更時。

### Operating Model
- 役割: UI Designer、Design System Designer、Frontend Engineer、Accessibility Specialist、Brand Designer。
- プロセス: content priority → layout sketch → component selection → token application → high-fidelity UI → design QA → implementation QA。
- 会議体: design critique、component review、visual QA、accessibility review。
- レビュー: design token 使用率、コンポーネント再利用、contrast、responsive、keyboard/focus、screen reader labels。
- 成果物: UI spec、responsive layout、component mapping、style/token mapping、design QA report。

### Technical / Business Specification
- すべてのUI要素を `component / variant / state / token / content rule / accessibility rule` にマッピングする。
- responsive breakpoint ごとに priority content、layout shift、hidden content、touch target を定義する。
- 視覚状態は `default / hover / active / focus / disabled / selected / error / loading` を最低セットとする。
- UI差分は token/theme/component のどれで表現するかを明示する。
- 実装時はデザインファイルとコードのコンポーネント名・props を同期する。

### Metrics
- Design QA pass rate、component reuse ratio、hard-coded style count、contrast violations、responsive defects、visual regression diffs、UI consistency defects、time-to-implement。

### Failure Modes
- 高忠実度デザインは美しいが、コンポーネント/トークンに落ちない。
- 状態パターン不足で実装時に ad hoc UI が増える。
- デバイス幅・ズーム・翻訳でレイアウトが崩れる。
- フォーカスやエラー状態が視覚的に弱い。

### Anti-patterns
- pixel-perfect を唯一の品質基準にする。
- コンポーネントが存在するのに毎回新規UIを作る。
- ブランド色をコントラスト確認なしに適用する。
- デザインファイルだけが source of truth になる。

### Maturity Model
- Level 0: UIは画面単位・担当者単位でばらつく。
- Level 1: 色/フォント程度のスタイルガイドがある。
- Level 2: コンポーネントと状態が定義される。
- Level 3: token/component mapping と design QA が運用される。
- Level 4: visual regression、a11y test、component adoption が計測される。
- Level 5: 多ブランド・多デバイス・多言語のUIがトークン/コンポーネントで自動同期される。

### Clone Implementation Guide
1. 主要画面を component inventory に分解する。  
2. 標準状態セットを定義し、デザインファイル/コードで同期する。  
3. 色・タイポグラフィ・余白を token 化する。  
4. デザインQA checklist に contrast、focus、responsive、i18n expansion を追加する。  
5. component reuse ratio と hard-coded value count を月次で見る。

### Confidence & Unknowns
- 確度A: WCAG、USWDS、Carbon、Fluent の公開UI/トークン/アクセシビリティ証拠。
- 確度B: Material/Apple の platform guidance に基づくUI判断。
- 確度C: 各企業の内部デザインレビュー閾値、ブランドガバナンス。
- 不明点: 実際のデザインファイル/コード同期率、内部UI defect taxonomy。

### Validation Queries
- `site:designsystem.digital.gov "Design tokens" "components"`
- `site:carbondesignsystem.com "accessibility" "components" "WCAG"`
- `site:developer.apple.com/design/human-interface-guidelines "components" "accessibility"`

---

## Clone Spec 05.05 — インタラクション設計

### Definition
インタラクション設計は、ユーザー入力、イベント、状態変化、フィードバック、エラー、取り消し、キーボード/タッチ/音声/支援技術操作、非同期挙動を決めるレイヤーである。

### Frontier Exemplars
- **WAI-ARIA 1.2 / APG / Using ARIA**: カスタムウィジェットの役割、状態、プロパティ、キーボード操作を標準化する [S07][S08][S09][S10]。
- **WCAG 2.2**: ドラッグ操作、ターゲットサイズ、フォーカス、認証、再入力などの最新操作要件を追加している [S04][S06]。
- **NN/g heuristics**: 状態可視化、ユーザー制御、エラー予防、認識優先をインタラクション判断に使える [S44]。
- **Fluent/Material/Apple/Carbon**: platform conventions とコンポーネント状態を組み合わせる [S28][S30][S33][S24]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| ARIAを使う前に native HTML/platform control を使うべき | S09, S10 | W3C guidance/spec | direct | A |
| すべての interactive ARIA control は keyboard で使える必要がある | S09, S08, S07 | W3C guidance/spec | direct | A |
| フィードバック、取り消し、エラー予防はユーザー信頼を作る | S44 | heuristic | near_direct | B |
| drag/touch/target/authentication などは WCAG 2.2 で強化された操作基準 | S06 | W3C update | direct | A |

### Core Philosophy
優れたインタラクションは「ユーザーが何をしたか」「システムがどう受け取ったか」「次に何が可能か」を即時・明確・可逆に伝える。見た目の状態と支援技術へ公開される状態が一致しなければならない。

### Decision Model
- 入力: 操作対象、入力モード、データ状態、権限、エラー条件、支援技術要件、プラットフォーム慣習。
- 判断基準: feedback、predictability、keyboard equivalence、semantic correctness、reversibility、error prevention、latency、state consistency。
- 優先順位: 1) native control、2) semantic correctness、3) keyboard/touch equivalence、4) state feedback、5) custom interaction。
- 禁止事項: click-only interaction、focusable element の aria-hidden、visual state と ARIA state の不一致、disabled の意味を曖昧にする。
- 例外条件: HTMLに適切な native control がない場合。ただし APG/Open UI を参照し、キーボード/ARIA/test を追加する。
- 承認者: Interaction Designer、Frontend Lead、Accessibility Engineer、QA Lead。
- 見直し頻度: 新規コンポーネント、新規入力方式、支援技術不具合、主要 browser/platform update 時。

### Operating Model
- 役割: Interaction Designer、Frontend Engineer、Accessibility Engineer、QA Automation、Design System Owner。
- プロセス: control selection → native-vs-custom decision → state matrix → keyboard map → semantic spec → prototype/test → component release。
- 会議体: interaction spec review、component accessibility review、frontend pairing。
- レビュー: keyboard-only、screen reader、touch-only、zoom、reduced motion、error recovery、latency/loading state。
- 成果物: interaction state matrix、event table、keyboard shortcut map、ARIA/semantic mapping、automated/manual test plan。

### Technical / Business Specification
- すべての操作要素に `role/native element / accessible name / state / keyboard action / pointer action / touch action / disabled behavior / error behavior` を定義する。
- `hover` だけに依存する機能は禁止し、focus/click/touch/keyboard の同等導線を持つ。
- カスタムコンポーネントは APG pattern と差分を明示する。
- 非同期操作は `pending / optimistic / success / failure / retry / cancelled` を状態として扱う。
- エラー予防、確認、undo、redo、cancel の適用基準を定義する。

### Metrics
- Keyboard coverage、screen reader task success、interaction defect density、event/state test coverage、error recovery success、latency feedback coverage、ARIA validation defects。

### Failure Modes
- ARIA属性だけ追加し、キーボード動作を実装しない。
- hover/focus/active/selected/disabled の状態が曖昧。
- 視覚的にはボタンだが semantic には div で、支援技術に伝わらない。
- エラー後に復旧できず、ユーザーが入力を失う。
- disabled にした理由や次にできる行動を伝えない。

### Anti-patterns
- “No ARIA is bad” と誤解し、native control より ARIA を優先する。
- interaction spec を実装者の裁量に任せる。
- happy path だけで操作を検証する。
- 状態をデザインファイルに描くだけで、コードAPIに落とさない。

### Maturity Model
- Level 0: 操作仕様はコード実装時に決まる。
- Level 1: 主要ボタン/フォームの状態だけ定義。
- Level 2: component state matrix と keyboard map がある。
- Level 3: APG/WCAGに基づくアクセシビリティレビューがある。
- Level 4: interaction state が自動テスト・a11y test・visual regression と接続。
- Level 5: コンポーネント単位で操作契約が標準化され、製品横断で再利用される。

### Clone Implementation Guide
1. 主要コンポーネントを native / custom / hybrid に分類する。  
2. custom は APG pattern 参照、keyboard map、ARIA state、manual screen-reader test を必須にする。  
3. state matrix を design system のコンポーネントページに追加する。  
4. CIに axe/pa11y 等を入れつつ、keyboard/screen reader は手動検査を維持する。  
5. 重大操作は undo/cancel/error recovery のルールを事前定義する。

### Confidence & Unknowns
- 確度A: WAI-ARIA/APG/Using ARIA/WCAG の直接証拠。
- 確度B: NN/g heuristics と各 design system の状態設計。
- 確度C: 具体的な interaction review 体制。
- 不明点: 各企業の実際の支援技術テスト範囲、ブラウザ/ATサポート表、custom control の失敗率。

### Validation Queries
- `site:w3.org/TR/using-aria "First Rule of ARIA"`
- `site:w3.org/WAI/ARIA/apg/patterns "Keyboard Interaction"`
- `"aria" "keyboard" "custom widget" "bug"`

---

## Clone Spec 05.06 — アクセシビリティ

### Definition
アクセシビリティは、障害、年齢、デバイス、入力手段、支援技術、法規制、認知負荷などの多様な条件下で、ユーザーが同等品質の体験を得られるように設計・実装・検証・運用するレイヤーである。

### Frontier Exemplars
- **WCAG 2.2 / WAI**: 現行の推奨アクセシビリティ基準として、知覚可能・操作可能・理解可能・堅牢の原則と A/AA/AAA の成功基準を提供する [S04][S05][S06]。
- **WAI-ARIA / APG / Using ARIA**: 動的/高度UIの支援技術連携を定義し、カスタムウィジェットの失敗を防ぐ [S07][S08][S09][S10]。
- **USWDS / Carbon**: screen reader、keyboard、zoom、touch、automated scan、manual specialist test をコンポーネント運用へ組み込む [S22][S25]。
- **DOJ ADA Title II / EAA / Section 508 / EN 301 549**: 法域別の基準・施行・調和の制約を提供する [S39][S40][S41][S42][S43]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| WCAG 2.2 は広範な障害とデバイスのWebアクセシビリティを扱う | S04, S05 | standard | direct | A |
| WCAG 2.2は13ガイドライン、4原則、A/AA/AAA成功基準で構成される | S05 | standard overview | direct | A |
| USWDS は screen reader/keyboard/zoom/touch/automation/manual/audit を組み込む | S22 | official process | direct | A |
| Carbon components は WCAG AA, Section 508, European standards に基づく checklist を参照する | S25 | official design system | direct | A |
| 法的基準は法域で異なる。EN 301 549 v3.2.1 は WCAG 2.1 に基づき、WCAG 2.2 が自動で法的基準になるわけではない | S43 | official compliance guidance | direct | A |
| EAA は 2025-06-28 に施行フェーズへ入り、e-commerce等を含む | S40, S41 | official/regulatory | direct | A |
| DOJ Title II final rule は web/mobile apps に具体的要件を導入し、2026年IFRで compliance date が延長された | S39 | official/regulatory | direct | A |

### Core Philosophy
アクセシビリティは「準拠チェック」ではなく、製品品質・リスク管理・ユーザー包摂の継続的運用である。標準準拠は最低条件であり、実ユーザー、支援技術、コンポーネント、コンテンツ、法域別基準を横断して管理する。

### Decision Model
- 入力: 対象法域、製品種別、ユーザー特性、WCAG target、支援技術、既存 defects、コンポーネント/コンテンツ在庫、third-party/vendor dependency。
- 判断基準: legal baseline、WCAG conformance、actual usability with AT、risk severity、component reuse impact、remediation cost、release criticality。
- 優先順位: 1) blocking/critical access defects、2) legal baseline、3) reusable component defects、4) high-traffic user journeys、5) supplemental cognitive/mobile guidance。
- 禁止事項: 自動検査だけで合格判定、代替版を安易に提供、ARIA misuse、フォーカス削除、色のみの情報提示、キーボード不可のUI。
- 例外条件: 技術的/法的/セキュリティ制約により完全修正できない場合。ただし documented exception、代替手段、期限、owner を持つ。
- 承認者: Accessibility Lead、Legal/Compliance、QA Lead、Product Owner、Design System Lead。
- 見直し頻度: 各リリース、design system update、標準/法令改定、重大 defect 発生時、年次監査。

### Operating Model
- 役割: Accessibility Lead、Accessibility Engineer、UX/Content Designer、Frontend Engineer、QA、Legal、Procurement/Vendor Manager。
- プロセス: target standard設定 → component/page inventory → automated scan → keyboard/manual/AT test → issue severity → remediation → conformance documentation → monitoring。
- 会議体: a11y triage、release gate review、legal/compliance review、component accessibility board。
- レビュー: 自動検査、手動キーボード、screen reader、zoom/reflow、touch、cognitive clarity、contrast、forms/errors、ARIA semantics。
- 成果物: accessibility policy、WCAG matrix、test plan、audit report、ACR/VPAT、exception log、remediation backlog。

### Technical / Business Specification
- 基本 target は `WCAG 2.2 AA` を推奨 baseline とし、法務上は各法域の要求（例: Section 508/WCAG 2.0 AA、EN 301 549/WCAG 2.1、ADA Title II/WCAG 2.1 AA等）を明記する。
- 主要コンポーネントは `automated + keyboard + screen reader + zoom + touch + manual specialist` の検査セットを持つ。
- すべてのアクセシビリティ defect は `severity / affected users / affected tasks / legal risk / component impact / owner / due date` を持つ。
- Design system component は conformance status と known limitations を公開する。
- third-party component/vendor は ACR/VPAT または同等の適合証拠を要求する。

### Metrics
- WCAG pass rate、critical a11y defects、keyboard pass、screen reader pass、automated scan trend、component conformance status、remediation SLA、exceptions overdue、ACR coverage、a11y defects per release。

### Failure Modes
- 自動検査に通るが、キーボードやスクリーンリーダーでは使えない。
- 法域別基準を混同し、WCAG 2.2推奨と法的義務の差を誤る。
- component defect が全製品へ横展開される。
- exception log が期限・ownerなしで放置される。
- 認知アクセシビリティ、モバイル、拡大表示、言語差を軽視する。

### Anti-patterns
- “最後にa11yチェックする” release process。
- `aria-label` 追加で問題が解決したとみなす。
- 法令対応だけを目的にし、実利用検査をしない。
- アクセシビリティを専門家だけの責任にする。

### Maturity Model
- Level 0: 苦情/監査後に個別対応。
- Level 1: 自動検査のみ。
- Level 2: WCAG target と手動検査 checklist がある。
- Level 3: コンポーネント・主要フローごとに a11y test が release gate 化。
- Level 4: ACR/VPAT、vendor review、defect SLA、design system conformance が統合。
- Level 5: 障害当事者テスト、法域管理、予防的 component governance、continuous monitoring が運用される。

### Clone Implementation Guide
1. 製品ごとの legal baseline と recommended baseline を分けて記述する。  
2. 主要コンポーネントから accessibility conformance matrix を作る。  
3. CI自動検査に加え、keyboard/screen reader/zoom/touch の手動検査をリリースゲートに入れる。  
4. defect severity と SLA を定義し、component defect を最優先で修正する。  
5. ACR/VPAT、exception log、vendor evidence を維持する。

### Confidence & Unknowns
- 確度A: WCAG/WAI-ARIA/USWDS/Carbon/DOJ/EAA/Section508/EN301549 の直接証拠。
- 確度B: 組織内での品質ゲート設計。
- 確度C: 個別企業の legal-risk threshold、訴訟/監査の内部対応。
- 不明点: 実際の障害当事者テスト範囲、AT/browser matrix、海外法域ごとの契約要件。

### Validation Queries
- `site:w3.org/WAI/standards-guidelines/wcag "WCAG 2.2" "A AA AAA"`
- `site:ada.gov "web content and mobile apps" "WCAG 2.1 AA"`
- `site:digital-strategy.ec.europa.eu "EN 301 549" "WCAG 2.1"`

---

## Clone Spec 05.07 — 多言語化・国際化

### Definition
多言語化・国際化は、言語、文字エンコーディング、方向、翻訳、地域形式、文化差、フォント、レイアウト伸縮、コンテンツ運用を、製品設計・実装・運用へ組み込むレイヤーである。

### Frontier Exemplars
- **W3C Internationalization Activity**: コンテンツ作者・開発者向けの国際化要求・技術リソースを提供する [S11][S12][S13]。
- **Apple HIG / Material / Fluent / Carbon**: platform conventions、tokens、themes、component design を locale/contrast/platform variation と結合する [S28][S30][S33][S24]。
- **GOV.UK / USWDS content guidance**: 明確なコンテンツ、ラベル、入力、エラー、アクセシビリティと国際化の接点を示す [S19][S20]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| i18nは文字エンコーディング、言語、方向、検証、authoring techniquesを含む | S11, S12, S13 | W3C guidance | direct | A |
| RTLでは `dir` など方向指定を設計/実装上の一級要件にする | S12 | W3C guidance | direct | A |
| UI文言は明確なリンク・見出し・ラベルとしてアクセシビリティと一体で設計する | S19, S04 | official guidance/standard | direct | A |
| Token/theme system は locale/brand/accessibility variants に拡張しやすい | S28, S35, S36 | token guidance/spec | near_direct | B |

### Core Philosophy
国際化は翻訳工程ではない。文字列、レイアウト、フォーマット、方向、語彙、検索、アクセシビリティ、コンポーネント状態を最初から locale variant として扱う。

### Decision Model
- 入力: 対象言語/地域、文字方向、翻訳範囲、地域法規制、通貨/日時/数値形式、フォント、コンテンツ所有者、リリース頻度。
- 判断基準: translatability、layout resilience、semantic correctness、locale formatting、RTL/bidi safety、accessibility、content governance。
- 優先順位: 1) 文字列外部化、2) locale formatting、3) レイアウト伸縮/RTL、4) 翻訳品質、5) 文化固有の最適化。
- 禁止事項: 文字列連結、ハードコードされた日付/通貨/語順、画像内文字、LTR前提アイコン/フロー、翻訳者に文脈を渡さない。
- 例外条件: 法定文言やブランド名など翻訳不可要素。ただし locale-specific note を付ける。
- 承認者: Localization PM、i18n Lead、Content Design Lead、Frontend Lead、Legal（規制文言の場合）。
- 見直し頻度: 言語追加、新コンテンツ/機能、locale defect増加、ブランド/法定文言変更時。

### Operating Model
- 役割: Localization Manager、i18n Engineer、Content Designer、Product Designer、QA、Legal/Market Owner。
- プロセス: locale strategy → string inventory → pseudo-localization → translation with context → locale QA → RTL/bidi test → release sync → content drift monitoring。
- 会議体: localization readiness review、content review、market launch review。
- レビュー: pseudo-translation、text expansion、RTL、date/number/currency、pluralization、screen reader language、localized search。
- 成果物: locale matrix、translation keys、string context notes、formatting rules、RTL spec、localized QA report。

### Technical / Business Specification
- UI文字列はすべて key 管理し、文脈、スクリーンショット、変数、文字数制約を添える。
- 文字列連結は禁止し、plural/gender/case/word-order に対応する ICU MessageFormat 等を採用する。
- date/time/number/currency/address/name/phone は locale-aware format API を使う。
- RTLはページ方向、アイコン、ナビゲーション、motion、フォーカス順を検査する。
- 画像内テキスト、動画字幕、alt text、error text、aria-label も翻訳対象に含める。

### Metrics
- Translation coverage、untranslated key count、pseudo-localization defects、RTL defects、locale formatting defects、localized release lag、translation rework rate、localized support contact rate。

### Failure Modes
- 翻訳後にボタン/カード/モーダルが崩れる。
- 英語前提の語順・文字列連結で意味が壊れる。
- `lang`/`dir`/読み上げ言語が不一致。
- 日本語・アラビア語・タイ語などで検索/改行/フォントが破綻する。
- 法定文言や市場固有要件が翻訳工程で漏れる。

### Anti-patterns
- 翻訳をリリース直前の作業にする。
- 画面幅を固定し、text expansion を想定しない。
- 翻訳者にUI文脈を提供しない。
- `en-US` を全市場の初期値として放置する。

### Maturity Model
- Level 0: 文字列ハードコード、単一言語。
- Level 1: 翻訳ファイルはあるがUI文脈やQAなし。
- Level 2: string inventory、locale matrix、formatting rules がある。
- Level 3: pseudo-localization、RTL、locale QA が release gate 化。
- Level 4: design system/token/component が locale variants に対応。
- Level 5: 多市場で継続運用され、コンテンツ・検索・支援技術・法務が統合される。

### Clone Implementation Guide
1. UI/ARIA/alt/error/help を含む全文字列を棚卸しする。  
2. pseudo-localization と RTL smoke test をCIまたはQAに入れる。  
3. locale formatting rules を product requirements に入れる。  
4. design system components に min/max text、wrapping、direction rules を追加する。  
5. 翻訳 workflow に screenshot/context と approval owner を付ける。

### Confidence & Unknowns
- 確度A: W3C i18n の直接証拠。
- 確度B: design token/theming と i18n の接続。
- 確度C: 実際の翻訳TMS・市場別承認プロセス。
- 不明点: 各組織の locale coverage、翻訳品質評価、market launch governance。

### Validation Queries
- `site:w3.org/International "dir=rtl" "HTML"`
- `"pseudo-localization" "design system" "RTL"`
- `site:developer.apple.com/design/human-interface-guidelines "right-to-left"`

---

## Clone Spec 05.08 — デザインシステム

### Definition
デザインシステムは、プロダクト群で再利用される設計原則、スタイル、トークン、コンポーネント、パターン、コード、ドキュメント、貢献/承認/版管理/品質保証の運用を決めるレイヤーである。

### Frontier Exemplars
- **GOV.UK Design System**: styles/components/patterns、アクセシビリティ戦略、コミュニティ、roadmap、release notes を公開する [S17][S18]。
- **USWDS**: 連邦政府向けに components、patterns、design tokens、utilities、accessibility process を公開する [S20][S21][S22][S23]。
- **Carbon**: IBM の open source design system として、code/design tools/resources/HIG/community を公開する [S24][S25]。
- **Fluent / Material / Apple HIG**: platform/product-wide consistency と tokens/components を提供する [S28][S29][S30][S33]。
- **DTCG / Open UI**: tokens と component anatomy/behavior を標準化方向へ進める [S35][S36][S37][S38]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| Design system は styles/components/patterns により一貫性と再利用を作る | S17, S20, S24 | official design system | direct | A |
| Mature system は community/contribution/roadmap/release を公開運用する | S17, S18, S24 | official process | direct | A/B |
| Accessibility は design system component の品質保証に組み込むべき | S22, S25, S23 | official process | direct | A |
| Tokens は設計判断を cross-tool/platform に共有する source of truth になり得る | S35, S36, S21, S28 | spec/guidance | direct | A/B |

### Core Philosophy
デザインシステムは部品集ではなく、プロダクト横断の意思決定基盤である。何を共通化し、何を例外として認め、どの品質ゲートで配布し、どう改善するかを運用する。

### Decision Model
- 入力: 複数プロダクトのUI在庫、重複部品、ブランド要件、アクセシビリティ欠陥、開発速度、チーム体制、技術スタック、貢献需要。
- 判断基準: reuse value、accessibility risk、implementation readiness、platform coverage、documentation quality、governance cost、migration impact。
- 優先順位: 1) 高頻度/高リスク部品、2) アクセシビリティ改善効果、3) token/style基盤、4) contributor demand、5) brand refinement。
- 禁止事項: design system を中央チームの制作物だけにする、docs と code を分離、unversioned breaking changes、例外の野放し。
- 例外条件: product-specific innovation。ただし実験期限、測定、再利用可能性判定、system backlog への接続を持つ。
- 承認者: Design System Lead、Frontend Platform Lead、Accessibility Lead、Product Design Leads、Brand/Content Lead。
- 見直し頻度: monthly roadmap、release cycle、major brand refresh、accessibility audit、component deprecation/migration。

### Operating Model
- 役割: Design System Lead、DesignOps、Component Designers、Frontend Platform Engineers、Accessibility Specialists、Content Designers、Community Contributors。
- プロセス: inventory → priority scoring → component/token design → implementation → accessibility QA → documentation → release notes → adoption/migration → feedback loop。
- 会議体: design system council、component review board、contribution triage、accessibility QA sync、release planning。
- レビュー: token use、component API、a11y test、docs completeness、migration impact、versioning。
- 成果物: docs site、component library、token package、design kits、roadmap、release notes、contribution guide、adoption dashboard。

### Technical / Business Specification
- Design system artifact は `principles / tokens / components / patterns / content guidance / accessibility / code / contribution / release` を最低構成とする。
- Component page には `when to use / when not to use / anatomy / variants / accessibility / content / code / changelog` を含める。
- Release は semantic versioning または同等の breaking-change policy を持つ。
- Contribution は intake criteria、evidence requirement、review stages、maintainer ownership、deprecation rule を持つ。
- Adoption dashboard は product/team 単位で component/token adoption と exceptions を可視化する。

### Metrics
- Component adoption、token adoption、duplicate component count、contribution lead time、docs completeness、a11y defects per component、release cadence、breaking change count、migration completion、consumer satisfaction。

### Failure Modes
- Component library はあるが採用されず、各プロダクトがforkする。
- ドキュメント・Figma・コードの状態がずれる。
- アクセシビリティ欠陥が共通部品で増幅される。
- Governance が重すぎて現場が迂回する。
- 例外/拡張の仕組みがなく、中央チームがボトルネック化する。

### Anti-patterns
- Design system を静的 style guide として扱う。
- UI在庫や採用データなしにコンポーネントを作る。
- Contribution を受けない中央集権運用。
- token/component/design kit/code を別々に更新する。

### Maturity Model
- Level 0: 画面/チームごとのUI断片。
- Level 1: スタイルガイド・一部Figma部品。
- Level 2: コンポーネント・トークン・基本ドキュメント。
- Level 3: 貢献/レビュー/release/versioning が運用。
- Level 4: adoption、a11y、migration、exceptions が計測される。
- Level 5: 複数ブランド/プラットフォーム/プロダクトで自律的に改善し、標準・コミュニティと接続する。

### Clone Implementation Guide
1. UI inventory を行い、重複/高頻度/高リスク要素を抽出する。  
2. Design system の最小構成を `tokens + 10 core components + docs + a11y test + contribution guide` に絞る。  
3. 既存プロダクトへ adoption plan と migration path を提示する。  
4. monthly contribution triage と quarterly roadmap を運用する。  
5. component/token adoption と exceptions をダッシュボード化する。

### Confidence & Unknowns
- 確度A: GOV.UK/USWDS/Carbon の公開 design system/operations evidence。
- 確度B: Fluent/Material/Apple/DTCG/Open UI から抽出した横断パターン。
- 確度C: 内部DesignOps体制、採用KPI閾値。
- 不明点: 各組織の内部design system funding model、ROI、component deprecation実態。

### Validation Queries
- `site:design-system.service.gov.uk "roadmap" "components" "patterns"`
- `site:designsystem.digital.gov "accessibility" "component" "scan"`
- `"design system" "adoption" "duplicate components" "migration"`

---

## Clone Spec 05.09 — コンポーネント設計

### Definition
コンポーネント設計は、UI部品の anatomy、props/API、variants、states、events、content、tokens、accessibility、responsive behavior、test、使用条件を契約として定義するレイヤーである。

### Frontier Exemplars
- **WAI-ARIA APG**: Accordion、Dialog、Tabs、Listbox 等の accessible widget pattern、keyboard interaction、ARIA roles/states/properties を提供する [S08]。
- **Open UI**: built-in controls の parts/states/behaviors/accessibility requirements を研究し、design systems/frameworks/web platform の相互運用を目指す [S37][S38]。
- **GOV.UK / USWDS / Carbon**: コンポーネントに guidance、coded examples、accessibility、implementation を統合する [S17][S20][S22][S24]。
- **Fluent UI / Polaris Web Components**: open source components と web standards / accessibility / internationalization を接続する [S29]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| Accessible components require roles/states/properties and keyboard support | S07, S08, S09 | W3C spec/guidance | direct | A |
| Component anatomy, states, behavior, accessibility requirements are emerging standardization targets | S37, S38 | community spec/research | direct | B |
| Design systems publish reusable accessible components with guidance and code | S17, S20, S22, S24 | design system | direct | A/B |
| Native semantics should be preferred and ARIA conflicts avoided | S09, S10 | W3C spec/guidance | direct | A |

### Core Philosophy
コンポーネントは「見た目の部品」ではなく、意味・操作・状態・実装・アクセシビリティ・トークン・文言を束ねた contract である。使い回すほど影響が大きいため、標準化とテストが必要になる。

### Decision Model
- 入力: UI inventory、user tasks、APG/Open UI pattern、platform controls、states、content rules、token needs、technical stack、a11y requirements。
- 判断基準: native availability、reuse frequency、semantic correctness、behavior completeness、testability、API simplicity、composition flexibility、migration cost。
- 優先順位: 1) native/platform control、2) accessible behavior、3) stable API、4) design token alignment、5) extensibility。
- 禁止事項: visual-only component、unbounded props、states未定義、keyboard未対応、docsなし、accessibility caveatなし。
- 例外条件: product-specific experimental component。ただし experiment flag、owner、sunset/review date を付ける。
- 承認者: Component Designer、Frontend Lead、Accessibility Engineer、Design System Lead、QA Lead。
- 見直し頻度: component release、APG/WCAG update、browser/AT support change、major product adoption、defect spike。

### Operating Model
- 役割: Component Designer、Frontend Engineer、Accessibility Engineer、QA Automation、Content Designer、Design System Maintainer。
- プロセス: need intake → native/custom decision → anatomy/state/API spec → prototype → a11y/interaction test → docs/storybook → release/version → adoption support。
- 会議体: component review、API review、accessibility review、release review。
- レビュー: API stability、state matrix、focus/keyboard、responsive/i18n、visual regression、token use、docs completeness。
- 成果物: component spec、prop table、state matrix、event table、accessibility test, Storybook/examples, Figma component, changelog。

### Technical / Business Specification
- Component spec 必須項目: `purpose / anatomy / variants / slots / props / states / events / keyboard / ARIA/native mapping / tokens / content rules / responsive rules / i18n / do-don't / tests / version`。
- States 最低セット: default, hover, active, focus, disabled, loading, selected, error, success, readonly, expanded/collapsed（該当時）。
- Props/API は behavior を過度に分岐させず、variants は use case と accessibility impact を持つ。
- Storybook等に keyboard/a11y test と screen reader notes を置く。
- Component deprecation は migration guide と removal date を持つ。

### Metrics
- Component reuse、API breaking changes、component defects、a11y pass、keyboard coverage、visual regression pass、docs completeness、prop misuse count、migration completion。

### Failure Modes
- デザイン上は同じだがコードは複数実装になり、欠陥が分散する。
- props が肥大化し、使い方が予測できない。
- APG pattern とズレた custom widget を作る。
- コンポーネント更新が既存画面を壊す。
- aria-label や content rules が利用側に丸投げされる。

### Anti-patterns
- “見た目が同じなら同じコンポーネント”と判定する。
- コンポーネントAPIを実装都合だけで決める。
- variant追加を無制限に許す。
- Storybookを見本集にし、契約/テスト/制約を載せない。

### Maturity Model
- Level 0: コンポーネントなし、画面単位で実装。
- Level 1: 共通部品はあるが状態・API・a11yが不十分。
- Level 2: component spec、state、props、docs がある。
- Level 3: APG/WCAGに基づくテストと release/versioning がある。
- Level 4: visual/a11y/unit/e2e test、migration/deprecation が運用。
- Level 5: Open UI/DTCG等の標準動向と連動し、multi-platform component contract を維持する。

### Clone Implementation Guide
1. ボタン、入力、選択、ダイアログ、タブ、メニュー、表、通知など高頻度部品から spec 化する。  
2. APG pattern と native control availability を必ず確認する。  
3. `state matrix + keyboard map + token map + content rules` を component page に追加する。  
4. CIに visual regression、unit、a11y scan を組み、手動 keyboard/screen-reader を補完する。  
5. component contribution に evidence requirement と API review を導入する。

### Confidence & Unknowns
- 確度A: WAI-ARIA/APG/Using ARIA/ARIA in HTML。
- 確度B: Open UI と design system exemplars から抽出した component contract pattern。
- 確度C: 具体的な社内API review委員会、prop naming convention。
- 不明点: browser/assistive technology matrix、実際のcomponent adoption data、内部migration cost。

### Validation Queries
- `site:open-ui.org "states" "behaviors" "accessibility requirements"`
- `site:w3.org/WAI/ARIA/apg/patterns "tabs" "keyboard interaction"`
- `site:designsystem.digital.gov "component" "accessibility guidance"`

---

## Clone Spec 05.10 — スタイル・トークン設計

### Definition
スタイル・トークン設計は、色、タイポグラフィ、余白、サイズ、角丸、影、z-index、motion、テーマ、ブランド、アクセシビリティバリアントの値体系と変換・配布・利用ルールを決めるレイヤーである。

### Frontier Exemplars
- **DTCG Design Tokens 2025.10**: デザイントークンを色・余白・タイポグラフィ等の設計判断の不可分単位として扱い、ファイル形式・交換・相互運用を標準化する [S35][S36]。
- **USWDS Design Tokens**: typography、spacing、color 等を discrete options として管理し、Sass/mixins/utilities に接続する [S21]。
- **Fluent Tokens**: global/alias tokens、theming、light/dark/high-contrast/brand support を公開する [S28]。
- **Carbon Spacing/Color Tokens**: 2/4/8 scale、semantic color roles、focus/support tokens など実装可能な token spec を公開する [S26][S27]。
- **Material Design Tokens**: Material UI elements の building blocks として tokens を扱う [S31]。

### Evidence Map
| Claim | Source | Evidence Type | Directness | Confidence |
|---|---|---|---|---|
| デザイントークンは色・余白・タイポグラフィ等の設計判断の単位である | S35, S36, S21 | spec/guidance | direct | A |
| Token system は hard-coded values を減らし、デザイン/開発の共通語彙を作る | S21, S28, S27 | official guidance | direct | A/B |
| Semantic/alias tokens はテーマ・高コントラスト・ブランド差分に有効 | S28, S36, S27 | official guidance/spec | direct | A/B |
| Spacing/color/typography scales はUI密度・階層・一貫性を制御する | S21, S26, S27, S31 | token guidance | direct | A/B |

### Core Philosophy
スタイルは好みの値ではなく、製品横断で配布・検証・変換される設計決定である。値の直接指定を減らし、primitive → semantic/alias → component token の階層で、ブランド・テーマ・アクセシビリティ・プラットフォーム差分を制御する。

### Decision Model
- 入力: brand palette、accessibility contrast、platform requirements、component needs、theme modes、locale typography、motion policy、existing hard-coded styles。
- 判断基準: semantic clarity、accessibility safety、cross-platform transformability、theming support、naming consistency、value minimality、governance overhead。
- 優先順位: 1) semantic tokens、2) contrast/readability、3) theme/platform compatibility、4) component mapping、5) primitive value expansion。
- 禁止事項: hex/pixel値の直接利用、ブランド色の無制限利用、alias/semantic layerなしのprimitive露出、命名ルールなしのtoken追加。
- 例外条件: one-off illustration/marketing asset。ただし product UI への流用は禁止。
- 承認者: Design Token Owner、Brand Lead、Accessibility Lead、Frontend Platform Lead、Design System Lead。
- 見直し頻度: brand refresh、theme addition、WCAG/legal update、platform update、major component release。

### Operating Model
- 役割: Design Token Owner、Visual/Brand Designer、Frontend Platform Engineer、Accessibility Specialist、Design System Maintainer。
- プロセス: value inventory → token taxonomy → naming rules → accessibility validation → platform transforms → component mapping → release/version → drift monitoring。
- 会議体: token review、brand/accessibility review、platform implementation review。
- レビュー: contrast、semantic naming、hard-coded value scan、theme output、design-code sync、breaking changes。
- 成果物: token taxonomy、token JSON、theme files、style dictionary/build outputs、usage docs、migration guide、visual regression suite。

### Technical / Business Specification
- Token hierarchy: `primitive/global → semantic/alias → component → state`。
- Token categories: color, typography, spacing, sizing, radius, border, elevation/shadow, opacity, z-index, motion, focus, support/status, breakpoints。
- Token names は意味を持つ。例: `color.text.primary`, `color.background.surface`, `space.component.md`, `focus.ring.default`。
- Contrast check は token composition 時点で行い、component usage で再検証する。
- Token file は DTCG format を参照し、platform output（web CSS variables、iOS、Android、Figma）を生成する。
- Deprecated token は alias/migration period/removal date を持つ。

### Metrics
- Token adoption、hard-coded style count、contrast violations、theme coverage、platform build success、visual regression diffs、deprecated token usage、design-code drift、token PR lead time。

### Failure Modes
- token 数が増えすぎ、選択肢が統制不能になる。
- primitive token を直接使い、テーマ変更や高コントラストで破綻する。
- design tool と code の token source が二重化する。
- contrast は単体値で確認したが、組み合わせで失敗する。
- component-specific token が乱立し、意味体系が崩れる。

### Anti-patterns
- token を単なる CSS variable の言い換えとして扱う。
- semantic layer なしで全色・全余白を公開する。
- デザイナーだけ/エンジニアだけで token taxonomy を決める。
- breaking change を release notes なしに行う。

### Maturity Model
- Level 0: 直接値が画面・CSSに散在。
- Level 1: 色/フォントの primitive 変数のみ。
- Level 2: semantic tokens と基本 theme がある。
- Level 3: component tokens、platform transforms、contrast checks がある。
- Level 4: token release/versioning、visual regression、hard-coded scan が運用。
- Level 5: DTCG互換、多ブランド/高コントラスト/多プラットフォーム/多言語の token system が継続改善。

### Clone Implementation Guide
1. CSS/Figma/コードから hard-coded values を棚卸しする。  
2. primitive / semantic / component token の3階層を定義する。  
3. WCAG contrast と focus/status tokens を先に安定化する。  
4. DTCG format を参照し、web/mobile/design tool output を生成する pipeline を作る。  
5. deprecated token usage と hard-coded style count を月次で監視する。

### Confidence & Unknowns
- 確度A: DTCG/USWDS/Fluent/Carbon の直接証拠。
- 確度B: Material/brand/platform token の横断パターン。
- 確度C: 各組織の token naming 具体ルール、brand approval threshold。
- 不明点: DTCG spec 実装の実普及率、各ツールの互換性、内部 design-to-code sync tooling。

### Validation Queries
- `site:designtokens.org "2025.10" "Design Tokens" "theming"`
- `site:fluent2.microsoft.design "Design tokens" "high-contrast"`
- `site:carbondesignsystem.com/elements "Tokens" "spacing" "color"`

---

## 7. Cross-cluster Failure Modes and Anti-patterns

| Failure Mode | Affected Layers | Mechanism | Prevention |
|---|---|---|---|
| Opinion-driven UX | 05.01–05.05 | 調査・指標・標準に接続せず、会議の好みで決定 | Research playback、decision log、task metrics |
| Accessibility-afterthought | 05.04–05.10 | 最終監査で欠陥が発覚し、大規模手戻り | Component-level a11y tests, release gate, owner/SLA |
| Bad ARIA / custom control failure | 05.05, 05.06, 05.09 | 見た目だけの custom UI が支援技術に伝わらない | Native-first, APG pattern, keyboard/screen reader tests |
| Design-code drift | 05.04, 05.08–05.10 | Figma、docs、code、tokens が同期しない | Token pipeline, Storybook, versioning, visual regression |
| Token sprawl | 05.08, 05.10 | token が増えすぎて統制不能 | Semantic taxonomy, review board, deprecation policy |
| Localization retrofit | 05.02, 05.04, 05.07, 05.10 | 翻訳後にレイアウト/意味/フォーマットが崩れる | Pseudo-localization, RTL, locale QA, string context |
| Pattern cargo cult | 05.01–05.09 | 他社パターンをユーザー文脈なしにコピー | Evidence requirement, usability testing, adaptation notes |
| Governance bottleneck | 05.08–05.10 | 中央チームしか更新できず、現場が迂回 | Contribution model, clear intake criteria, federated ownership |
| Legal baseline confusion | 05.06 | WCAG推奨と法的義務の差を誤認 | Jurisdiction matrix, legal review, conformance documentation |
| Motion/visual overload | 05.03–05.05, 05.10 | 情報伝達でなく装飾としてmotion/colorを使う | Reduced motion, non-color indicators, task-based testing |

---

## 8. Cluster QA / Validation Queries

These queries are intended to break or qualify the claims above.

1. `site:w3.org/TR/WCAG22 "WCAG 2.2" "does not address every user need"`
2. `site:w3.org/TR/using-aria "All interactive ARIA controls must be usable with the keyboard"`
3. `site:w3.org/TR/html-aria "MUST NOT" "conflicts with the semantics"`
4. `site:designsystem.digital.gov/documentation/accessibility "If it doesn’t pass, we don’t merge"`
5. `site:carbondesignsystem.com/guidelines/accessibility "WCAG AA" "Section 508"`
6. `site:gov.uk/service-manual "user research" "share findings" "design decisions"`
7. `site:design-system.service.gov.uk "release notes" "GOV.UK Frontend" "components"`
8. `site:designtokens.org "Design Tokens Technical Reports 2025.10" "not a W3C Standard"`
9. `site:digital-strategy.ec.europa.eu "EN 301 549" "WCAG 2.2" "not yet"`
10. `site:accessible-eu-centre.ec.europa.eu "European Accessibility Act" "28 June 2025"`
11. `site:w3.org/International "dir=rtl" "validate"`
12. `site:open-ui.org "accessibility requirements" "states" "behaviors"`

---

## 9. Implementation Roadmap for a Clone Organization

### Phase 0: Baseline inventory（2–4 weeks）
- 主要ユーザージャーニー、画面、コンポーネント、スタイル値、アクセシビリティ defect、翻訳対象文字列を棚卸し。
- WCAG/legal baseline と jurisdiction matrix を作成。
- UI/UX metrics の最低セットを定義。

### Phase 1: Foundation（4–8 weeks）
- UX decision log、research playback、design QA checklist を開始。
- 10 core components、basic tokens、accessibility testing checklist を整備。
- String inventory と pseudo-localization を導入。

### Phase 2: Systemization（8–16 weeks）
- Design system docs site / Storybook / token pipeline / visual regression を構築。
- Component contribution process と release/versioning を整備。
- Accessibility matrix と remediation SLA を導入。

### Phase 3: Adoption and Governance（16–32 weeks）
- プロダクト単位の adoption dashboard、exception log、migration plan を運用。
- Quarterly roadmap と contribution triage を定着。
- 障害当事者テスト、locale QA、design-system UX research を拡張。

---

## 10. Confidence & Unknowns

### A: Direct evidence
- WCAG 2.2、WAI-ARIA、APG、Using ARIA、ARIA in HTML、W3C i18n、ISO 9241-210/11、GOV.UK/USWDS/Carbon/Fluent/DTCG の公開文書。

### B: Strong inference from multiple evidence families
- Component-as-contract、tokens-as-source-of-truth、accessibility-as-release-gate、evidence-based patterns、motion-for-orientation。

### C: Reasonable but public-evidence-limited
- 各組織の内部レビュー会議、具体的な KPI threshold、design system funding model、deprecation enforcement、UX research cadence。

### D: Hypotheses not adopted as core claims
- 特定企業の内部 design maturity、未公開 component QA matrix、未公開 user research results。

### Unknowns / Follow-up
- 各 exemplar の実際の adoption rate と defect trend。
- コンポーネント別の支援技術サポート実測表。
- DTCG 2025.10 の実装普及率とツール間互換性。
- 法域ごとのEAA国内実装差分、調達要件、監督機関運用。
- Apple/Google/Microsoft/IBM の内部 design governance、承認閾値、失敗事例。

---

## 11. Minimal `clone_specs.csv` Projection

| spec_id | layer_id | version | decision_question | frontier_candidates | core_philosophy | primary_metrics |
|---|---|---|---|---|---|---|
| UXUI-05.01-v1 | 05.01 | 1.0 | どのユーザー/状況/目的に対し、どのタスク成功条件・検証方法・改善サイクルで体験を成立させるか | ISO 9241, GOV.UK, NN/g, USWDS | UXは利用結果の改善である | task success, error, satisfaction |
| UXUI-05.02-v1 | 05.02 | 1.0 | どの情報構造なら利用者が迷わず発見・理解・完了できるか | GOV.UK, USWDS, NN/g IA, W3C COGA | IAは組織分類ではなくユーザー探索モデル | findability, tree-test success |
| UXUI-05.03-v1 | 05.03 | 1.0 | どの状態遷移なら現在地・次アクション・完了条件を理解できるか | Material, Apple HIG, GOV.UK, WCAG/APG | 遷移は方向感覚と回復性の設計 | funnel completion, focus defects |
| UXUI-05.04-v1 | 05.04 | 1.0 | どのUI構造・視覚規則・標準部品で認知負荷を下げるか | Material, Apple, USWDS, Carbon, Fluent | UIは見た目と利用可能性の結合 | component reuse, contrast pass |
| UXUI-05.05-v1 | 05.05 | 1.0 | どの操作モデルなら全入力モードで安全・予測可能・可逆に使えるか | WAI-ARIA, APG, WCAG, NN/g | Interaction is semantic state plus feedback | keyboard coverage, error recovery |
| UXUI-05.06-v1 | 05.06 | 1.0 | どの基準・検査・責任・例外管理でアクセシビリティを保証するか | WCAG, USWDS, Carbon, ADA/EAA/508/EN301549 | A11y is continuous product quality | WCAG pass, critical defects |
| UXUI-05.07-v1 | 05.07 | 1.0 | どのi18n/l10n構造なら言語追加時に破綻しないか | W3C i18n, Apple, Fluent, GOV.UK | Locale is a first-class design variant | untranslated keys, RTL defects |
| UXUI-05.08-v1 | 05.08 | 1.0 | 何を共通資産化し、どの統治でプロダクト群へ配布するか | GOV.UK, USWDS, Carbon, Fluent, DTCG | Design system is a decision platform | adoption, duplicate components |
| UXUI-05.09-v1 | 05.09 | 1.0 | どのcomponent contractなら再利用しても挙動・品質が崩れないか | APG, Open UI, GOV.UK, USWDS, Carbon | Component is behavior + semantics + tokens | a11y pass, API defects |
| UXUI-05.10-v1 | 05.10 | 1.0 | どのtoken階層でブランドと可用性を全平台へ同期するか | DTCG, USWDS, Fluent, Carbon, Material | Tokens are portable design decisions | token adoption, hard-coded values |

---

## 12. Notes on Source Freshness

- WCAG 2.2 is current W3C Recommendation material, with W3C advising use of the most current version for new/update accessibility work [S04][S05].
- USWDS and GOV.UK Design System show active current releases/updates in 2026 [S17][S20][S21].
- Carbon showed active current component/library status and last update metadata in 2026 [S24].
- DTCG 2025.10 is stable/candidate community specification evidence, not a W3C Recommendation; use it as interoperability direction and implementation reference, not as a formal W3C standard [S35][S36].
- Legal baselines are jurisdiction-dependent; do not treat WCAG 2.2 recommendation status as automatically replacing EN 301 549 / Section 508 / ADA target standards [S39][S42][S43].
