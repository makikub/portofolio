# ハーネスの作業終了ログ

会話全文を後から巡回する代わりに、作業を行ったエージェントが終了時に短い振り返りを保存する。人は毎回のフォーム入力をしない。実験・修正・検証の区切りで、成功だけでなく失敗や保留も残す。

運用で呼ぶ入口は [許可範囲付きハーネス手順](harness-operations.md) の `harness.py`。以下の `worklog.py` は共通保存形式と低レベルCLIの説明です。

## 共通形式

テンプレート: `tools/article_pipeline/worklog.template.json`

JSON Schema: `tools/article_pipeline/worklog.schema.json`

- 必須: `provenance`（端末別名・ツール・project）、`goal`。
- エージェントが埋める: AIと人の分担、試行と結果、最終状態、失敗、根拠、学び。
- 不明な項目は空配列・unknownで保存。実施していない検証や人の判断を捏造しない。
- 根拠は `kind: pr|commit|test|artifact|note`、`ref`、`verification: observed|reported|not_run`。実行したテストと、資料で見ただけの結果を分ける。
- `visibility` の既定は `private`。`consider_for_article` は記事候補として検討してよいという印で、公開許可ではない。
- `event_id` は省略可能。本文とprojectから自動生成し、同じログの再保存を重複排除する。両端末で同じタスクを引き継ぐ場合は共通IDを指定できる。内容変更時はrevision IDを付ける。

記録先はローカルconfigのstate_dir内。端末名は `mac-mini` / `macbook-pro` のような別名を指定し、ホスト名・シリアル・アカウント情報を取得しない。私的ファイル参照も公開seedへ移さない。

## 終了時に呼ぶCLI

ハーネスがログJSONを標準入力で渡す場合:

```sh
python3 tools/article_pipeline/worklog.py record \
  --config .article-local/config.json --file -
```

エージェントがJSONファイルを作る場合:

```sh
python3 tools/article_pipeline/worklog.py record \
  --config .article-local/config.json \
  --file .article-local/task-finish.json
```

CLIは `private_log_saved`、event_id、保存先path、重複フラグを返す。成功時exit 0、検査失敗はexit 1。外部API・会話履歴・参照先ファイルにはアクセスしない。ファイルやコマンドのパスをrefに書いても実行しない。

保存したログを私的記事候補へ変換:

```sh
python3 tools/article_pipeline/worklog.py candidate \
  --config .article-local/config.json \
  --file .article-local/state/worklogs/RETURNED_FILE.json
```

返されたpathを引用して使う。候補はstate/intakeに保存され、public_releaseは必ずfalse。元ログの目標・分担・試行・結果・失敗・学びを記事構造へ並べ、再現条件や根拠未確認は未確認と残す。公開seed_dirには出力しない。完全な記事にする際、作業エージェントが根拠を照合して文章を整え、本人が公開可能とした内容だけを別途releaseする。

## 終了時プロンプトの共通ブロック

次のブロックをハーネスの最終処理指示へ組み込む。今回、既存の永続hookやツール設定は変更していない。

> 作業の一区切りで、今回自分が扱った範囲だけの短い作業ログを保存する。共通worklog形式で目標、AIと人の分担、試行、結果、失敗、根拠、学びを記入する。本人への入力フォームは要求しない。不明な項目はunknownまたは空配列にする。実行した検証・他の資料からの伝聞・未実施を区別する。会話全文、秘密値、顧客の実データは貼らない。根拠は参照と短い結果だけ。device_id・project_idはハーネスから渡された別名、source_toolは現在のツールとする。visibilityはprivate。worklog.py recordを1回呼び、返されたpathと成否を最終報告へ添える。失敗しても本来の成果物を破棄せず、保存失敗を報告する。ネットワーク接続や別端末探索を追加しない。

目安は各項目1〜3点、全体300〜800字程度。標準出力をシェルコマンドとしてevalしない。JSONはファイルまたはstdinで渡す。

## 各ハーネスへの組み込み案

| ツール | 組み込む位置 | 渡す情報 |
|---|---|---|
| Codex | 個人projectのAGENTS.mdまたは既存ハーネスの最終処理プロンプト | 共通ブロック、CLIの絶対パス、非公開configパス、device_id、project_id。source_tool=codex |
| Claude Code | 個人projectのCLAUDE.mdまたは既存ハーネスの最終処理プロンプト | 同じ情報。source_tool=claude-code |
| Grokbot | 本人が管理するハーネスのタスク完了処理。ローカル実行が許可されている場合だけCLI呼出 | 同じ情報。source_tool=grokbot。ローカル実行不可ならJSONを私的exportし、本人が選択して取り込む |

エージェントへの終了時指示は、強制実行されるネイティブhookと同じ保証ではない。確実な保存が必要なら本人のハーネス側でタスク完了時にJSON生成とCLIのexit codeを確認する。各製品固有のhook設定形式やGrokbotのAPIは、この実装では仮定しない。

両Macに同じCLIを置き、configと保存領域は端末ごとに用意する。共通project IDを使い、本人が認めた私的な経路でログを集約する。公開Gitを私的ログの同期に使わない。MacBook Proへのアクセス・配布・同期設定は帰宅後の本人操作を待ち、別経路接続はしない。

## 記事化までの境界

作業終了ログ → 私的候補 → エージェントによる根拠照合と文章化 → 本人が公開可能としたseed → Draft PR → 本人マージ。

この変更は左側の記録・候補変換を実装する。本人の公開許可、公開根拠、現在配信中サイトとの同期、定期実行は別の条件。公開サイトに対応するmainは同期済み。サイトbuild検証と本人によるPRレビュー・マージまでは本番公開しない。
