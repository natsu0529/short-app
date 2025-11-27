# フォロー API

## エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|----------|-----|------|------|
| `GET` | `/api/follows/` | フォロー一覧 | 不要 |
| `POST` | `/api/follows/` | フォロー作成 | 必要 |
| `GET` | `/api/follows/{id}/` | フォロー詳細 | 不要 |
| `DELETE` | `/api/follows/{id}/` | フォロー解除 | 必要 |

---

## GET /api/follows/

フォロー関係の一覧を取得します。

### クエリパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `user_id` | integer | このユーザーがフォローしている一覧 |
| `aim_user_id` | integer | このユーザーをフォローしている一覧 |
| `page` | integer | ページ番号 |
| `page_size` | integer | 1ページあたりの件数（最大100） |

### 使用例

#### 特定ユーザーのフォロー一覧（フォローしている人）

```
GET /api/follows/?user_id=1
```

#### 特定ユーザーのフォロワー一覧（フォローされている人）

```
GET /api/follows/?aim_user_id=1
```

### レスポンス例

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "user_id": 1,
        "username": "john_doe",
        "user_name": "John Doe",
        ...
      },
      "aim_user": {
        "user_id": 2,
        "username": "jane_doe",
        "user_name": "Jane Doe",
        ...
      },
      "time": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

## POST /api/follows/

ユーザーをフォローします。

### 副作用

- フォローした側の `following_count` が +1
- フォローされた側の `follower_count` が +1

### リクエストボディ

```json
{
  "aim_user_id": 2
}
```

### 必須フィールド

| フィールド | 型 | 説明 |
|------------|-----|------|
| `aim_user_id` | integer | フォローするユーザーのID |

### レスポンス（201 Created）

```json
{
  "id": 1,
  "user": {
    "user_id": 1,
    ...
  },
  "aim_user": {
    "user_id": 2,
    ...
  },
  "time": "2024-01-20T15:00:00Z"
}
```

### エラーレスポンス

#### 自分自身をフォロー（400 Bad Request）

```json
{
  "non_field_errors": ["自分自身をフォローすることはできません。"]
}
```

#### 既にフォロー済み（400 Bad Request）

```json
{
  "non_field_errors": ["既にフォロー済みです。"]
}
```

---

## DELETE /api/follows/{id}/

フォローを解除します。**自分のフォローのみ解除可能**です。

### 副作用

- フォローした側の `following_count` が -1
- フォローされた側の `follower_count` が -1

### パスパラメータ

| パラメータ | 型 | 説明 |
|------------|-----|------|
| `id` | integer | フォローID |

### エラーレスポンス（403 Forbidden）

```json
{
  "detail": "自分のフォローのみ解除できます。"
}
```
