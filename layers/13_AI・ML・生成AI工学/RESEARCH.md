# AI・ML・生成AI工学 Frontier Operating Model Research

- 指示書タイトル推奨単位: **AI・ML・生成AI工学**
- 対象レイヤー: **13**
- 出力日: **2026-05-13**
- 調査制約: 公開情報のみ。規制・標準・公式ドキュメント・OSS公式ドキメント・公開論文を優先し、マーケティング資料や二次解説は補助扱いにした。
- 注意: レイヤーIDの正式名称リストは提示されていないため、本成果物ではユーザー指定サブテーマから作業名を付与した。IDは保持し、後続で正式レイヤー名に差し替え可能な構造にしている。

---

## 1. Executive Summary

AI/ML・生成AI工学レイヤーの Frontier Operating Model は、単なるモデル開発手順ではなく、**データ、評価、モデル、プロンプト、検索、エージェント、ツール、監視、ガバナンスを一つの変更管理システムとして扱う運用モデル**である。先端組織に共通する設計原理は次のとおりである。

1. **Version everything**: データセット、ラベル、特徴量、実験、チェックポイント、モデル、プロンプト、テンプレート、ベクトルインデックス、RAGコーパス、ツール定義、ガードレール、評価データセットをすべてバージョン化する。
2. **Evaluation-gated release**: モデルやプロンプトを「動いたから出す」のではなく、事前に定義した評価セット、回帰テスト、安全性テスト、RAG根拠性評価、ツール実行テスト、監視閾値を満たした場合だけ昇格する。
3. **Grounded-by-design**: 生成AIの回答品質はモデル単体では保証せず、検索、引用、根拠性検出、ツール実行結果、構造化出力、ヒューマンレビューで補強する。
4. **Least-privilege agency**: エージェントとツール呼び出しは、明示スキーマ、権限境界、サンドボックス、冪等性、監査ログ、人間承認によって制御する。
5. **Closed-loop improvement**: 本番ログ、ユーザーフィードバック、ヒューマンレビュー、ドリフト検出、失敗トレースを、評価データセット・プロンプト・RAGコーパス・モデル再学習へ戻す。
6. **Risk-tiered governance**: ユースケースのリスク、法規制、ユーザー影響、不可逆操作、外部公開範囲に応じて、承認者、文書化、監査、監視頻度を変える。

この結論は、NIST AI RMF / Generative AI Profile、ISO/IEC 42001、EU AI Act、OECD AI Principles、GoogleのML engineering best practices、Google Cloud MLOps、Feast、Label Studio、Hugging Face dataset/model cards、TFX、Ray Train、MLflow、DVC、W&B、KServe、OpenAI / Anthropic / Google Gemini / LangChain / LangGraph / LlamaIndex / Phoenix / Evidently / Azure AI Content Safety / OWASP LLM Top 10 などの公開一次情報・公式情報に基づく。

---

## 2. Research Protocol Applied

RESEARCH.mdの運用プレイブックに従い、各レイヤーを「何を入力に、何を決め、どの基準・閾値・例外で運用し、誰が責任を持ち、何を成果物として残し、何を指標に正しさを判定するか」という意思決定問題に変換した。

### Evidence tier

| Tier | 本調査での扱い | 主な該当ソース |
|---|---|---|
| T0 | 規範的一次情報。定義、MUST/SHOULD、制度要求、標準語彙の根拠 | NIST AI RMF、NIST GenAI Profile、ISO/IEC 42001、EU AI Act、OECD AI Principles、OWASP LLM Top 10 |
| T1 | 規制・制度・公式政策情報 | European Commission AI Act / GPAI Code of Practice |
| T2 | 実行可能成果物・API・スキーマ・製品公式仕様 | OpenAI API docs、Anthropic docs、Azure AI Content Safety、KServe、MLflow、Feast、Pinecone、Weaviate、Qdrant |
| T3 | OSS/公式運用文書・ベストプラクティス | Google Rules of ML、Google Cloud MLOps、TFX、Ray、DVC、W&B、LangChain、LangGraph、LlamaIndex、Evidently、Phoenix |
| T4 | 学術・歴史的基礎文献 | Datasheets for Datasets、Model Cards、RAG paper、Hidden Technical Debt in ML Systems |
| T5 | 外部検証・ベンチマーク・失敗検出 | OWASP LLM Top 10、cloud monitoring docs、observability docs |
| T6 | 補助情報 | ベンダーブログ、二次解説、事例記事。中核判断には使わない |

### Confidence scale

| 確度 | 意味 | 本成果物での扱い |
|---|---|---|
| A | 公式仕様・標準・API・制度文書・OSS公式docsで直接裏付け | Clone Specの中核に採用 |
| B | 独立した複数ソースで整合 | 中核または強い推奨に採用 |
| C | 公式情報に近いが、具体運用は推定 | 実装ガイドでは条件付き採用 |
| D | 仮説 | Unknownsに隔離 |
| X | 破棄 | 採用しない |

---

## 3. Source Catalog

