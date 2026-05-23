# Frontier Operating Model Research: サービスプラットフォーム・エッジ・暗号基盤（Layers 14）

生成日: 2026-05-13  
対象: web/app server、reverse proxy、API gateway、load balancer、WAF、CDN、service mesh、discovery、config/secret/key/certificate management、encryption、hashing、digital signature  
調査方針: 公開情報限定。標準、公式ドキュメント、OSS公式運用文書、クラウド公式ドキュメント、公開インシデント/NVDを優先した。  
注意: 正式レイヤー名一覧が未提示のため、対象サブテーマを20レイヤーに運用分解して 14 に割り当てた。既存レジストリがある場合は `layer_name` のみ差し替えればよい。

---

## 0. Scope Normalization

この単位の意思決定問題は次の一文に集約できる。

> 先端組織は、サービス公開面、エッジ制御、サービス間通信、設定・秘密・鍵・証明書・暗号プリミティブを、どの契約、制約、ライフサイクル、所有権、監査、失敗時制御で設計し、どう安全に変更し続けるのか。

| Layer ID | Layer Name | Decision Object | 主なOwner | 代表Artifact |
|---:|---|---|---|---|
| 14.01 | Web Server | HTTP(S)終端、静的配信、基本ヘッダ、TLS終端の構成 | Platform / SRE / Security | server config、TLS policy、security headers、access log |
| 14.02 | Application Server | アプリ実行基盤、health/readiness、shutdown、runtime設定 | App Platform / Backend | runtime profile、health endpoint、actuator/metrics config |
| 14.03 | Reverse Proxy | upstream選択、ヘッダ変換、buffering、open proxy防止 | Platform / Edge | proxy config、upstream map、timeout policy |
| 14.04 | API Gateway | API公開契約、authn/z、quota/rate、protocol mediation | API Platform / Security | gateway route、auth policy、OpenAPI、quota policy |
| 14.05 | Load Balancer | 負荷分散、health check、failover、session affinity | SRE / Network | LB listener、target group、probe、algorithm policy |
| 14.06 | WAF | HTTPリクエスト検査、managed/custom rule、rate-based防御 | Security / Edge | WAF ACL、managed rules、exception list、false-positive register |
| 14.07 | CDN / Edge Cache | edge caching、TTL、cache key、purge、origin protection | Edge / Performance | cache policy、TTL table、purge workflow、origin shield setting |
| 14.08 | Edge Routing / Gateway API / Ingress | Kubernetes/edge routing API、HTTPRoute、責任分界 | Platform / Cluster Ops | GatewayClass、Gateway、HTTPRoute、Ingress |
| 14.09 | Service Mesh | mTLS、L7 policy、traffic split、sidecar/ambient control | Platform / Service Owner / Security | mesh policy、PeerAuthentication、AuthorizationPolicy |
| 14.10 | Service Discovery | service name、endpoint resolution、DNS/xDS/registry | Platform / SRE | DNS record、Service、EndpointSlice、xDS cluster |
| 14.11 | Config Management | 非機密設定、環境差分、feature flag、config drift | Platform / App Owner | ConfigMap、env var、feature flag、config schema |
| 14.12 | Secret Management | secret storage、provisioning、rotation、lease、audit | Security / Platform | secret path、lease policy、rotation runbook、access audit |
| 14.13 | Key Management / KMS | key hierarchy、rotation、wrapping、envelope encryption | Security / Crypto Owner | KMS key、key policy、alias/version、rotation schedule |
| 14.14 | Certificate Management / PKI | issuance、renewal、revocation、trust bundle | Security / Platform | Issuer、Certificate、ACME challenge、trust bundle |
| 14.15 | Transport Encryption / TLS / mTLS | 通信暗号、TLS version/cipher、certificate validation | Security / Network / Platform | TLS profile、mTLS policy、cipher suite policy |
| 14.16 | Data-at-rest / Application Encryption | 保存データ暗号化、DEK/KEK、application-level encryption | Security / Data Platform | envelope design、transit encryption policy、encrypted resource config |
| 14.17 | Hashing / Password Hashing / Integrity Digest | digest、password hashing、salt/pepper、HMAC | Security / App Owner | password hashing policy、digest policy、KDF parameter set |
| 14.18 | Digital Signature / Artifact Signing | 署名、検証、JWS、コード/OCI artifact signing | Security / Supply Chain | signing policy、verification gate、attestation、JWS profile |
| 14.19 | Entropy / Randomness / Crypto Runtime | entropy source、DRBG、crypto module assurance | Security / Runtime Platform | RNG policy、FIPS module list、health test evidence |
| 14.20 | Crypto Governance / Crypto Agility / PQC | 暗号棚卸、移行、非推奨、PQC readiness | CISO / Crypto Governance | crypto inventory、algorithm policy、migration roadmap |

---

## 1. Executive Synthesis

この20レイヤーのfrontier operating modelは、単一製品の選定ではなく、制御面とデータ面の分離、公開契約の明示、ライフサイクル自動化、段階的変更、暗号資産の棚卸、失敗時のblast radius制御で成立する。

第一に、edge-facingレイヤーでは、web server、reverse proxy、API gateway、load balancer、WAF、CDNを「入口の連続した制御点」として設計する。先端組織は、HTTP contract、routing、health check、rate limit、cache key、WAF rule、TLS profileを別々の設定として管理しながら、変更時にはcanary、staged rollout、rollbackを必須化する。FastlyとCloudflareの大規模障害は、edge設定が世界規模の障害要因になり得ることを示しており、特にWAF/CDNのrule deploymentは性能検証と段階適用が必要である。

第二に、service platformレイヤーでは、Gateway API、Ingress、service mesh、service discoveryを「アプリ開発者が使う契約」と「インフラ運用者が管理する実装」に分ける。Kubernetes Gateway APIのrole-oriented model、Istio/LinkerdのmTLS/authorization、EnvoyのxDS/service discoveryは、この分離を明確にする典型例である。先端組織では、L7 route、service identity、authorization、traffic split、observabilityをGitOps/IaC化し、手作業のproxy変更を減らす。

第三に、config/secret/key/certificate管理では、非機密設定、秘密、鍵、証明書を混同しない。ConfigMapや12-Factorのconfigは非機密設定に適するが、secretは中央管理、最小権限、audit、rotation、TTL/leaseを持つべきである。KMSは鍵材料の露出を減らし、envelope encryptionやkey versioningを通じて暗号運用を制御する。証明書はACME/cert-manager等で発行・更新を自動化し、有効期限切れを運用事故にしない。

第四に、暗号基盤では、TLS、保存データ暗号、hashing、digital signature、entropy、crypto module assuranceを別々の意思決定として扱う。パスワードに高速ハッシュを使う、signatureとMACを混同する、乱数品質を検証しない、鍵ローテーションを「定期作業」だけにする、PQC移行を棚卸なしに開始する、という設計はfrontierではない。NIST/IETF/OWASPの標準・ガイドをpolicy baselineにし、例外はrisk acceptance付きで管理する。

---

## 2. Source Catalog

