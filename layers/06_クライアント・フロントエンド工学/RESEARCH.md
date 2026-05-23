# Frontier Operating Model Research: クライアント・フロントエンド工学（06）

Generated: 2026-05-13 JST  
Scope: Web / モバイル / デスクトップ / 組み込み、Browser / WebView / Native UI、HTML / CSS / JavaScript / TypeScript、DOM / イベント、状態管理、ルーティング、フォーム、PWA、ストレージ、ビルド / バンドル、セキュリティ、アクセシビリティ、性能、テスト、運用  
Method: `RESEARCH.md` の Frontier Operating Model Research プレイブックに基づく。公開情報のみを対象に、標準・公式ドキュメント・OSS公式文書・公開仕様・測定指標を優先した。  
Output type: Clone Spec + layer registry + evidence map + pattern library

---

## 0. Executive Summary

クライアント・フロントエンド工学の先端運用モデルは、単なる「UI実装」ではなく、**人間の操作、ブラウザ / OS / WebView の実行環境、ネットワーク、アクセシビリティ、セキュリティ、ローカル状態、ビルド成果物を、測定可能な契約として統制する意思決定システム**である。

本レイヤーの Frontier pattern は次の 7 点に集約される。

1. **標準ファースト**: HTML / DOM / CSS / ECMAScript / Web App Manifest / Service Worker / Storage / IndexedDB / WCAG / CSP のような標準・準標準を contract の基準にし、ライブラリは標準上に置く。
2. **互換性を仮説ではなく測定で管理**: Baseline、Web Platform Tests、Interop、ブラウザ互換表、実機 / 実ブラウザ E2E、RUM を使い、「動くはず」を「どの環境でどの程度動いたか」に変換する。
3. **UX品質を客観指標へ落とす**: LCP、INP、CLS、accessibility tree、フォーム完了率、エラー率、route transition latency、JS / CSS payload、hydration / render cost を SLI として扱う。
4. **状態・ルーティング・フォームを UI から分離する**: component local state、shared UI state、server state、URL state、form mutation、persistent offline state を分け、更新・検証・再同期の規則を明文化する。
5. **進歩的拡張と劣化時の設計**: JavaScript、Service Worker、WebView、OS API、storage quota、network availability、permission、third-party dependency が失敗しても、ユーザー操作と復旧経路が維持されるようにする。
6. **安全な境界を先に定義する**: DOM XSS、unsafe sink、CSP、Trusted Types、WebView IPC、Electron preload、Tauri capability、client storage secret、native bridge の境界を設計時にレビューする。
7. **ビルド成果物をプロダクト品質の一部として管理する**: bundle splitting、tree shaking、module target、source map、dependency audit、lockfile、browser target、cache strategy、release rollback を仕様化する。

このレイヤーで clone すべきものは、特定のフレームワーク名ではない。模倣対象は、**UI仕様、実行環境、データフロー、操作性、性能、アクセシビリティ、セキュリティ、ビルド成果物を一貫した decision model で制御する運用能力**である。

---

## 1. Layer Normalization

### Layer ID

`06`

### Layer Name

クライアント・フロントエンド工学

### Definition

ユーザーの端末上で実行される UI / インタラクション / 表示 / ローカル状態 / クライアント側データ処理 / ブラウザまたはネイティブ表示環境 / ビルド成果物を設計・実装・検証・運用するレイヤー。対象は Web、モバイル、デスクトップ、組み込み、WebView、Native UI を含む。

### Decision Object

「どのユーザー・端末・ブラウザ・OS・WebView・ネットワーク条件に対して、どの UI contract、状態 contract、操作 contract、性能 contract、セキュリティ境界、ビルド成果物を提供するか」

### Decision Question

世界トップの主体は、クライアント実行環境の差異、標準仕様、フレームワーク、状態管理、ルーティング、フォーム、PWA / storage、native bridge、ビルド / バンドル、性能、アクセシビリティ、セキュリティを、どの判断基準・閾値・例外・レビュー・測定で制御しているか。

### Primary Owner Roles

- Staff Frontend Engineer / Frontend Architect
- Web Platform Engineer
- Mobile UI Engineer / Native UI Engineer
- Design System Engineer
- Client Performance Engineer
- Accessibility Engineer
- Frontend Security Engineer
- Developer Experience / Build Tooling Engineer
- QA Automation / E2E Engineer
- Product Designer / UX Researcher
- Product Owner for client surface

---

## 2. Sublayer Registry（06）

提示された表では 06 の個別名称が明示されていないため、本成果物では「クライアント・フロントエンド工学」を 30 サブレイヤーへ正規化した。番号は調査・運用のための分解単位であり、既存台帳の正式名称がある場合は差し替える。

| Layer | Sublayer | Decision Object | Default Artifacts | Owner Roles | Default Metrics |
|---|---|---|---|---|---|
| 06.01 | クライアント戦略・実行環境選定 | Web / Native / Hybrid / PWA / Desktop / Embedded の選択 | platform decision record, target matrix | Frontend Architect, Product | delivery cost, UX fit, platform coverage |
| 06.02 | Web標準・互換性管理 | 使用可能な HTML/CSS/JS/Web API と fallback | baseline matrix, compatibility policy | Web Platform Engineer | browser pass rate, fallback coverage |
| 06.03 | レンダリング・ハイドレーション設計 | SSR / CSR / SSG / streaming / hydration / island の境界 | rendering ADR, route rendering map | Frontend Architect | TTFB, LCP, hydration cost |
| 06.04 | コンポーネント設計・Design System連携 | UI component contract と design token | component spec, token schema, Storybook | Design System Engineer | reuse rate, visual diff pass |
| 06.05 | HTMLセマンティクス・アクセシビリティ | 構造、ランドマーク、フォーム、ARIA使用境界 | semantic checklist, a11y review | Accessibility Engineer | WCAG pass, a11y tree completeness |
| 06.06 | CSS設計・レイアウト・レスポンシブ | layout, cascade, theming, motion, adaptive UI | CSS architecture, token map | Frontend Engineer, Designer | CLS, style payload, theme coverage |
| 06.07 | JavaScript / TypeScript言語規律 | language target, type safety, module discipline | tsconfig, lint rules, module policy | Staff Frontend Engineer | type errors, runtime error rate |
| 06.08 | DOM・イベント・入力モデル | event propagation, pointer/keyboard/touch, focus | interaction spec, input map | UI Engineer | input latency, focus trap defects |
| 06.09 | 状態管理 | local / shared / server / URL / persistent state の分離 | state model, store schema | Frontend Architect | duplicate state defects, stale data defects |
| 06.10 | ルーティング・ナビゲーション | route hierarchy, loaders/actions, transition behavior | route manifest, navigation contract | Frontend Engineer | route latency, broken navigation |
| 06.11 | フォーム・入力検証 | native validation, schema validation, mutation, error UX | form spec, validation schema | Frontend Engineer, Product | completion rate, validation error rate |
| 06.12 | PWA・Service Worker | installability, offline, cache, push, update lifecycle | manifest, SW strategy, update test | Web Platform Engineer | offline success, SW rollback time |
| 06.13 | クライアントストレージ | Web Storage / IndexedDB / Cache / quota / persistence | storage model, migration plan | Frontend Engineer | quota errors, migration failures |
| 06.14 | フロントエンドセキュリティ | XSS, CSP, Trusted Types, client secret policy | CSP, sink inventory, threat model | Security Engineer | CSP violations, XSS findings |
| 06.15 | 性能・Core Web Vitals | loading, responsiveness, visual stability | perf budget, RUM dashboard | Performance Engineer | p75 LCP/INP/CLS, JS bytes |
| 06.16 | ビルド・バンドル | bundler, transpilation, splitting, target | build config, bundle report | DX Engineer | build time, bundle size, cache hit |
| 06.17 | 依存関係・パッケージ統制 | npm/package risk, license, update cadence | lockfile policy, SBOM | DX/Security | vuln count, outdated critical deps |
| 06.18 | テスト・品質保証 | component/integration/E2E/visual/a11y/perf test | test pyramid, CI gates | QA Automation | flake rate, coverage, defect escape |
| 06.19 | RUM・クライアント観測 | field metrics, errors, session signals | telemetry schema, dashboard | Observability Engineer | RUM coverage, error budget burn |
| 06.20 | 国際化・地域化 | locale, language, bidi, timezone, number/date | i18n spec, translation workflow | Frontend/Product | missing translations, locale defects |
| 06.21 | モバイルUI工学 | mobile UI state, gestures, system UI, adaptive | mobile UI guidelines | Mobile UI Engineer | jank, crash-free sessions |
| 06.22 | iOS / Apple UI適合 | HIG, UIKit/SwiftUI/WebKit/WKWebView境界 | Apple platform checklist | iOS Engineer | HIG defects, app review issues |
| 06.23 | Android UI適合 | Material, Jetpack Compose, WebView, state holders | Android UI architecture | Android Engineer | recomposition/jank, ANR rate |
| 06.24 | WebView / Hybrid工学 | native bridge, navigation, JS binding, permissions | bridge spec, WebView policy | Hybrid Engineer | bridge errors, security findings |
| 06.25 | デスクトップフロントエンド | Electron/Tauri/native desktop shell | desktop shell spec | Desktop Engineer | startup time, IPC errors |
| 06.26 | 組み込み / HMIフロントエンド | constrained device UI, offline, graphics, input | HMI spec, hardware profile | Embedded UI Engineer | frame rate, boot-to-ui time |
| 06.27 | クロスプラットフォームUI | React Native / Flutter / Qt / MAUI等の境界 | platform abstraction ADR | Frontend/Mobile Architect | shared code %, platform defect rate |
| 06.28 | UIリリース・移行 | migration, deprecation, gradual rollout | rollout plan, migration guide | Release Engineer | rollback time, migration completion |
| 06.29 | フロントエンドガバナンス | review board, standards, ADR, exception process | governance charter | Staff Engineer | exception aging, review SLA |
| 06.30 | フロントエンド開発者体験 | scaffolding, local dev, HMR, docs, templates | starter kit, dev server, docs | DX Engineer | time-to-first-render, build failures |