| ID | Source | Evidence tier | Source family | 主に効くレイヤー | Locator |
|---|---|---:|---|---|---|
| S1 | NIST AI Risk Management Framework 1.0 | T0 | 標準/政府 | 13.01, 13.19, 13.26 | https://www.nist.gov/itl/ai-risk-management-framework |
| S2 | NIST AI RMF: Generative AI Profile, NIST AI 600-1 | T0 | 標準/政府 | 13.01, 13.24, 13.25, 13.26 | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence |
| S3 | ISO/IEC 42001:2023 AI management systems | T0 | 国際標準 | 13.01, 13.19, 13.26 | https://www.iso.org/standard/42001 |
| S4 | European Commission AI Act page | T0/T1 | 規制/公式政策 | 13.01, 13.19, 13.21, 13.24, 13.26 | https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai |
| S5 | EU AI Act Explorer | T0/T1 | 規制/公式政策 | 13.19, 13.21, 13.26 | https://ai-act-service-desk.ec.europa.eu/en/ai-act-explorer |
| S6 | European Commission GPAI Code of Practice | T0/T1 | 規制/公式政策 | 13.19, 13.26 | https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai |
| S7 | OECD AI Principles | T0 | 国際政策 | 13.01, 13.19, 13.26 | https://www.oecd.org/en/topics/ai-principles.html |
| S8 | Google Rules of Machine Learning | T3 | 公式ベストプラクティス | 13.02–13.07, 13.20, 13.25 | https://developers.google.com/machine-learning/guides/rules-of-ml |
| S9 | Google ML Crash Course: Production ML Systems / Monitoring | T3 | 公式ベストプラクティス | 13.05–13.07, 13.20, 13.25 | https://developers.google.com/machine-learning/crash-course/production-ml-systems |
| S10 | Google Cloud: MLOps Continuous Delivery and Automation Pipelines | T3 | 公式アーキテクチャ | 13.06–13.13, 13.25–13.26 | https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning |
| S11 | Datasheets for Datasets | T4 | 学術/透明性 | 13.02–13.04 | https://arxiv.org/abs/1803.09010 |
| S12 | Hugging Face Dataset Cards | T2/T3 | 公式Docs | 13.02–13.04 | https://huggingface.co/docs/hub/datasets-cards |
| S13 | Hugging Face Model Cards | T2/T3 | 公式Docs | 13.08–13.12, 13.19 | https://huggingface.co/docs/hub/model-cards |
| S14 | Model Cards for Model Reporting | T4 | 学術/透明性 | 13.08, 13.19 | https://research.google/pubs/model-cards-for-model-reporting/ |
| S15 | Label Studio Overview / Labeling docs | T2/T3 | OSS公式Docs | 13.03, 13.18, 13.21 | https://labelstud.io/guide/get_started |
| S16 | Label Studio Active Learning loop | T2/T3 | OSS公式Docs | 13.03, 13.18 | https://docs.humansignal.com/guide/active_learning |
| S17 | Feast Feature Store docs | T2/T3 | OSS公式Docs | 13.05 | https://docs.feast.dev/ |
| S18 | Feast Registry docs | T2/T3 | OSS公式Docs | 13.05, 13.08 | https://docs.feast.dev/getting-started/components/registry |
| S19 | TFX Production ML Pipelines | T2/T3 | OSS/公式Docs | 13.06–13.09 | https://www.tensorflow.org/tfx |
| S20 | Ray Train docs | T2/T3 | OSS公式Docs | 13.07–13.08 | https://docs.ray.io/en/latest/train/train.html |
| S21 | MLflow Tracking | T2/T3 | OSS公式Docs | 13.06, 13.10, 13.11 | https://mlflow.org/docs/latest/ml/tracking/ |
| S22 | MLflow Model Registry | T2/T3 | OSS公式Docs | 13.08, 13.12 | https://mlflow.org/docs/latest/ml/model-registry/ |
| S23 | MLflow Registry Workflows / aliases & tags | T2/T3 | OSS公式Docs | 13.08, 13.12 | https://mlflow.org/docs/latest/ml/model-registry/workflow/ |
| S24 | W&B Artifacts | T2/T3 | 公式Docs | 13.06, 13.11 | https://docs.wandb.ai/models/artifacts |
| S25 | W&B Registry | T2/T3 | 公式Docs | 13.08, 13.12 | https://docs.wandb.ai/models/registry |
| S26 | DVC Pipelines | T2/T3 | OSS公式Docs | 13.02, 13.06, 13.11 | https://doc.dvc.org/user-guide/pipelines |
| S27 | KServe docs | T2/T3 | OSS公式Docs | 13.13, 13.14 | https://kserve.github.io/website/ |
| S28 | BentoML docs / repository | T2/T3 | OSS公式Docs | 13.13, 13.14 | https://github.com/bentoml/BentoML |
| S29 | OpenAI Prompt Engineering | T2 | 公式API Docs | 13.15–13.16 | https://developers.openai.com/api/docs/guides/prompt-engineering |
| S30 | Anthropic Prompt Engineering | T2 | 公式API Docs | 13.15–13.16 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview |
| S31 | Google Gemini Prompt Design Strategies | T2 | 公式API Docs | 13.15–13.16 | https://ai.google.dev/gemini-api/docs/prompting-strategies |
| S32 | OpenAI Embeddings | T2 | 公式API Docs | 13.17 | https://developers.openai.com/api/docs/guides/embeddings |
| S33 | Sentence Transformers Semantic Search | T2/T3 | 公式Docs | 13.17, 13.19 | https://sbert.net/examples/sentence_transformer/applications/semantic-search/README.html |
| S34 | Pinecone indexing / metadata filtering | T2 | 公式Docs | 13.18–13.19 | https://docs.pinecone.io/guides/index-data/indexing-overview |
| S35 | Weaviate hybrid search | T2 | 公式Docs | 13.18–13.19 | https://docs.weaviate.io/weaviate/concepts/search/hybrid-search |
| S36 | Qdrant payload filtering | T2 | 公式Docs | 13.18–13.19 | https://qdrant.tech/documentation/search/filtering/ |
| S37 | Retrieval-Augmented Generation paper | T4 | 学術 | 13.20–13.21 | https://arxiv.org/abs/2005.11401 |
| S38 | LangChain Retrieval / RAG docs | T2/T3 | OSS公式Docs | 13.20–13.21 | https://docs.langchain.com/oss/python/langchain/retrieval |
| S39 | LangChain Build a RAG agent | T2/T3 | OSS公式Docs | 13.20–13.22 | https://docs.langchain.com/oss/python/langchain/rag |
| S40 | LlamaIndex Evaluation docs | T2/T3 | OSS公式Docs | 13.09, 13.21, 13.25 | https://developers.llamaindex.ai/python/framework/understanding/evaluating/evaluating/ |
| S41 | OpenAI Function Calling | T2 | 公式API Docs | 13.23 | https://developers.openai.com/api/docs/guides/function-calling |
| S42 | OpenAI Tools | T2 | 公式API Docs | 13.22–13.23 | https://developers.openai.com/api/docs/guides/tools |
| S43 | Anthropic Tool Use | T2 | 公式API Docs | 13.22–13.23 | https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview |
| S44 | OpenAI Agents SDK / Agents guide | T2/T3 | 公式Docs | 13.22–13.24, 13.26 | https://developers.openai.com/api/docs/guides/agents |
| S45 | OpenAI Agents SDK Guardrails | T2/T3 | 公式Docs | 13.24, 13.26 | https://openai.github.io/openai-agents-python/guardrails/ |
| S46 | OpenAI Guardrails and Human Review | T2/T3 | 公式Docs | 13.21, 13.24, 13.26 | https://developers.openai.com/api/docs/guides/agents/guardrails-approvals |
| S47 | LangGraph Overview | T2/T3 | OSS公式Docs | 13.22, 13.25, 13.26 | https://docs.langchain.com/oss/python/langgraph/overview |
| S48 | LangGraph Durable Execution | T2/T3 | OSS公式Docs | 13.22, 13.25 | https://docs.langchain.com/oss/python/langgraph/durable-execution |
| S49 | LangChain Human-in-the-loop | T2/T3 | OSS公式Docs | 13.21, 13.23, 13.26 | https://docs.langchain.com/oss/python/langchain/human-in-the-loop |
| S50 | OWASP Top 10 for LLM Applications | T0/T5 | セキュリティ標準/コミュニティ | 13.24, 13.26 | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| S51 | NVIDIA NeMo Guardrails | T2/T3 | OSS公式Docs | 13.24 | https://docs.nvidia.com/nemo-guardrails/index.html |
| S52 | Azure AI Content Safety Overview | T2 | 公式Docs | 13.24, 13.25 | https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview |
| S53 | Azure AI Content Safety Prompt Shields | T2 | 公式Docs | 13.24 | https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection |
| S54 | Azure AI Content Safety Groundedness | T2 | 公式Docs | 13.21, 13.24 | https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/groundedness |
| S55 | OpenAI Evals | T2 | 公式API Docs | 13.09, 13.21, 13.25 | https://developers.openai.com/api/docs/guides/evals |
| S56 | OpenAI Evaluation Best Practices | T2 | 公式API Docs | 13.09, 13.21, 13.25 | https://developers.openai.com/api/docs/guides/evaluation-best-practices |
| S57 | LangSmith Evaluation | T2/T3 | 公式Docs | 13.09, 13.21, 13.25–13.26 | https://docs.langchain.com/langsmith/evaluation |
| S58 | Phoenix Observability and Evaluation | T2/T3 | OSS/公式Docs | 13.22, 13.25–13.26 | https://arize.com/docs/phoenix |
| S59 | Evidently Data Drift | T2/T3 | OSS/公式Docs | 13.20, 13.25 | https://docs.evidentlyai.com/metrics/preset_data_drift |
| S60 | Vertex AI Model Monitoring | T2 | 公式クラウドDocs | 13.20, 13.25 | https://docs.cloud.google.com/vertex-ai/docs/model-monitoring/overview |
| S61 | Azure ML Model Monitoring | T2 | 公式クラウドDocs | 13.20, 13.25 | https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-monitoring?view=azureml-api-2 |
| S62 | Amazon SageMaker Model Monitor | T2 | 公式クラウドDocs | 13.20, 13.25 | https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html |
| S63 | Hidden Technical Debt in ML Systems | T4 | 学術/Google Research | 13.01, 13.05–13.26 | https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/ |
| S64 | Humanloop Datasets / Evaluators | T2 | 公式Docs | 13.09, 13.18, 13.26 | https://humanloop.com/docs/explanation/datasets |

---

## 4. Layer Registry

