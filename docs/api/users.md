# ユーザー API

## エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|----------|-----|------|------|
| `GET` | `/api/users/` | ユーザー一覧 | 不要 |
| `POST` | `/api/users/` | ユーザー登録 | 不要 |
| `GET` | `/api/users/{id}/` | ユーザー詳細 | 不要 |
| `PUT` | `/api/users/{id}/` | ユーザー更新（全項目） | 必要 |
| `PATCH` | `/api/users/{id}/` | ユーザー更新（一部） | 必要 |
| `DELETE` | `/api/users/{id}/` | ユーザー削除 | 必要 |
| `GET` | `/api/users/me/` | 自分の情報取得 | 必要 |

---

## GET /api/users/

ユーザー一覧を取得します。いいね獲得数順でソートされます。

### レスポンス例

```json
{
  "count": 50,
  "next": "/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "user_id": 1,
      "username": "john_doe",
      "user_name": "John Doe",
      "user_rank": "",
      "user_level": 5,
      "user_mail": "john@example.com",
      "user_URL": "https://example.com",
      "user_bio": "Hello, I'm John!",
      "stats": {
        "experience_points": 120,
        "total_likes_received": 50,
        "total_likes_given": 30,
        "follower_count": 10,
        "following_count": 5,
        "post_count": 15,
        "last_level_up": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T15:00:00Z"
      },
      "rank": 1
    }
  ]
}
```

---

## POST /api/users/

新規ユーザーを登録します。

### リクエストボディ

```json
{
  "username": "new_user",
  "user_name": "New User",
  "user_mail": "newuser@example.com",
  "password": "securepassword123",
  "user_URL": "",
  "user_bio": ""
}
```

### 必須フィールド

| フィールド | 型 | 制約 |
|------------|-----|------|
| `username` | string | 一意、150文字以内 |
| `user_name` | string | 50文字以内 |
| `user_mail` | string | 一意、有効なメールアドレス |
| `password` | string | write_only |

### レスポンス（201 Created）

```json
{
  "user_id": 2,
  "username": "new_user",
  "user_name": "New User",
  "user_rank": "",
  "user_level": 1,
  "user_mail": "newuser@example.com",
  "user_URL": "",
  "user_bio": "",
  "stats": {
    "experience_points": 0,
    "total_likes_received": 0,
    "total_likes_given": 0,
    "follower_count": 0,
    "following_count": 0,
    "post_count": 0,
    "last_level_up": null,
    "updated_at": "2024-01-20T15:00:00Z"
  },
  "rank": null
}
```

---

## GET /api/users/{id}/

指定したユーザーの詳細を取得します。

### パスパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `id` | integer | ユーザーID |

### レスポンス（200 OK）

```json
{
  "user_id": 1,
  "username": "john_doe",
  "user_name": "John Doe",
  "user_rank": "",
  "user_level": 5,
  "user_mail": "john@example.com",
  "user_URL": "https://example.com",
  "user_bio": "Hello!",
  "stats": {...},
  "rank": 1
}
```

---

## PUT/PATCH /api/users/{id}/

ユーザー情報を更新します。**自分のアカウントのみ更新可能**です。

### リクエストボディ（PATCH例）

```json
{
  "user_name": "Updated Name",
  "user_bio": "Updated bio"
}
```

### エラーレスポンス（403 Forbidden）

```json
{
  "detail": "自分のアカウントのみ更新できます。"
}
```

---

## DELETE /api/users/{id}/

ユーザーを削除します。**自分のアカウントのみ削除可能**です。

### エラーレスポンス（403 Forbidden）

```json
{
  "detail": "自分のアカウントのみ削除できます。"
}
```

---

## GET /api/users/me/

認証済みユーザー自身の情報を取得します。

### レスポンス（200 OK）

```json
{
  "user_id": 1,
  "username": "john_doe",
  "user_name": "John Doe",
  ...
}
```

### エラーレスポンス（401 Unauthorized）

```json
{
  "detail": "認証情報が含まれていません。"
}
```
