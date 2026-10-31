# 個人ハーネスの実運用

作業終了ログは `harness.py` を入口にする。ローカルconfigの許可プロジェクトだけを対象とし、対象外では入力JSONさえ読まず終了する。記録は必ずprivateで、記事への公開許可は別工程に残す。認証・権限・会社プロジェクトの設定は変更しない。

## 配置と設定

本人の安定したcheckoutを作業場所にし、configとstateはgitignore済みの `.article-local/` に置く。`device_id` と `worklog_projects` をローカルconfigへ追加する。rootは物理パスで照合し、曖昧な重複指定は拒否する。

```json
{
  "device_id": "mac-mini",
  "worklog_projects": [
    {"project_id": "personal-project", "root": "/path/to/personal-project", "include_descendants": true}
  ]
}
```

実際のパス・顧客名などのdenylistは公開repoへ入れない。新しいprojectは本人が許可してから追加する。MacBook ProやGrokbotへの認証追加・権限変更をこの設定で行わない。

## Codex / Claude Code の終了時指示

既存のAGENTS.md / CLAUDE.mdをバックアップし、次の手順だけ追記する。これはモデルへの作業終了指示であり、イベントhookが保存を強制する仕組みではない。新しいセッションで指示を読み込ませる。既に動いているセッションへの遡及適用は保証しない。

1. タスク開始時に `harness.py context --config <private-config> --cwd <task-cwd> --tool codex`（Claudeは `claude-code`）を実行。
2. skippedなら、そのタスクについてログ生成・過去会話探索を行わない。
3. eligibleなら、終了時に今回の目標・分担・試行・結果・失敗・根拠・学びを短いJSONとして用意する。不明はunknown。秘密値や全会話は貼らない。
4. `harness.py record --config <private-config> --cwd <task-cwd> --tool <tool> --file -` にstdinで渡す。provenanceはconfigから注入される。`visibility` はprivate以外を拒否する。
5. 保存結果を確認し、失敗したら本来の成果物を保持して保存失敗を報告する。自動で承認や権限を拡大しない。

## 公開接続の現状

2026-10-31の既存Wrangler認証による読み取りで、Pages `masaki-portfolio` の `Git Provider` は `No` と確認した。PR #1はmainへマージ済みだが、独自ドメインとPages URLの `/notes/` はトップページへフォールバックしており未反映。既存READMEのGit連携記述は実設定と一致しない。現在はマージだけで公開される状態ではないため、自動デプロイ経路は別途承認して整備する。今回、手動deploy・設定変更・credential追加は行っていない。

## 週1回の公式automation用手順

cron/launchdは登録しない。実行環境はそのcheckoutへアクセスできるMacとし、cwdをcheckout rootに固定する。

```sh
python3 tools/article_pipeline/harness.py weekly --config .article-local/config.json
python3 tools/article_pipeline/pipeline.py collect --config .article-local/config.json
python3 tools/article_pipeline/pipeline.py dry-run --verify-remote --config .article-local/config.json
```

weeklyは許可されたproject/deviceのログを私的記事候補へ変換する。全期間を再走査してもproject/event単位で重複しない。既存の編集済み候補は上書きしない。収集候補から自動で公開許可を付けない。

automation側のエージェントは、読者への学びがあるか、根拠は直接確認できるか、実施と構想が分かれているかを確認する。公開可能とされたseedだけを使い、未知・機密・公開許可が不明な内容は私的候補に留める。公開可能な候補がなければPRを作らない。

公開許可済みseedがあり、本人がその定期タスクのDraft PR作成を許可済みの場合のみ、dry-runのpayloadを確認して以下を実行する。

```sh
python3 tools/article_pipeline/pipeline.py publish --config .article-local/config.json
```

認証失敗、公開根拠のprivate化、内容衝突、設定不備は停止して報告する。成功・失敗はCLIのexit code、pipelineのruns.jsonl、週次コマンドの結果を確認する。mainへpush・自動マージ・手動deployはしない。公式automationがMacへアクセスできない環境なら登録だけで稼働済みと扱わない。

## Grokbotと別端末

共通JSONは対応済みだが、サービス側へのメッセージ送信・credential追加・grant拡大は別途確認する。ローカル実行が既に許可されている場合だけ `--tool grokbot` を使う。別端末は同じCLIと個別configを用意し、本人が認めた私的経路で選択ログだけを渡す。公開Gitへ私的ログを同期しない。
