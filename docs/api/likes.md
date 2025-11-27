# いいね API

## エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|----------|-----|------|------|
| `GET` | `/api/likes/` | いいね一覧 | 不要 |
| `POST` | `/api/likes/` | いいね作成 | 必要 |
| `DELETE` | `/api/likes/{id}/` | いいね解除 | 必要 |
| `GET` | `/api/posts/liked-status/` | 投稿のいいね状態確認 | 必要 |
| `GET` | `/api/users/{user_id}/liked-posts/` | ユーザーがいいねした投稿一覧 | 不要 |

---

## GET /api/likes/

いいねの一覧を取得します。

### クエリパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `user_id` | integer | このユーザーがしたいいね一覧 |
| `post_id` | integer | この投稿へのいいね一覧 |
| `page` | integer | ページ番号 |
| `page_size` | integer | 1ページあたりの件数（最大100） |

### リクエスト例

```
GET /api/likes/?post_id=1
```

### レスポンス例

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "user_id": 2,
        "username": "jane_doe",
        ...
      },
      "post": {
        "post_id": 1,
        "context": "Hello!",
        ...
      },
      "created_at": "2024-01-20T10:00:00Z"
    }
  ]
}
```

---

## POST /api/likes/

投稿にいいねします。

### 副作用

- 投稿の `like_count` が +1
- いいねした人が **+2 EXP** を獲得
- 投稿者が **+5 EXP** を獲得
- いいねした人の `total_likes_given` が +1
- 投稿者の `total_likes_received` が +1

### リクエストボディ

```json
{
  "post_id": 1
}
```

### 必須フィールド

| フィールド | 型 | 説明 |
|------------|-----|------|
| `post_id` | integer | いいねする投稿のID |

### レスポンス（201 Created）

```json
{
  "id": 1,
  "user": {...},
  "post": {...},
  "created_at": "2024-01-20T15:00:00Z"
}
```

### エラーレスポンス

#### 既にいいね済み（400 Bad Request）

```json
{
  "non_field_errors": ["既にいいね済みです。"]
}
```

#### 未ログイン（403 Forbidden）

```json
{
  "detail": "ログインしてください。"
}
```

---

## DELETE /api/likes/{id}/

いいねを解除します。**自分のいいねのみ解除可能**です。

### 副作用

- 投稿の `like_count` が -1
- いいねした人の `total_likes_given` が -1
- 投稿者の `total_likes_received` が -1

### パスパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `id` | integer | いいねID |

### エラーレスポンス（403 Forbidden）

```json
{
  "detail": "自分のいいねのみ解除できます。"
}
```

---

## GET /api/posts/liked-status/

指定した投稿IDのうち、ログインユーザーがいいね済みのIDを返します。

### クエリパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `ids` | string | カンマ区切りの投稿ID（例: `1,2,3,4,5`） |

### リクエスト例

```
GET /api/posts/liked-status/?ids=1,2,3,4,5
```

### レスポンス（200 OK）

```json
{
  "liked_post_ids": [1, 3]
}
```

---

## GET /api/users/{user_id}/liked-posts/

指定したユーザーがいいねした投稿の一覧を取得します。

### パスパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `user_id` | integer | ユーザーID |

### レスポンス例

```json
{
  "count": 20,
  "next": "/api/users/1/liked-posts/?page=2",
  "previous": null,
  "results": [
    {
      "post_id": 5,
      "user": {...},
      "context": "Great post!",
      "like_count": 15,
      "time": "2024-01-18T12:00:00Z",
      "is_liked": true
    }
  ]
}
```