| Source ID | Entity | Source | Tier | Layer Scope | Key Fact / Use | URL |
|---|---|---|---|---|---|---|
| S-001 | Apache HTTP Server | Security Tips | T3 | 14.01 | web server hardening baseline | https://httpd.apache.org/docs/current/misc/security_tips.html |
| S-002 | Apache HTTP Server | mod_proxy | T2/T3 | 14.03 | proxy/gateway/reverse proxy; open proxy warning | https://httpd.apache.org/docs/current/mod/mod_proxy.html |
| S-003 | NGINX | Product docs index | T2/T3 | 14.01,14.03,14.05 | web server, reverse proxy, cache, load balancer | https://nginx.org/en/docs/ |
| S-004 | NGINX | Reverse Proxy Guide | T2/T3 | 14.03 | upstream forwarding, headers, buffering | https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/ |
| S-005 | NGINX | HTTP Load Balancing | T2/T3 | 14.05 | load-balancing methods and upstream pools | https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/ |
| S-006 | HAProxy | Health Checks | T2/T3 | 14.05 | only healthy servers remain in rotation | https://www.haproxy.com/documentation/haproxy-configuration-tutorials/reliability/health-checks/ |
| S-007 | HAProxy | Project / documentation | T2/T3 | 14.03,14.05 | reverse proxy and load balancing | https://www.haproxy.org/ |
| S-008 | Envoy | Dynamic configuration / xDS | T2/T3 | 14.03,14.08,14.10 | runtime-discovered route/config updates | https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/operations/dynamic_configuration |
| S-009 | Envoy | Service discovery | T2/T3 | 14.10 | upstream cluster membership discovery | https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/service_discovery |
| S-010 | Envoy | HTTP connection manager | T2/T3 | 14.03,14.04 | HTTP event/codec manager | https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/intro |
| S-011 | Kong Gateway | Rate limiting | T2/T3 | 14.04 | API gateway rate governance | https://docs.konghq.com/gateway/latest/rate-limiting/ |
| S-012 | AWS | API Gateway throttling | T2/T3 | 14.04 | throttling/quota as API protection | https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html |
| S-013 | Google Cloud | API Gateway overview | T2/T3 | 14.04 | API gateway as secure REST entry point | https://cloud.google.com/api-gateway/docs/about-api-gateway |
| S-014 | Envoy Gateway | Documentation | T2/T3 | 14.04,14.08 | Gateway API-driven Envoy management | https://gateway.envoyproxy.io/docs/ |
| S-015 | Kubernetes SIG Network | Gateway API | T0/T3 | 14.08 | role-oriented, extensible routing APIs | https://gateway-api.sigs.k8s.io/ |
| S-016 | Kubernetes | Ingress | T0/T3 | 14.08 | cluster external HTTP access rules | https://kubernetes.io/docs/concepts/services-networking/ingress/ |
| S-017 | AWS | Application Load Balancer | T2/T3 | 14.05 | target groups and health checks | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html |
| S-018 | Google Cloud | Cloud Load Balancing overview | T2/T3 | 14.05 | proxy LB architecture | https://cloud.google.com/load-balancing/docs/load-balancing-overview |
| S-019 | Microsoft Azure | Load Balancer health probes | T2/T3 | 14.05 | health probe based routing | https://learn.microsoft.com/azure/load-balancer/load-balancer-custom-probe-overview |
| S-020 | OWASP | Core Rule Set | T3/T5 | 14.06 | generic WAF attack detection rules | https://owasp.org/www-project-modsecurity-core-rule-set/ |
| S-021 | AWS | WAF rules | T2/T3 | 14.06 | request inspection and match actions | https://docs.aws.amazon.com/waf/latest/developerguide/waf-rules.html |
| S-022 | AWS | WAF rate-based rule | T2/T3 | 14.06 | rate limit by aggregation key/window | https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based.html |
| S-023 | Cloudflare | Cache docs | T2/T3 | 14.07 | geographically distributed edge cache | https://developers.cloudflare.com/cache/ |
| S-024 | Cloudflare | Default cache behavior | T2/T3 | 14.07 | file-extension based default cache behavior | https://developers.cloudflare.com/cache/concepts/default-cache-behavior/ |
| S-025 | Fastly | June 8 outage summary | T5 | 14.07 | valid customer config triggered latent bug; global outage | https://www.fastly.com/blog/summary-of-june-8-outage |
| S-026 | Cloudflare | July 2 2019 outage | T5 | 14.06,14.07 | WAF managed rule caused CPU exhaustion globally | https://blog.cloudflare.com/cloudflare-outage/ |
| S-027 | Istio | AuthorizationPolicy | T2/T3 | 14.09 | CUSTOM/DENY/ALLOW policy evaluation | https://istio.io/latest/docs/reference/config/security/authorization-policy/ |
| S-028 | Istio | mTLS migration | T2/T3 | 14.09,14.15 | permissive-to-strict mTLS migration | https://istio.io/latest/docs/tasks/security/authentication/mtls-migration/ |
| S-029 | Linkerd | Automatic mTLS | T2/T3 | 14.09,14.15 | automatic mTLS between meshed workloads | https://linkerd.io/2.16/features/automatic-mtls/ |
| S-030 | Linkerd | Certificate rotation | T2/T3 | 14.09,14.14 | workload identity depends on trust anchor/issuer certs | https://linkerd.io/2.16/tasks/automatically-rotating-control-plane-tls-credentials/ |
| S-031 | NIST | SP 800-204A Service Mesh | T0 | 14.09 | service mesh security deployment guidance | https://csrc.nist.gov/pubs/sp/800/204/a/final |
| S-032 | Kubernetes | DNS for Services and Pods | T0/T3 | 14.10 | stable DNS discovery for Services/Pods | https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/ |
| S-033 | Kubernetes | ConfigMaps | T0/T3 | 14.11 | non-confidential key-value config | https://kubernetes.io/docs/concepts/configuration/configmap/ |
| S-034 | Twelve-Factor App | Config | T3 | 14.11 | environment variables as deployment config | https://12factor.net/config |
| S-035 | OpenFeature | Specification/docs | T0/T3 | 14.11 | vendor-agnostic feature flag API | https://openfeature.dev/ |
| S-036 | Kubernetes | Secrets | T0/T3 | 14.12 | sensitive data object for password/token/key | https://kubernetes.io/docs/concepts/configuration/secret/ |
| S-037 | OWASP | Secrets Management Cheat Sheet | T3/T5 | 14.12 | centralize secret storage/provisioning/auditing/rotation | https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html |
| S-038 | HashiCorp Vault | Secrets engines | T2/T3 | 14.12,14.13,14.16 | store/generate/encrypt data | https://developer.hashicorp.com/vault/docs/secrets |
| S-039 | HashiCorp Vault | Leases | T2/T3 | 14.12 | dynamic secret lease, TTL, revocation | https://developer.hashicorp.com/vault/docs/concepts/lease |
| S-040 | Kubernetes | Encrypt data at rest | T0/T3 | 14.12,14.16 | resource data encryption, including Secrets | https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/ |
| S-041 | Kubernetes | KMS provider | T0/T3 | 14.13,14.16 | KMS v2 for envelope encryption provider | https://kubernetes.io/docs/tasks/administer-cluster/kms-provider/ |
| S-042 | AWS KMS | Key concepts | T2/T3 | 14.13 | customer managed keys, policies, grants, rotation | https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html |
| S-043 | Google Cloud KMS | Key rotation | T2/T3 | 14.13 | regular/event-driven key rotation | https://cloud.google.com/kms/docs/key-rotation |
| S-044 | Azure Key Vault | Key rotation | T2/T3 | 14.13 | automatic key rotation policy | https://learn.microsoft.com/azure/key-vault/keys/how-to-configure-key-rotation |
| S-045 | Vault Transit | Transit secrets engine | T2/T3 | 14.13,14.16,14.17,14.18,14.19 | encryption/sign/hash/HMAC/random-as-a-service | https://developer.hashicorp.com/vault/docs/secrets/transit |
| S-046 | IETF | RFC 8555 ACME | T0 | 14.14 | automated certificate issuance and revocation | https://datatracker.ietf.org/doc/html/rfc8555 |
| S-047 | cert-manager | Documentation | T2/T3 | 14.14 | Kubernetes certificate issuance/renewal | https://cert-manager.io/docs/ |
| S-048 | Let's Encrypt | Integration Guide | T3 | 14.14 | renewal timing and ACME integration guidance | https://letsencrypt.org/docs/integration-guide/ |
| S-049 | CA/Browser Forum | Baseline Requirements | T0 | 14.14 | public TLS server certificate requirements | https://cabforum.org/working-groups/server/baseline-requirements/requirements/ |
| S-050 | IETF | RFC 8446 TLS 1.3 | T0 | 14.15 | TLS protects against eavesdropping/tampering/forgery | https://datatracker.ietf.org/doc/html/rfc8446 |
| S-051 | NIST | SP 800-52 Rev.2 TLS | T0 | 14.15 | TLS selection/configuration guidance | https://csrc.nist.gov/pubs/sp/800/52/r2/final |
| S-052 | OWASP | Cryptographic Storage Cheat Sheet | T3/T5 | 14.16 | cryptographic storage design and password caveat | https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html |
| S-053 | OWASP | Password Storage Cheat Sheet | T3/T5 | 14.17 | Argon2id/bcrypt/PBKDF2, salt, no fast hash for passwords | https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html |
| S-054 | NIST | FIPS 180-4 Secure Hash Standard | T0 | 14.17 | message digest algorithms | https://csrc.nist.gov/pubs/fips/180/4/upd1/final |
| S-055 | NIST | FIPS 186-5 Digital Signature Standard | T0 | 14.18 | RSA/ECDSA/EdDSA signature generation/verification | https://csrc.nist.gov/pubs/fips/186/5/final |
| S-056 | IETF | RFC 7515 JWS | T0 | 14.18 | JSON Web Signature integrity/signature/MAC format | https://datatracker.ietf.org/doc/html/rfc7515 |
| S-057 | Sigstore | Cosign Quickstart | T2/T3 | 14.18 | sign and verify blobs/containers | https://docs.sigstore.dev/quickstart/quickstart-cosign/ |
| S-058 | NIST | SP 800-90A Rev.1 DRBG | T0 | 14.19 | deterministic random bit generators | https://csrc.nist.gov/pubs/sp/800/90/a/r1/final |
| S-059 | NIST | SP 800-90B Entropy Sources | T0 | 14.19 | entropy source requirements/tests | https://csrc.nist.gov/pubs/sp/800/90/b/final |
| S-060 | IETF | RFC 4086 Randomness Requirements | T0 | 14.19 | entropy pitfalls and random source guidance | https://datatracker.ietf.org/doc/html/rfc4086 |
| S-061 | NIST | FIPS 140-3 | T0 | 14.19,14.20 | cryptographic module security requirements | https://csrc.nist.gov/pubs/fips/140-3/final |
| S-062 | NIST | SP 800-57 Part 1 Rev.5 | T0 | 14.13,14.20 | key management guidance and best practices | https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final |
| S-063 | NVD | CVE-2014-0160 Heartbleed | T5 | 14.15,14.19 | TLS library memory leak exposing keys/secrets | https://nvd.nist.gov/vuln/detail/CVE-2014-0160 |
| S-064 | NVD | CVE-2021-44228 Log4Shell | T5 | 14.02,14.04 | app/runtime dependency vulnerability and RCE risk | https://nvd.nist.gov/vuln/detail/CVE-2021-44228 |
| S-065 | NIST | Post-Quantum Cryptography | T0/T3 | 14.20 | PQC standardization and algorithm transition | https://csrc.nist.gov/projects/post-quantum-cryptography |
| S-066 | NIST NCCoE | PQC migration project | T3/T5 | 14.20 | migration practices from quantum-vulnerable algorithms | https://www.nccoe.nist.gov/crypto-agility-considerations-migrating-post-quantum-cryptographic-algorithms |
| S-067 | CISA | Quantum Readiness | T3/T5 | 14.20 | inventory and migration readiness guidance | https://www.cisa.gov/resources-tools/resources/quantum-readiness-migration-post-quantum-cryptography |
| S-068 | Apache Tomcat | Security Considerations | T3 | 14.02 | app server hardening | https://tomcat.apache.org/tomcat-11.0-doc/security-howto.html |
| S-069 | Spring Boot | Actuator | T2/T3 | 14.02 | application health/metrics/management endpoints | https://docs.spring.io/spring-boot/reference/actuator/index.html |
| S-070 | Jakarta EE | Specifications | T0/T3 | 14.02 | application server/runtime specification family | https://jakarta.ee/specifications/ |

---

## 3. Evidence Graph: Major Claims