| Layer ID | 作業名 | Decision Object | Decision Question | 主な成果物 | 主なOwner | 既定メトリクス |
|---:|---|---|---|---|---|---|
| 13.01 | AI/ML・生成AI工学統合アーキテクチャ | AIシステム全体の責任境界と変更管理 | AI機能をどのデータ、モデル、検索、エージェント、ツール、監視、ガバナンス単位で設計・承認・改善するか | AI system design doc, risk tier, architecture decision record, eval gate policy | Head of AI Platform, AI Governance Lead, Product Owner | release pass rate, safety incident rate, time-to-rollback, audit completeness |
| 13.02 | Dataset governance | 学習・評価・RAG用データセットの採用可否 | どのデータを、どの根拠・ライセンス・品質・バイアス評価で採用するか | dataset card, datasheet, data lineage, license register | Data Steward, Legal, ML Lead | coverage, missingness, representativeness, license clearance |
| 13.03 | Labeling / annotation | ラベル定義・ラベル作業・レビューの設計 | どのラベル体系、作業指示、品質検査、再ラベル条件でデータを教師信号に変換するか | labeling rubric, annotation UI, gold tasks, adjudication log | Labeling Ops Lead, Domain SME | inter-annotator agreement, defect rate, adjudication rate |
| 13.04 | Data quality / validation | データ品質ゲート | どのスキーマ、分布、重複、リーク、PII、外れ値条件でデータを通すか | validation suite, schema tests, leakage report | Data Engineer, ML Engineer | schema pass rate, leakage count, drift distance, PII hit rate |
| 13.05 | Feature store | 特徴量定義・保存・提供 | どの特徴量を、offline/online整合性、point-in-time correctness、低遅延要件で提供するか | feature registry, feature views, offline/online store, materialization job | Feature Platform Owner | feature freshness, online latency, train-serving skew |
| 13.06 | Pipeline / experiment tracking | 実験・パイプライン実行の再現性 | どのコード、データ、設定、パラメータ、メトリクス、成果物を実験単位で残すか | experiment run, pipeline DAG, params/metrics/artifacts | ML Engineer, Platform Engineer | reproducibility pass, run success, lineage completeness |
| 13.07 | Training orchestration | 学習ジョブの実行方式 | 単一/分散学習、fine-tuning、チェックポイント、コスト制約をどう決めるか | training config, compute plan, checkpoint policy | ML Engineer, Infra/SRE | GPU utilization, checkpoint recovery, cost per run |
| 13.08 | Model evaluation | モデル採否の評価ゲート | どの評価セット、評価指標、安全性基準、閾値で昇格を許可するか | eval suite, benchmark report, regression test report | Eval Lead, ML Lead, Risk Owner | task score, regression delta, safety fail rate |
| 13.09 | LLM / RAG evaluation | 生成AI出力の品質評価 | LLM出力を、正確性、根拠性、関連性、形式、トーン、安全性でどう評価するか | eval dataset, judge prompts, human rubric, eval dashboard | LLM Eval Lead, Domain SME | faithfulness, answer relevance, format pass, human agreement |
| 13.10 | Model documentation | model card / dataset card | モデルの用途、制約、評価結果、リスク、非推奨用途をどう文書化するか | model card, intended use, limitation statement | Model Owner, Governance | card completeness, stale documentation age |
| 13.11 | Artifact / checkpoint management | モデル成果物と依存物 | どの成果物を保存し、署名し、再現・復旧・監査できるようにするか | artifact registry, model checkpoint, SBOM-like dependency list | ML Platform, SRE | artifact availability, hash mismatch, rollback readiness |
| 13.12 | Model registry / promotion | モデル版の昇格・参照 | どのモデル版をchampion/challenger/prod aliasに割り当てるか | registered model, aliases/tags, approval log | Model Owner, Release Manager | promotion cycle time, alias correctness, rollback success |
| 13.13 | Inference serving | 推論エンドポイント | どのAPI、モデルサーバ、SLA、autoscaling、batch/online方式で提供するか | inference service, API spec, deployment manifest | Serving Platform Owner | p95/p99 latency, error rate, throughput, availability |
| 13.14 | Inference optimization | 推論コスト・性能最適化 | どの量子化、キャッシュ、バッチング、ルーティング、モデル選択で性能/費用を最適化するか | routing policy, cache policy, cost dashboard | ML Infra, FinOps | cost per 1k requests, cache hit, token/GPU efficiency |
| 13.15 | Prompt engineering | プロンプト設計 | どの指示、例、制約、出力形式、コンテキストをプロンプトに含めるか | prompt spec, prompt tests, output schema | Prompt Engineer, Product Owner | eval score, format pass, prompt regression |
| 13.16 | Prompt / template registry | テンプレートの変更管理 | プロンプトテンプレートをどの変数、版、テスト、承認で運用するか | prompt registry, variables schema, release notes | Prompt Platform Owner | template coverage, stale prompt rate, rollback time |
| 13.17 | Embedding model | 埋め込み生成方式 | どのembeddingモデル、次元数、正規化、更新頻度で意味表現を作るか | embedding spec, embedding job, vector schema | Retrieval Engineer | retrieval recall, embedding drift, cost per vector |
| 13.18 | Vector store | ベクトル保存・マルチテナント | どのindex、namespace、metadata、filter、TTL、削除規則で保存するか | vector index, metadata schema, namespace policy | Search Platform Owner | index freshness, filter correctness, storage cost |
| 13.19 | Vector search / reranking | 検索・ランキング | dense/sparse/hybrid/rerankをどう組み合わせ、top-kと閾値をどう決めるか | search config, reranker config, relevance eval | Search Lead | recall@k, precision@k, MRR/NDCG, latency |
| 13.20 | RAG ingestion / grounding | RAGコーパスと根拠付与 | どのchunking、metadata、retrieval、citation、groundingで回答を支えるか | RAG corpus registry, citation policy, retrieval traces | RAG Engineer, Knowledge Owner | groundedness, citation accuracy, stale source rate |
| 13.21 | RAG / generated-answer evaluation | RAG品質ゲート | 回答と根拠の一致、幻覚、過不足、禁止内容をどう判定するか | RAG eval suite, golden queries, failure taxonomy | Eval Lead, Domain SME | faithfulness, hallucination rate, unsupported answer rate |
| 13.22 | Agent architecture | エージェント構造 | どの状態、記憶、計画、handoff、停止条件でエージェントを動かすか | agent graph, state schema, memory policy | Agent Architect | task completion, loop rate, interruption count |
| 13.23 | Tool calling | ツール定義・実行 | どの関数/APIを、どのスキーマ、権限、冪等性、検証で呼ばせるか | tool schema, function registry, execution logs | Integration Owner, Security | tool success, invalid call rate, approval rate |
| 13.24 | Guardrails / safety controls | 入出力・ツール・検索の安全制御 | どのポリシー、検出器、ブロック/修正、エスカレーションで危険挙動を抑えるか | safety policy, guardrail config, prompt shield, content filter | Safety Lead, Security | guardrail precision/recall, blocked unsafe rate, false positive |
| 13.25 | AI monitoring / observability / drift | 本番挙動の観測 | どのログ、trace、span、評価、ドリフト、コスト、SLOを監視するか | observability dashboard, trace store, drift alerts | AI SRE, ML Platform | p95 latency, cost, drift score, eval regression, incident count |
| 13.26 | Feedback loop / human review / model governance | 改善・承認・監査 | 本番失敗、ユーザーフィードバック、人間判断、規制要求をどう改善サイクルに戻すか | feedback queue, human review workflow, risk register, governance board minutes | AI Governance Lead, Product Owner, SME Reviewer | feedback closure time, review SLA, accepted corrections, audit findings |

---

## 5. Frontier Exemplars and Selection Rationale

| Exemplar group | 採用理由 | Transferable pattern | Evidence refs | Confidence |
|---|---|---|---|---|
| NIST AI RMF / GenAI Profile | AIリスクをMap/Measure/Manage/Governの機能に分解し、生成AI固有リスクに拡張する公式プロファイルを提供 | リスクベースのAI lifecycle governance | S1, S2 | A |
| ISO/IEC 42001 | AI management systemとして、組織的な継続改善・リスク/機会管理を要求する国際標準 | AI運用を品質マネジメントシステム化する | S3 | A |
| EU AI Act / GPAI Code | 高リスクAI、透明性、GPAI、記録、human oversight、post-market monitoringを制度要求にする | 規制対応を設計要件に変換する | S4, S5, S6 | A |
| Google Rules of ML / MLOps | training-serving skew、data validation、CI/CD/CT、監視など実運用の失敗条件を体系化 | MLをソフトウェア + データ + 継続学習のシステムとして扱う | S8, S9, S10, S63 | A/B |
| Feast | feature registry、offline store、online serving、feature validationをOSSとして公開 | 特徴量をモデル実験と本番推論の共通契約にする | S17, S18 | A |
| Label Studio / Argilla型 human annotation | ラベルUI、pre-annotation、ML backend、active learning、human feedbackを公開 | ラベルと人間評価を閉ループ化する | S15, S16 | A/B |
| Hugging Face dataset/model cards + Model Cards paper | データセット・モデルの用途、制約、バイアス、評価を文書化する慣行 | 透明性文書をレジストリ必須成果物にする | S12, S13, S14 | A/B |
| TFX / Ray Train / DVC | pipeline DAG、分散学習、データ/モデル再現性をOSS docsで公開 | trainingを再現可能な有向グラフ + compute jobとして管理する | S19, S20, S26 | A/B |
| MLflow / W&B | experiment tracking、artifact、registry、aliases/tags、lineage、promotionを公開 | 実験から本番までの成果物・モデル版を一元管理する | S21–S25 | A |
| KServe / BentoML | Kubernetes推論、serverless/autoscaling、multi-framework serving、REST API化を公開 | 推論を標準Deployment + SLO + rollback対象にする | S27, S28 | A/B |
| OpenAI / Anthropic / Gemini prompt and tool docs | プロンプト、構造化出力、function/tool calling、agents、evals、guardrails、人間承認を公式化 | LLMアプリをprompt + tool + eval + trace + guardrailとして設計する | S29–S31, S41–S46 | A |
| Vector DB ecosystem | vector + metadata、namespace、hybrid search、payload filteringを公式Docsで明示 | 意味検索を構造化フィルタとランキング評価に接続する | S32–S36 | A/B |
| LangChain / LangGraph / LlamaIndex / Phoenix | RAG、agent graph、durable execution、human-in-the-loop、traces、RAG評価を公開 | LLM workflowを状態機械 + trace + evalで運用する | S38–S40, S47–S49, S58 | A/B |
| OWASP LLM Top 10 / NeMo / Azure Content Safety | prompt injection、tool/plugin設計、supply chain、content safety、groundedness検出を公開 | 生成AI固有リスクをコントロールに落とす | S50–S54 | A/B |
| Vertex / Azure ML / SageMaker / Evidently monitoring | feature skew、data drift、model monitoring、alertingを公式Docsで公開 | 本番入力・出力・性能・品質の継続監視 | S59–S62 | A |

