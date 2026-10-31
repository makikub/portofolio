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

Cloudflare PagesはGitHub連携で自動デプロイします。

### 1. ローカルビルド確認

```bash
npm run build
```

### 2. Cloudflare Pages設定

Cloudflare Pagesで以下の設定を使います。

```txt
Project name: masaki-portfolio
Framework preset: Astro
Build command: npm run build
Build output directory: dist
Deploy branch: main
Node.js version: 20
```

### 3. デプロイ確認

GitHubの `main` ブランチにpushすると、Cloudflare Pagesが自動でビルド・デプロイします。

```bash
curl -I https://mklabos.dev
```

期待値は `HTTP/2 200` です。

本番URL: https://mklabos.dev

Cloudflare Pages URL: https://masaki-portfolio-dqt.pages.dev

### 4. 手動デプロイ

GitHub連携の自動デプロイが動かない、または本番URLが古い内容を返し続ける場合は、`dist` を Cloudflare Pages に直接デプロイします。

```bash
npm run build
npx wrangler pages deploy dist --project-name masaki-portfolio --branch main
```

デプロイ後、Cloudflare が返すプレビューURLと本番URLの両方で最新内容を確認します。

```bash
curl -L https://mklabos.dev
```

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