| Claim ID | Claim | Layer Scope | Evidence | Confidence |
|---|---|---:|---|---|
| C-001 | web/app serverは「コード実行」と「公開入口」を分離し、health/readiness、shutdown、security headers、TLS、logsを明示設定する必要がある。 | 14.01,14.02 | S-001, S-003, S-068, S-069 | B |
| C-002 | reverse proxyはupstream routing、header transformation、buffering、TLS offloadを制御するが、open proxy化は明示的に禁止すべきである。 | 14.03 | S-002, S-004, S-007, S-010 | A |
| C-003 | API gatewayは公開API contract、auth、quota/rate、observability、backend abstractionを集約する制御点である。 | 14.04 | S-011, S-012, S-013, S-014 | A |
| C-004 | load balancerはalgorithmよりもhealth check/probe、failover、readiness gating、observabilityを優先して設計される。 | 14.05 | S-005, S-006, S-017, S-018, S-019 | A |
| C-005 | WAFはmanaged rulesだけで完結しない。false positive、performance regression、rate-based thresholds、exception governanceが必要である。 | 14.06 | S-020, S-021, S-022, S-026 | A |
| C-006 | CDN/edge cacheの正しさはcache key、TTL、purge、origin fallback、staged rolloutで決まる。 | 14.07 | S-023, S-024, S-025 | A |
| C-007 | Gateway API/Ingressは「infra ownerがGatewayを、app ownerがRouteを管理する」責任分界を可能にする。 | 14.08 | S-015, S-016, S-014 | A |
| C-008 | service meshはmTLS、identity、authorization、traffic policy、telemetryをservice単位に移すが、証明書/CA lifecycleが新しい運用リスクになる。 | 14.09 | S-027, S-028, S-029, S-030, S-031 | A |
| C-009 | service discoveryはIPではなく安定名・endpoint集合・health/readiness情報で接続先を決める。 | 14.10 | S-008, S-009, S-032 | A |
| C-010 | configはsecretではない。非機密設定はConfigMap/env/feature flag、secretはSecret/Vault/KMSへ分離する。 | 14.11,14.12 | S-033, S-034, S-035, S-036, S-037 | A |
| C-011 | secret managementは保存場所ではなく、provisioning、least privilege、audit、rotation、lease/revocationを含むライフサイクルである。 | 14.12 | S-037, S-038, S-039 | A |
| C-012 | KMSではkey hierarchy、policy/grant、version/alias、rotation、envelope encryptionを設計単位にする。 | 14.13 | S-041, S-042, S-043, S-044, S-062 | A |
| C-013 | certificate managementはACME等で発行・更新・失効・trust bundle配布を自動化し、期限切れをSLO違反として扱う。 | 14.14 | S-046, S-047, S-048, S-049 | A |
| C-014 | TLS/mTLSは通信の盗聴・改ざん・偽造を防ぐ基盤だが、protocol/cipher/cert validation/rollbackのpolicyがなければ安全でない。 | 14.15 | S-050, S-051, S-028, S-029, S-063 | A |
| C-015 | 保存データ暗号化は、storage encryption、resource encryption、application-level encryption、transit/envelope encryptionを区別する。 | 14.16 | S-040, S-041, S-045, S-052 | A |
| C-016 | password hashingは一般のmessage digestと異なり、slow KDF、unique salt、必要に応じたpepper/parameter upgradeを要する。 | 14.17 | S-053, S-054 | A |
| C-017 | digital signatureはintegrity、origin authentication、non-repudiation/third-party verifiabilityを担う。JWSやartifact signingは運用上の具体化である。 | 14.18 | S-055, S-056, S-057 | A |
| C-018 | entropy/RNG品質は全暗号レイヤーの前提であり、DRBG・entropy source・module self-testの統制が必要である。 | 14.19 | S-058, S-059, S-060, S-061 | A |
| C-019 | crypto governanceではアルゴリズム、鍵長、モジュール、証明書、使用箇所を棚卸し、非推奨・PQC移行・例外承認を運用する。 | 14.20 | S-061, S-062, S-065, S-066, S-067 | A |
| C-020 | edge/global control planeの変更はblast radiusが大きいため、canary、synthetic test、automatic rollback、human break-glassを必須化する。 | 14.04–14.08 | S-025, S-026, S-008, S-015 | B |

---

## 4. Cross-layer Operating Model

### 4.1 Core Philosophy

1. **Contract first, implementation second.** API、Gateway、Route、Service、TLS、KMS、Certificateは、実装より先に契約・policy・schemaとして定義する。
2. **Control plane / data plane separation.** Gateway API、Envoy xDS、service mesh、KMS、certificate managerは、変更制御と実トラフィック処理を分離する。
3. **Lifecycle automation by default.** secret、key、certificate、WAF rules、cache rules、route rulesは、作成だけでなくrotation、renewal、revocation、rollback、auditまで設計対象にする。
4. **Fail safe and observable.** health check、readiness、mTLS、authorization、WAF、rate limit、TLS validationは、障害時の挙動を事前に決める。
5. **Crypto agility.** 暗号方式を固定資産ではなく移行対象として扱い、棚卸、期限、例外、PQC移行を持つ。

### 4.2 Ownership Matrix

| Capability | Primary Owner | Secondary Owner | Approval Trigger |
|---|---|---|---|
| web/app server baseline | Platform Engineering | Security | TLS/profile変更、public exposure変更 |
| reverse proxy / LB | SRE / Edge Platform | App Owner | routing、timeout、health check、failover変更 |
| API gateway | API Platform | Security / Product | public API auth/quota/contract変更 |
| WAF/CDN | Security / Edge Platform | App Owner | managed rule update、cache key/TTL変更、bypass/exception |
| Gateway API / Ingress | Cluster Platform | Service Owner | cross-namespace route、external exposure |
| service mesh | Platform Security | Service Owner | strict mTLS、AuthorizationPolicy、traffic split |
| config/secret/key/cert | Security Platform | App Owner | secret scope、KMS key policy、CA/trust anchor変更 |
| crypto standards | CISO / Crypto Governance | Architecture Board | algorithm/key length/module/PQC exception |

### 4.3 Standard Artifacts

- `edge_baseline.yaml`: default TLS、headers、timeouts、access logging、compression、body limits。
- `gateway_contract.yaml`: GatewayClass/Gateway/HTTPRoute/API gateway route/Auth/RateLimit。
- `waf_policy.yaml`: managed rule groups、custom rules、rate-based rules、allowlist、exception expiry。
- `cache_policy.yaml`: cache key、TTL、purge、origin shield、bypass rules。
- `mesh_security.yaml`: PeerAuthentication、AuthorizationPolicy、mTLS mode、service identity。
- `config_schema.json`: environment-specific non-secret config schema。
- `secret_lifecycle.md`: secret owner、source、lease、rotation、break-glass、audit。
- `kms_key_registry.csv`: key ID、alias、purpose、owner、rotation、retirement、dependent systems。
- `certificate_registry.csv`: CN/SAN、issuer、owner、renewal window、trust bundle、expiry SLO。
- `crypto_inventory.csv`: algorithm、key length、library/module、data class、deprecation date、PQC migration status。

### 4.4 Default Metrics

| Metric Family | Representative Metrics |
|---|---|
| Availability | edge availability、LB healthy target ratio、origin error rate、mesh success rate |
| Performance | p50/p95/p99 latency、TLS handshake latency、cache hit ratio、WAF inspection latency |
| Safety | WAF false positive rate、blocked attack classes、rate-limit exceed count、auth failure rate |
| Change Quality | failed rollout count、rollback MTTR、config drift、policy lint failures |
| Secret/Key/Cert Hygiene | secret age、rotation compliance、KMS key usage anomaly、cert expiry under 30 days |
| Crypto Governance | deprecated algorithm count、PQC inventory coverage、FIPS module coverage、exception age |

---

## 5. Clone Specs by Layer

### Layer 14.01: Web Server

**Definition**  
HTTP(S)リクエストを受け、静的ファイル、基本rewrite、TLS終端、security headers、access/error logging、connection timeoutを制御する基盤。

**Frontier Exemplars**  
Apache HTTP Server、NGINX、Caddy系の自動証明書Web server。根拠は、長期運用された公式hardening docs、reverse proxy/TLS docs、豊富な設定artifactが公開されていること。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | public/private exposure、traffic volume、static/dynamic ratio、TLS requirement、header policy、log retention |
| Criteria | least exposure、secure defaults、simple config、observability、graceful reload |
| Priorities | TLS 1.2+/1.3、HSTS/secure headers、directory listing禁止、必要最小module、access/error log標準化 |
| Prohibitions | server version漏洩、default document root放置、wildcard unsafe rewrite、機密ファイル配信、manual cert更新依存 |
| Exceptions | legacy client対応、internal-only endpoint、temporary redirect migration |
| Owners | Platform Engineering、Security、SRE |
| Cadence | baseline quarterly review、TLS/cert/security advisory immediate review |

**Operating Model**  
server configはIaC化し、公開前にTLS scanner、header scanner、access log validationを通す。default vhostはdenyまたは固定レスポンス。reloadはzero-downtimeで実施し、証明書期限は30日前警告ではなく自動更新を前提にする。

**Metrics**  
TLS handshake success、4xx/5xx、security header compliance、unexpected directory listing count、certificate days-to-expiry、reload failure count。

**Failure Modes**  
誤ったdocument root公開、古いTLS/cipher、期限切れ証明書、log未取得、module脆弱性、large bodyでworker枯渇。

**Anti-patterns**  
アプリごとに個別手作業でserver configを変更する。default configを本番で使う。証明書更新を人手カレンダーに依存する。

**Validation Queries**  
`site:httpd.apache.org security tips`, `site:nginx.org docs ssl certificate`, `"web server" "directory listing" security`。

**Confidence & Unknowns**  
Confidence A/B。組織固有のHTTP header policy、legacy client許容範囲は未確定。

---

### Layer 14.02: Application Server

**Definition**  
アプリケーションコードを実行し、request lifecycle、thread/worker、connection pool、health/readiness、management endpoint、graceful shutdownを制御する層。

**Frontier Exemplars**  
Apache Tomcat、Spring Boot Actuator、Jakarta EE application server群。公式security hardening、health/metrics endpoint、specificationが公開されている。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | runtime language、traffic pattern、dependency risk、container lifecycle、health semantics |
| Criteria | predictable startup/shutdown、bounded resources、observable health、dependency isolation |
| Priorities | health/readiness endpoint、graceful shutdown、management endpoint access control、dependency patching |
| Prohibitions | public management endpoint、default credentials、unbounded thread pool、unsafe deserialization endpoint |
| Exceptions | batch-only workloads、internal debug in isolated environment |
| Owners | App Platform、Backend Owner、Security |
| Cadence | release trainごと、critical CVE即時 |

**Operating Model**  
health endpointは「プロセス生存」と「依存先ready」を分ける。management endpointはprivate network + authn/zで保護する。dependency SBOMとCVE triageをrelease gateに入れる。Log4Shellのようなruntime dependency脆弱性を想定し、緊急patch/disable/mitigation runbookを用意する。

**Metrics**  
startup time、readiness failure、graceful shutdown success、thread/connection pool saturation、management endpoint exposure、critical CVE MTTR。

**Failure Modes**  
管理endpoint公開、readinessが依存先障害を反映しない、SIGTERM時に処理中requestを失う、dependency RCE。

**Anti-patterns**  
health checkを`/`の200だけにする。actuator/admin endpointをinternet-facingに置く。JVM/container resource limitを未設定にする。

**Validation Queries**  
`site:tomcat.apache.org security howto`, `site:docs.spring.io actuator security health`, `CVE-2021-44228 application server mitigation`。

**Confidence & Unknowns**  
Confidence B。具体的なruntime標準は組織の言語/フレームワーク依存。

---

### Layer 14.03: Reverse Proxy

**Definition**  
client requestをupstream serviceへ転送し、routing、header、TLS offload、buffering、compression、timeout、retryを制御する層。

