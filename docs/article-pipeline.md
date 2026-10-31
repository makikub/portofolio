# 実践ノートの収集・レビュー運用

個人開発と副業でのAIエージェント活用から、他の人が学べる実践知を記事にする。成果の羅列ではなく、課題、AIの役割、人の判断、試した手順、確認できた成果、失敗、再現条件、限界、持ち帰れる学びを扱う。既存のプロジェクト事例は維持し、継続的な実践ノートを `/notes/` に分ける。

## 公開接続の確認が必要

ユーザー指定サイトは https://mklabos.dev 。既存スキルとこのリポジトリのREADME/CLAUDE.mdは `makikub/portofolio`、Cloudflare Pages `masaki-portfolio`、`main` → `npm run build` → `dist` を示す。ただし、2026-10-31の読み取りで公開サイトの見出し・構成とGitHub mainの内容に相違があった。GitHubの最新pushは2026-07-11。Cloudflareの実設定・現在配信しているソースは未確認。

**この基盤PRをマージする前に、現在の公開サイトのソースとGit連携先を特定し、必要なら現在のソースへこの変更を移植する。古いmainをそのまま公開しない。** canonical設定は今回変更していない。既存のPages preview設定も未確認で、Draft PRの段階でプレビューが公開される可能性がある。

## データの境界

1. `collect_repos`: 生の活動候補を収集してよい公開個人リポジトリのallowlist。初期値は空。収集は直近7日、各repo100件未満のコミットのIDと公開URLのみ。差分やコミット本文、会話履歴、Slack/DM、顧客資料、秘密ファイルは読まない。100件に達した場合は取りこぼしを防ぐため停止する。高頻度repoは期間分割・ページングを追加するまで対象にしない。
2. `seed_dir`: 本人または作業中のエージェントが記事用に抽象化したJSONを置くローカル領域。生の候補と分離する。副業の経験も、顧客情報や非公開URLを除いた学びだけを保存する。
3. `public_release: true`: 本人が公開可能とした記事種だけ。生の候補にこのフラグを自動設定しない。許可不明ならfalseのままにし、公開用seed_dirへ入れない。
4. `public_evidence_repos`: 公開記事にリンクしてよい根拠repo。初期値はこのポートフォリオのみ。collectの許可とは別。新しい根拠repoはローカルconfigと追跡対象の `config.example.json` の両方をレビューして追加する（後者をbuild検査にも使用）。
5. 出力は構造化JSONのみ。HTMLやMarkdownを実行・展開せず、Astroのエスケープで表示する。本文からの任意コマンド実行、LLM APIへの送信は行わない。

## 初回設定

Python 3標準ライブラリ、git、認証済みghを使用。追加パッケージはCLIに不要。Mac/Linux向け（flock使用）。サイトの型・build検証は既存Astro依存が必要。

リポジトリrootを作業ディレクトリとして:

```sh
mkdir -p .article-local/seeds
cp tools/article_pipeline/config.example.json .article-local/config.json
python3 tools/article_pipeline/pipeline.py collect --config .article-local/config.json
python3 tools/article_pipeline/pipeline.py dry-run --config .article-local/config.json
```

`denied_terms` には会社名・顧客名・内部プロジェクト名をローカルconfigだけで指定する。実名の除外リストを公開Gitへコミットしない。

config、候補、preview、実行履歴はgitignoreされた `.article-local/` に置く。別の場所を使うなら絶対パスをconfigへ設定する。Cursor/Codex/Claudeは共通の `docs/article-seed-prompt.md` とJSON形式を使用する。設定パスはCLIの引数なので特定エージェントやサービスに依存しない。

`collect` は候補収集のみ。学びの選別と文章化はローカルで作業するエージェントが共通プロンプトに従って行う。無人でコミットを解釈して公開許可を付ける処理はない。本人が記事用に公開許可したseedがなければ、その回はスキップする。

## 記事種の形式