---

## 6. Evidence Map: Core Claims

| Claim ID | Claim | Decision field | Evidence refs | Confidence |
|---|---|---|---|---|
| C01 | AI/MLレイヤーは、モデル単体ではなく、データ、評価、運用、監視、ガバナンスの総合システムとして設計すべきである | core philosophy | S1, S2, S3, S10, S63 | A |
| C02 | 生成AIは幻覚、プロンプト注入、情報完全性、データプライバシー、価値連鎖など従来MLと異なるリスク分類を持つ | risk taxonomy | S2, S50, S52–S54 | A |
| C03 | dataset card / datasheetは、動機、構成、収集、利用条件、バイアス、制約を文書化する中核成果物である | artifacts | S11, S12 | A/B |
| C04 | ラベル品質はrubric、gold task、annotator agreement、adjudicationで管理し、active learningで再学習ループへ接続する | operating model | S15, S16 | A/B |
| C05 | Feature storeは、training用offline storeとserving用online storeの整合性、registry、materializationを制御する | interface rules | S17, S18 | A |
| C06 | ML pipelineはデータ検証、変換、学習、評価、push/deployのDAGとして扱う | process | S10, S19, S26 | A |
| C07 | 実験はparameters、metrics、artifacts、source run、lineageを保存し、後から探索・比較できなければならない | artifacts/metrics | S21, S24 | A |
| C08 | model registryはversion、alias/tag、metadata、lineage、promotion/rollbackを管理する | registry | S22, S23, S25 | A |
| C09 | モデルリリースはoffline eval、online/shadow/canary、human review、monitoringを通るgateとして設計する | controls | S10, S22, S27, S55–S57 | A/B |
| C10 | 生成AIの評価は、変動性を前提に、task-specific eval、LLM-as-judge、human review、production tracesを組み合わせる | evaluation | S55–S58, S64 | A/B |
| C11 | プロンプトは自然文メモではなく、instruction、context、examples、output schema、variables、testsを持つ版管理対象である | artifacts | S29–S31, S55, S57 | A/B |
| C12 | Embeddingは検索・クラスタリング・推薦・分類のための数値表現であり、モデル・次元・正規化・更新頻度を明示すべきである | technical spec | S32, S33 | A |
| C13 | Vector storeではID、vector、metadata、namespace/filterを管理し、検索対象範囲とtenant隔離を明示する必要がある | interface rules | S34, S36 | A |
| C14 | Hybrid searchはvector similarityとkeyword/BM25を組み合わせ、意味的近さと正確語彙の両方を扱う | search criteria | S35 | A |
| C15 | RAGはparametric memoryだけでなく、明示的なnon-parametric memory / retrieverを使って根拠を追加する | architecture | S37, S38 | A |
| C16 | RAGはingestionとretrieval/generationを分離し、chunking、metadata、top-k、rerank、citation、groundingを評価対象にする | operating model | S38–S40, S54 | A/B |
| C17 | Tool callingは、モデルが構造化されたtool callを返し、アプリケーション側またはサーバ側が実行して結果を戻す多段ループである | interface rules | S41–S43 | A |
| C18 | エージェントはdurable execution、state、memory、handoff、human-in-the-loop、tracingを設計単位にする | architecture | S44, S47–S49 | A/B |
| C19 | Guardrailはinput/output/tool behaviorを検査し、block、modify、escalate、human approvalに分岐させる | controls | S45, S46, S51–S54 | A |
| C20 | OWASP LLM Top 10は、prompt injection、training data poisoning、DoS、supply chain、excessive agencyなどを生成AIアプリの主要リスクとして扱う | failure modes | S50 | A |
| C21 | 本番AI監視は、latency/error/costだけでなく、data drift、training-serving skew、feature drift、eval regression、trace qualityも含む | metrics | S59–S62, S58 | A |
| C22 | human reviewは不可逆操作、外部送信、金融/法務/医療/人事、権限昇格、低信頼出力で必須ゲートになる | exceptions/approval | S4, S46, S49 | A/B |
| C23 | feedback loopは本番ログと人間評価を評価データセット、プロンプト修正、RAG更新、再学習候補へ戻す | cadence | S16, S57, S58, S64 | A/B |
| C24 | AI governanceはrisk register、technical documentation、record keeping、human oversight、post-market monitoringを含めるべきである | governance | S1–S6 | A |
| C25 | Hidden technical debt in MLは、境界浸食、データ依存、フィードバックループ、設定負債、監視不足として現れる | failure modes | S8, S63 | A/B |

---

## 7. Clone Spec

### Layer ID

13

### Layer Name

AI/ML・生成AI工学

### Definition

AI/ML・生成AI工学レイヤーは、データセット、ラベル、特徴量、学習、評価、実験、成果物、モデル登録、推論、プロンプト、埋め込み、ベクトル検索、RAG、エージェント、ツール呼び出し、ガードレール、監視、フィードバック、ガバナンス、人間レビューを制御し、AIシステムを安全・再現可能・評価可能・改善可能にするための意思決定システムである。

### Decision Question

優れたAI/ML・生成AI工学組織は、どのデータとモデルを採用し、どの評価・安全性・性能・コスト・リスク基準でリリースし、どの監視・人間レビュー・フィードバックループで継続改善するのか。

### Frontier Candidates

1. NIST AI RMF / GenAI Profile, ISO/IEC 42001, EU AI Act, OECD AI Principles: ガバナンスとリスク階層の規範。
2. Google Rules of ML / Google Cloud MLOps / Hidden Technical Debt: MLシステム運用の失敗条件と予防策。
3. Feast, Label Studio, Hugging Face cards, TFX, Ray, DVC, MLflow, W&B, KServe: データから推論までのOSS/公式運用パターン。
4. OpenAI / Anthropic / Gemini / LangChain / LangGraph / LlamaIndex: 生成AIアプリ、RAG、agent、tool calling、eval、human-in-the-loopの実装パターン。
5. OWASP LLM Top 10, NeMo Guardrails, Azure AI Content Safety, Phoenix, Evidently, Vertex/Azure/SageMaker monitoring: セキュリティ、ガードレール、監視、ドリフト検出。

### Core Philosophy

- **Contract-first ML/LLMOps**: データ、特徴量、モデル、プロンプト、ツール、検索、評価を暗黙知ではなく契約として定義する。
- **Lineage before optimization**: 性能改善より先に、どのデータ・コード・モデル・プロンプト・検索結果が出力を作ったか追跡できることを優先する。
- **Evaluation as product specification**: 評価セットとrubricが、AI機能の仕様書である。
- **Risk-tiered autonomy**: 自動化できる範囲は、ユーザー影響・不可逆性・外部権限・法規制・安全リスクに応じて段階的に拡大する。
- **Monitor what the model cannot know**: モデル単体が検知できない分布変化、検索鮮度、ツール失敗、ユーザー不満、規制変更を外部監視する。

### Decision Model