**Frontier Exemplars**  
NGINX、HAProxy、Envoy、Apache mod_proxy。公式docsがreverse proxy、load balancing、open proxy禁止、HTTP connection managementを公開している。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | upstream topology、protocol、header requirements、timeout budget、body size、TLS mode |
| Criteria | explicit upstream selection、safe header propagation、bounded buffering、fast rollback |
| Priorities | open proxy禁止、X-Forwarded/Forwarded正規化、request size制限、timeout標準化、upstream health連動 |
| Prohibitions | arbitrary destination proxy、unbounded retry、client IP spoofing、opaque header pass-through |
| Exceptions | migration bridge、legacy service shim、controlled egress proxy |
| Owners | Edge Platform、SRE |
| Cadence | route changeごと、baseline monthly review |

**Operating Model**  
reverse proxy configはroute tableとupstream poolに分離する。header mutationはallowlist方式にし、proxyが生成するtrust boundary headerを明示する。retryはidempotent methodに限定し、timeout budgetを上位gatewayと整合させる。

**Metrics**  
upstream 5xx、proxy 4xx、timeout/retry count、request body reject count、config reload failure、unknown upstream access。

**Failure Modes**  
open proxy、header spoofing、retry storm、large requestによるmemory pressure、誤route、bufferingによるlatency増。

**Anti-patterns**  
proxyを「一時的な転送箱」として手作業で変更する。upstream destinationをrequest parameterで決める。timeoutsを無限大にする。

**Validation Queries**  
`site:httpd.apache.org mod_proxy open proxy`, `site:nginx.com reverse proxy proxy_set_header`, `site:envoyproxy.io http connection manager`。

**Confidence & Unknowns**  
Confidence A。legacy protocol bridgingの許容条件は個別判断。

---

### Layer 14.04: API Gateway

**Definition**  
API公開面におけるrouting、authentication、authorization、rate/quota、request/response transformation、protocol mediation、API observabilityを担う制御層。

**Frontier Exemplars**  
Kong Gateway、AWS API Gateway、Google Cloud API Gateway、Envoy Gateway。公開docsにrate limiting、throttling、secure entry point、Gateway API連携がある。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | API contract、consumer identity、auth scheme、quota tier、backend route、abuse risk |
| Criteria | contract stability、least privilege、quota fairness、backend abstraction、developer experience |
| Priorities | OpenAPI/route contract、authn/z、rate limit、request validation、versioning、observability |
| Prohibitions | anonymous high-risk API、undocumented backend exposure、unbounded quota、gateway bypass |
| Exceptions | internal-only route、emergency bypass with expiry、migration dual-write/dual-route |
| Owners | API Platform、Security、Product/API Owner |
| Cadence | API releaseごと、consumer tier changeごと、abuse event後 |

**Operating Model**  
API gatewayは単なるreverse proxyではなく、consumer contractのenforcement pointとして扱う。routeはAPI specと結びつけ、auth/rate/quotaはconsumerまたはAPI key単位で管理する。backend implementation変更はpublic API contractに影響しないようにする。

**Metrics**  
request volume by consumer、rate-limit exceed、auth failure、backend latency、schema validation failure、API version adoption、gateway bypass count。

**Failure Modes**  
quota過小/過大、auth misconfiguration、backend route leak、breaking change、rate-limit best-effort上限を絶対値と誤解する、observability欠落。

**Anti-patterns**  
API gatewayを「全APIの巨大な手作業設定」にする。consumer identityなしでrate limitする。public API contractなしにbackendを公開する。

**Validation Queries**  
`site:docs.konghq.com gateway rate limiting`, `site:docs.aws.amazon.com apigateway throttling`, `site:cloud.google.com api gateway secure access`。

**Confidence & Unknowns**  
Confidence A。API monetization/tenantごとのquota policyは事業設計に依存。

---

### Layer 14.05: Load Balancer

**Definition**  
複数targetにtrafficを分配し、health check、failover、session affinity、regional/global routing、connection terminationを制御する層。

**Frontier Exemplars**  
AWS ALB/NLB、Google Cloud Load Balancing、Azure Load Balancer、NGINX、HAProxy。公式docsはhealth checks/probesとload-balancing algorithmsを明記する。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | target health、capacity、latency、region、protocol、session stickiness need |
| Criteria | healthy-only routing、fast failover、latency/cost balance、readiness correctness |
| Priorities | health probe、readiness endpoint、connection draining、multi-zone targets、probe source allowlist |
| Prohibitions | unhealthy target routing、manual target removal only、probe path drift、single-zone public LB |
| Exceptions | maintenance drain、blue/green migration、canary weighted target |
| Owners | SRE、Network、Platform |
| Cadence | topology changeごと、probe quarterly review |

**Operating Model**  
LBはtarget groupとhealth checkを分離して管理する。probeはアプリのreadiness semanticsに合わせ、firewall/security groupでprobe sourceを許可する。draining期間はp99 request duration以上を基本にする。

**Metrics**  
healthy target ratio、target response time、5xx by target、connection drain success、probe failure duration、cross-zone imbalance。

**Failure Modes**  
health checkが浅すぎる、probe block、affinityでhotspot化、drainなしdeploy、global failover未検証。

**Anti-patterns**  
round-robin algorithm選定だけでLB設計を完了扱いする。health check endpointをアプリ仕様変更から切り離す。

**Validation Queries**  
`site:docs.aws.amazon.com elasticloadbalancing health checks`, `site:cloud.google.com load balancing overview proxy`, `site:haproxy.com health checks`。

**Confidence & Unknowns**  
Confidence A。具体的SLO/latency budgetはサービスcriticality依存。

---

### Layer 14.06: WAF

**Definition**  
HTTP(S) requestを検査し、OWASP Top Ten系攻撃、bot/abuse、rate anomaly、known exploit signaturesに対するblock/count/challenge/allowを決める層。

**Frontier Exemplars**  
OWASP Core Rule Set、AWS WAF、Cloudflare WAF。公式ルール/managed ruleと、公開障害から得られる運用上の失敗条件がある。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | app risk profile、request patterns、known attacks、false positive tolerance、traffic volume |
| Criteria | attack coverage、low false positive、performance safety、explainability、rollout control |
| Priorities | count-mode test、managed rule versioning、rate-based rules、exception expiry、log sampling |
| Prohibitions | global instant rollout、permanent allowlist without owner、opaque block reason、rule update without rollback |
| Exceptions | business-critical false positive bypass、temporary CVE virtual patch、emergency block |
| Owners | Security、Edge Platform、App Owner |
| Cadence | managed rule updateごと、new CVE/advisoryごと、false-positive weekly review |

**Operating Model**  
WAF ruleは検知、count、blockの段階を持つ。新ruleはsampled trafficでCPU/latency/false positiveを測る。exceptionにはowner、scope、expiry、risk reasonを付ける。global deploymentはcanary POP/regionから開始する。

**Metrics**  
blocked requests、false positive rate、challenge success、WAF latency、CPU overhead、exception age、managed rule drift。

**Failure Modes**  
正規表現ruleのCPU爆発、false positiveで決済/API停止、exception肥大化、log不足、WAF bypass route。

**Anti-patterns**  
managed ruleを無条件に即時blockで全世界適用する。false positive対応を永続allowlistにする。

**Validation Queries**  
`site:owasp.org Core Rule Set false positives`, `site:docs.aws.amazon.com waf rate-based rule`, `Cloudflare WAF outage CPU managed rule`。

**Confidence & Unknowns**  
Confidence A。各アプリ固有のfalse-positive toleranceは業務影響分析が必要。

---

### Layer 14.07: CDN / Edge Cache

**Definition**  
edge locationでcontentをcacheし、cache key、TTL、purge、origin shield、dynamic/static differentiation、edge security integrationを制御する層。

**Frontier Exemplars**  
Cloudflare、Fastly、Akamai系CDN。公式cache docsと大規模outage postmortemが運用証拠を与える。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | asset type、cacheability、privacy、origin capacity、latency goal、purge need |
| Criteria | correctness before hit ratio、bounded staleness、fast purge、origin protection、blast-radius control |
| Priorities | explicit cache key、TTL by content class、private/no-store handling、purge workflow、origin fallback |
| Prohibitions | user-specific content cache、implicit cache key、unbounded TTL、global config change without canary |
| Exceptions | emergency cache bypass、stale-while-revalidate for outage mitigation、regional purge |
| Owners | Edge Platform、Performance、App Owner |
| Cadence | release/changeごと、cache incident後、quarterly policy review |

**Operating Model**  
cache policyをHTML/API/static/media別に定義する。personalized responseはdefaultでcacheしない。purgeはURL/tag/key単位で操作し、global purgeの権限を制限する。origin overload時はstale serving policyを事前定義する。

**Metrics**  
cache hit ratio、origin offload、stale serve count、purge latency、cache poisoning attempt、edge error rate、config rollback time。

**Failure Modes**  
個人情報cache、cache poisoning、purge不能、origin overload、global config bug、TTL misclassification。

**Anti-patterns**  
cache hit ratioだけを最重要KPIにする。API/HTMLを静的assetと同じcache ruleで扱う。

**Validation Queries**  
`site:developers.cloudflare.com cache default cache behavior`, `Fastly June 8 outage configuration change`, `CDN cache key poisoning`。

**Confidence & Unknowns**  
Confidence A/B。business-specific cacheability matrixは追加設計が必要。

---

### Layer 14.08: Edge Routing / Gateway API / Ingress

**Definition**  
Kubernetesやedge platformにおける外部/内部traffic routingのAPIモデルを定義し、infra ownerとapplication ownerの責任分界を制御する層。

**Frontier Exemplars**  
Kubernetes Gateway API、Kubernetes Ingress、Envoy Gateway。Gateway APIはrole-oriented、protocol-aware、extensibleなrouting APIを公開する。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | cluster tenancy、route ownership、protocol、TLS termination、cross-namespace needs |
| Criteria | clear ownership、least privilege route binding、portable routing contract、policy attachment |
| Priorities | GatewayClass/Gateway/Route分離、namespace boundary、HTTPRoute/GRPCRoute、conformance profiles |
| Prohibitions | app ownerによるshared gateway破壊、wildcard host無制限、cross-namespace bind無審査 |
| Exceptions | platform-managed shared route、emergency route block、legacy Ingress migration |
| Owners | Cluster Platform、Network、Service Owner |
| Cadence | route changeごと、Gateway API version upgradeごと |

