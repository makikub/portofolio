# ポートフォリオサイト

Astro + Tailwind CSSで構築した、AI駆動開発、AWS設計、エンジニアリングマネジメントの専門性と実践を紹介するポートフォリオサイトです。
技術顧問の設計ブリーフを思わせる情報設計と、paper / graphite / cobaltを基調にしたエディトリアルなデザインを採用しています。

## 🚀 特徴

- ⚡ **超高速** - Astroの静的サイト生成により、最高のパフォーマンス
- 🎨 **エディトリアルデザイン** - 専門領域、支援内容、実践を読みやすく構成
- 📱 **完全レスポンシブ** - モバイル、タブレット、デスクトップに対応
- 🔍 **SEO最適化** - メタタグ、OGP、SNS共有カード、サイトマップ対応
- 🎯 **読みやすさ重視** - タイポグラフィとスペーシングを重視したデザイン
- 💰 **低コスト運用** - Cloudflare Pagesの無料枠で運用可能

## 🎨 デザインテーマ

**カラースキーム:**
- Paper: `#f3f0e8`
- Graphite: `#262826`
- Cobalt: `#174cd3`

## 📋 セクション

- **About / Expertise** - AI、クラウド、組織、データを横断する専門性
- **Services** - 技術顧問、AI導入支援、AWS設計レビュー
- **AI-Driven Delivery** - Frame → Delegate → Verify → Learn
- **Organizational Cases** - Claude Code / Cline導入と組織浸透の公開事例
- **Product Cases** - ScreenshotApp / GlassDBの実装・検証・配布
- **Speaking & Writing** - Speaker Deck、Findy Tools、note、Zenn、X
- **Philosophy / Contact** - AI協調開発への考え方と公開窓口

## 🛠️ 技術スタック