| Field | Specification |
|---|---|
| Inputs | product use case, user segment, data sources, data rights, risk tier, model candidates, prompt candidates, retrieval corpus, tool APIs, deployment environment, budget, latency/SLA, regulatory scope, user feedback |
| Decision object | AI system contract: data + model + prompt + retrieval + tools + guardrails + eval + monitoring + governance |
| Criteria | correctness, groundedness, safety, latency, cost, privacy, auditability, reproducibility, maintainability, business impact, user trust |
| Priorities | 1. legal/safety compliance, 2. traceability, 3. evaluation pass, 4. rollback readiness, 5. quality/performance, 6. cost optimization |
| Prohibitions | unversioned training data, undocumented prompt changes, model promotion without eval gate, tools without schema/least privilege, RAG without source freshness controls, monitoring only infrastructure metrics, human review without rubric |
| Thresholds | eval pass threshold, safety fail = 0 for critical classes, latency p95/p99, max cost/request, retrieval recall@k, hallucination/unsupported-answer threshold, drift alert threshold, reviewer SLA |
| Owners | AI Platform Lead, ML Lead, Data Steward, Prompt/RAG Engineer, Search Engineer, Safety Lead, AI Governance Lead, Product Owner, SRE, Legal/Compliance, Domain SME reviewers |
| Review cadence | pre-release; after model/provider update; after prompt/template update; after corpus refresh; weekly production eval review; monthly governance review; incident-triggered review; quarterly risk re-assessment |
| Controls | data validation, model/prompt registry, eval gates, canary/shadow release, guardrails, content safety, prompt shields, tool approval, trace logging, drift detection, audit log, human review, rollback |
| Exceptions | emergency rollback, legal takedown, high-severity safety incident, stale critical corpus, model provider change, high-risk jurisdiction, low-confidence answer, irreversible tool action |
| Metrics | eval score, safety pass rate, groundedness, retrieval metrics, label quality, drift/skew, latency, cost, incident count, human override rate, audit completeness |

### Operating Model

#### Roles

| Role | Accountability |
|---|---|
| AI Platform Lead | 共通AI基盤、registry、observability、guardrail、deployment標準 |
| Data Steward | データ由来、権利、品質、スキーマ、dataset card |
| Labeling Ops Lead | annotation rubric、annotator calibration、QA、adjudication |
| ML Engineer | feature、training、evaluation、artifact、model registry |
| LLM / Prompt Engineer | prompt/template、structured output、LLM eval |
| Retrieval / Search Engineer | embedding、vector store、hybrid search、RAG ingestion |
| Agent Architect | agent state、tool orchestration、handoff、durable execution |
| Safety / Security Lead | OWASP LLM risk、prompt injection、guardrail、red teaming |
| AI SRE | inference SLO、monitoring、incident、rollback、cost |
| AI Governance Lead | risk tier、documentation、human oversight、audit |
| Domain SME Reviewer | 高リスク出力、評価rubric、人間レビュー、フィードバック承認 |

#### Process

1. **Use case intake**: AI機能の目的、対象ユーザー、影響、法域、リスクtierを登録。
2. **Data readiness gate**: dataset card、license、PII、schema、split、label plan、feature planを承認。
3. **Build / experiment**: code、config、data、params、metrics、artifactsをtracking systemに残す。
4. **Evaluation design**: task eval、safety eval、RAG eval、tool eval、human rubricを定義。
5. **Registry and promotion**: model/prompt/template/RAG corpus/tool schemaをregistryへ登録し、alias/tagで環境参照。
6. **Pre-production verification**: canary/shadow、load test、guardrail tests、prompt injection tests、rollback testを通す。
7. **Production monitoring**: trace、eval-in-prod、drift、cost、latency、safety、feedbackを監視。
8. **Closed-loop improvement**: 失敗例をannotation queue / eval dataset / RAG corpus refresh / prompt update / retraining候補へ送る。
9. **Governance review**: risk register、model card、incident、human review結果を月次または高リスクでは週次で審査。

### Technical / Business Specification

#### 7.1 Dataset, labeling, feature store

- すべてのデータセットに `dataset_id`, `version`, `owner`, `source`, `license`, `collection method`, `intended use`, `prohibited use`, `known bias`, `PII status`, `retention`, `split`, `baseline statistics` を付与する。
- ラベルは `label taxonomy`, `rubric`, `examples`, `edge cases`, `annotator qualification`, `gold tasks`, `review workflow`, `adjudication criteria` を持つ。
- ラベリング品質は inter-annotator agreement、gold task accuracy、adjudication rate、label driftで監視する。
- Feature storeは entity、feature view、offline store、online store、registry、materialization、freshness、point-in-time join、serving latencyを契約化する。
- train-serving skewを防ぐため、trainingとservingで特徴量生成ロジックを共有し、serving-time featuresのログをtraining/evalに戻す。

#### 7.2 Training, evaluation, registry, artifact, inference

- Training jobは `code commit`, `data version`, `feature version`, `model config`, `hyperparameters`, `random seed`, `compute type`, `environment`, `metrics`, `artifacts`, `checkpoint`, `logs` を必ず保存する。
- Evaluationは、offline benchmark、slice evaluation、robustness、safety、bias、latency、cost、regression delta、human rubricを含める。
- LLM/RAG evalは、exact answerだけでなく、根拠性、引用精度、回答関連性、形式遵守、拒否妥当性、tool correctness、agent task completionを測る。
- Registryでは model version、aliases/tags、model card、signature、input/output schema、approval status、deployment historyを管理する。
- Inferenceは online/batch、model server、autoscaling、queue、timeout、retry、circuit breaker、rollback、canary/shadow、observabilityを設計する。

#### 7.3 Prompt/template

- Promptは `system/developer/user instruction`, `context`, `examples`, `constraints`, `output schema`, `tool policy`, `safety policy`, `fallback behavior`, `evaluation cases` を含む。
- Prompt templateは変数スキーマ、デフォルト値、禁止入力、PII redaction、モデル互換性、評価結果を持つ。
- Prompt更新はコード変更と同等に扱い、semantic version、diff、release note、eval run、rollback aliasを残す。

#### 7.4 Embedding, vector store/search, RAG

- Embedding specは model name、dimension、normalization、language coverage、chunk input policy、re-embedding trigger、cost、retentionを定義する。
- Vector storeは record ID、dense/sparse vector、metadata、namespace、tenant、ACL、TTL、delete semantics、index build version、filter policyを持つ。
- Searchは dense/vector、keyword/BM25、hybrid、metadata filter、reranker、top-k、score threshold、diversity、freshness boostを明示する。
- RAGは ingestion pipelineとruntime retrieval/generationを分離し、chunking、metadata、citation、source freshness、groundedness evaluationを持つ。
- RAG回答は「根拠なしなら回答しない」「引用不一致なら低信頼で返す」「source ageが閾値を超えたら再取得または拒否」をルール化する。

#### 7.5 Agent, tool calling, guardrail

- Agentは role、goal、state schema、memory policy、tool inventory、handoff policy、stop condition、retry budget、human approval policyを持つ。
- Toolは name、description、JSON schema、auth scope、idempotency、side-effect classification、timeout、rate limit、input validation、output validation、audit logを持つ。
- 不可逆または外部影響のあるtool actionは human approvalを必須にする。例: email送信、決済、削除、権限変更、外部公開、契約/法務判断。
- Guardrailは input、retrieved documents、tool call、tool output、model output、final responseの各境界で検査する。
- Prompt injection対策は「検出器を置く」だけではなく、retrieved textを命令として扱わない、tool privilegeを絞る、出力をアプリ側で検証する、human reviewへ回す、の多層防御にする。

#### 7.6 Monitoring, feedback loop, governance, drift, human review

- Monitoringは logs、traces、spans、prompts、retrieval hits、tool calls、guardrail decisions、latency、token/cost、user feedback、human review outcomesを収集する。
- Driftは data drift、feature skew、concept drift、embedding drift、retrieval corpus drift、prompt performance drift、model provider driftに分ける。
- Feedbackは user rating、thumbs down、correction、appeal、human annotation、incident report、support ticketを統合し、triage queueに送る。
- Human reviewはrubric、SLA、reviewer資格、sample policy、escalation、appeal、audit trailを持つ。
- Governanceは risk register、model card、dataset card、technical documentation、record keeping、post-market monitoring、incident reportを維持する。

### Metrics