**Operating Model**  
infra teamはGatewayClass/Gatewayを管理し、app teamはHTTPRoute等を管理する。shared gatewayではhostname claim、listener attach、cross-namespace referenceをpolicy化する。Ingressは単純なHTTP exposureに限定し、高度なtraffic policyはGateway APIへ移行する。

**Metrics**  
route attach success、rejected route count、policy violation、route propagation latency、orphan route、conformance test pass rate。

**Failure Modes**  
namespace境界破壊、wildcard host conflict、TLS secret参照ミス、route shadowing、controller差異。

**Anti-patterns**  
Ingress annotationに全制御を詰め込む。shared gatewayをアプリチームが直接編集する。

**Validation Queries**  
`site:gateway-api.sigs.k8s.io role oriented Gateway API`, `site:kubernetes.io ingress external access`, `site:gateway.envoyproxy.io Gateway API`。

**Confidence & Unknowns**  
Confidence A。controller-specific implementation差は検証が必要。

---

### Layer 14.09: Service Mesh

**Definition**  
サービス間通信にmTLS、service identity、authorization、traffic split/retry、telemetryを付与するcontrol plane/data plane層。

**Frontier Exemplars**  
Istio、Linkerd、Envoyベースmesh、NIST SP 800-204A。公式docsはAuthorizationPolicy、mTLS migration、automatic mTLS、certificate rotationを公開する。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | service identity、trust domain、traffic topology、zero-trust objective、latency budget |
| Criteria | default encryption、least privilege service access、safe rollout、observable policy impact |
| Priorities | permissive-to-strict mTLS migration、AuthorizationPolicy、identity-based access、telemetry、cert rotation |
| Prohibitions | mesh-wide permissive放置、policyなしstrict移行、sidecar resource未設定、CA/trust anchor無管理 |
| Exceptions | legacy workload、non-TCP protocol、temporary policy audit mode |
| Owners | Platform Security、Service Owner、SRE |
| Cadence | workload onboardingごと、cert/trust root lifecycleごと |

**Operating Model**  
mTLSを最初から全域strictにせず、permissive/auditで通信棚卸を行う。AuthorizationPolicyはdeny/allow評価順とauditを理解して段階適用する。mesh certificate chainはissuer/trust anchor rotationをrunbook化する。

**Metrics**  
mTLS coverage、policy deny count、unknown identity traffic、cert expiry、sidecar CPU/memory overhead、mesh latency。

**Failure Modes**  
strict mTLSでlegacy通信停止、AuthorizationPolicy誤block、CA期限切れ、sidecar resource枯渇、observability過信。

**Anti-patterns**  
「service meshを入れればzero trust」と見なす。identity設計なしにmTLSだけ有効化する。

**Validation Queries**  
`site:istio.io AuthorizationPolicy CUSTOM DENY ALLOW`, `site:istio.io mtls migration strict`, `site:linkerd.io automatic mTLS certificate rotation`。

**Confidence & Unknowns**  
Confidence A。ambient mesh/sidecar選択やmulti-cluster trustは追加検証が必要。

---

### Layer 14.10: Service Discovery

**Definition**  
サービス名、endpoint集合、health/readiness、DNS/xDS/registryを通じて、呼び出し元が接続先を解決する仕組み。

**Frontier Exemplars**  
Kubernetes DNS/Service/EndpointSlice、Envoy xDS/service discovery、Consul系registry。公式docsはDNS recordとupstream cluster discoveryを公開する。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | service name、namespace、endpoint health、protocol、cluster/region、TTL |
| Criteria | stable identity、fresh endpoint set、low lookup latency、failure isolation |
| Priorities | DNS/service名標準化、readiness連動、endpoint pruning、TTL設計、multi-region naming |
| Prohibitions | hard-coded IP、stale endpoint routing、unbounded DNS TTL、ambiguous service name |
| Exceptions | stateful service static identity、external service alias、migration CNAME |
| Owners | Platform、SRE、Service Owner |
| Cadence | service lifecycleごと、cluster upgradeごと |

**Operating Model**  
service discoveryは名前解決だけでなく、endpoint healthとroute eligibilityを決める。KubernetesではService/EndpointSlice/DNSを標準とし、EnvoyではxDS cluster membershipをcontrol planeから配布する。external dependencyはServiceEntry/ExternalName等で明示管理する。

**Metrics**  
lookup latency、stale endpoint count、NXDOMAIN、endpoint churn、unready endpoint traffic、cross-region misroute。

**Failure Modes**  
DNS cache stale、readiness無視、service name collision、endpoint storm、control plane不達。

**Anti-patterns**  
アプリ設定にPod IPやインスタンスIPを直接入れる。DNS TTLを短くしすぎてresolverを過負荷にする。

**Validation Queries**  
`site:kubernetes.io DNS for Services and Pods`, `site:envoyproxy.io service discovery upstream cluster`, `service discovery stale endpoints incident`。

**Confidence & Unknowns**  
Confidence A。サービスレジストリ選定はプラットフォーム構成依存。

---

### Layer 14.11: Config Management

**Definition**  
アプリケーションやプラットフォームの非機密設定を、コードから分離し、環境差分、feature flag、validation、drift管理を可能にする層。

**Frontier Exemplars**  
Kubernetes ConfigMap、Twelve-Factor Config、OpenFeature。公式docsは非機密設定、環境変数、vendor-neutral feature flag APIを示す。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | environment、tenant、feature state、runtime parameters、config sensitivity |
| Criteria | code/config separation、safe rollout、validation、auditability、no secret leakage |
| Priorities | schema validation、environment overlay、feature flag standard API、change audit、rollback |
| Prohibitions | secretをConfigMap/env plain textに置く、config drift放置、flag permanent化、unvalidated config deploy |
| Exceptions | immutable build-time config、emergency feature disable、temporary migration flag |
| Owners | App Owner、Platform、Release Engineering |
| Cadence | release/changeごと、flag expiry review monthly |

**Operating Model**  
ConfigMap/env/feature flagを用途で分ける。feature flagはowner、purpose、rollout%、expiryを必須にする。config schemaとpolicy lintをCI/CDで実行し、production changeはdiffとrollbackを保存する。

**Metrics**  
config drift、invalid config deploy、flag age、rollback time、config-related incident count、secret leakage in config scan。

**Failure Modes**  
secret混入、環境差分の未管理、flag debt、設定値typoで全停止、runtime reload不可。

**Anti-patterns**  
設定をコード内定数に戻す。feature flagを恒久的分岐として残す。ConfigMapをsecret store代わりに使う。

**Validation Queries**  
`site:kubernetes.io ConfigMap non-confidential`, `site:12factor.net config environment variables`, `site:openfeature.dev feature flag API`。

**Confidence & Unknowns**  
Confidence A。feature flag governanceの閾値は組織規模依存。

---

### Layer 14.12: Secret Management

**Definition**  
password、token、API key、private key等の秘密情報を、保存、配布、利用、rotation、revocation、auditする層。

**Frontier Exemplars**  
Kubernetes Secrets、HashiCorp Vault、OWASP Secrets Management、SOPS/GitOps型secret管理。公式docsはsecret object、centralization、dynamic leaseを示す。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | secret type、consumer identity、scope、TTL、rotation capability、audit requirement |
| Criteria | least privilege、short lifetime、central audit、no plaintext in repo/image/log、revocability |
| Priorities | central secret store、dynamic secret where possible、lease/TTL、rotation runbook、access audit |
| Prohibitions | secrets in code/image/log、shared long-lived credentials、ownerless secret、manual copy/paste distribution |
| Exceptions | break-glass secret、offline bootstrap secret、third-party static credential with compensating controls |
| Owners | Security Platform、App Owner、IAM |
| Cadence | creation approval、rotation schedule、access review quarterly、incident immediate revocation |

**Operating Model**  
secretはpath、owner、scope、consumer、TTLで登録する。dynamic credentialが可能なDB/cloud/APIではlease付きで発行する。static secretはrotation feasibilityとcompensating controlを記録する。GitOpsではSOPS/age/KMS等で暗号化し、復号権限をCI/CD identityに限定する。

**Metrics**  
secret age、long-lived secret count、rotation success、access anomaly、orphan secret、secret leak detection MTTR。

**Failure Modes**  
repository leak、log leak、shared credential、rotation不能、lease revocation failure、break-glass濫用。

**Anti-patterns**  
Kubernetes Secretを暗号化なしetcdに置いて十分とみなす。secretをSlack/メールで配布する。rotationができないcredentialを無期限に使う。

**Validation Queries**  
`site:kubernetes.io Secrets password token key`, `site:cheatsheetseries.owasp.org Secrets Management centralize rotation`, `site:developer.hashicorp.com/vault lease TTL revocation`。

**Confidence & Unknowns**  
Confidence A。具体的secret taxonomyとrotation intervalはリスク分類依存。

---

### Layer 14.13: Key Management / KMS

**Definition**  
暗号鍵の生成、保管、利用、wrap/unwrap、rotation、versioning、policy、deletion、auditを制御する層。

**Frontier Exemplars**  
AWS KMS、Google Cloud KMS、Azure Key Vault、Vault Transit、NIST SP 800-57。公式docsはkey policy、rotation、key version、transit cryptoを公開する。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | data classification、key purpose、algorithm、key hierarchy、rotation trigger、compliance |
| Criteria | minimum key exposure、separation of duties、versioned rotation、auditable use、recoverability |
| Priorities | CMK/KEKとDEK分離、envelope encryption、alias/version、policy/grant、automatic/event-driven rotation |
| Prohibitions | raw key export、multi-purpose key、ownerless key、rotation without re-encryption plan、hard-coded key ID |
| Exceptions | asymmetric signing key、HSM/non-exportable key、legacy key under migration |
| Owners | Crypto Owner、Security、Data Platform |
| Cadence | key creation approval、rotation schedule/event、annual crypto review |

**Operating Model**  
KMS keyはpurpose-specificに作成し、aliasでアプリ参照を安定化する。encryptionではDEKをdata近くで使い、DEKをKEK/KMSでwrapする。rotationは「新規暗号化に使うprimary key version」と「過去データ復号に使うold version」を分ける。key deletionはretentionとdata recovery影響を確認する。

**Metrics**  
key age、rotation compliance、disabled key dependency、KMS access anomaly、decrypt failure、keys without owner、multi-purpose key count。

**Failure Modes**  
鍵削除で復号不能、policy過剰権限、rotation後の旧データ復号不能、raw key漏洩、KMS outage dependency。

**Anti-patterns**  
同一鍵を暗号化・署名・HMACに使い回す。key policyを`*` principalにする。rotationを実施してもre-encryption/consumer compatibilityを検証しない。

