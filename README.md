# ポートフォリオサイト

Astro + Tailwind CSSで構築した、シンプルでミニマルなポートフォリオサイトです。
Saralテーマをベースにしたクリーンなデザインが特徴です。

## 🚀 特徴

- ⚡ **超高速** - Astroの静的サイト生成により、最高のパフォーマンス
- 🎨 **ミニマルデザイン** - Saralテーマをベースにしたシンプルで美しいUI
- 📱 **完全レスポンシブ** - モバイル、タブレット、デスクトップに対応
- 🔍 **SEO最適化** - メタタグ、OGP、構造化データ対応
- 🎯 **読みやすさ重視** - タイポグラフィとスペーシングを重視したデザイン
- 💰 **低コスト運用** - Firebase Hostingの無料枠で運用可能

## 🎨 デザインテーマ

このサイトは[Saral Theme](https://yashjawale.in/saral-theme-astro/)からインスピレーションを得ています。

**カラースキーム:**
- Primary: `#1a1a1a` (ダークグレー)
- Secondary: `#6b6b6b` (ミディアムグレー)
- Accent: `#f5f5f0` (ベージュ)
- Background: `#fafaf8` (ライトベージュ)

## 📋 セクション

- **Hero** - Welcome メッセージとソーシャルリンク
- **Recent Posts** - プロジェクト/ブログ記事一覧
- **About Me** - 自己紹介と経歴
- **Get in touch** - お問い合わせ情報

## 🛠️ 技術スタック

- [Astro](https://astro.build/) 4.x - 静的サイトジェネレーター
- [Tailwind CSS](https://tailwindcss.com/) 3.x - CSSフレームワーク
- [TypeScript](https://www.typescriptlang.org/) - 型安全性
- [Firebase Hosting](https://firebase.google.com/products/hosting) - ホスティング

## 📦 プロジェクト構造

```
portofolio/
├── public/                    # 静的ファイル
│   ├── images/               # 画像
│   │   ├── profile.jpg       # プロフィール写真
│   │   └── projects/         # プロジェクト画像
│   ├── robots.txt            # SEO設定
│   └── favicon.svg           # ファビコン
├── src/
│   ├── components/           # Astroコンポーネント
│   │   ├── Header.astro      # ヘッダー・ナビゲーション
│   │   ├── Hero.astro        # ヒーローセクション
│   │   ├── About.astro       # 自己紹介
│   │   ├── Skills.astro      # スキル表示
│   │   ├── Projects.astro    # プロジェクト一覧
│   │   ├── ProjectCard.astro # プロジェクトカード
│   │   ├── Contact.astro     # お問い合わせ
│   │   └── Footer.astro      # フッター
│   ├── layouts/
│   │   └── Layout.astro      # ベースレイアウト
│   ├── data/                 # データファイル
│   │   ├── projects.json     # プロジェクト情報
│   │   └── skills.json       # スキル情報
│   ├── styles/
│   │   └── global.css        # グローバルスタイル
│   └── pages/
│       └── index.astro       # トップページ
├── astro.config.mjs          # Astro設定
├── tailwind.config.cjs       # Tailwind CSS設定
├── firebase.json             # Firebase Hosting設定
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
- `src/data/skills.json` - スキル情報
- `src/components/Footer.astro` - SNSリンク、メールアドレス
- `src/components/Contact.astro` - 連絡先情報

### 2. 画像の配置

以下の画像を配置してください：

- `public/images/profile.jpg` - プロフィール写真（推奨：500x500px以上）
- `public/images/projects/*.jpg` - プロジェクト画像（推奨：1200x630px）
- `public/images/og-image.jpg` - OGP画像（推奨：1200x630px）

### 3. カラースキームの変更

`tailwind.config.cjs` でカラーを変更できます：

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        DEFAULT: '#1a1a1a',  // メインテキストカラー
        light: '#4a4a4a',    // ホバー時のカラー
      },
      secondary: {
        DEFAULT: '#6b6b6b',  // サブテキストカラー
        light: '#9b9b9b',
      },
      beige: {
        50: '#fafaf8',       // 背景カラー
        100: '#f5f5f0',
        200: '#e8e8e0',
        300: '#d1d1c8',      // ボーダーカラー
      },
    },
  },
},
```

### 4. フォントの変更

`src/styles/global.css` でGoogle Fontsのインポートを変更：

```css
@import url('https://fonts.googleapis.com/css2?family=Your+Font&display=swap');
```

## 🔥 Firebase Hostingへのデプロイ

### 1. Firebase CLIのインストール

```bash
npm install -g firebase-tools
```

### 2. Firebaseにログイン

```bash
firebase login
```

### 3. Firebaseプロジェクトの作成

[Firebase Console](https://console.firebase.google.com/)でプロジェクトを作成します。

### 4. プロジェクトIDの設定

`.firebaserc` を編集して、作成したプロジェクトIDを設定：

```json
{
  "projects": {
    "default": "your-project-id"
  }
}
```

### 5. ビルドとデプロイ

```bash
npm run build
firebase deploy
```

デプロイが完了すると、URLが表示されます：
```
Hosting URL: https://your-project-id.web.app
```

### カスタムドメインの設定（オプション）

Firebase Consoleの Hosting セクションから、カスタムドメインを設定できます。

## 📊 パフォーマンス最適化

このサイトは以下の最適化が施されています：

- ✅ 静的サイト生成（SSG）
- ✅ ゼロJavaScriptデフォルト
- ✅ 画像の遅延読み込み
- ✅ CSSの自動最小化
- ✅ キャッシュ制御ヘッダー設定済み

**期待されるLighthouseスコア：**
- Performance: 95+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 100

## 🔧 トラブルシューティング

### ビルドエラーが発生する場合

```bash
# node_modulesを削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

### 画像が表示されない場合

- 画像パスが正しいか確認
- `public/images/` ディレクトリに画像が配置されているか確認
- 画像ファイル名が `projects.json` の記載と一致しているか確認

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
