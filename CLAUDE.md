# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Astro + Tailwind CSSで構築された静的ポートフォリオサイト。Cloudflare Pagesにデプロイ。

## コマンド

```bash
npm run dev      # 開発サーバー起動 (http://localhost:4321)
npm run build    # 型チェック + 本番ビルド (dist/に出力)
npm run preview  # ビルド後のプレビュー
```

## アーキテクチャ

### データ駆動設計
- `src/data/projects.json` - プロジェクト情報（Projects.astroで使用）
- `src/data/social.json` - 公開プロフィールへのリンク（Header、ActivityLinks、Contactで使用）

コンテンツ更新はJSONファイルを編集するだけで完了。ホットリロード対応。

### レイアウト構成
- `src/layouts/Layout.astro` - ベースレイアウト（SEOメタタグ、OGP設定を含む）
- `src/pages/index.astro` - projects-first構成のトップページ
- `src/layouts/CaseLayout.astro` - プロジェクト詳細ページの共通レイアウト
- `src/pages/projects/*.astro` - ScreenshotApp / GlassDB のケース詳細
- `src/pages/projects.astro` - 旧一覧URLからトップページへのリダイレクト

### 静的アセット
- `public/favicon.svg` - ファビコン

## コーディング規約

### Astroコンポーネント
- フロントマター（`---`内）でロジック・型定義・データ取得を記述
- Props は interface で型定義: `interface Props { title: string; }`
- JSONデータは `import data from '../data/xxx.json'` でインポート

### スタイリング
- `src/styles/global.css` のデザイントークンを使用
- 基調色は paper / graphite / cobalt
- レスポンシブと `prefers-reduced-motion` に対応する

### データ形式

**projects.json の必須フィールド:**
- `slug`: ケース詳細ページのURL識別子
- `challenge`: 解決した課題
- `result`: 検証・配布を含む成果
- `technologies`: 使用技術

## デプロイ

Cloudflare PagesでGitHub連携デプロイ。

- Project name: `masaki-portfolio`
- Production URL: https://masaki-portfolio-dqt.pages.dev
- Build command: `npm run build`
- Build output directory: `dist`
- Deploy branch: `main`
- Node.js version: 20