**Validation Queries**  
`site:docs.aws.amazon.com/kms customer managed keys rotation`, `site:cloud.google.com/kms key rotation key versions`, `site:csrc.nist.gov SP 800-57 key management`。

**Confidence & Unknowns**  
Confidence A。規制別のHSM/FIPS要件はjurisdiction別確認が必要。

---

### Layer 14.14: Certificate Management / PKI

**Definition**  
X.509証明書、issuer、ACME challenge、renewal、revocation、trust anchor、trust bundle配布を制御する層。

**Frontier Exemplars**  
ACME、cert-manager、Let’s Encrypt、CA/Browser Forum Baseline Requirements、trust-manager。公式標準とKubernetes-native運用docsが公開されている。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | hostname/SAN、issuer、validation method、certificate lifetime、trust domain、renewal window |
| Criteria | automated issuance、early renewal、revocation path、trust distribution、expiry prevention |
| Priorities | ACME automation、DNS01/HTTP01選択、renewBefore、issuer separation、expiry SLO、trust bundle management |
| Prohibitions | manual renewal dependence、private key reuse without policy、untracked cert、wildcard cert overuse、expired trust anchor |
| Exceptions | offline root CA、air-gapped issuance、emergency replacement cert |
| Owners | PKI/Security、Platform、Service Owner |
| Cadence | certificate issuance/renewal lifecycle、CA/trust anchor rotation plan |

**Operating Model**  
public TLS証明書はACMEで自動更新し、KubernetesではCertificate/Issuer/ClusterIssuerを用いる。private PKIはroot/intermediate/leafを分け、trust bundleの配布先を棚卸する。renewalは期限30日前警告に頼らず、lifetimeの1/3程度前から再発行可能な設計にする。

**Metrics**  
cert expiry under 30 days、renewal success、failed challenges、untracked cert、trust bundle drift、revocation propagation time。

**Failure Modes**  
期限切れ、ACME challenge失敗、CA compromise、trust anchor expiry、証明書秘密鍵漏洩、wildcard cert乱用。

**Anti-patterns**  
証明書台帳がなく、監視だけで期限切れを防ごうとする。private CAとpublic CAの責任分界がない。

**Validation Queries**  
`site:datatracker.ietf.org RFC 8555 ACME`, `site:cert-manager.io Certificate renewBefore`, `site:letsencrypt.org integration guide renewal`。

**Confidence & Unknowns**  
Confidence A。private PKI topologyは組織trust model依存。

---

### Layer 14.15: Transport Encryption / TLS / mTLS

**Definition**  
client-serverおよびservice-to-service通信で、TLS/mTLSによる機密性、完全性、peer authenticationを制御する層。

**Frontier Exemplars**  
IETF TLS 1.3、NIST SP 800-52、Istio mTLS、Linkerd automatic mTLS。標準とmesh docsが直接証拠になる。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | protocol、client base、service identity、certificate trust、cipher policy、legacy support |
| Criteria | modern protocol、verified identity、forward secrecy、automated cert lifecycle、compatibility risk |
| Priorities | TLS 1.2+/1.3、certificate validation、mTLS for service identity、cipher/profile baseline、downgrade prevention |
| Prohibitions | plaintext internal traffic by default、disabled certificate validation、obsolete protocol/cipher、shared private key |
| Exceptions | controlled legacy endpoint、temporary permissive mTLS during migration、non-sensitive isolated traffic |
| Owners | Security、Network、Platform |
| Cadence | TLS policy semiannual review、CA/cert lifecycle、critical vulnerability immediate |

**Operating Model**  
external TLSとinternal mTLSを別profileで管理する。service meshではpermissive/auditからstrictへ移行し、policy denyをobservabilityで確認する。HeartbleedのようなTLS library vulnerabilityを想定し、key/cert rotation runbookを持つ。

**Metrics**  
TLS version distribution、failed handshakes、mTLS coverage、certificate validation failures、weak cipher use、key/cert rotation MTTR。

**Failure Modes**  
証明書検証無効化、古いTLS、CA期限切れ、mTLS移行で通信断、library memory leakによるkey exposure。

**Anti-patterns**  
「internalだから平文でよい」とする。temporary permissive mTLSを恒久化する。TLS offload point以降の平文区間を台帳化しない。

**Validation Queries**  
`site:datatracker.ietf.org RFC 8446 TLS 1.3`, `site:csrc.nist.gov SP 800-52 TLS`, `CVE-2014-0160 cryptographic keys`。

**Confidence & Unknowns**  
Confidence A。legacy client互換性は実トラフィック計測が必要。

---

### Layer 14.16: Data-at-rest / Application Encryption

**Definition**  
保存データ、Kubernetes resource、application payload、field-level sensitive dataを、storage/KMS/applicationのどの層で暗号化するかを決める層。

**Frontier Exemplars**  
Kubernetes encryption at rest/KMS provider、Vault Transit、OWASP Cryptographic Storage、cloud KMS envelope encryption。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | data class、threat model、storage layer、query need、key owner、rotation/re-encryption need |
| Criteria | data exposure reduction、key separation、operability、recoverability、least privilege decrypt |
| Priorities | envelope encryption、field-level encryption for high-risk data、resource encryption for Secrets、KMS/HSM key control |
| Prohibitions | reversible encryption for passwords、same key across tenants/classes、application logs with plaintext sensitive data |
| Exceptions | low-risk data under storage encryption only、search/index constraints、legacy migration window |
| Owners | Data Security、App Owner、KMS Owner |
| Cadence | data classification change、key rotation、schema migration |

**Operating Model**  
保存データ暗号化は「ディスク暗号化」だけで完結しない。高リスクデータはapplication-levelまたはfield-level encryptionで保護し、DEK/KEK構造を使う。Kubernetes Secrets等のresourceはetcd/API server側のencryption at restとKMS providerで守る。

**Metrics**  
encrypted field coverage、decrypt access count、KMS latency、re-encryption backlog、plaintext finding、data class without encryption policy。

**Failure Modes**  
keyとciphertext同居、loggingで平文露出、passwordを可逆暗号化、rotation後の復号不能、search機能破壊。

**Anti-patterns**  
「クラウドのdisk encryptionがあるからapplication encryption不要」と一律判断する。パスワードを暗号化保存する。

**Validation Queries**  
`site:kubernetes.io encrypt data at rest secrets`, `site:developer.hashicorp.com/vault transit encryption as a service`, `site:cheatsheetseries.owasp.org Cryptographic Storage password`。

**Confidence & Unknowns**  
Confidence A。具体的field-level encryption範囲はdata classificationが必要。

---

### Layer 14.17: Hashing / Password Hashing / Integrity Digest

**Definition**  
message digest、integrity check、HMAC、password hashing/KDFを区別し、それぞれのアルゴリズム、salt/pepper、parameter、upgrade policyを制御する層。

**Frontier Exemplars**  
NIST FIPS 180-4、OWASP Password Storage、Vault Transit hash/HMAC、Argon2id/bcrypt/PBKDF2 implementations。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | use case: digest/HMAC/password、attacker model、performance budget、compliance、upgrade path |
| Criteria | correct primitive choice、work factor resilience、unique salt、parameter upgrade、verification safety |
| Priorities | passwordにはArgon2id/bcrypt/PBKDF2、unique salt、optional pepper、constant-time compare、hash parameter storage |
| Prohibitions | SHA-256だけでpassword保存、salt reuse、unsalted hash、home-grown hash、password encryption |
| Exceptions | FIPS-only environment with PBKDF2、legacy hash migration with rehash-on-login |
| Owners | App Security、Identity Platform、Crypto Governance |
| Cadence | annual parameter review、hardware cost shift review、breach immediate reset/rehash |

**Operating Model**  
password hashing policyは通常digest policyから分離する。hash recordにはalgorithm、version、salt、work factorを保存し、login時に必要ならrehashする。HMAC keyはKMS/secret storeで管理し、一般のmessage digestとは区別する。

**Metrics**  
legacy hash count、rehash coverage、password verification latency、unsalted hash finding、KDF parameter age。

**Failure Modes**  
高速hashでpassword保存、saltなし、work factor不足、pepper漏洩、hash comparison timing leak。

**Anti-patterns**  
「SHA-256は暗号学的ハッシュだからpasswordにも十分」と判断する。自作KDFを使う。

**Validation Queries**  
`site:cheatsheetseries.owasp.org Password Storage Argon2id bcrypt PBKDF2`, `site:csrc.nist.gov FIPS 180-4 Secure Hash Standard`, `password hashing fast hash anti pattern`。

**Confidence & Unknowns**  
Confidence A。FIPS制約下の具体的KDF parameterは環境依存。

---

### Layer 14.18: Digital Signature / Artifact Signing

**Definition**  
文書、token、artifact、container image、software releaseの完全性、出所、署名者、検証条件、失効/透明性を制御する層。

**Frontier Exemplars**  
NIST FIPS 186-5、IETF JWS、Sigstore Cosign、Vault Transit sign/verify。標準とartifact signing toolingが公開されている。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | artifact type、signer identity、verification environment、key/cert lifecycle、non-repudiation need |
| Criteria | verifiable identity、tamper evidence、key protection、automated verification gate、auditability |
| Priorities | signature algorithm policy、key/cert provenance、CI signing、deployment verification、attestation storage |
| Prohibitions | unsigned production artifact、verification bypass、shared signing key、signature without identity/audit |
| Exceptions | emergency unsigned deploy with break-glass approval、legacy artifact under migration |
| Owners | Supply Chain Security、Release Engineering、Crypto Owner |
| Cadence | releaseごと、key/cert rotation、algorithm deprecation review |

**Operating Model**  
artifact signingはCI/CD pipelineに組み込み、signing identityをworkload identityまたはcode signing certに紐づける。deployment側は署名検証をenforcement gate化し、allowlistではなくpolicyで許可する。JWS等のmessage-level signatureでは、alg header、key ID、audience、expiry、replay対策を設計する。

**Metrics**  
signed artifact ratio、verification failure、unsigned deploy attempt、signing key age、attestation coverage、bypass approvals。

**Failure Modes**  
署名鍵漏洩、CI identity乗っ取り、verification disabled、alg confusion、expired signing certificate、attestation未保存。

**Anti-patterns**  
署名は作るがdeploy時に検証しない。JWSの`alg`を信頼しすぎる。release manager個人の長期秘密鍵で全artifactを署名する。

**Validation Queries**  
`site:csrc.nist.gov FIPS 186-5 digital signature`, `site:datatracker.ietf.org RFC 7515 JWS`, `site:docs.sigstore.dev cosign sign verify container`。