---

## 3. Frontier Exemplars

| Exemplar | Evidence Tier | Why frontier-relevant | Transferable Decision Pattern |
|---|---:|---|---|
| WHATWG HTML Living Standard | T0 | HTML、forms、web storage、workers などの現行 Web contract を定義する living standard | UI 実装はライブラリより下位の標準 contract に合わせる |
| WHATWG DOM Standard | T0 | DOM events、EventTarget、event dispatch の基礎を定義 | 入力・イベント・ライフサイクルは標準イベントモデルで設計する |
| W3C CSS Snapshot / CSS WG | T0 | CSS の仕様安定性をスナップショットとして提示 | CSS採用は流行ではなく安定性と実装状況で判断する |
| ECMA-262 / TC39 | T0 | JavaScript の標準言語仕様と提案プロセス | JS language target と transpilation を標準版・proposal段階で分離する |
| Web.dev / Chrome Core Web Vitals / Baseline | T0/T2 | LCP/INP/CLS、75パーセンタイル評価、Baseline互換性を公開 | UX品質と互換性を定量ゲートとして運用する |
| W3C WCAG 2.2 / WAI | T0 | Web accessibility の国際的 recommendation | UI品質の最低線を WCAG とアクセシビリティツリーで定義する |
| React / Next.js / React Router | T2/T3 | component model、state model、App Router、Server Components、data router を公式化 | UI、route、server/client boundary、mutationを明示する |
| Redux Style Guide | T3 | shared state の推奨パターン・正規化・selector等を公開 | global state は domain model と normalized shape で管理する |
| Android Jetpack Compose / Material Design 3 | T0/T3 | unidirectional data flow、state holder、Material 3の実装指針を公式化 | native UI でも状態は一方向データフローで管理する |
| Apple Human Interface Guidelines | T0/T3 | Apple platform の設計原則・コンポーネント・更新情報を公開 | platform-native expectations を UI contract に含める |
| Electron / Tauri | T2/T3 | desktop WebView shell、IPC、context isolation、security boundaries を公開 | Web 技術を desktop 化するときは native boundary を最小権限化する |
| Qt Quick / QML | T2/T3 | embedded / desktop / cross-platform UI の公式UI framework | 組み込み・HMIは rendering、animation、C++ backend 連携を別設計にする |
| Playwright / Testing Library / Web Platform Tests | T2/T5 | browser automation、user-centric testing、標準互換テスト | テストは implementation detail ではなく user-visible contract に寄せる |

---

## 4. Source Catalog