| Category | Metrics |
|---|---|
| Data | dataset coverage, schema pass rate, missingness, duplication, leakage count, PII hit rate, license clearance, data freshness |
| Labeling | inter-annotator agreement, gold task accuracy, label defect rate, adjudication rate, label throughput, cost per accepted label |
| Feature | feature freshness, point-in-time correctness, online latency, offline/online parity, train-serving skew |
| Training | run success, reproducibility pass, GPU utilization, cost/run, checkpoint recovery, experiment velocity |
| Evaluation | task score, slice performance, regression delta, safety fail rate, calibration, robustness score, human agreement |
| Registry | promotion cycle time, stale model age, alias correctness, rollback success, model card completeness |
| Inference | p50/p95/p99 latency, availability, error rate, timeout, queue depth, cost/request, tokens/request |
| Prompt | eval pass rate, format pass, prompt regression, invalid variable rate, rollback time |
| Retrieval/RAG | recall@k, precision@k, MRR/NDCG, groundedness, citation accuracy, unsupported-answer rate, stale source rate |
| Agent/tool | task completion, tool success, invalid tool call, approval rate, loop count, side-effect errors, sandbox escape attempts |
| Guardrail | unsafe block rate, false positive/false negative, jailbreak detection, policy violation rate, escalation volume |
| Monitoring/governance | drift score, incident count, MTTR, feedback closure time, human review SLA, audit finding count |

### Failure Modes

| Failure mode | Mechanism | Prevention / detection |
|---|---|---|
| Dataset leakage | train/testやRAG corpusに評価答えが混入 | split governance, leakage tests, source separation |
| Low-quality labels | rubric不明、annotator calibration不足 | gold tasks, agreement checks, adjudication |
| Train-serving skew | trainingとservingで特徴量処理が異なる | feature store, shared transforms, serving logs |
| Benchmark overfitting | public benchmarkだけで最適化 | private eval, rotating test set, production traces |
| Artifact loss | checkpointや依存が再現不能 | artifact registry, hashes, environment capture |
| Prompt regression | prompt変更が特定sliceを破壊 | prompt registry, eval gate, rollback alias |
| Stale RAG corpus | 更新されない文書で回答 | source freshness monitor, TTL, recrawl policy |
| Retrieval blind spot | semantic searchだけで正確語を落とす | hybrid search, metadata filter, reranking |
| Prompt injection | user/retrieved contentが命令を上書き | prompt shields, context isolation, least privilege tools |
| Tool overreach | agentが過剰権限toolを実行 | tool scopes, approval gates, audit logs |
| Infinite agent loops | goal/stop condition不明 | max steps, timeout, loop detector |
| Ungrounded generation | sourceにない内容を断定 | groundedness eval, citation requirement, refusal rule |
| Monitoring theater | infra metricsだけで品質を見ない | production evals, traces, user feedback, drift alerts |
| Human review bottleneck | 全件レビューで遅延、rubric不一致 | risk sampling, reviewer training, clear SLA |
| Governance paper-only | 文書が現行の実装を反映しない | registry-linked docs, release gates, audit diffs |

### Anti-patterns

- 「モデルを選べばAI機能は完成」と考え、データ・評価・監視・人間レビューを後付けする。
- dataset card/model cardを作っても、registryやrelease gateに接続しない。
- promptをアプリコードや管理画面に散在させ、版管理・評価・ロールバックできない。
- RAGでvector similarityだけを信じ、metadata filter、hybrid search、rerank、source freshnessを使わない。
- LLM-as-judgeだけで合否を決め、人間基準や実ユーザー失敗例を評価セットに戻さない。
- tool callingで自然文descriptionだけを頼りにし、スキーマ、権限、冪等性、出力検証を定義しない。
- guardrailを単一フィルタに依存し、retrieval、tool、output、human approvalの多層制御を置かない。
- drift検出をtabular featuresだけに限定し、embedding drift、retrieval corpus drift、prompt/model provider driftを見ない。

### Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | notebook、手作業データ、手元モデル、未評価prompt、監視なし |
| 1 | 個人依存 | 実験ログや評価があるが、所有者とgateが曖昧。promptやRAG corpusが属人的 |
| 2 | 文書化 | dataset/model/prompt card、rubric、basic eval、registry、basic monitoringがある |
| 3 | 標準化 | pipeline、feature store、model/prompt registry、eval gates、canary/rollback、guardrail、HITLが標準運用化 |
| 4 | 自動化・計測 | CI/CD/CT、production eval、drift alerts、trace analysis、feedback loop、policy-as-codeが稼働 |
| 5 | 自律改善・業界先端 | production tracesとhuman feedbackが評価・RAG・prompt・trainingへ継続還流し、risk-tiered autonomyと監査が統合されている |

---

## 8. Layer-by-Layer Specification Capsules

### 13.01 AI/ML・生成AI工学統合アーキテクチャ

- Definition: AI systemを、data、model、prompt、retrieval、tools、guardrails、monitoring、governanceの統合契約として設計する。
- Core decisions: risk tier、ownership、release gate、fallback、human oversight、audit logging。
- Required artifacts: AI system card、architecture decision record、risk register、eval gate policy、incident playbook。
- Metrics: release gate pass rate、safety incident count、audit completeness、MTTR、rollback success。
- Failure modes: AI governanceと実装が分断される、誰も最終責任を持たない、評価が仕様になっていない。

### 13.02 Dataset governance

- Definition: 学習・評価・RAG用データの採用可否を決める。
- Required artifacts: dataset card/datasheet、license/PII register、data lineage、split manifest。
- Controls: source approval、license check、PII scan、bias/coverage review、retention policy。
- Metrics: coverage、missingness、representativeness、source freshness、license clearance。
- Failure modes: 権利不明データ、評価リーク、偏った収集、削除不能データ。

### 13.03 Labeling / annotation

- Definition: 人間またはモデル補助によるラベル生成を制御する。
- Required artifacts: rubric、label taxonomy、annotator guide、gold tasks、adjudication log。
- Controls: calibration、double annotation、pre-annotation review、active learning sampling。
- Metrics: inter-annotator agreement、gold task accuracy、defect rate、review SLA。
- Failure modes: ラベル定義の曖昧さ、SME不足、低品質ラベルの大量生成。

### 13.04 Data quality / validation

- Definition: データが学習・評価・推論に耐えるか検証する。
- Required artifacts: validation suite、schema contract、data quality report、leakage report。
- Controls: schema tests、distribution tests、PII/toxicity checks、duplicate detection。
- Metrics: schema pass、drift score、leakage count、outlier count。
- Failure modes: raw dataは通るが特徴量加工後に破綻する、評価データに本番分布が反映されない。

### 13.05 Feature store

- Definition: trainingとservingで共有する特徴量の契約と提供面を管理する。
- Required artifacts: feature registry、feature view、offline/online store config、materialization job。
- Controls: point-in-time join、freshness thresholds、serving log replay、feature owner approval。
- Metrics: feature freshness、online latency、offline/online parity、training-serving skew。
- Failure modes: training用特徴量と本番特徴量が別物になる、過去値joinが漏洩する。

### 13.06 Pipeline / experiment tracking

- Definition: 実験とpipeline実行を再現可能にする。
- Required artifacts: run record、pipeline DAG、parameters、metrics、artifacts、environment snapshot。
- Controls: experiment naming、run lineage、mandatory logging、reproducibility smoke test。
- Metrics: reproducibility pass、run success、artifact completeness、experiment comparison coverage。
- Failure modes: notebookの一回限り実験、モデルはあるが生成条件が不明。

### 13.07 Training orchestration

- Definition: 学習ジョブ、分散学習、fine-tuning、checkpoint、compute利用を決める。
- Required artifacts: training config、compute plan、checkpoint policy、training logs。
- Controls: resource quota、checkpoint/restart、seed control、data/model version binding。
- Metrics: GPU utilization、cost/run、checkpoint recovery、training throughput。
- Failure modes: compute cost暴走、checkpoint不能、モデル更新の再現不能。

### 13.08 Model evaluation

- Definition: モデル版の採否と昇格を評価で決める。
- Required artifacts: eval suite、benchmark report、slice analysis、thresholds、approval log。
- Controls: private eval、safety eval、regression eval、human review for ambiguous slices。
- Metrics: task score、slice delta、safety fail、calibration、business KPI uplift。
- Failure modes: aggregate scoreだけで少数派sliceを見落とす、公開benchmarkに過適合する。

### 13.09 LLM / RAG evaluation

- Definition: 生成AI出力の品質・根拠・安全性・形式を評価する。
- Required artifacts: eval dataset、judge prompt、human rubric、trace-linked examples。
- Controls: LLM-as-judge calibration、pairwise eval、human adjudication、production trace sampling。
- Metrics: faithfulness、answer relevance、format pass、refusal precision、human agreement。
- Failure modes: judge modelのバイアス、長い回答への過大評価、専門ドメイン誤答の見落とし。

### 13.10 Model documentation