`tools/article_pipeline/seed.template.json` をコピーして全項目を埋める。これは未公開の空テンプレートであり、そのままでは検査に通らない。

- `id`: 安定した小文字英数字とハイフン。記事URLとPRブランチにも使う。内容変更時も同じIDを維持。
- `date`: YYYY-MM-DD。
- `title` / `summary`: 公開してよい日本語。8文字以上。
- `evidence`: 公開GitHubコミット（40桁SHA）、PR、IssueへのURLと説明。
- 各sectionは `{text, kind, evidence}` の配列。
- `kind`: `observed`（確認した事実）、`inference`（考察）、`planned`（計画）。事実には根拠URLが必須。成果sectionは事実のみ。失敗が未観測ならその旨を考察として明記し、失敗を捏造しない。
- 公開seedの全フィールドは外部に出る。秘密値、顧客情報、ローカルパス、非公開URLを入れない。

## 検査とDraft PR

```sh
python3 -m unittest discover -s tests -v
python3 tools/article_pipeline/pipeline.py dry-run --config .article-local/config.json
# 公開ソースの同期・基盤PRの本人レビューとマージが完了してから:
python3 tools/article_pipeline/pipeline.py publish --config .article-local/config.json
```

`dry-run` はネットワークなしで形式・機密パターン・根拠対応を検査し、preview.jsonを作る。URLの実在・公開状態は未検証と表示する。

`publish` は本人アカウント、対象repo、main、根拠repoのpublic状態と根拠URLの実在を読み戻す。別の一時cloneにJSONを1記事だけ追加し、`articles/<id>` にpushしてDraft PRを作る。作業中checkoutは変更しない。基盤routeがmainになければ停止する。CLIはmerge、approve、deployを実装しない。

公開リポジトリではDraftでも差分とPR本文は公開される。機密パターン検査は完全な情報漏洩防止ではない。URLの存在は主張の正しさを証明しない。人または作業エージェントは根拠と本文を照合し、本人が公開可能とした内容のみseedにする。本人はPRで正確性・公開可否・読者への価値を最終確認する。

## 冪等性と失敗

- 記事IDと根拠URL/commitの重複を排除。同じ根拠を使う続編は初期実装では保守的にスキップ。
- mainの記事、全状態の過去PRのブランチ、PR本文の根拠hashを確認。却下・閉鎖したPRも自動再投稿しない。
- 同じstate_dirを使うMac上で排他ロック。複数ホストで同時実行しない。
- push後にPR作成だけ失敗した場合は既存ブランチの記事内容・変更ファイルが完全一致する場合のみPR作成を再試行。既存remoteへのforce pushはしない。
- PR作成成功後に応答が失われても、次回PR一覧から回復。別の記事種があれば次へ進む。
- `.article-local/state/runs.jsonl` に成功・skip・失敗をJSONLで記録。外部コマンドのstderrや記事本文をログに残さない。失敗時はexit 1。
- 長期間公開根拠がprivate化・削除された場合はpublishを停止する。dry-run/buildのオフライン検査だけでは検出しない。

## 定期実行（未登録）

仮の頻度は週1回。親スレッドが頻度・時間帯・実行環境を調整して1つだけ登録する。このPRはcron/launchd/Actions scheduleを登録しない。

将来のジョブはこのrepoをcwdにし、`collect` → ローカルで公開許可済みの種から学びを選別 → `dry-run` → `publish` の順に実行する。価値ある記事種がなければ終了する。生の活動候補しかない場合も終了する。各コマンドのexit codeとruns.jsonlで失敗を通知する。1回に1本まで。自動マージ禁止。

公開ソースの一致とCloudflareのmain連携が確認された後、本人による記事PRのmainへのマージを公開の唯一の入口にする。ブランチ保護と本人レビュー必須化は管理設定を確認してから行う（今回未変更）。直接mainへpushできる既存権限までこのCLIでは禁止できない。