| ID | Source | Type | Tier | Locator |
|---|---|---:|---:|---|
| S01 | WHATWG HTML Living Standard | standard | T0 | https://html.spec.whatwg.org/ |
| S02 | WHATWG DOM Living Standard | standard | T0 | https://dom.spec.whatwg.org/ |
| S03 | W3C Web Platform Design Principles | standard/guideline | T0 | https://www.w3.org/TR/design-principles/ |
| S04 | W3C CSS Snapshot 2026 | standard snapshot | T0 | https://www.w3.org/TR/css-2026/ |
| S05 | ECMA-262 ECMAScript 2025 | standard | T0 | https://ecma-international.org/publications-and-standards/standards/ecma-262/ |
| S06 | TypeScript Handbook | official docs | T2 | https://www.typescriptlang.org/docs/handbook/intro.html |
| S07 | Web.dev Baseline 2026 | official guidance | T2 | https://web.dev/baseline/2026 |
| S08 | Web.dev Web Vitals | official guidance | T2 | https://web.dev/articles/vitals |
| S09 | Web.dev Core Web Vitals thresholds | official guidance | T2 | https://web.dev/articles/defining-core-web-vitals-thresholds |
| S10 | W3C WCAG 2.2 | standard | T0 | https://www.w3.org/TR/WCAG22/ |
| S11 | W3C IndexedDB 3.0 | standard | T0 | https://www.w3.org/TR/IndexedDB/ |
| S12 | WHATWG Storage Standard | standard | T0 | https://storage.spec.whatwg.org/ |
| S13 | W3C Service Workers | standard | T0 | https://www.w3.org/TR/service-workers/ |
| S14 | W3C Web Application Manifest | standard | T0 | https://www.w3.org/TR/appmanifest/ |
| S15 | OWASP XSS Prevention Cheat Sheet | security guidance | T3 | https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html |
| S16 | OWASP DOM-based XSS Prevention Cheat Sheet | security guidance | T3 | https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html |
| S17 | W3C Content Security Policy Level 3 | standard | T0 | https://www.w3.org/TR/CSP3/ |
| S18 | W3C Trusted Types | standard draft | T0 | https://www.w3.org/TR/trusted-types/ |
| S19 | React: State as a Snapshot | official docs | T2 | https://react.dev/learn/state-as-a-snapshot |
| S20 | React: Managing State | official docs | T2 | https://react.dev/learn/managing-state |
| S21 | Next.js App Router | official docs | T2 | https://nextjs.org/docs/app |
| S22 | React Router | official docs | T2 | https://reactrouter.com/ |
| S23 | React Router Form | official docs | T2 | https://reactrouter.com/api/components/Form |
| S24 | Redux Style Guide | official docs | T3 | https://redux.js.org/style-guide/ |
| S25 | Redux Normalizing State Shape | official docs | T3 | https://redux.js.org/usage/structuring-reducers/normalizing-state-shape |
| S26 | Vite Guide | official docs | T2 | https://vite.dev/guide/ |
| S27 | Vite 8 announcement | release note | T3 | https://vite.dev/blog/announcing-vite8 |
| S28 | webpack Code Splitting | official docs | T2 | https://webpack.js.org/guides/code-splitting/ |
| S29 | webpack Tree Shaking | official docs | T2 | https://webpack.js.org/guides/tree-shaking/ |
| S30 | Rollup | official docs | T2 | https://rollupjs.org/ |
| S31 | esbuild | official docs | T2 | https://esbuild.github.io/ |
| S32 | Apple Human Interface Guidelines | official docs | T0/T3 | https://developer.apple.com/design/human-interface-guidelines |
| S33 | Material Design 3 | official docs | T0/T3 | https://m3.material.io/ |
| S34 | Android Compose UI Architecture | official docs | T2/T3 | https://developer.android.com/develop/ui/compose/architecture |
| S35 | Android UI State Production | official docs | T2/T3 | https://developer.android.com/topic/architecture/ui-layer/state-production |
| S36 | Android WebView | official docs | T2 | https://developer.android.com/reference/android/webkit/WebView |
| S37 | Apple WKWebView | official docs | T2 | https://developer.apple.com/documentation/webkit/wkwebview |
| S38 | Electron Context Isolation | official docs | T2/T3 | https://electronjs.org/docs/latest/tutorial/context-isolation |
| S39 | Electron BrowserWindow | official docs | T2 | https://electronjs.org/docs/latest/api/browser-window |
| S40 | Tauri Architecture | official docs | T2/T3 | https://v2.tauri.app/concept/architecture/ |
| S41 | Tauri Security | official docs | T3 | https://v2.tauri.app/security/ |
| S42 | Qt Quick / QML Applications | official docs | T2/T3 | https://doc.qt.io/qt-6/qmlapplications.html |
| S43 | Qt Quick Best Practices | official docs | T3 | https://doc.qt.io/qt-6/qtquick-bestpractices.html |
| S44 | React Native New Architecture | official docs | T2/T3 | https://reactnative.dev/architecture/landing-page |
| S45 | React Native Fabric Native Components | official docs | T2 | https://reactnative.dev/docs/fabric-native-components-introduction |
| S46 | Lighthouse | official docs | T2/T5 | https://developer.chrome.com/docs/lighthouse |
| S47 | Playwright Auto-waiting | official docs | T2/T3 | https://playwright.dev/docs/actionability |
| S48 | Playwright Best Practices | official docs | T3 | https://playwright.dev/docs/best-practices |
| S49 | Testing Library | official docs | T3 | https://testing-library.com/docs/ |
| S50 | Web Platform Tests | project docs | T5 | https://web-platform-tests.org/ |
| S51 | Interop 2026 / wpt.fyi | benchmark/dashboard | T5 | https://wpt.fyi/interop |

---

## 5. Evidence Map

| Claim ID | Claim | Field | Confidence | Supporting Sources |
|---|---|---|---:|---|
| C01 | HTML / forms / web storage / workers は WHATWG HTML Living Standard を基準に扱うべきである。 | rules / interface | A | S01 |
| C02 | DOM event handling は EventTarget と event dispatch の標準モデルに従うべきである。 | rules / interface | A | S02 |
| C03 | Web platform feature adoption は「仕様の安定性」と「ブラウザ互換性」を分離して評価する必要がある。 | criteria | A | S03, S04, S07, S50, S51 |
| C04 | ECMAScript の採用は ratified standard、draft、proposal を分けて管理する必要がある。 | rules | A | S05, TC39 proposal process |
| C05 | TypeScript は実行前に型整合性を確認する静的 typechecker として扱い、runtime safety そのものとは区別する。 | controls | A | S06 |
| C06 | Core Web Vitals の主要閾値は LCP 2.5s以内、INP 200ms以内、CLS 0.1以内で、p75で評価する。 | thresholds / metrics | A | S08, S09 |
| C07 | Accessibility は WCAG 2.2 と accessibility tree / semantic HTML の両面で検証する。 | controls / metrics | A | S10, S46 |
| C08 | Service Worker は browser / app / network 間の proxy 的役割を持つため、cache strategy と update lifecycle を設計対象にする必要がある。 | technical spec | A | S13 |
| C09 | Web App Manifest は installable web application の metadata contract であり、PWA仕様の必須成果物である。 | artifact | A | S14 |
| C10 | IndexedDB は key-value record と index を持つクライアント側構造化DBとして扱う。 | interface / storage | A | S11 |
| C11 | Storage quota / persistence は Storage Standard に従い、localStorage・IndexedDB・Cache を混同しない。 | rules | A | S12, S11, S13 |
| C12 | XSS対策は output encoding、safe DOM APIs、sink inventory、DOM-based XSS対策、CSP / Trusted Types に分解する必要がある。 | controls / failure_modes | A | S15, S16, S17, S18 |
| C13 | React state は render 時点の snapshot として扱い、重複 state は bug source と見なす。 | state model | A | S19, S20 |
| C14 | Routing は URL階層だけでなく data loading、mutation、pending state、revalidation を含む contract として扱う。 | routing / forms | A | S21, S22, S23 |
| C15 | Shared application state は正規化・selector・domain boundary を持つ場合に外部 state manager を採用する。 | decision rule | B | S20, S24, S25 |
| C16 | Build / bundling は dev feedback loop と production optimization を分離して設計する。 | build | A | S26, S27, S28, S30, S31 |
| C17 | Code splitting と tree shaking は load time と payload control の主要手段である。 | controls | A | S28, S29, S30 |
| C18 | Native UI は platform guideline への適合を品質要件として持つ。 | native UI | B | S32, S33, S34, S35 |
| C19 | Compose の UI state は state holder と unidirectional data flow に適合する。 | native state | A | S34, S35 |
| C20 | WebView は full browser と同等ではなく、navigation、JS binding、permission、security を別途設計する必要がある。 | WebView | A | S36, S37 |
| C21 | Electron は context isolation / preload / Node integration / webview tag の扱いをセキュリティ境界として明示する必要がある。 | desktop security | A | S38, S39 |
| C22 | Tauri は WebView + Rust backend + message passing / capability の境界設計が中核になる。 | desktop security | A | S40, S41 |
| C23 | Qt Quick / QML は fluid animated UI と C++ backend 連携のための公式パスであり、組み込み・デスクトップUIの重要選択肢である。 | embedded UI | B | S42, S43 |
| C24 | React Native New Architecture は JS/native boundary の serialization cost を JSI 等で減らす設計であり、native bridge decision に影響する。 | mobile hybrid | A | S44, S45 |
| C25 | UI testing は implementation detail より user-visible behavior と actionability を優先すべきである。 | QA | A | S47, S48, S49 |
| C26 | Cross-browser quality は Web Platform Tests / Interop / real-browser E2E で検証する。 | QA / compatibility | A | S50, S51, S47 |