**Confidence & Unknowns**  
Confidence A。組織のsupply-chain policyとSLSA水準は追加指定が必要。

---

### Layer 14.19: Entropy / Randomness / Crypto Runtime

**Definition**  
暗号用途の乱数、entropy source、DRBG、crypto module、self-test、runtime/library選定を制御する層。

**Frontier Exemplars**  
NIST SP 800-90A/B、RFC 4086、FIPS 140-3、platform crypto libraries。標準がentropy/DRBG/module assuranceを直接定義する。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | cryptographic use case、runtime environment、entropy availability、compliance、module boundary |
| Criteria | sufficient entropy、validated DRBG、library provenance、self-test、failure detection |
| Priorities | OS CSPRNG、approved DRBG、entropy health test、FIPS module where required、library version governance |
| Prohibitions | `Math.random()`等の非暗号乱数、seed reuse、predictable nonce、unvalidated crypto library in regulated scope |
| Exceptions | simulation/non-security randomness、test determinism with non-production guard |
| Owners | Runtime Platform、Security、Crypto Governance |
| Cadence | runtime upgradeごと、FIPS validation change、critical crypto library CVE |

**Operating Model**  
暗号用乱数は標準library/OS CSPRNGから取得する。nonce、key generation、salt、session tokenは用途ごとに必要entropyを定義する。FIPS対象システムはmodule boundaryとvalidated versionを台帳化する。entropy failureはsecurity incidentとして扱う。

**Metrics**  
crypto library inventory coverage、FIPS module coverage、weak RNG finding、nonce collision、crypto library CVE MTTR、module self-test failure。

**Failure Modes**  
predictable token、nonce reuse、weak seed、library downgrade、FIPS module version mismatch、entropy starvation。

**Anti-patterns**  
乱数生成をアプリ独自実装にする。test用seeded RNGをproductionに残す。暗号libraryのversionをSBOMに含めない。

**Validation Queries**  
`site:csrc.nist.gov SP 800-90A DRBG`, `site:csrc.nist.gov SP 800-90B entropy source`, `site:datatracker.ietf.org RFC 4086 randomness requirements`, `site:csrc.nist.gov FIPS 140-3 cryptographic modules`。

**Confidence & Unknowns**  
Confidence A。FIPS対象範囲とmodule boundaryはシステム分類依存。

---

### Layer 14.20: Crypto Governance / Crypto Agility / PQC

**Definition**  
組織内の暗号アルゴリズム、鍵長、証明書、crypto module、library、使用箇所を棚卸し、非推奨、例外、移行、PQC readinessを制御する層。

**Frontier Exemplars**  
NIST SP 800-57、FIPS 140-3、NIST Post-Quantum Cryptography project、NIST NCCoE PQC migration、CISA Quantum Readiness。

**Decision Model**

| Field | Spec |
|---|---|
| Inputs | crypto inventory、algorithm/key length、data lifetime、threat horizon、regulatory requirement、vendor readiness |
| Criteria | algorithm strength、migration feasibility、data exposure duration、interoperability、compliance |
| Priorities | crypto inventory、algorithm allow/deny list、exception expiry、library/module lifecycle、PQC migration plan |
| Prohibitions | unknown crypto usage、permanent exception、hard-coded algorithm、no owner for deprecated primitive |
| Exceptions | legacy interop with compensating controls、short-lived low-risk data、vendor transition delay |
| Owners | CISO、Crypto Governance Board、Enterprise Architecture、Platform Security |
| Cadence | semiannual crypto review、new NIST/IETF guidance、PQC milestone、critical crypto break |

**Operating Model**  
crypto inventoryをSBOM/CMDB/IaC/code scanから作り、algorithm、key length、library、module、certificate、data class、ownerを記録する。NIST/IETF/OWASP等のbaselineに照らしてallow/deny/monitorを分類し、非推奨primitiveにはmigration deadlineとrisk acceptanceを付ける。PQCではまずpublic-key cryptographyの使用箇所と長期機密データを特定する。

**Metrics**  
crypto inventory coverage、deprecated algorithm count、exception age、PQC readiness coverage、vendor dependency readiness、FIPS module compliance、migration backlog。

**Failure Modes**  
暗号使用箇所の未把握、PQC移行対象の見落とし、ベンダー依存、algorithm agilityなし、例外の恒久化、互換性破壊。

**Anti-patterns**  
「PQC製品を買えば完了」と考える。暗号棚卸なしにアルゴリズム置換を始める。hard-coded crypto algorithmをアプリに散在させる。

**Validation Queries**  
`site:csrc.nist.gov post quantum cryptography FIPS 203 204 205`, `site:nccoe.nist.gov crypto agility post-quantum migration`, `site:cisa.gov quantum readiness cryptographic inventory`。

**Confidence & Unknowns**  
Confidence A/B。PQC標準と各ベンダー実装は今後も変わるため、継続更新が必要。

---

## 6. Pattern Library

| Pattern ID | Pattern | Layer Scope | Description | Preconditions | Tradeoffs | Confidence |
|---|---|---|---|---|---|---|
| P-001 | Edge Contract Separation | 14.03–14.08 | reverse proxy/API gateway/LB/WAF/CDN/Gateway APIを別artifactに分離し、変更責任を明確化する | IaC/GitOps、owner registry | 初期設計コスト増 | A |
| P-002 | Health-gated Routing | 14.02,14.05,14.10 | health/readiness情報でLB/discoveryのrouting eligibilityを決める | 正しいhealth endpoint | readiness設計が難しい | A |
| P-003 | Count-before-block WAF | 14.06 | WAF ruleをcount/auditで検証してからblock化する | traffic sampling/logging | 即時防御力は遅れる | A |
| P-004 | Explicit Cache Key | 14.07 | CDN cache keyとTTLをcontent classごとに定義する | content classification | 運用複雑性 | A |
| P-005 | Gateway Role Boundary | 14.08 | GatewayClass/Gateway/Routeのownerを分ける | platform team成熟 | controller差異 | A |
| P-006 | Permissive-to-strict mTLS | 14.09,14.15 | service mesh mTLSを観測・棚卸後にstrict化する | mesh telemetry | 移行期間中の混在 | A |
| P-007 | Secret Lease Lifecycle | 14.12 | secretにTTL/lease/revocation/auditを付ける | central secret store | 一部legacyと不整合 | A |
| P-008 | Envelope Encryption | 14.13,14.16 | DEK/KEKを分離し、KMSでkey exposureを減らす | KMS/HSM | KMS latency/dependency | A |
| P-009 | Automated Certificate Renewal | 14.14 | ACME/cert-managerで証明書発行・更新を自動化する | DNS/HTTP challenge管理 | CA/issuer依存 | A |
| P-010 | Password Hashing Distinction | 14.17 | password hashingを一般digestから分離する | identity platform policy | latency増 | A |
| P-011 | Verification Gate | 14.18 | signed artifactだけをdeploy可能にする | CI/CD identity、signing tooling | emergency bypass設計 | A |
| P-012 | Crypto Inventory First | 14.20 | 暗号移行前に使用箇所・鍵・証明書・libraryを棚卸する | SBOM/CMDB/code scan | 初期棚卸コスト | B |

---

## 7. Candidate Scoring

| Candidate / Standard | Performance | Adoption | Artifact Richness | Peer Validation | Recency | Transferability | Failure Evidence | Score / 100 | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Kubernetes Gateway API | 4 | 4 | 5 | 4 | 5 | 5 | 3 | 87 | role-oriented routing APIとして移植性が高い |
| Envoy / Envoy Gateway | 5 | 5 | 5 | 4 | 5 | 4 | 3 | 89 | xDS/API gateway/service mesh基盤で証拠密度が高い |
| NGINX / HAProxy | 5 | 5 | 5 | 4 | 4 | 4 | 3 | 86 | reverse proxy/LBの運用証拠が豊富 |
| Istio | 5 | 5 | 5 | 4 | 5 | 4 | 3 | 88 | mTLS/authz/traffic policyのdocsが厚い |
| Linkerd | 4 | 4 | 5 | 4 | 5 | 4 | 3 | 82 | automatic mTLSとcert lifecycleが明確 |
| OWASP CRS / OWASP Cheat Sheets | 4 | 5 | 4 | 5 | 4 | 5 | 4 | 87 | WAF/secret/password/storageの標準的実務知識 |
| Cloudflare / Fastly CDN incidents | 5 | 5 | 4 | 4 | 4 | 4 | 5 | 88 | failure evidenceが非常に強い |
| NIST SP/FIPS family | 5 | 5 | 5 | 5 | 5 | 4 | 3 | 93 | 暗号・鍵・TLS・module assuranceの規範性が高い |
| IETF RFC 8446/8555/7515 | 5 | 5 | 5 | 5 | 4 | 5 | 3 | 92 | protocol標準として直接証拠 |
| Vault / KMS providers | 5 | 5 | 5 | 4 | 5 | 4 | 3 | 88 | secret/key/encryption lifecycleの実装証拠が多い |
| Sigstore Cosign | 4 | 4 | 5 | 4 | 5 | 5 | 3 | 83 | artifact signingの実装patternが明確 |
| NIST/CISA PQC readiness | 4 | 4 | 4 | 5 | 5 | 5 | 2 | 83 | 移行modelとして重要、実装成熟は継続観測が必要 |

---

## 8. Maturity Model

| Level | Name | Criteria |
|---:|---|---|
| 0 | 未整備 | web/proxy/WAF/CDN/TLS/secret/key/certが個別手作業。台帳なし。secretがコードや設定に混入。 |
| 1 | 個人依存 | 一部標準設定はあるがowner、review、rollback、rotationが個人知識に依存。 |
| 2 | 文書化 | baseline config、runbook、certificate/secret/key台帳、basic health check、manual reviewがある。 |
| 3 | 標準化 | Gateway/API/LB/WAF/CDN/mesh/config/secret/key/certがIaC化され、policy lintとapprovalがある。 |
| 4 | 自動化・計測 | canary/rollback、mTLS、cert renewal、secret rotation、KMS rotation、cache/WAF metrics、crypto inventoryが自動化。 |
| 5 | 自律改善・業界先端 | incident learning、adaptive rate/WAF、continuous crypto agility、PQC readiness、supply-chain signing enforcement、global blast-radius controlが成熟。 |

---

## 9. Clone Implementation Guide

### Phase 1: Baseline Inventory（0–30日）

