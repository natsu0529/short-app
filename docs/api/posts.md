# 投稿 API

## エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|----------|-----|------|------|
| `GET` | `/api/posts/` | 投稿一覧 | 不要 |
| `POST` | `/api/posts/` | 投稿作成 | 必要 |
| `GET` | `/api/posts/{id}/` | 投稿詳細 | 不要 |
| `PUT` | `/api/posts/{id}/` | 投稿更新（全項目） | 必要 |
| `PATCH` | `/api/posts/{id}/` | 投稿更新（一部） | 必要 |
| `DELETE` | `/api/posts/{id}/` | 投稿削除 | 必要 |

---

## GET /api/posts/

投稿一覧を取得します。

### クエリパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `user_id` | integer | 特定ユーザーの投稿のみ取得 |
| `page` | integer | ページ番号 |
| `page_size` | integer | 1ページあたりの件数（最大100） |

### リクエスト例

```
GET /api/posts/?user_id=1&page=1&page_size=10
```

### レスポンス例

```json
{
  "count": 100,
  "next": "/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "post_id": 1,
      "user": {
        "user_id": 1,
        "username": "john_doe",
        "user_name": "John Doe",
        "user_level": 5,
        ...
      },
      "context": "Hello, this is my first post!",
      "like_count": 10,
      "time": "2024-01-20T12:00:00Z",
      "is_liked": false
    }
  ]
}
```

---

## POST /api/posts/

新規投稿を作成します。投稿作成時に **+10 EXP** を獲得します。

### リクエストボディ

```json
{
  "context": "This is my new post!"
}
```

### 必須フィールド

| フィールド | 型 | 説明 |
|------------|-----|------|
| `context` | string | 投稿内容 |

### レスポンス（201 Created）

```json
{
  "post_id": 2,
  "user": {
    "user_id": 1,
    ...
  },
  "context": "This is my new post!",
  "like_count": 0,
  "time": "2024-01-20T15:30:00Z",
  "is_liked": false
}
```

---

## GET /api/posts/{id}/

指定した投稿の詳細を取得します。

### パスパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `id` | integer | 投稿ID |

### レスポンス（200 OK）

```json
{
  "post_id": 1,
  "user": {...},
  "context": "Hello, this is my first post!",
  "like_count": 10,
  "time": "2024-01-20T12:00:00Z",
  "is_liked": true
}
```

---

## PUT/PATCH /api/posts/{id}/

投稿を更新します。**自分の投稿のみ更新可能**です。

### リクエストボディ

```json
{
  "context": "Updated content"
}
```

### エラーレスポンス（403 Forbidden）

```json
{
  "detail": "自分の投稿のみ更新できます。"
}
```

---

## DELETE /api/posts/{id}/

投稿を削除します。**自分の投稿のみ削除可能**です。

### エラーレスポンス（403 Forbidden）

```json
{
  "detail": "自分の投稿のみ削除できます。"
}
```