---

## 6. Core Philosophy

### 6.1 標準を最下層の契約にする

Frontier organization は、React、Next.js、Vue、Svelte、Flutter、React Native、Electron のような実装選択を、HTML / DOM / CSS / ECMAScript / Web API / WCAG / security policy の上位抽象として扱う。フレームワークが変わっても、ユーザー入力、フォーム、リンク、フォーカス、アクセシビリティ、URL、ストレージ、セキュリティ境界の contract は標準に戻せるようにする。

### 6.2 UI品質を「見た目」ではなく contract として扱う

UI は画面仕様だけでは不十分である。先端運用では、component API、semantic role、keyboard navigation、focus management、loading / error / empty state、route transition、cache invalidation、state ownership、accessibility tree、visual regression、performance budget までを UI contract として扱う。

### 6.3 実行環境の差異を設計時に吸収する

Web / WebView / Native / Desktop / Embedded は同じ「画面」でも failure mode が異なる。Web は browser compatibility と network、Mobile は OS lifecycle と gesture、WebView は bridge と permission、Desktop は IPC と sandbox、Embedded は hardware budget と boot-time が支配的制約になる。Frontier pattern は「同一UIを無理に共通化する」ではなく、「共通化できる contract と platform-specific exception を分ける」である。

### 6.4 Client state は taxonomy で管理する

状態管理の失敗は、local UI state、server cache、URL state、form state、persistent offline state、native state、security-sensitive state を同じ store に入れることで起きる。先端組織は、state を種類ごとに owner・lifetime・persistence・source of truth・revalidation rule へ分解する。

### 6.5 性能・アクセシビリティ・セキュリティは後付けしない

LCP / INP / CLS、WCAG、CSP、Trusted Types、bundle budget、input latency、focus order、storage quota、cache strategy は、リリース直前の修正項目ではなく、最初の architectural decision に含める。

### 6.6 Build output is product output

`dist/` に出る JavaScript、CSS、asset、manifest、service worker、source map、chunk graph、cache header はプロダクト成果物である。Frontier team は、ビルドツールを単なる開発環境ではなく、性能・互換性・セキュリティ・運用性の制御面として扱う。

---

## 7. Decision Model

### Inputs

- User personas, device classes, browser / OS / WebView matrix
- Product interaction model: read-heavy, write-heavy, collaborative, offline, media, realtime, embedded, admin, ecommerce, content
- Accessibility requirements and legal / policy requirements
- Security threat model: XSS, token exposure, bridge abuse, third-party script, supply chain
- Network model: online-only, intermittent, offline-first, low bandwidth, high latency
- Rendering constraints: SEO, first load, auth wall, personalization, realtime updates, streaming, edge deployment
- Data model: server state, local state, URL state, form state, persistent cache, native state
- Platform API needs: camera, geolocation, filesystem, push, notification, native controls, IPC, hardware input
- Build constraints: browser target, package ecosystem, monorepo, CI time, SSR, source maps, CDN caching
- Observability signals: RUM, Core Web Vitals, client errors, replay, logs, E2E failure, support tickets

### Criteria

1. Standards conformance and forward compatibility
2. User-visible correctness under degraded conditions
3. Accessibility and semantic integrity
4. Performance at p75 field measurement, not only lab score
5. Security boundary clarity
6. State ownership and revalidation clarity
7. Browser / OS / device interoperability
8. Developer feedback loop and maintainability
9. Production build determinism
10. Migration and rollback safety

### Priorities

1. Protect user task completion and safety.
2. Preserve semantics, focus, keyboard, and accessibility before visual polish.
3. Prefer standards and progressive enhancement over framework-only behavior.
4. Keep state close to its source of truth; globalize only when lifetime and sharing demand it.
5. Measure field performance before optimizing lab-only numbers.
6. Minimize client-side authority; never store high-value secrets in browser persistence.
7. Define platform exceptions explicitly instead of hiding them behind a leaky abstraction.
8. Make build output auditable and repeatable.

### Prohibitions

- Using non-standard browser APIs without compatibility matrix and fallback.
- Storing access tokens, long-lived secrets, private keys, or high-risk authorization material in localStorage.
- Injecting untrusted HTML through `innerHTML` / unsafe sinks without sanitizer, Trusted Types policy, or explicit review.
- Replacing native form semantics with custom widgets without keyboard, focus, label, validation, and screen reader parity.
- Treating Lighthouse lab score as a substitute for RUM / field Core Web Vitals.
- Treating WebView as a full browser without separate navigation, permission, bridge, and update policy.
- Shipping a Service Worker without cache invalidation, versioning, update, and rollback test.
- Adding global state to solve prop drilling without lifetime/source-of-truth analysis.
- Bundling all route code into a single initial payload when route-level splitting is viable.
- Enabling Electron `nodeIntegration` or disabling context isolation for remote/untrusted content without exception approval.

### Thresholds

| Threshold | Default | Confidence | Evidence |
|---|---:|---:|---|
| LCP | p75 ≤ 2.5s | A | S08, S09 |
| INP | p75 ≤ 200ms | A | S08, S09 |
| CLS | p75 ≤ 0.1 | A | S08, S09 |
| Core Web Vitals pass | all three good at p75, segmented by mobile/desktop where possible | A | S08, S09 |
| Accessibility | WCAG 2.2 AA as default product baseline unless jurisdiction specifies otherwise | B | S10 |
| Browser target | Baseline Widely Available for production default; exceptions documented | B | S07, S26 |
| XSS controls | output encoding + safe DOM APIs + CSP; Trusted Types for high-risk DOM sinks | A | S15–S18 |
| Service Worker release | update/activate/rollback path tested before production | B | S13 |
| Build determinism | lockfile required; production bundle report generated per release | C | S26–S31 |
| E2E quality | critical flows run in at least Chromium + WebKit + Firefox or justified subset | B | S47–S51 |

### Owners

- Frontend Architect owns layer architecture and exception policy.
- Feature team owns component implementation, route behavior, forms, and state.
- Design System team owns tokens, reusable components, visual states, accessibility guidance.
- Security team owns CSP, Trusted Types, XSS review, WebView / desktop bridge threat model.
- Performance team owns Core Web Vitals, bundle budget, RUM instrumentation.
- DX team owns build system, scaffolding, package governance, local feedback loop.
- QA automation owns E2E, visual regression, a11y automation, cross-browser gates.
- Platform-specific native team owns iOS / Android / Desktop / Embedded exceptions.

### Cadence

- Per feature: UI contract review, state model review, a11y smoke, perf risk classification.
- Per route / screen: RUM instrumentation and critical-flow E2E.
- Per release: bundle report, Core Web Vitals dashboard review, dependency audit, CSP violation review.
- Per quarter: browser target and Baseline review, framework / bundler upgrade review, design system audit.
- Per major platform update: Apple HIG / Material / Android / WebView / Electron / Tauri / Qt compatibility review.

---

## 8. Operating Model

### 8.1 Roles