- Definition: モデルの用途、制約、性能、リスクを利用者と監査者に伝える。
- Required artifacts: model card、intended/prohibited use、evaluation summary、limitations。
- Controls: registry promotion requires current model card; high-risk models require governance review。
- Metrics: card completeness、stale age、coverage of risk sections。
- Failure modes: cardが実装版や最新評価を反映しない。

### 13.11 Artifact / checkpoint management

- Definition: モデル成果物、依存物、チェックポイント、関連データを保存・復旧可能にする。
- Required artifacts: checkpoint、model binary、environment spec、hash、dependency list。
- Controls: immutable storage、artifact signing、retention policy、rollback rehearsal。
- Metrics: artifact availability、hash mismatch、restore time、storage cost。
- Failure modes: 本番モデルは動くが再デプロイ不能、依存ライブラリが消える。

### 13.12 Model registry / promotion

- Definition: モデル版、alias/tag、昇格、rollbackを制御する。
- Required artifacts: registered model、model version、alias/tag、promotion request、approval log。
- Controls: champion/challenger、stage/alias policy、model signature check、deployment binding。
- Metrics: promotion cycle time、alias correctness、rollback success、stale champion age。
- Failure modes: latestを本番参照し破壊的更新を拾う、aliasが意図せず別版を指す。

### 13.13 Inference serving

- Definition: モデルをオンライン/バッチ推論として提供する。
- Required artifacts: inference service spec、API schema、deployment manifest、SLO/SLA。
- Controls: autoscaling、timeout、retry、canary/shadow、health check、rollback。
- Metrics: p95/p99 latency、availability、error rate、throughput、cold start。
- Failure modes: load増加で遅延、モデル更新でAPI互換性破壊、rollback不能。

### 13.14 Inference optimization

- Definition: 推論の性能、費用、品質を最適化する。
- Required artifacts: routing policy、batching policy、cache policy、model selection policy。
- Controls: cost budget、latency/error guardrails、quality floor、A/B test。
- Metrics: cost/request、tokens/request、cache hit、GPU utilization、quality degradation。
- Failure modes: cost削減のため品質を落とす、cacheで古い/権限外回答を返す。

### 13.15 Prompt engineering

- Definition: LLMへの指示、文脈、例、形式制約を設計する。
- Required artifacts: prompt spec、examples、output schema、prompt eval set。
- Controls: instruction hierarchy、variable validation、redaction、prompt regression tests。
- Metrics: task success、format pass、policy pass、prompt regression delta。
- Failure modes: 曖昧指示、プロンプトが長く維持不能、モデル更新で性能劣化。

### 13.16 Prompt / template registry

- Definition: prompt/templateを版管理・承認・rollback可能にする。
- Required artifacts: template version、variables schema、test results、release note。
- Controls: semantic versioning、eval gate、owner approval、environment alias。
- Metrics: stale prompt count、eval pass、rollback time、variable error rate。
- Failure modes: テンプレート変更が本番で即時反映され事故化する。

### 13.17 Embedding model

- Definition: テキスト/画像/コード等を検索可能なベクトルへ変換する。
- Required artifacts: embedding spec、model version、dimension、normalization、embedding job。
- Controls: model compatibility、language/domain coverage、re-embedding triggers、cost threshold。
- Metrics: retrieval recall、embedding generation cost、vector freshness、embedding drift。
- Failure modes: embedding model変更後に既存indexと互換性を失う、再embeddingが未完了。

### 13.18 Vector store

- Definition: ベクトルとmetadataを保存し、検索可能にする。
- Required artifacts: vector index、namespace policy、metadata schema、delete/TTL policy。
- Controls: tenant isolation、metadata filters、ACL、index build version、backup。
- Metrics: index freshness、query latency、filter correctness、storage cost。
- Failure modes: tenant間漏洩、metadata不足で検索制御不能、削除要求に追従不能。

### 13.19 Vector search / reranking

- Definition: dense/sparse/hybrid/rerankで関連情報を返す。
- Required artifacts: search config、reranker config、relevance evaluation、query log。
- Controls: top-k/threshold、hybrid weighting、metadata filter、freshness boost、reranker cutoff。
- Metrics: precision@k、recall@k、MRR/NDCG、latency、zero-result rate。
- Failure modes: semantic類似だけで法務/製品IDなど正確一致を落とす。

### 13.20 RAG ingestion / grounding

- Definition: 外部知識をRAGコーパスとして取り込み、回答根拠に接続する。
- Required artifacts: corpus registry、chunking policy、source metadata、citation policy。
- Controls: canonical source priority、chunk overlap、ACL propagation、source freshness、reindex trigger。
- Metrics: groundedness、citation accuracy、stale source rate、retrieval coverage。
- Failure modes: 古い文書、権限外文書、断片化されたchunk、引用不一致。

### 13.21 RAG / generated-answer evaluation

- Definition: RAGの回答と根拠の一致を評価する。
- Required artifacts: golden queries、expected sources、faithfulness rubric、unsupported answer taxonomy。
- Controls: groundedness detector、human review、source-required answers、refusal rule。
- Metrics: faithfulness、unsupported answer rate、citation precision、answer relevance。
- Failure modes: もっともらしいが根拠にない回答、sourceは正しいが解釈が誤る。

### 13.22 Agent architecture

- Definition: LLMが複数ステップで状態・記憶・ツール・handoffを使う構造を設計する。
- Required artifacts: agent graph、state schema、memory policy、handoff policy、stop condition。
- Controls: durable execution、max steps、interrupts、checkpointing、loop detection。
- Metrics: task completion、step count、loop rate、handoff success、state recovery。
- Failure modes: 目的逸脱、無限ループ、過去状態の誤用、handoff責任不明。

### 13.23 Tool calling

- Definition: LLM/agentが外部関数・API・DB・ブラウザ・コード実行を呼ぶ境界を定義する。
- Required artifacts: tool schema、auth scope、input/output validation、execution log。
- Controls: JSON schema、least privilege、rate limit、timeout、idempotency、side-effect class。
- Metrics: valid call rate、tool success、invalid arg rate、approval rate、side-effect error。
- Failure modes: tool description injection、過剰権限、冪等でない再試行、出力未検証。

### 13.24 Guardrails / safety controls

- Definition: 生成AIの入力、検索文書、tool call、出力をポリシーに従って制御する。
- Required artifacts: safety policy、guardrail config、content filter、prompt shield、escalation rule。
- Controls: input/output moderation、prompt injection detection、groundedness、tool guardrail、human approval。
- Metrics: unsafe block、false positive、false negative、jailbreak success、escalation count。
- Failure modes: guardrail回避、過剰拒否、toolへの危険入力、ガードレールがhandoffに効かない境界。

### 13.25 AI monitoring / observability / drift

- Definition: AIアプリの本番挙動、品質、コスト、リスク、変化を観測する。
- Required artifacts: trace store、dashboard、drift monitor、production eval、incident log。
- Controls: OpenTelemetry-style tracing、production sampling、data/feature drift、eval regression、alert routing。
- Metrics: p95/p99 latency、cost、drift score、eval pass trend、incident MTTR、trace coverage。
- Failure modes: traceがPIIを漏らす、品質劣化をユーザー報告まで検知できない。

### 13.26 Feedback loop / human review / model governance

- Definition: 本番失敗と人間判断を改善・承認・監査に戻す。
- Required artifacts: feedback queue、review rubric、risk register、governance minutes、post-market report。
- Controls: human approval for sensitive actions、review sampling、audit trail、risk re-assessment、change approval。
- Metrics: feedback closure、human review SLA、accepted correction rate、audit findings、policy violations。
- Failure modes: feedbackが溜まるだけで改善されない、人間レビューがrubricなしで属人化する。

---

## 9. Implementation Guide

### First 30 days: minimum viable control plane

1. AI use case intake formを作り、risk tier、owner、data sources、model/provider、tools、user impactを登録する。
2. dataset card、model card、prompt spec、tool schema、eval rubricの最小テンプレートを導入する。
3. 実験管理にMLflow/W&B等を導入し、params、metrics、artifacts、data/model versionを必須化する。
4. prompt/template registryを作り、prompt変更にeval runを必須化する。
5. RAGがある場合、corpus registry、source metadata、chunking policy、citation requirementを設定する。
6. tool callingがある場合、side-effect class、least privilege、human approval requirementを定義する。
7. 最低限のproduction monitoring: latency、error、cost、token、trace、user feedback、guardrail hitを可視化する。

### 31–60 days: release gates and feedback loop

