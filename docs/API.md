# ShortSNS API ドキュメント

## 概要

ShortSNS は短文投稿型SNSのバックエンドAPIです。

- **ベースURL**: `/api/`
- **認証**: Session認証 / Token認証（Django REST Framework標準）
- **レスポンス形式**: JSON

---

## エンドポイント一覧

| カテゴリ | エンドポイント | 説明 |
|----------|----------------|------|
| **ユーザー** | `/api/users/` | ユーザーCRUD |
| **投稿** | `/api/posts/` | 投稿CRUD |
| **フォロー** | `/api/follows/` | フォロー管理 |
| **いいね** | `/api/likes/` | いいね管理 |
| **タイムライン** | `/api/timeline/` | フィード取得 |
| **検索** | `/api/search/users/`, `/api/search/posts/` | ユーザー・投稿検索 |
| **ランキング** | `/api/rankings/...` | 各種ランキング |

---

## 認証

### 認証が必要なエンドポイント

| メソッド | 認証 |
|----------|------|
| `GET` | 多くは不要（公開データ） |
| `POST`, `PUT`, `PATCH`, `DELETE` | 必要 |

### 認証ヘッダー例

```
Authorization: Token <your-token>
```

---

## 共通レスポンス形式

### ページネーション

リスト系エンドポイントはページネーションを使用します。

```json
{
  "count": 100,
  "next": "http://example.com/api/posts/?page=2",
  "previous": null,
  "results": [...]
}
```

| パラメータ | デフォルト | 最大 |
|------------|------------|------|
| `page` | 1 | - |
| `page_size` | 20 | 100 |

### エラーレスポンス

```json
{
  "detail": "エラーメッセージ"
}
```

または

```json
{
  "field_name": ["エラーメッセージ"]
}
```

---

## データモデル概要

### User（ユーザー）

| フィールド | 型 | 説明 |
|------------|-----|------|
| `user_id` | integer | ユーザーID（PK） |
| `username` | string | ログインID |
| `user_name` | string | 表示名 |
| `user_level` | integer | レベル（1〜） |
| `user_rank` | string | ランク称号 |
| `user_mail` | string | メールアドレス |
| `user_URL` | string | プロフィールURL |
| `user_bio` | string | 自己紹介 |
| `stats` | object | 統計情報 |
| `rank` | integer | いいねランキング順位 |

### UserStats（ユーザー統計）

| フィールド | 型 | 説明 |
|------------|-----|------|
| `experience_points` | integer | 経験値 |
| `total_likes_received` | integer | 獲得いいね数 |
| `total_likes_given` | integer | したいいね数 |
| `follower_count` | integer | フォロワー数 |
| `following_count` | integer | フォロー数 |
| `post_count` | integer | 投稿数 |
| `last_level_up` | datetime | 最終レベルアップ日時 |

### Post（投稿）

| フィールド | 型 | 説明 |
|------------|-----|------|
| `post_id` | integer | 投稿ID（PK） |
| `user` | object | 投稿者情報 |
| `context` | string | 投稿内容 |
| `like_count` | integer | いいね数 |
| `time` | datetime | 投稿日時 |
| `is_liked` | boolean | ログインユーザーがいいね済みか |

### Follow（フォロー）

| フィールド | 型 | 説明 |
|------------|-----|------|
| `id` | integer | フォローID（PK） |
| `user` | object | フォローしたユーザー |
| `aim_user` | object | フォローされたユーザー |
| `time` | datetime | フォロー日時 |

### Like（いいね）

| フィールド | 型 | 説明 |
|------------|-----|------|
| `id` | integer | いいねID（PK） |
| `user` | object | いいねしたユーザー |
| `post` | object | いいねされた投稿 |
| `created_at` | datetime | いいね日時 |

---

## 経験値・レベルシステム

### 経験値獲得

| アクション | 獲得EXP |
|------------|---------|
| 投稿を作成 | +10 |
| いいねをする | +2 |
| いいねをもらう | +5 |

### レベルアップ閾値

| レベル | 必要経験値 |
|--------|------------|
| 1 | 0 |
| 2 | 10 |
| 3 | 30 |
| 4 | 60 |
| 5 | 100 |
| 6-10 | 50ずつ増加（150, 200, 250, 300, 350） |
| 11-20 | 100ずつ増加（450, 550, ..., 1350） |
| 21-50 | 200ずつ増加（1550, 1750, ..., 7350） |
| 51-100 | 300ずつ増加（7650, 7950, ..., 22350） |
| 101+ | 500ずつ増加 |

---

## 詳細ドキュメント

- [ユーザーAPI](api/users.md)
- [投稿API](api/posts.md)
- [フォローAPI](api/follows.md)
- [いいねAPI](api/likes.md)
- [タイムラインAPI](api/timeline.md)
- [検索API](api/search.md)
- [ランキングAPI](api/rankings.md)