| Role | Responsibilities | Key Artifacts |
|---|---|---|
| Staff Frontend Engineer | Architecture decisions, review standards, exception arbitration | ADR, layer spec, exception register |
| Web Platform Engineer | Browser compatibility, standards tracking, PWA/storage/Web API | compatibility matrix, Web API policy |
| Design System Engineer | Component contract, tokens, visual/a11y states | component spec, token schema |
| Accessibility Engineer | WCAG mapping, semantic review, assistive tech checks | a11y checklist, test results |
| Performance Engineer | CWV, RUM, bundle and render budgets | RUM dashboard, perf budget |
| Security Engineer | XSS, CSP, Trusted Types, WebView/Desktop bridge review | threat model, CSP policy, sink inventory |
| Mobile / Native Engineer | iOS/Android platform correctness | platform checklist, native bridge spec |
| DX / Build Engineer | Vite/Webpack/Rollup/esbuild config, CI, monorepo tooling | build config, CI gates, starter templates |
| QA Automation Engineer | E2E, component tests, visual/a11y/perf tests | test plan, flake dashboard |

### 8.2 Process

1. **Surface classification**: featureを Web route、PWA、WebView、Native UI、Desktop shell、Embedded HMI に分類する。
2. **Contract draft**: route/component/form/state/storage/security/performance contract を 1 枚にまとめる。
3. **Compatibility decision**: target browser / OS / device / WebView / native platform を明記し、Baseline と exception を確認する。
4. **State model review**: local/shared/server/URL/form/persistent/native state の ownership と revalidation を決める。
5. **Security boundary review**: DOM sink、third-party script、CSP、storage secret、native bridge、IPC、permission を確認する。
6. **Build impact review**: route chunk、dependency、polyfill、transpilation target、service worker、manifest、CSS payload を確認する。
7. **Implementation**: component-driven に実装し、native semantics を壊さない。
8. **Validation**: component/user-centric test、E2E、a11y automation、RUM instrumentation、bundle diff、manual assistive tech smoke を通す。
9. **Release**: canary / progressive rollout、CSP report-only to enforce、SW update monitoring、rollback path を確認する。
10. **Post-release learning**: p75 CWV、client error、form abandonment、route latency、support tickets を確認し、pattern library を更新する。

### 8.3 Required Artifacts

- Platform target matrix
- Component contract and design token map
- Semantic HTML / ARIA checklist
- Route manifest and rendering strategy
- State model diagram
- Form validation schema and error UX spec
- PWA manifest and Service Worker strategy
- Storage model and data migration plan
- CSP / Trusted Types / XSS sink inventory
- WebView / native bridge / IPC contract
- Build config and bundle report
- E2E critical-flow suite
- RUM / Core Web Vitals dashboard
- Exception register and migration guide

---

## 9. Technical / Business Specification

### 9.1 Platform Targeting and Compatibility

**Rule**: Default target is web standards + Baseline-compatible browser set. Features outside Baseline or outside supported browser matrix require progressive enhancement, polyfill, or product exception.

Decision checklist:

- Which browser engines are target: Chromium, WebKit, Gecko?
- Is the feature Baseline Widely Available, Newly Available, limited, or experimental?
- Does the feature work in embedded WebView, not only full browser?
- Is server rendering or static rendering required for SEO / first load?
- Does the feature degrade to native HTML, server round-trip, or alternate UI?
- Does the application need Web Platform Tests / Interop awareness for this feature?

Implementation pattern:

```text
Feature proposal
  -> standards/spec status
  -> Baseline/browser support
  -> target user device share
  -> fallback/progressive enhancement
  -> E2E coverage across browser engines
  -> production RUM verification
```

### 9.2 Rendering and Hydration

Rendering decisions should be made per route, not per application.

| Route Type | Preferred Strategy | Risk | Control |
|---|---|---|---|
| Public content / SEO route | SSR / SSG / streaming | hydration cost, content mismatch | route-level CWV + hydration warning gate |
| Authenticated dashboard | CSR + data loader or SSR depending on latency | loading waterfalls | skeleton + server-state cache |
| Highly interactive editor | CSR / island / worker offload | INP / main thread blocking | interaction profiling + code splitting |
| Ecommerce / conversion route | SSR/SSG + minimal client JS | CLS/LCP regression | image/layout budget + RUM |
| Offline-first route | PWA + IndexedDB + SW strategy | stale data, cache poisoning | versioned cache + conflict UX |

Next.js App Router and React Router data APIs show the movement from page-only routing to route-level data and mutation contracts. The clone spec should therefore require each route to define loading, pending, error, mutation, revalidation, and cache behavior.

### 9.3 HTML / CSS / JavaScript / TypeScript

**HTML**

- Use semantic elements before ARIA.
- Preserve native link and button semantics.
- Use native form controls where possible.
- Use `form.requestSubmit()` rather than bypassing validation when programmatic submission must behave like user submission.
- Do not replace browser primitives unless accessibility parity is proven.

**CSS**

- Use CSS Snapshot and browser support to determine feature maturity.
- Prefer design tokens for color, spacing, typography, motion, and density.
- Use logical properties for internationalization and writing modes.
- Use media queries / container queries / responsive layout with explicit fallback.
- Treat CLS as a CSS and layout contract issue, not merely performance issue.

**JavaScript / TypeScript**

- Use ECMAScript standard target and transpilation target explicitly.
- Treat TypeScript as compile-time guard, not runtime validation.
- Prefer ESM and static imports for tree shaking; use dynamic imports for route or feature boundaries.
- Avoid proposal-stage features in production unless toolchain and browser target are controlled.
- Maintain `tsconfig` strictness and linting rules as governance artifacts.

### 9.4 DOM / Events / Input

Interaction model must include:

- Keyboard behavior and focus movement.
- Pointer, touch, mouse, and gesture differences.
- Event propagation and cancellation policy.
- Scroll behavior and scroll restoration.
- Composition input and IME behavior.
- Accessibility tree and screen reader announcement.
- Form submit, validation, and native browser behavior.

Decision rule: Do not implement custom controls unless the team can specify role, name, state, keyboard interaction, focus behavior, disabled state, error state, and assistive technology behavior.

### 9.5 Component and Design System Engineering

A component is approved only when it defines:

- Public props / slots / events.
- Semantic element mapping.
- Accessibility states.
- Loading / empty / error / disabled / readonly / pending states.
- Theming and token usage.
- Responsive behavior.
- Visual regression baseline.
- Interaction tests.
- Breaking change policy.

Frontier pattern: design system components are **contracts**, not merely reusable visuals.

### 9.6 State Management

State taxonomy:

| State Type | Source of Truth | Persistence | Default Tooling | Anti-pattern |
|---|---|---|---|---|
| Local UI state | component | ephemeral | React state / framework local state | global store for modal/input microstate |
| Shared UI state | UI subtree / domain | session | context, reducer, small store | duplicated state across components |
| Server state | backend/API | server cache | query/cache library or route loader | copying server data to global UI store |
| URL state | browser URL | shareable | router/search params | hidden filter state that cannot be linked |
| Form state | form model | until submit/draft | native form + schema + action | validation only after submit with poor errors |
| Persistent offline state | IndexedDB/Cache | durable | IndexedDB, Cache API | localStorage for large structured data |
| Security-sensitive state | memory/server | short-lived | httpOnly cookies, memory, worker | localStorage secrets |
| Native state | OS/native module | platform | native state holder / bridge | JS assumes native operation is synchronous |

Decision rule:

1. Keep state local until it needs sharing.
2. Derive instead of duplicate.
3. Normalize collections when lookup/update frequency or relational shape requires it.
4. Use URL state for shareable navigation/filtering.
5. Separate server cache from UI state.
6. Persist only with migration, quota, encryption/secret policy, and conflict handling.

### 9.7 Routing and Navigation

Routing contract must specify:

- Route hierarchy and layout nesting.
- URL schema and canonical URL.
- Data loading owner.
- Mutation/action owner.
- Pending UI and optimistic update policy.
- Error boundary and not-found behavior.
- Scroll restoration.
- Authorization state and redirects.
- Analytics pageview rule for SPA/PWA.
- Prefetch policy and bandwidth constraints.

