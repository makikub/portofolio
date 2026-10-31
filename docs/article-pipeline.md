# 実践ノートの収集・レビュー運用

個人開発と副業でのAIエージェント活用から、他の人が学べる実践知を記事にする。成果の羅列ではなく、課題、AIの役割、人の判断、試した手順、確認できた成果、失敗、再現条件、限界、持ち帰れる学びを扱う。既存のプロジェクト事例は維持し、継続的な実践ノートを `/notes/` に分ける。

## 公開ソースの同期確認

ユーザー指定サイトは https://mklabos.dev 。2026-10-31に本人がGitHub mainを更新し、`639524e` の独自ドメイン・新しいトップ構成をこのPRへmergeした。公開サイトとトップ見出し、canonical、OG画像URLが一致し、favicon・OG画像・既存sitemapはmainとバイト単位で一致した。以前の「古いmainへ戻る」不一致は解消した。

README/CLAUDE.mdはCloudflare Pages `masaki-portfolio`、`main` → `npm run build` → `dist` のGit連携を示す。Cloudflare管理画面の実設定と、このPRのマージ後デプロイは未実行・未確認。ローカルの型・build・PC/モバイル検証は成功した（[検証記録](article-pipeline-verification.md)）。PRはDraftのまま本人レビューを待つ。Pages previewがPR段階で公開される可能性も引き続き考慮する。

既存の発信コンポーネントへノート一覧の導線を追加し、sitemapは既存6ルートとノート一覧・記事JSONから生成する。トップの既存コンテンツ・デザイン・公開ケースは置換しない。

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
# サイトbuild検証・基盤PRの本人レビューとマージが完了してから:
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

## 複数端末・複数ツールの選択取り込み

全会話の自動同期や横断読取は実装しない。各端末で、作業をしたツール自身に共通プロンプトを使って振り返りを保存させる。Mac mini / MacBook Pro間の転送手段は未接続。SSH・クラウド履歴APIへの接続は行わない。本人が選んだJSONだけを、承認された方法でMac miniのローカルintakeへ渡す。

各振り返りは次のprivate envelopeにする。`seed` は上の共通記事種。`private_refs` は選択した成果物、検証メモ、会話exportなどをあとから本人が確認する参照で、CLIが読み取りに行くことはない。

```json
{
  "event_id": "motion-experiment-01",
  "device_id": "mac-mini",
  "source_tool": "codex",
  "project_id": "personal-video",
  "private_refs": ["selected-local-artifact-reference"],
  "seed": {"public_release": false}
}
```

`device_id` は本人が決めた別名（例: `mac-mini` / `macbook-pro`）。ホスト名やシリアル番号を自動取得しない。`source_tool` は `codex` / `claude-code` / `grokbot` / `manual`。`project_id` と `event_id` は同じ実験について端末間で共有する。各ツールは必要な作業記録だけから振り返りを作成し、非公開の会話本文や秘密値をenvelopeにも貼り付けない。

```sh
python3 tools/article_pipeline/intake.py --file .article-local/reflection.json --config .article-local/config.json
```

取り込みはローカルのみ。端末・ツール・project・private refsはstate/intakeへ保存し、公開JSONへ含めない。公開許可がfalseならprivate保存のみ。trueなら既存の公開検査を通ったseedだけseed_dirへ出す。同一project/eventを両端末から入れても1つに統合し、出典を追加する。本文が異なる衝突は上書きせず停止する。内容を見直したrevisionは新しいevent_idを付けるが、既存seed IDの異なる内容も自動上書きしないため、元のseedを本人が整理してから取り込む。異なるevent_idでも公開段階の同じ記事ID・根拠commit検査で重複を抑止する。

GrokbotがこのJSONを出せるか、履歴のexport方法があるかはサービス側の確認が必要。ローカル連携フォルダがあるだけでは会話履歴が読めることを意味しない。

## 選択した作業メモの自動収集

`collect_local.py` はローカルconfigの `local_sources` に指定した**個別ファイルだけ**を読み、私的な候補と下書きの骨子を生成する。再帰的な会話・ホームフォルダ走査は行わない。最近更新されたMarkdown/JSON/text（1ファイル64 KiB以下）を対象に、sourceのSHA-256で同じ内容の再取り込みを抑止する。root外へのsymlink、親ディレクトリ参照、認証・履歴系のファイル名は拒否する。

```json
{
  "local_sources": [{
    "project_id": "personal-experiment",
    "device_id": "mac-mini",
    "source_tool": "manual",
    "root": "/path/to/selected/personal-project",
    "files": ["README.md", "qa/technical.json"]
  }]
}
```

担当ツールを記録から確定できないメモは `manual` とする。別のCodex/Claude/Grokbotがこの候補をもとに振り返りを作成した場合、envelopeのsource_toolには振り返りの作成ツールを記録し、元の作業担当とは区別する。

```sh
# 通常の7日分
python3 tools/article_pipeline/collect_local.py --config .article-local/config.json
# 初回など、明示した期間だけ取り込む（最大90日）
python3 tools/article_pipeline/collect_local.py --config .article-local/config.json --days 30
```

候補は `state/local-candidates/` に保存し、更新日時、内容hash、端末・ツール・project、非公開参照、最大12,000文字の抜粋と下書き骨子を含む。抜粋の切詰めはフラグで示す。作業メモの記述を実施の直接証拠と同一視せず、記事化時は成果物・検証記録との照合が必要。公開許可は常にfalseであり、候補から直接PRにしない。作業を行うエージェントが共通プロンプトで学びを文章化し、公開可能な根拠と本人の許可を揃えたseedだけを公開側へ渡す。専用LLM APIや無人文章生成プロセスの追加接続は未実装。

この機構に設定するローカルパス・実名・具体的な個人実験名と生成された私的下書きは、公開repoに含めない。両端末の同期方法・定期実行は別途設定する。

## 推奨する入口: 作業終了ログ

日々の入口は [ハーネス作業ログ](harness-worklog.md)。作業エージェントが短いログを終了時に保存し、私的記事候補へ変換する。本人が毎回記事用の9項目を手入力する必要はない。既存メモのallowlist収集は過去の記録を取り込む補助手段として使用する。

## 記事ありdry-runのレビュー

`dry-run` は公開許可済みseedを検査し、`preview.json`、レビュー用 `preview.md`、実投稿と同じ生成関数を使う `pr-payload.json` をローカルstateへ出力する。PR payloadは1回1記事分（repo/base/head/draft/title/body/記事JSON）。非公開provenanceは含めない。Markdownは本文をエスケープし、任意HTMLやMarkdownリンクを有効化しない。サイト掲載形式は引き続きJSONで、MarkdownはPR本文とレビュー用に使う。

```sh
python3 tools/article_pipeline/pipeline.py dry-run --verify-remote --config .article-local/config.json
```

`--verify-remote` はGitHub根拠repoのpublic状態とURL実在を読み取り検証する。push・PR作成はしない。フラグなしの出力は `remote_evidence_verified: false` であり、根拠の公開可否は未確認。フラグありでもリモートの過去PR照合は未実施と表示する。公開処理は投稿時に再検査・重複照合する。dry-runの合格だけで公開を承認しない。

失敗・空実行の前に古いpreview/payloadを無効化する。seed_dirとstate_dirは別にする。秘密値検査は代表的な形式と私的パス・URLを検査するが、あらゆる機密や主張の真偽を判定できるものではない。
