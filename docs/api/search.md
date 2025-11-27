# 検索 API

## エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|----------|-----|------|------|
| `GET` | `/api/search/users/` | ユーザー検索 | 不要 |
| `GET` | `/api/search/posts/` | 投稿検索 | 不要 |

---

## GET /api/search/users/

ユーザーを検索します。`username` または `user_name` に対して部分一致検索を行います。

### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `q` | string | **必須** | 検索キーワード |
| `page` | integer | - | ページ番号 |
| `page_size` | integer | - | 1ページあたりの件数（最大100） |

### 検索対象

- `username`（ログインID）
- `user_name`（表示名）

### ソート順

1. 獲得いいね数（降順）
2. ユーザーレベル（降順）
3. 登録日時（降順）

### リクエスト例

```
GET /api/search/users/?q=john
```

### レスポンス例

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "user_id": 1,
      "username": "john_doe",
      "user_name": "John Doe",
      "user_level": 10,
      "stats": {
        "total_likes_received": 500,
        ...
      },
      ...
    },
    {
      "user_id": 15,
      "username": "johnny",
      "user_name": "Johnny Smith",
      ...
    }
  ]
}
```

### 検索キーワードが空の場合

空の結果を返します。

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

---

## GET /api/search/posts/

投稿を検索します。`context`（投稿内容）に対して部分一致検索を行います。

### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `q` | string | **必須** | 検索キーワード |
| `page` | integer | - | ページ番号 |
| `page_size` | integer | - | 1ページあたりの件数（最大100） |

### 検索対象

- `context`（投稿内容）

### ソート順

1. いいね数（降順）
2. 投稿日時（降順）

### リクエスト例

```
GET /api/search/posts/?q=hello
```

### レスポンス例

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "post_id": 42,
      "user": {...},
      "context": "Hello world! This is my first post.",
      "like_count": 25,
      "time": "2024-01-15T10:00:00Z",
      "is_liked": false
    },
    {
      "post_id": 88,
      "user": {...},
      "context": "Say hello to my new project!",
      "like_count": 10,
      "time": "2024-01-18T14:00:00Z",
      "is_liked": false
    }
  ]
}
```

### 検索キーワードが空の場合

空の結果を返します。

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```
