# ランキング API

## エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|----------|-----|------|------|
| `GET` | `/api/rankings/posts/likes/` | 投稿いいねランキング | 不要 |
| `GET` | `/api/rankings/users/total-likes/` | ユーザー総いいねランキング | 不要 |
| `GET` | `/api/rankings/users/level/` | ユーザーレベルランキング | 不要 |
| `GET` | `/api/rankings/users/followers/` | ユーザーフォロワーランキング | 不要 |

---

## GET /api/rankings/posts/likes/

いいね数が多い投稿のランキングを取得します。

### クエリパラメータ

| パラメータ | 型 | デフォルト | 説明 |
|------------|-----|------------|------|
| `range` | string | - | `24h` を指定すると過去24時間のみ |
| `page` | integer | 1 | ページ番号 |
| `page_size` | integer | 20 | 1ページあたりの件数（最大100） |

### 全期間ランキング

```
GET /api/rankings/posts/likes/
```

### 過去24時間ランキング

```
GET /api/rankings/posts/likes/?range=24h
```

### レスポンス例

```json
{
  "count": 100,
  "next": "/api/rankings/posts/likes/?page=2",
  "previous": null,
  "results": [
    {
      "post_id": 42,
      "user": {
        "user_id": 1,
        "username": "top_user",
        ...
      },
      "context": "Most liked post!",
      "like_count": 500,
      "time": "2024-01-10T12:00:00Z",
      "is_liked": true
    }
  ]
}
```

---

## GET /api/rankings/users/total-likes/

獲得いいね総数が多いユーザーのランキングを取得します。

### クエリパラメータ

| パラメータ | 型 | デフォルト | 説明 |
|------------|-----|------------|------|
| `page` | integer | 1 | ページ番号 |
| `page_size` | integer | 20 | 1ページあたりの件数（最大100） |

### リクエスト例

```
GET /api/rankings/users/total-likes/
```

### ソート順

1. 獲得いいね総数（降順）
2. 登録日時（降順）

### レスポンス例

```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "user_id": 1,
      "username": "popular_user",
      "user_name": "Popular User",
      "user_level": 25,
      "stats": {
        "total_likes_received": 1500,
        "total_likes_given": 200,
        "follower_count": 300,
        ...
      },
      "rank": 1
    }
  ]
}
```

---

## GET /api/rankings/users/level/

レベルが高いユーザーのランキングを取得します。

### クエリパラメータ

| パラメータ | 型 | デフォルト | 説明 |
|------------|-----|------------|------|
| `page` | integer | 1 | ページ番号 |
| `page_size` | integer | 20 | 1ページあたりの件数（最大100） |

### リクエスト例

```
GET /api/rankings/users/level/
```

### ソート順

1. ユーザーレベル（降順）
2. 登録日時（降順）

### レスポンス例

```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "user_id": 5,
      "username": "top_level_user",
      "user_name": "Top Level",
      "user_level": 50,
      "stats": {
        "experience_points": 7500,
        ...
      },
      ...
    }
  ]
}
```

---

## GET /api/rankings/users/followers/

フォロワー数が多いユーザーのランキングを取得します。

### クエリパラメータ

| パラメータ | 型 | デフォルト | 説明 |
|------------|-----|------------|------|
| `page` | integer | 1 | ページ番号 |
| `page_size` | integer | 20 | 1ページあたりの件数（最大100） |

### リクエスト例

```
GET /api/rankings/users/followers/
```

### ソート順

1. フォロワー数（降順）
2. 登録日時（降順）

### レスポンス例

```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "user_id": 3,
      "username": "influencer",
      "user_name": "Big Influencer",
      "user_level": 30,
      "stats": {
        "follower_count": 1000,
        "following_count": 50,
        ...
      },
      ...
    }
  ]
}
```