1. public/internal entrypointsを列挙する: web server、reverse proxy、API gateway、LB、WAF、CDN、Gateway/Ingress。
2. TLS/certificate/key/secret/config inventoryを作る: owner、expiry、rotation、consumer、environment。
3. crypto inventoryの最小版を作る: TLS versions、certs、KMS keys、hash/KDF、signature、crypto libraries。
4. incidents/failure riskを棚卸する: expired cert、WAF false positive、cache misconfiguration、secret leak、weak TLS。

### Phase 2: Control Artifacts（30–60日）

1. `edge_baseline.yaml` を作る: TLS、headers、timeouts、body limits、log標準。
2. `gateway_contract.yaml` を作る: route、auth、quota、consumer identity。
3. `waf_policy.yaml` と `cache_policy.yaml` を作る: count-before-block、cache key、TTL、purge。
4. `secret_lifecycle.md` と `kms_key_registry.csv` を作る。
5. cert-manager/ACMEまたは同等の自動renewalを導入する。

### Phase 3: Progressive Enforcement（60–120日）

1. Gateway API/Ingress責任分界を導入する。
2. service meshのmTLSをpermissive/auditからstrictへ段階移行する。
3. WAF/CDN/global edge変更にcanaryとautomatic rollbackを入れる。
4. signed artifact verificationをproduction deploy gateにする。
5. password hashing/KDF parameter reviewを実施し、legacy hashをrehash-on-loginで移行する。

### Phase 4: Crypto Agility（120日以降）

1. deprecated algorithm/key length/libraryをcrypto inventoryから抽出する。
2. exception registerを作り、owner、expiry、migration planを必須化する。
3. PQC readinessとして、public-key cryptography使用箇所、long-lived confidential data、vendor dependencyを特定する。
4. NIST/IETF/CA/B/OWASP更新をwatchし、semiannual crypto reviewを運用する。

---

## 10. Failure Modes and Controls

| Failure Mode | Affected Layers | Detection | Preventive Control | Recovery Control |
|---|---:|---|---|---|
| Open proxy exposure | 14.03 | external scan、unexpected outbound logs | explicit upstream allowlist、deny arbitrary destination | disable listener、rotate abused credentials |
| WAF rule CPU explosion | 14.06 | edge CPU/latency spike、global 5xx | count/canary rollout、regex performance test | rollback rule、disable managed group |
| Cache poisoning / private data cache | 14.07 | cache anomaly、privacy report | explicit cache key、no-store for personalized content | purge、invalidate keys、notify affected users |
| LB routes to unhealthy target | 14.05 | probe failure vs traffic logs | readiness-aware health check | drain/remove target、fix probe |
| mTLS strict migration outage | 14.09,14.15 | deny spike、connection failure | permissive/audit stage、service communication map | revert to permissive、add policy |
| Secret leakage | 14.12 | secret scanning、access anomaly | no secret in repo/image/log、central store | revoke/rotate、incident response |
| Key deletion / rotation breakage | 14.13,14.16 | decrypt failures | deletion waiting period、versioned keys、compatibility test | restore if possible、rollback primary version |
| Certificate expiry | 14.14,14.15 | expiry monitor、renew failure alert | ACME/cert-manager auto-renewal | emergency cert issuance、route fallback |
| Weak password hashes | 14.17 | identity audit | Argon2id/bcrypt/PBKDF2 policy | rehash-on-login、forced reset |
| Unsigned artifact deploy | 14.18 | deployment admission check | signature verification gate | rollback、sign/rebuild artifact |
| Weak RNG / nonce reuse | 14.19 | collision/anomaly、crypto review | OS CSPRNG、DRBG、library governance | rotate keys/tokens、patch runtime |
| PQC/algorithm surprise | 14.20 | crypto inventory gap | inventory, allow/deny list, agility design | migration program、exception expiry |

---

## 11. QA Report

| QA Check | Status | Evidence |
|---|---|---|
| Coverage | PASS | 20 layers all have T0/T2/T3/T5 sources. |
| Critical Claim | PASS | Major claims C-001–C-020 have at least two source families where feasible. |
| Recency | PASS with watchlist | Current docs used. PQC/Gateway API/TLS guidance should be monitored for 2026+ changes. |
| Exceptions | PASS | Each layer contains exception conditions. |
| Failure | PASS | Fastly, Cloudflare, Heartbleed, Log4Shell and generic failure modes included. |
| Provenance | PASS | Source IDs S-001–S-070 mapped to claims/layers. |
| Registry Integrity | PASS | Layer IDs 14.01-14.20 unique. |
| Output Integrity | PASS | Clone Spec fields present for each layer in condensed format. |

### Validation Query Bundle

```text
"API Gateway" (throttling OR quota OR rate limit) official docs
"Gateway API" "HTTPRoute" "cross-namespace" official docs
"Envoy" "xDS" "service discovery" official docs
"WAF" (incident OR outage OR rollback OR false positive)
"CDN" (cache poisoning OR purge OR outage OR configuration change)
"service mesh" (mTLS OR AuthorizationPolicy OR certificate rotation)
"Kubernetes" ConfigMap Secret KMS encryption at rest
"Vault" dynamic secrets lease revocation transit
"ACME" certificate renewal revocation RFC 8555
"TLS 1.3" RFC 8446 NIST SP 800-52
"password storage" Argon2id bcrypt PBKDF2 OWASP
"digital signature" FIPS 186-5 JWS Sigstore cosign
"entropy source" NIST SP 800-90B DRBG
"post quantum cryptography" NIST CISA crypto inventory migration
"FIPS 140-3" cryptographic module validation
```

---

## 12. Unknowns and Follow-up Research

1. 正式なlayer registryでの14の名称。ここではユーザー提示サブテーマから20レイヤーへ分解した。
2. 対象組織のtraffic pattern、latency budget、regulated data class、compliance jurisdiction。
3. 現行cloud/provider構成。AWS/GCP/Azure/Cloudflare/Fastly/Kubernetes/meshの有無でimplementation guideは変わる。
4. API gatewayとservice meshの責任境界。重複するauth/rate/observabilityをどちらに置くかは組織設計が必要。
5. Private PKI topology、root/intermediate CAの保管、trust bundle配布範囲。
6. FIPS対象範囲とcrypto module validation要件。
7. PQC移行の優先順位。長期機密データとpublic-key cryptography使用箇所の棚卸が必要。

---

## Appendix A: Condensed Registry Rows

```csv
layer_id,layer_name_ja,cluster,decision_object,owner_roles,default_metrics
14.01,Web Server,サービスプラットフォーム・エッジ・暗号基盤,HTTP(S)終端と基本公開制御,"Platform;SRE;Security","TLS success;headers compliance;cert expiry"
14.02,Application Server,サービスプラットフォーム・エッジ・暗号基盤,アプリ実行基盤とhealth/runtime制御,"App Platform;Backend;Security","readiness;thread saturation;CVE MTTR"
14.03,Reverse Proxy,サービスプラットフォーム・エッジ・暗号基盤,upstream routing/header/timeout制御,"Edge Platform;SRE","upstream 5xx;timeout;reload failure"
14.04,API Gateway,サービスプラットフォーム・エッジ・暗号基盤,API公開契約とauth/quota制御,"API Platform;Security;Product","rate-limit exceed;auth failure;schema failure"
14.05,Load Balancer,サービスプラットフォーム・エッジ・暗号基盤,traffic分配とhealth/failover制御,"SRE;Network;Platform","healthy targets;probe failure;5xx"
14.06,WAF,サービスプラットフォーム・エッジ・暗号基盤,HTTP request inspectionとrule governance,"Security;Edge;App Owner","blocked requests;false positives;WAF latency"
14.07,CDN / Edge Cache,サービスプラットフォーム・エッジ・暗号基盤,edge cache key/TTL/purge制御,"Edge;Performance;App Owner","cache hit;purge latency;origin offload"
14.08,Edge Routing / Gateway API / Ingress,サービスプラットフォーム・エッジ・暗号基盤,routing APIと責任分界,"Cluster Platform;Network;Service Owner","route rejection;propagation latency;policy violation"
14.09,Service Mesh,サービスプラットフォーム・エッジ・暗号基盤,mTLS/authz/traffic policy制御,"Platform Security;Service Owner;SRE","mTLS coverage;policy deny;mesh latency"
14.10,Service Discovery,サービスプラットフォーム・エッジ・暗号基盤,service nameとendpoint解決,"Platform;SRE;Service Owner","lookup latency;stale endpoint;NXDOMAIN"
14.11,Config Management,サービスプラットフォーム・エッジ・暗号基盤,非機密設定とfeature flag制御,"App Owner;Platform;Release","config drift;flag age;invalid deploy"
14.12,Secret Management,サービスプラットフォーム・エッジ・暗号基盤,秘密情報の保管/配布/rotation,"Security Platform;App Owner;IAM","secret age;rotation success;leak MTTR"
14.13,Key Management / KMS,サービスプラットフォーム・エッジ・暗号基盤,暗号鍵の生成/利用/rotation,"Crypto Owner;Security;Data Platform","key age;rotation compliance;decrypt failures"
14.14,Certificate Management / PKI,サービスプラットフォーム・エッジ・暗号基盤,証明書発行/更新/失効/trust管理,"PKI;Security;Platform","expiry;renewal success;trust drift"
14.15,Transport Encryption / TLS / mTLS,サービスプラットフォーム・エッジ・暗号基盤,通信暗号とpeer identity,"Security;Network;Platform","TLS version;handshake failure;mTLS coverage"
14.16,Data-at-rest / Application Encryption,サービスプラットフォーム・エッジ・暗号基盤,保存データ暗号化とDEK/KEK設計,"Data Security;App Owner;KMS Owner","encrypted coverage;KMS latency;plaintext findings"
14.17,Hashing / Password Hashing / Integrity Digest,サービスプラットフォーム・エッジ・暗号基盤,digest/KDF/HMAC選定,"App Security;Identity;Crypto Governance","legacy hash;rehash coverage;verification latency"
14.18,Digital Signature / Artifact Signing,サービスプラットフォーム・エッジ・暗号基盤,署名/検証/artifact integrity,"Supply Chain Security;Release;Crypto Owner","signed ratio;verification failure;bypass approvals"
14.19,Entropy / Randomness / Crypto Runtime,サービスプラットフォーム・エッジ・暗号基盤,entropy/DRBG/crypto module保証,"Runtime Platform;Security;Crypto Governance","weak RNG findings;library CVE MTTR;FIPS coverage"
14.20,Crypto Governance / Crypto Agility / PQC,サービスプラットフォーム・エッジ・暗号基盤,暗号棚卸/非推奨/PQC移行,"CISO;Crypto Board;Architecture","inventory coverage;deprecated algorithm;PQC readiness"
```