Decision rule: A route is not just a component. A route is the smallest externally addressable UI contract.

### 9.8 Forms and Validation

Form specification requires:

- Native control mapping.
- Label, hint, required, autocomplete, inputmode.
- Client validation and server validation boundary.
- Constraint validation usage.
- Async validation policy.
- Error message placement and screen reader announcement.
- Draft / autosave / offline behavior.
- Submit idempotency and duplicate submit prevention.
- Mutation success, revalidation, and redirect behavior.

Frontier pattern: keep browser form semantics where possible; enhance progressively with router/action APIs, pending state, and revalidation.

### 9.9 PWA, Service Worker, and Storage

PWA requires:

- Web App Manifest.
- Service Worker registration / update strategy.
- Cache strategy per asset/data class.
- Offline fallback route.
- IndexedDB schema and migration plan if structured offline data is used.
- Quota and eviction handling.
- Conflict resolution if offline writes are allowed.
- Push / notification permission UX if applicable.
- Clear uninstall / data clearing expectations.

Storage decision:

| Storage | Use | Avoid |
|---|---|---|
| memory | short-lived UI/session-sensitive data | long-lived offline needs |
| sessionStorage | per-tab transient state | security secrets, cross-tab coordination |
| localStorage | small non-sensitive preferences | tokens, large data, high-frequency writes |
| IndexedDB | large structured data, offline datasets | simple transient flags |
| Cache API | request/response cache | app data that requires query/index |
| cookies | server session / httpOnly auth | large client data |

### 9.10 Security

Mandatory controls:

- DOM sink inventory: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, script URL, `eval`, dangerous template injection.
- Output encoding by context: HTML, attribute, URL, JavaScript, CSS.
- CSP: start report-only, monitor violations, enforce after allowlist stabilizes.
- Trusted Types for high-risk applications or legacy DOM sink surfaces.
- Third-party script governance and subresource policy.
- No high-risk secrets in persistent browser storage.
- WebView JS bridge allowlist.
- Electron: context isolation on, `nodeIntegration` off for untrusted content, preload whitelist, `<webview>` disabled unless reviewed.
- Tauri: capability / permission boundaries and CSP.
- Source map policy: no public leakage of sensitive source or secrets.

### 9.11 Build / Bundle / Toolchain

Build decision fields:

- Bundler: Vite / webpack / Rollup / esbuild / framework-integrated.
- Dev mode optimizer vs production optimizer.
- Browser target and transpilation target.
- Code splitting strategy: route, component, vendor, worker, dynamic import.
- Tree shaking strategy: ESM, side effects policy, package fields.
- CSS extraction and critical CSS policy.
- Asset optimization: image formats, responsive images, fonts, preload/preconnect.
- Source map and error symbolication policy.
- Dependency and license governance.
- CI cache and deterministic build.

Decision rule:

- Vite-like tooling optimizes feedback loop and production build defaults.
- webpack remains strong for mature plugin ecosystems and complex legacy configs.
- Rollup is strong for ESM libraries and tree-shaking-oriented output.
- esbuild is strong for speed and transform/bundle workloads, but feature fit must be checked.

The clone spec should avoid one-size-fits-all bundler selection. Selection must be based on route architecture, library/application output, plugin needs, SSR integration, monorepo scale, and migration risk.

### 9.12 Mobile, WebView, Desktop, Embedded

**Mobile Native UI**

- Respect platform navigation, gestures, safe area, accessibility, text scaling, keyboard, lifecycle.
- Android Compose: define UI state holder and unidirectional data flow.
- Apple platforms: use HIG as platform expectation contract.
- Material Design 3: use component, motion, color, typography guidance for Android surfaces.

**WebView / Hybrid**

- Treat WebView as controlled embedded renderer, not a browser clone.
- Specify allowed origins, navigation handling, JS bridge contract, permission handling, storage/cookie model, update model.
- Avoid exposing broad native APIs to arbitrary web content.

**Desktop**

- Electron: sandbox, context isolation, preload, IPC, Node integration, remote content policy.
- Tauri: WebView + Rust backend, message passing, capability boundaries, CSP.
- Desktop-specific UX: menus, shortcuts, file system, windowing, update, crash recovery.

**Embedded / HMI**

- Define hardware profile: CPU/GPU/RAM, boot time, display resolution, input mode, offline behavior.
- Prefer deterministic rendering and resource budgets.
- Use Qt Quick / QML or similar frameworks when fluid UI + C++ backend integration and platform reach are critical.

---

## 10. Metrics

### Quality / UX

- Task completion rate
- Form completion rate
- Validation error rate
- Navigation success rate
- UI defect escape rate
- Support tickets per route / feature

### Performance

- p75 LCP ≤ 2.5s
- p75 INP ≤ 200ms
- p75 CLS ≤ 0.1
- JS initial payload per route
- CSS payload per route
- Hydration duration
- Long tasks per session
- Route transition latency
- Time to interactive action
- WebView startup time / desktop startup time / embedded boot-to-ui time

### Accessibility

- WCAG 2.2 AA pass rate
- Automated a11y violations by severity
- Keyboard-only critical flow pass rate
- Screen reader smoke pass rate
- Accessibility tree completeness
- Focus order defects

### Security

- CSP violation rate by directive
- Trusted Types violations
- Unsafe DOM sink count
- Third-party script count
- Client-side secret findings
- Dependency vulnerabilities by severity
- WebView / IPC bridge findings

### Reliability / Operations

- Client error rate
- Crash-free sessions for native / hybrid surfaces
- E2E flake rate
- Service Worker update success rate
- Offline operation success rate
- IndexedDB migration success rate
- Rollback time

### Developer Experience

- Time to first local render
- HMR / fast refresh latency
- Build time
- CI duration
- Bundle analysis time
- Dependency update lead time
- Framework / bundler upgrade effort

---

## 11. Failure Modes

| Failure Mode | Typical Cause | Detection | Prevention / Control |
|---|---|---|---|
| Good lab score, poor field UX | lab device/network differs from users | RUM p75 CWV | field-first performance budget |
| Hydration mismatch | SSR and client state diverge | console/runtime errors, E2E | route-level rendering contract |
| Duplicate state bugs | server/local/global state copied | stale UI, inconsistent data | state taxonomy and single source of truth |
| Invisible accessibility regression | visual QA only | a11y tests, screen reader smoke | semantic component contract |
| Custom control keyboard failure | replacing native controls | keyboard E2E | native-first forms and controls |
| DOM XSS | unsafe sink with untrusted data | security scan, CSP/TT violation | sink inventory, encoding, Trusted Types |
| Stale PWA shell | SW caches HTML/app shell incorrectly | support tickets, version mismatch | versioned cache, update prompts, rollback test |
| Storage migration data loss | IndexedDB schema change unmanaged | migration errors, user reports | schema versioning and migration tests |
| WebView bridge abuse | broad JS-native API exposure | security review, pentest | allowlisted bridge and origin checks |
| Electron privilege escalation | nodeIntegration/contextIsolation misconfig | security audit | context isolation and preload whitelist |
| Bundle bloat | route code / vendor code uncontrolled | bundle report, CWV | code splitting, tree shaking, budget gate |
| Cross-browser breakage | Chromium-only testing | WebKit/Firefox E2E failure | Interop/WPT awareness and browser matrix |
| Native platform mismatch | ignoring HIG/Material/system UI | usability defects, app review | platform guideline checklist |
| Embedded jank | resource budget ignored | frame drops, telemetry | hardware profile and render budget |

