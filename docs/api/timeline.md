# タイムライン API

## エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|----------|-----|------|------|
| `GET` | `/api/timeline/` | タイムライン取得 | 一部必要 |

---

## GET /api/timeline/

タイムラインを取得します。3種類のタブを切り替えて異なるフィードを取得できます。

### クエリパラメータ

| パラメータ | 型 | デフォルト | 説明 |
|------------|-----|------------|------|
| `tab` | string | `latest` | タイムラインの種類 |
| `page` | integer | 1 | ページ番号 |
| `page_size` | integer | 20 | 1ページあたりの件数（最大100） |

### tab パラメータ

| 値 | 説明 | 認証 | ソート順 |
|----|------|------|----------|
| `latest` | 最新の投稿 | 不要 | 投稿日時の降順 |
| `popular` | 過去24時間の人気投稿 | 不要 | いいね数の降順 → 投稿日時の降順 |
| `following` | フォロー中ユーザーの投稿 | **必要** | 投稿日時の降順 |

---

### latest（最新）

全ての投稿を新しい順で取得します。

```
GET /api/timeline/?tab=latest
```

#### レスポンス例

```json
{
  "count": 1000,
  "next": "/api/timeline/?tab=latest&page=2",
  "previous": null,
  "results": [
    {
      "post_id": 100,
      "user": {
        "user_id": 5,
        "username": "alice",
        "user_name": "Alice",
        ...
      },
      "context": "Just posted this!",
      "like_count": 0,
      "time": "2024-01-20T15:30:00Z",
      "is_liked": false
    }
  ]
}
```

---

### popular（人気）

過去24時間の投稿をいいね数順で取得します。

```
GET /api/timeline/?tab=popular
```

#### レスポンス例

```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "post_id": 42,
      "user": {...},
      "context": "This went viral!",
      "like_count": 150,
      "time": "2024-01-20T10:00:00Z",
      "is_liked": true
    }
  ]
}
```

---

### following（フォロー中）

フォローしているユーザーの投稿のみを取得します。**認証必須**です。

```
GET /api/timeline/?tab=following
```

#### 認証済みの場合

フォロー中ユーザーの投稿を新しい順で返します。

#### 未認証の場合

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

## is_liked フィールド

認証済みの場合、各投稿に `is_liked` フィールドが含まれます。

| 状態 | 値 |
|------|-----|
| いいね済み | `true` |
| 未いいね | `false` |
| 未認証 | `false` |
