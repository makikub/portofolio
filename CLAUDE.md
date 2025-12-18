# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Astro + Tailwind CSSで構築された静的ポートフォリオサイト。Firebase Hostingにデプロイ。

## コマンド

```bash
npm run dev      # 開発サーバー起動 (http://localhost:4321)
npm run build    # 型チェック + 本番ビルド (dist/に出力)
npm run preview  # ビルド後のプレビュー
firebase deploy --only hosting  # Firebase Hostingにデプロイ
```

## アーキテクチャ

### データ駆動設計
- `src/data/projects.json` - プロジェクト情報（Projects.astro, ProjectCard.astroで使用）
- `src/data/skills.json` - スキル情報（Skills.astroで使用）

コンテンツ更新はJSONファイルを編集するだけで完了。ホットリロード対応。

### レイアウト構成
- `src/layouts/Layout.astro` - ベースレイアウト（SEOメタタグ、OGP設定を含む）
- `src/pages/index.astro` - エントリーポイント、全コンポーネントを統合

### 静的アセット
- `public/images/profile.jpg` - プロフィール写真
- `public/images/projects/` - プロジェクト画像（1200x630px推奨）
- `public/images/og-image.jpg` - SNSシェア用OGP画像

## コーディング規約

### Astroコンポーネント
- フロントマター（`---`内）でロジック・型定義・データ取得を記述
- Props は interface で型定義: `interface Props { title: string; }`
- JSONデータは `import data from '../data/xxx.json'` でインポート

### スタイリング
- Tailwind CSSユーティリティクラスを優先
- カスタムカラー: `primary`, `secondary`, `beige-50/100/200/300` （tailwind.config.cjsで定義）
- 共通クラス: `.section`, `.container`, `.btn-primary`, `.btn-secondary`, `.card`
- モバイルファースト設計、ブレークポイント: `md:`, `lg:`, `xl:`

### データ形式

**projects.json の必須フィールド:**
- `challenge`: 解決した課題（定量的な改善を含める）
- `result`: 実際の成果を数値で示す
- `technologies`: 5〜8個推奨

**skills.json:**
- `level`: 0〜100の整数（プログレスバー幅として表示）

## デプロイ

Firebase Hosting設定済み。`firebase.json`でdist/を公開ディレクトリとして設定。
本番URL: https://masaki-k-portofolio.web.app
