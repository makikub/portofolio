# 投稿基盤の検証記録（2026-10-31）

## 検証した範囲

本人が更新したmain `639524e` を取り込み、公開サイトのトップ見出し・canonical・OG画像URLが一致することを確認した。favicon、OG画像、既存sitemapもmainとバイト単位で一致した。

承認された `npm ci --registry=https://registry.npmjs.org/ --no-audit --no-fund` で既存lockfileの依存を導入した。package.jsonの依存指定とlockfileは変更していない。追加購入、認証・npm許可設定の変更はしていない。

環境のユーザー設定ディレクトリへ書き込まないよう、検証コマンドに限って `ASTRO_TELEMETRY_DISABLED=1` を指定した。

```sh
python3 -m unittest discover -s tests -q
ASTRO_TELEMETRY_DISABLED=1 npm run build
```

- Python: 46テスト成功。
- Astro check: 28ファイル、エラー0・警告0・ヒント0。
- 通常build: 8ページ成功。公開許可済み記事は0件で、ノート一覧は準備中を表示。
- 公開情報だけの合成fixture build: 9ページ成功。記事詳細と一覧・sitemapへの追加を確認。
- fixtureは検証中だけソースへ置き、別のローカル出力先へbuild後に削除した。Gitや通常distへfixture記事を残していない。
- sitemapは通常7URL、fixtureあり8URL。既存6URLを維持。
- 通常の生成HTMLに私的候補、端末情報、ローカルパス、fixture記事がないことを検査。

## UI

既存Playwrightと既存Chromiumを使用し、127.0.0.1の検証サーバーだけへアクセスした。新しいブラウザは導入していない。

1440px、390px、320pxの各幅で、トップ・発信・ノート一覧・プロフィール・問い合わせ・既存ケース2件・合成記事詳細を検査。合計24画面ケースで次を確認した。

- HTTP 200、h1、canonical、ノート導線
- 横スクロールなし
- モバイルメニューの開閉とEscape操作
- ノート一覧の未公開候補非表示
- 合成記事の見出し、根拠リンク、一覧から詳細への遷移
- JavaScriptのpageerror 0

PCとモバイルのスクリーンショットも目視した。320pxで既存ScreenshotAppの長いタイトルが横にはみ出す問題を発見し、520px以下のケース見出しだけ文字サイズと折り返しを調整して再検証した。既存コンテンツ・ケース本文は変更していない。

## 制約と残る接続

- buildにはBrowserslistデータが古いという通知がある。依存更新はこの変更に含めていない。
- npmは一部install scriptのallowScriptsに関する警告を出したが、許可設定を変更せず上記build・UI検証は成功した。
- 本番deploy、Cloudflare管理画面の設定確認、本人マージ後の公開確認は未実施。
- ハーネスへの永続組み込み、MacBook Proとの私的同期、Grokbot側の呼出、定期automationは未接続。
- 根拠URLの実在や形式検査は、主張の正しさ・公開可否の最終判断を代替しない。

## PRレビュー対応

GitHubの収集APIへ渡すsinceのUTCオフセットをurlencodeでエンコードし、`+00:00` がクエリ解析時に空白へ変わる問題を修正。7日前の日時がAPI側で元通りに復元される回帰テストを追加した。
