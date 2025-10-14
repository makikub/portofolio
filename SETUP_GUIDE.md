# セットアップガイド

このガイドでは、ポートフォリオサイトを自分用にカスタマイズする手順を説明します。

## 📝 必須カスタマイズ項目

### 1. プロフィール情報の更新

#### `src/components/Hero.astro`
- 名前、肩書き
- 自己紹介文

#### `src/components/About.astro`
- 詳細な自己紹介
- 経験年数、プロジェクト数などの数値

### 2. プロジェクト情報の更新

#### `src/data/projects.json`

各プロジェクトには以下の情報を記載してください：

```json
{
  "id": 1,
  "title": "プロジェクト名",
  "description": "プロジェクトの簡単な説明（1〜2文）",
  "challenge": "解決した課題の詳細（ビフォー・アフターを含む）",
  "result": "定量的な成果（例：売上2倍、処理速度3倍など）",
  "technologies": ["使用した", "技術", "スタック"],
  "image": "/images/projects/プロジェクト画像.jpg",
  "liveUrl": "https://デモサイトURL（オプション）",
  "githubUrl": "https://github.com/your-repo（オプション）",
  "duration": "開発期間",
  "role": "あなたの役割"
}
```

**重要：**
- `challenge` フィールドには、具体的な課題と解決方法を記載
- 定量的な成果（数値）を含めると説得力が増します
- 最低3つ以上のプロジェクトを追加することを推奨

### 3. スキル情報の更新

#### `src/data/skills.json`

自分の技術スタックに合わせて編集：

```json
{
  "categories": [
    {
      "name": "カテゴリ名",
      "skills": [
        { "name": "技術名", "level": 90 }
      ]
    }
  ]
}
```

- `level` は 0〜100 の数値（プログレスバーに反映）
- カテゴリは自由に追加・削除可能

### 4. 連絡先情報の更新

#### `src/components/Footer.astro`
```javascript
const socialLinks = [
  {
    name: 'GitHub',
    url: 'https://github.com/yourusername', // ← 変更
    icon: '...'
  },
  // ...
];
```

#### `src/components/Contact.astro`
- メールアドレス
- SNSのURL

**すべての `yourusername` と `your.email@example.com` を検索して置き換えてください。**

### 5. 画像の追加

必要な画像を以下のディレクトリに配置：

```
public/images/
├── profile.jpg          # あなたのプロフィール写真（500x500px推奨）
├── og-image.jpg         # SNSシェア用画像（1200x630px推奨）
└── projects/
    ├── project1.jpg     # プロジェクト画像（1200x630px推奨）
    ├── project2.jpg
    └── project3.jpg
```

**画像のファイル名は `projects.json` の `image` フィールドと一致させてください。**

## 🎨 オプションカスタマイズ

### カラースキームの変更

`tailwind.config.cjs` を編集：

```javascript
colors: {
  primary: '#3B82F6',    // ← お好みの色に変更
  secondary: '#8B5CF6',
  accent: '#10B981',
},
```

### フォントの変更

`src/styles/global.css` の先頭を編集：

```css
@import url('https://fonts.googleapis.com/css2?family=Your+Font&display=swap');
```

### メタ情報の更新

`src/layouts/Layout.astro` を編集：
- サイトのデフォルト説明文
- OG画像のパス

## 🔥 Firebase Hosting設定

### 1. Firebase プロジェクトの作成

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. 「プロジェクトを追加」をクリック
3. プロジェクト名を入力（例：my-portfolio）
4. Google Analyticsは任意で設定

### 2. Firebase CLIのインストール

```bash
npm install -g firebase-tools
```

### 3. ログイン

```bash
firebase login
```

### 4. プロジェクトIDの設定

`.firebaserc` を編集：

```json
{
  "projects": {
    "default": "あなたのプロジェクトID"
  }
}
```

プロジェクトIDは Firebase Console の「プロジェクトの設定」で確認できます。

### 5. 初回デプロイ

```bash
# ビルド
npm run build

# デプロイ
firebase deploy
```

成功すると、以下のようなURLが表示されます：
```
Hosting URL: https://your-project-id.web.app
```

### カスタムドメインの設定（オプション）

1. Firebase Console の「Hosting」セクションを開く
2. 「カスタムドメインを追加」をクリック
3. ドメインを入力して、指示に従ってDNS設定を行う

## ✅ カスタマイズチェックリスト

デプロイ前に以下をチェック：

- [ ] `src/data/projects.json` に自分のプロジェクトを追加
- [ ] `src/data/skills.json` に自分のスキルを記載
- [ ] すべての `yourusername` を自分のユーザー名に変更
- [ ] すべての `your.email@example.com` を自分のメールアドレスに変更
- [ ] プロフィール写真を `public/images/profile.jpg` に配置
- [ ] プロジェクト画像を `public/images/projects/` に配置
- [ ] OG画像を `public/images/og-image.jpg` に配置
- [ ] `astro.config.mjs` の `site` URLを自分のドメインに変更
- [ ] `public/robots.txt` の Sitemap URLを変更
- [ ] `.firebaserc` にFirebaseプロジェクトIDを設定
- [ ] 自己紹介文を書き換え
- [ ] SNSリンクを更新

## 🐛 よくある問題と解決方法

### Q: 開発サーバーが起動しない

```bash
# node_modulesを再インストール
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Q: 画像が表示されない

- 画像のパスが `/images/` で始まっているか確認
- `public/images/` ディレクトリに画像が配置されているか確認
- ファイル名の大文字・小文字が一致しているか確認

### Q: Tailwind CSSのスタイルが適用されない

```bash
# ビルドをやり直す
npm run build
npm run dev
```

### Q: Firebase デプロイが失敗する

1. Firebase CLIが最新版か確認：
```bash
npm install -g firebase-tools@latest
```

2. 再度ログイン：
```bash
firebase logout
firebase login
```

3. プロジェクトIDが正しいか確認：
```bash
firebase projects:list
```

## 📚 参考リソース

- [Astro ドキュメント](https://docs.astro.build/)
- [Tailwind CSS ドキュメント](https://tailwindcss.com/docs)
- [Firebase Hosting ドキュメント](https://firebase.google.com/docs/hosting)
- [Google Fonts](https://fonts.google.com/)
- [Unsplash（無料画像）](https://unsplash.com/)

## 💡 ヒント

1. **定期的な更新**: 新しいプロジェクトを完成させたら、すぐにポートフォリオに追加しましょう

2. **数値で示す**: 成果は可能な限り数値化すると説得力が増します
   - ❌ 「パフォーマンスを改善しました」
   - ✅ 「ページ読み込み速度を70%改善しました」

3. **ビジュアルを重視**: 各プロジェクトには必ず魅力的なスクリーンショットを用意

4. **モバイル確認**: スマートフォンでの見た目も必ず確認してください

5. **Analytics導入**: Google Analytics 4を導入して、訪問者の行動を分析しましょう

---

質問や問題がある場合は、GitHub Issuesで報告してください！