- [Astro](https://astro.build/) 4.x - 静的サイトジェネレーター
- [Tailwind CSS](https://tailwindcss.com/) 3.x - CSSフレームワーク
- [TypeScript](https://www.typescriptlang.org/) - 型安全性
- [Cloudflare Pages](https://pages.cloudflare.com/) - ホスティング

## 📦 プロジェクト構造

```
portofolio/
├── public/                    # 静的ファイル
│   ├── robots.txt            # SEO設定
│   ├── sitemap.xml           # 公開ルート一覧
│   ├── og.png                # SNS共有カード
│   └── favicon.svg           # ファビコン
├── src/
│   ├── components/           # Astroコンポーネント
│   │   ├── Header.astro      # ヘッダー・ナビゲーション
│   │   ├── HomeIntro.astro   # トップの自己紹介
│   │   ├── Expertise.astro   # 専門領域
│   │   ├── Services.astro    # 支援内容
│   │   ├── OrganizationCases.astro # 組織導入事例
│   │   ├── Projects.astro    # プロジェクト一覧
│   │   ├── ProjectVisual.astro # プロダクト画面表現
│   │   ├── OperatingModel.astro # 仕事の進め方
│   │   ├── Contact.astro     # お問い合わせ
│   │   └── Footer.astro      # フッター
│   ├── layouts/
│   │   ├── Layout.astro      # ベースレイアウト
│   │   └── CaseLayout.astro  # ケース詳細レイアウト
│   ├── data/                 # データファイル
│   │   ├── projects.json     # プロジェクト情報
│   │   └── social.json       # 公開プロフィールリンク
│   ├── styles/
│   │   └── global.css        # グローバルスタイル
│   └── pages/
│       ├── index.astro       # トップページ
│       └── projects/         # ケース詳細ページ
├── astro.config.mjs          # Astro設定
├── tailwind.config.cjs       # Tailwind CSS設定
└── package.json              # 依存関係
```

## 🚀 開発手順

### 1. 依存関係のインストール

```bash
npm install
```

### 2. 開発サーバーの起動

```bash
npm run dev
```

ブラウザで http://localhost:4321 を開きます。

### 3. ビルド

```bash
npm run build
```

ビルドされたファイルは `dist/` ディレクトリに出力されます。

### 4. プレビュー

```bash
npm run preview
```

ビルド後のサイトをローカルでプレビューできます。

## 📝 カスタマイズ方法

### 1. 個人情報の更新

以下のファイルを編集して、自分の情報に置き換えてください：

- `src/data/projects.json` - プロジェクト情報
- `src/data/social.json` - 公開プロフィールリンク
- `src/components/*.astro` - 専門領域、支援内容、公開事例、発信
- `src/pages/profile.astro` - 経歴・仕事の原則

### 2. デザインの変更

色、タイポグラフィ、レスポンシブ設定は `src/styles/global.css` のデザイントークンと共通スタイルで管理します。

## Cloudflare Pagesへのデプロイ

既存の `masaki-portfolio` はDirect Upload方式です。CloudflareのGit連携ではなく、`.github/workflows/pages-deployment.yaml` がGitHub Actionsでテスト・ビルドした `dist` を配備します。

### 1. 初期設定

対象Cloudflareアカウントに限定したCI専用API token（Account / Cloudflare Pages / Edit）を作成し、以下をこのrepoのActions Secretsに登録します。token値はチャット、ログ、repoへ残しません。この権限は単一project限定ではありません。

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Secretsの登録完了を確認してからworkflowのPRをマージします。既存project・ドメイン・DNSは変更しません。

### 2. 検証と公開

PRではPythonテスト、記事検査、Astro型検査とbuildだけを実行します。mainへのpushでは同じ検証後、Secretsを配備stepだけに渡して既存Pagesへ公開します。検証失敗・Secrets不足・mainの先行更新では公開しません。PR作成だけでは公開されません。

CIはNode.js 22、Python 3.12、lockfileに従う `npm ci` を使用します。公式Actionsをcommit SHA、Wranglerを固定versionで指定しています。依存導入は公式npm registryから行い、既存依存のinstall scriptが実行されます。

```sh
npm run test:articles
ASTRO_TELEMETRY_DISABLED=1 npm run build
```

### 3. 公開確認と失敗時

GitHub Actionsの実行結果とCloudflareのproduction deploymentを確認し、対象main commitが公開されたことを確かめます。対象ページの見出し・canonical・sitemapも確認してください。存在しないURLでもトップページがHTTP 200で返る場合があるため、HTTP statusだけで成功とは判断しません。

- 本番URL: https://mklabos.dev
- Pages URL: https://masaki-portfolio-dqt.pages.dev

失敗時は原因を修正してから対象runを再実行します。古いcommitのrunはmain先行更新チェックで停止します。手動deployやDNS変更で迂回しません。公開後の不具合は修正またはrevert PRをレビューし、mainへマージして再配備します。

### 5. カスタムドメイン

Cloudflare Pagesの Custom domains に `mklabos.dev` を登録し、同じCloudflareアカウントのDNSからPagesへ接続しています。Astroのcanonical、OGP、robots、サイトマップも `https://mklabos.dev` を正規URLとして生成します。

## 📊 パフォーマンス最適化

このサイトは以下の最適化を行っています：

- ✅ 静的サイト生成（SSG）
- ✅ CSSの自動最小化
- ✅ レスポンシブ対応
- ✅ reduced motion対応

## 🔧 トラブルシューティング

### ビルドエラーが発生する場合

```bash
# node_modulesを削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

### スタイルが適用されない場合

```bash
# Tailwind CSSの再ビルド
npm run build
```

## 📝 ライセンス

MIT License - 自由に使用、変更、配布できます。

## 🤝 貢献

このプロジェクトはポートフォリオテンプレートとして自由にカスタマイズしてご使用ください。

## 📧 お問い合わせ

質問や提案があれば、お気軽にご連絡ください。

---

**Built with ❤️ using Astro & Tailwind CSS**

## 実践ノートの投稿基盤

AI活用の学びを記事種からDraft PRにする手順は [運用ガイド](docs/article-pipeline.md) を参照。公開サイトに対応する最新mainは取り込み済みです。ローカルの型・build・PC/モバイル検証は完了しています。本人レビュー後に有効化してください。定期実行は未登録です。