1. Offline eval suiteを作り、model/prompt/RAG/tool変更ごとの合格閾値を設定する。
2. 失敗例、user feedback、human review結果からevaluation datasetを自動増補する。
3. label QA、gold task、adjudication workflowを導入する。
4. model registry / prompt registry / vector index registryのalias policyを統一する。
5. canary/shadow release、rollback rehearsal、incident playbookを標準化する。
6. prompt injection、unsafe output、ungrounded answer、invalid tool callのred-team casesを作る。

### 61–90 days: risk-tiered autonomy and governance

1. risk tier別に、human review、audit、monitoring cadence、documentation depthを差別化する。
2. Drift monitoringをdata、feature、embedding、retrieval、prompt performance、model provider changeに拡張する。
3. AI governance boardを月次で運用し、risk register、incidents、eval trend、human review backlogをレビューする。
4. High-risk AIについてtechnical documentation、record keeping、human oversight、post-market monitoringを制度要求に合わせる。
5. Agentをdurable execution + checkpoint + interrupt + approval + traceで運用する。

---

## 10. QA / Validation Queries

以下のクエリは、Clone Specの主要主張を反証・更新するために定期実行する。

```text
site:nist.gov "AI Risk Management Framework" "Generative AI Profile" after:2025-01-01
site:iso.org "ISO/IEC 42001" "artificial intelligence management system"
site:digital-strategy.ec.europa.eu "AI Act" "GPAI" "Code of Practice" after:2025-01-01
site:developers.openai.com/api/docs "evals" "production" "evaluation"
site:developers.openai.com/api/docs "guardrails" "human review" "Agents SDK"
site:platform.claude.com/docs "tool use" "agentic loop"
site:docs.langchain.com "human-in-the-loop" "durable execution"
site:docs.feast.dev "feature registry" "offline store" "online store"
site:mlflow.org/docs "Model Registry" "aliases" "tags"
site:docs.cloud.google.com/vertex-ai "Model Monitoring" "skew" "drift"
site:learn.microsoft.com/azure/ai-services/content-safety "Prompt Shields" "Groundedness"
site:owasp.org "Top 10 for Large Language Model Applications" "2025"
"RAG" "faithfulness" "evaluation" site:developers.llamaindex.ai OR site:docs.langchain.com
"prompt injection" "incident" "LLM" after:2025-01-01
"model registry" "incident" OR "rollback" "MLflow" after:2025-01-01
"AI agent" "tool call" "security incident" after:2025-01-01
```

---

## 11. Pattern Library

| Pattern ID | Pattern | Scope | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P01 | Registry-linked documentation | 13.02, 13.10, 13.12, 13.16, 13.18, 13.26 | dataset/model/prompt/vector/toolの文書をregistry objectに紐づける | registryがある | 文書更新コスト | A |
| P02 | Evaluation-gated promotion | 13.08, 13.09, 13.12, 13.15, 13.21 | 昇格前にoffline/human/safety/RAG evalを通す | eval suiteがある | release速度低下 | A |
| P03 | Champion/challenger alias | 13.12, 13.13 | 本番参照を固定版でなくaliasで管理し、切替/rollbackする | model registry | alias誤操作リスク | A |
| P04 | RAG corpus registry | 13.18–13.21 | 文書source、chunk、embedding、indexをregistry化する | source metadata | 管理面が増える | B |
| P05 | Hybrid retrieval + metadata filter | 13.19–13.21 | dense semantic検索にBM25/keywordとmetadata制約を追加する | metadata整備 | latency増加 | A/B |
| P06 | Prompt as deployable artifact | 13.15–13.16 | promptをコード同様に版管理・評価・rollbackする | prompt registry | 運用負荷 | A/B |
| P07 | Least-privilege tool schema | 13.23–13.24 | tool権限を最小化し、schemaとside-effectで制御する | API catalog | agent柔軟性低下 | A |
| P08 | Human approval interrupt | 13.21, 13.23, 13.26 | 不可逆操作でagent実行を停止し、人間承認後に再開する | review UI, policy | SLAが必要 | A |
| P09 | Production trace to eval dataset | 13.09, 13.25–13.26 | 本番失敗traceを評価セットへ還流する | trace store | privacy処理が必要 | A/B |
| P10 | Drift-triggered review | 13.04, 13.05, 13.20, 13.25–13.26 | drift/skew/embedding drift検出で再評価・再学習・RAG更新を起動する | drift monitor | false alarm | A/B |
| P11 | Guardrail at every boundary | 13.24 | input、retrieved docs、tool call、tool output、final outputで検査する | policy taxonomy | false positive | A/B |
| P12 | Risk-tiered autonomy | 13.01, 13.22–13.26 | low-riskでは自動化、高-riskではhuman oversight/approvalを増やす | risk tiering | 運用複雑性 | A |

---

## 12. Control Checklist

### Pre-release checklist

- [ ] use case, risk tier, owner, jurisdictionが登録済み
- [ ] dataset card / datasheetが最新版
- [ ] data license / PII / retention確認済み
- [ ] label rubric / annotation QA / adjudication logがある
- [ ] feature definitions and point-in-time join確認済み
- [ ] experiment runはcode/data/config/params/metrics/artifactsを保持
- [ ] model cardがregistry versionと一致
- [ ] offline eval / safety eval / slice eval / regression eval合格
- [ ] prompt/template eval合格
- [ ] RAG corpus freshness and citation policy確認済み
- [ ] vector index metadata and ACL確認済み
- [ ] tool schema / least privilege / idempotency / timeout定義済み
- [ ] guardrails and prompt injection tests合格
- [ ] human review条件が実装済み
- [ ] canary/shadow/rollback plan確認済み
- [ ] monitoring dashboard and alerts設定済み

### Production review checklist

- [ ] latency, error, cost, token, availabilityがSLO内
- [ ] eval-in-prodの低下なし
- [ ] data/feature/embedding/retrieval driftが閾値内
- [ ] guardrail false positive/false negativeレビュー済み
- [ ] human review backlogがSLA内
- [ ] user feedbackの重大未処理なし
- [ ] incidents and near missesがrisk registerへ反映済み
- [ ] model/prompt/RAG/tool changesが監査ログに残っている

---

## 13. Unknowns and Follow-up Research

| Unknown | Why it matters | Follow-up |
|---|---|---|
| 企業内部の実際のAI governance board運用 | 公開情報だけでは承認会議体の詳細は不明 | 公開監査資料、trust center、case study、regulatory filingsを追加確認 |
| 各ベンダーの最新モデル別tool calling制約 | モデル更新で仕様が変わる | OpenAI / Anthropic / Google docsを月次確認 |
| Guardrail precision/recallの実測 | ベンダーdocsは機能説明であり、現場性能はuse case依存 | 自社red-team datasetで検証 |
| RAG評価metricの標準化 | faithfulnessやrelevanceは実装により定義差がある | LlamaIndex, LangSmith, Phoenix, RAGAS等を比較実験 |
| EU AI Actの実装ガイドライン更新 | 適用時期・解釈が2026年も更新中 | EC AI Actページ、AI Act Service Desk、GPAI Code更新を継続監視 |

---

## 14. Short Clone Implementation Blueprint

```yaml
ai_system_control_plane:
  registries:
    dataset_registry: required
    feature_registry: required_if_predictive_ml
    experiment_tracking: required
    artifact_registry: required
    model_registry: required
    prompt_registry: required_if_llm
    vector_index_registry: required_if_rag
    tool_registry: required_if_agent_or_tool_calling
  gates:
    data_gate:
      required_artifacts: [dataset_card, license_check, pii_check, validation_report]
    eval_gate:
      required_artifacts: [eval_dataset, thresholds, run_report, regression_report]
    safety_gate:
      required_artifacts: [red_team_cases, guardrail_config, policy_report]
    release_gate:
      required_artifacts: [approval_log, rollback_plan, monitoring_config]
  monitoring:
    telemetry: [trace, prompt, retrieval_hits, tool_calls, guardrail_decisions, output, feedback]
    metrics: [latency, error_rate, cost, eval_score, groundedness, drift, safety_events]
    alerts: [slo_breach, eval_regression, drift_threshold, unsafe_output, tool_failure]
  human_review:
    required_for: [irreversible_action, external_send, financial_or_legal_action, high_risk_domain, low_confidence, policy_boundary]
    artifacts: [review_rubric, reviewer_decision, audit_log]
  governance:
    artifacts: [risk_register, model_card, dataset_card, technical_documentation, incident_report]
    cadence: [pre_release, monthly, incident_triggered, model_provider_change]
```