---

## 12. Anti-patterns

1. **Framework monoculture as architecture**: 「Reactを使う」などの選択を、状態・routing・security・a11y・performance の設計の代替にする。
2. **SPA by default**: route別に SSR/SSG/CSR/PWA を判断せず、全画面を単一CSRにする。
3. **Global store dumping**: local form state、server data、URL state、UI toggles、offline data を同じ global store に入れる。
4. **A11y after visual completion**: semantic HTML と keyboard/focus を実装後に修正する。
5. **PWA without lifecycle**: Service Worker を入れたが cache invalidation / update prompt / rollback を設計しない。
6. **localStorage auth**: 永続 Web Storage に access token や高価値 secret を置く。
7. **Unsafe HTML convenience**: Markdown/HTML rendering を sanitizer / Trusted Types / CSP なしで行う。
8. **Chromium-only QA**: 実装・E2E・手動確認が Chromium に偏る。
9. **Build tool as black box**: bundler設定、target、polyfill、chunk graph、source map、cache header をレビューしない。
10. **Leaky cross-platform abstraction**: iOS/Android/Web/Desktop/Embedded の期待差を隠し、UX欠陥を「共通化」で生む。
11. **WebView as browser**: full browser と同じ前提で storage、navigation、permission、security を扱う。
12. **Pixel-only design system**: component contract に role/name/state/focus/keyboard/loading/error を含めない。

---

## 13. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | UI実装が個人依存。標準・互換性・a11y・security・build output の管理がない。 |
| 1 | 個別最適 | フレームワークとビルドはあるが、状態・routing・forms・performance はチームごとにばらつく。 |
| 2 | 文書化 | browser target、component guidelines、state conventions、build config、a11y checklist が存在する。 |
| 3 | 標準化 | route/component/form/storage/security/perf contract が標準化され、CIで一部検査される。 |
| 4 | 自動化・計測 | RUM、CWV、bundle budget、a11y automation、cross-browser E2E、security policy violation が継続監視される。 |
| 5 | 自律改善・業界先端 | 標準動向・Baseline・Interop・platform updates を定期反映し、pattern library と exception register が組織横断で更新される。 |

---

## 14. Clone Implementation Guide

### Phase 1: 0–30 days — 現状把握とガードレール

Deliverables:

- Client surface inventory: Web / Mobile / Desktop / Embedded / WebView の一覧。
- Browser / OS / WebView target matrix。
- Critical user flows top 10。
- Current Core Web Vitals / client error baseline。
- Current bundle report and dependency risk inventory。
- Accessibility smoke findings。
- XSS sink inventory and current CSP status。
- Service Worker / PWA / storage inventory。

Actions:

1. すべてのクライアント surface を分類し、routing / rendering / storage / build / deployment を棚卸しする。
2. 主要 route で RUM と client error collection を確認する。
3. Critical flows を Playwright 等で 1 ブラウザからでも自動化し、後続で複数ブラウザへ広げる。
4. `localStorage` / `sessionStorage` / IndexedDB / cookies / Cache API の利用箇所を調べ、secret risk を除去する。
5. Bundle analyzer を導入し、route単位の initial JS/CSS を可視化する。

### Phase 2: 31–90 days — Contract 化

Deliverables:

- Frontend architecture standard。
- Component contract template。
- State taxonomy and decision tree。
- Route manifest template。
- Form spec template。
- PWA / storage strategy。
- CSP report-only policy and violation dashboard。
- Bundle budget and build output gate。
- Cross-browser E2E critical flows。

Actions:

1. 状態管理を local/shared/server/URL/form/persistent に分類し、各 feature の state owner を修正する。
2. Component spec に semantic role、focus、keyboard、a11y、error/loading/disabled states を追加する。
3. Routeごとに rendering strategy、data loader、pending/error、cache、revalidation を定義する。
4. CSPを report-only から始め、違反を減らして enforce へ段階移行する。
5. p75 CWV で routeごとの改善 backlog を作る。

### Phase 3: 91–180 days — 自動化と移行

Deliverables:

- Enforced CI gates: type/lint/unit/component/E2E/a11y/bundle/security。
- RUM-driven performance budgets。
- Service Worker update/rollback tests。
- IndexedDB migration tests。
- Native / WebView bridge security checklist。
- Exception register and quarterly review。
- Pattern library initial release。

Actions:

1. Critical flows を Chromium / WebKit / Firefox または対象環境に拡張する。
2. Trusted Types を high-risk DOM sink へ導入する。
3. SW / cache / manifest / offline fallback の release test を整備する。
4. WebView / Electron / Tauri の native bridge を allowlist 化する。
5. Framework / bundler upgrade を release process に組み込み、migration guide と rollback を標準化する。

### Phase 4: 181+ days — 継続改善

Deliverables:

- Quarterly browser / Baseline / platform update review。
- Standards watch: WHATWG/W3C/CSSWG/TC39。
- Design system maturity scorecard。
- Client quality business dashboard。
- Frontend incident taxonomy and postmortems。

Actions:

1. Interop / Web Platform Tests / Baseline の変化を定期的に取り込む。
2. UI incidents を performance、a11y、state、storage、build、security、platform mismatch に分類して pattern library に反映する。
3. Product KPI と client quality metric の相関を見て投資優先度を再配分する。

---

## 15. Pattern Library

| Pattern ID | Pattern | Type | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---:|
| P01 | Standards-first progressive enhancement | principle | 標準HTML/DOM/CSSを基盤に、JS/Framework/Web APIを段階的に追加する | public web surface | advanced UX may require more design effort | A |
| P02 | Route as contract | decision_rule | routeをURL + data + mutation + loading + error + analytics + cacheの単位にする | routed app | framework dependence if overcoupled | A |
| P03 | State taxonomy before store | decision_rule | store選定前に state type / owner / lifetime / source を分類する | complex UI | upfront design cost | A |
| P04 | Native-form-first | operating_model | browser form semanticsを保持し、JSで progressively enhance する | form-heavy product | custom visual control requires adapter | A |
| P05 | Field-first performance budget | metric | Lighthouseではなく RUM p75 CWV を最終評価軸にする | sufficient traffic or synthetic proxy | low traffic pages need lab fallback | A |
| P06 | Secure client boundary | control | DOM sinks、CSP、Trusted Types、storage secrets、bridgeを一体管理する | user input / rich text / WebView | CSP adoption has rollout friction | A |
| P07 | Build output governance | operating_model | chunk graph、target、polyfill、source maps、cacheをreview対象にする | modern build toolchain | requires DX ownership | B |
| P08 | WebView allowlisted bridge | control | Native bridgeはorigin + capability + method allowlistで限定する | Hybrid/WebView app | more boilerplate | A |
| P09 | Service Worker release lifecycle | control | SWをversioned cache, update prompt, rollback testで管理する | PWA/offline app | release complexity | A |
| P10 | User-centric test selectors | testing | implementation detailではなくrole/name/text/test contractで操作する | accessible components | tests may need better a11y names | A |
| P11 | Platform-native exception register | governance | cross-platform共通化できない差分を明示して管理する | iOS/Android/Desktop/Embedded | may reduce shared code ratio | B |
| P12 | Component contract maturity | maturity_pattern | componentをvisual unitではなく semantic + state + a11y + test contractにする | design system | design/engineering coordination cost | A |

---

## 16. Validation Queries

Use these queries periodically to challenge the clone spec and find regressions, counterexamples, or outdated assumptions.

```text
site:html.spec.whatwg.org "forms" "requestSubmit" "constraint validation"
site:dom.spec.whatwg.org "EventTarget" "addEventListener" "dispatch"
site:w3.org/TR/css-2026 "current state of Cascading Style Sheets"
site:web.dev "Core Web Vitals" "75th percentile" "INP"
site:web.dev/baseline "Baseline Widely available" "2026"
site:w3.org/TR/WCAG22 "success criteria" "2.2"
site:w3.org/TR/service-workers "update" "cache" "fetch event"
site:w3.org/TR/appmanifest "metadata" "launch" "icon"
site:cheatsheetseries.owasp.org "DOM based XSS" "innerHTML"
site:w3.org/TR/CSP3 "fetch or execute" "policy"
site:w3.org/TR/trusted-types "attacker-controlled inputs"
site:react.dev "State as a Snapshot" "duplicate state"
site:nextjs.org/docs/app "Server Components" "Suspense" "Server Functions"
site:reactrouter.com "loader" "action" "Form" "revalidated"
site:redux.js.org "Normalizing State Shape" "selectors"
site:vite.dev "Baseline Widely Available" "production builds"
site:webpack.js.org "code splitting" "tree shaking"
site:electronjs.org "contextIsolation" "nodeIntegration" "preload"
site:v2.tauri.app "capabilities" "security" "Webview"
site:developer.android.com "unidirectional data flow" "Compose" "UI state"
site:developer.apple.com/design "Human Interface Guidelines" "what's new"
site:playwright.dev "auto-waits" "actionability"
site:testing-library.com "Guiding Principles" "resemble how users interact"
site:web-platform-tests.org "cross-browser test suite"
"{product}" (incident OR outage OR rollback OR deprecation OR migration) "frontend"
"{framework_or_tool}" (breaking change OR migration OR security advisory OR CVE)
```

---

## 17. Confidence & Unknowns

### Confidence A

- HTML / DOM / CSS / ECMAScript / Service Worker / Web App Manifest / Storage / IndexedDB / WCAG / CSP / Trusted Types の標準・仕様に基づく contract。
- Core Web Vitals の p75 閾値。
- React state snapshot、React Router Form/data behavior、Android Compose unidirectional data flow、Electron context isolation、Tauri architecture/security など公式文書で直接確認できる設計原則。

### Confidence B

- WCAG 2.2 AA を default baseline とする運用判断。標準そのものは A だが、AA をどのプロダクトに義務化するかは組織・法域・契約により変わる。
- Baseline Widely Available を production target とする判断。Vite などの公式 default と Web.dev Baseline に裏付けられるが、プロダクトのユーザー分布次第で例外が必要。
- Native / cross-platform UI における platform-native exception register。公式 guideline から強く推定できるが、各企業の組織設計は非公開。

### Confidence C

- Initial JS / CSS bundle size の具体閾値。公式標準の universal threshold はないため、RUM と business KPI から組織別に設定すべき。
- Team topology、review board、quarterly cadence の具体頻度。公開情報から一般化した運用推定であり、組織の規模・規制・リリース頻度に合わせる必要がある。
- Embedded / HMI の詳細性能閾値。hardware profile に大きく依存する。

### Unknowns

- 各 frontier 企業の内部 review board、exception approval、incident taxonomy、actual bundle budget は公開情報だけでは確定できない。
- Browser / OS / WebView の実ユーザー分布がないため、target matrix は仮設である。
- 組織内のデザインシステム成熟度、既存 codebase、framework lock-in、native skill mix によって clone implementation の順序は変わる。
- PWA / offline / IndexedDB の採否は product domain と規制要件に大きく依存する。

---

## 18. Minimal Clone Spec Checklist

```yaml
layer: 06_client_frontend_engineering
required_decisions:
  - platform_target_matrix
  - browser_baseline_policy
  - route_rendering_strategy
  - component_contract_template
  - state_taxonomy
  - routing_data_mutation_contract
  - form_validation_contract
  - pwa_service_worker_policy
  - storage_and_migration_policy
  - frontend_security_policy
  - webview_native_bridge_policy
  - build_bundle_policy
  - performance_budget
  - accessibility_baseline
  - testing_strategy
  - rum_observability_schema
minimum_quality_gates:
  - typecheck_and_lint
  - component_contract_review
  - accessibility_automation
  - critical_flow_e2e
  - bundle_report
  - csp_or_security_review_for_high_risk_surfaces
  - p75_core_web_vitals_monitoring
  - dependency_audit
exception_register_required_for:
  - non_baseline_web_api
  - custom_accessibility_control
  - localStorage_sensitive_data
  - unsafe_dom_sink
  - webview_bridge_method
  - electron_node_integration
  - service_worker_cache_html
  - global_state_for_server_data
  - unsupported_browser_or_os
```

---

## 19. Short Implementation Templates

### 19.1 Route Contract Template

```markdown
Route:
URL pattern:
Rendering mode: SSR / SSG / CSR / streaming / island / native
Data loader:
Mutation/action:
Pending UI:
Error boundary:
Not found behavior:
Auth/permission:
SEO/canonical:
Analytics pageview:
Cache/revalidation:
Offline behavior:
Performance budget:
Accessibility notes:
Security notes:
E2E critical flow:
```

### 19.2 State Decision Template

```markdown
State name:
Type: local_ui / shared_ui / server / url / form / persistent / native / security_sensitive
Source of truth:
Owner:
Lifetime:
Persistence:
Revalidation:
Serialization:
Migration:
Security classification:
Failure behavior:
```

### 19.3 Component Contract Template

```markdown
Component:
Purpose:
Native semantic element:
ARIA role/name/state:
Keyboard behavior:
Focus behavior:
Visual states:
Loading/error/empty states:
Responsive behavior:
Tokens used:
Events emitted:
Props/slots:
Breaking change policy:
A11y tests:
Visual tests:
E2E usage:
```

### 19.4 Frontend Security Review Template

```markdown
Surface:
Untrusted input sources:
DOM sinks:
HTML rendering:
Third-party scripts:
CSP directives:
Trusted Types policy:
Storage of sensitive data:
WebView/native bridge:
Electron/Tauri/native permissions:
Source maps:
Residual risk:
Approval:
```

---

## 20. Final Clone Specification

クライアント・フロントエンド工学を clone する組織は、まず framework selection ではなく、**client surface contract** を定義するべきである。contract には、標準互換性、route単位の rendering/data/mutation、component semantics、state taxonomy、forms、storage、PWA、security boundary、performance budget、accessibility baseline、build output、cross-browser/native validation を含める。

最小実装は次の順で進める。

1. 対象 surface と target matrix を確定する。
2. Critical routes と critical flows を特定する。
3. Component / route / state / form の contract template を導入する。
4. RUM と bundle report を導入し、p75 CWV と initial payload を測定する。
5. XSS sink、client storage、CSP、WebView/native bridge をレビューする。
6. Critical flows を user-centric E2E で自動化し、対象ブラウザ / OS / WebView へ広げる。
7. PWA / Service Worker / IndexedDB を採用する場合だけ、release lifecycle と migration tests を義務化する。
8. Quarterly に Baseline、browser support、framework/bundler、HIG/Material、security policy を見直す。

この運用により、フロントエンドは「画面を作る工程」から、**端末上で動く product contract を継続的に検証・改善する engineering system**へ変わる。
