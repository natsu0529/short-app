# 認証API

## 概要

ShortSNSでは、Google Sign-inとSign in with Appleによる認証をサポートしています。
認証に成功すると、APIトークンが発行され、以降のAPIリクエストに使用できます。

---

## エンドポイント

### Google Sign-in

**POST** `/api/auth/google/`

Google ID Tokenを検証してAPIトークンを発行します。

#### リクエスト

```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI1M...",
  "email": "user@example.com",
  "display_name": "山田太郎"
}
```

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `id_token` | string | ✓ | Google ID Token（JWT） |
| `email` | string | | メールアドレス（トークンから取得可能な場合は省略可） |
| `display_name` | string | | 表示名 |

#### レスポンス

**成功時（200 OK）**

```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
}
```

| フィールド | 型 | 説明 |
|------------|-----|------|
| `token` | string | APIトークン |

**エラー時（400 Bad Request）**

```json
{
  "error": "id_token is required"
}
```

**エラー時（401 Unauthorized）**

```json
{
  "error": "Invalid token: ..."
}
```

#### 動作

1. Google ID Tokenを検証
2. トークンからメールアドレスを取得
3. ユーザーを検索、存在しない場合は新規作成
4. APIトークンを発行して返却

#### 注意事項

- 初回ログイン時は自動的にユーザーアカウントが作成されます
- メールアドレスがユニーク識別子として使用されます

---

### Sign in with Apple

**POST** `/api/auth/apple/`

Apple Identity Tokenを検証してAPIトークンを発行します。

#### リクエスト

```json
{
  "identity_token": "eyJraWQiOiJZdXlYb1kiLCJhbGciOiJSUzI1NiJ9...",
  "user_id": "001234.abc123def456789.1234",
  "email": "user@privaterelay.appleid.com",
  "given_name": "太郎",
  "family_name": "山田"
}
```

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `identity_token` | string | ✓ | Apple Identity Token（JWT） |
| `user_id` | string | ✓ | AppleユーザーID（一意識別子） |
| `email` | string | | メールアドレス（初回のみ提供される） |
| `given_name` | string | | 名（初回のみ提供される） |
| `family_name` | string | | 姓（初回のみ提供される） |

#### レスポンス

**成功時（200 OK）**

```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
}
```

| フィールド | 型 | 説明 |
|------------|-----|------|
| `token` | string | APIトークン |

**エラー時（400 Bad Request）**

```json
{
  "error": "identity_token and user_id are required"
}
```

**エラー時（401 Unauthorized）**

```json
{
  "error": "Invalid token: ..."
}
```

または

```json
{
  "error": "user_id mismatch"
}
```

#### 動作

1. Apple Identity Tokenを検証
   - Appleの公開鍵を取得してJWT署名を検証
   - Client ID（Bundle ID/Service ID）を確認（iOS/Web両対応）
   - issuerが`https://appleid.apple.com`であることを確認
2. トークン内の`sub`（AppleユーザーID）と`user_id`が一致するか確認
3. `apple_user_id`でユーザーを検索、存在しない場合は新規作成
4. APIトークンを発行して返却

#### 注意事項

- **メール・名前は初回のみ提供される**: Appleは初回ログイン時のみ`email`、`given_name`、`family_name`を提供します。2回目以降のログインではこれらの値は`null`になります。
- **プライベートリレーメール**: ユーザーが「メールを非公開」を選択した場合、`@privaterelay.appleid.com`のメールアドレスが提供されます。
- **user_idの重要性**: `user_id`（Appleが提供する一意識別子）が同じユーザーを識別する唯一の方法です。メールアドレスではなく`user_id`でユーザーを管理します。
- **初回ログイン時のみアカウント作成**: 新規ユーザーの場合、初回ログイン時に自動的にアカウントが作成されます。

---

## トークンの使用方法

発行されたトークンは、以降のAPIリクエストで`Authorization`ヘッダーに含めて使用します。

```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### 例

```bash
curl -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
  https://api.example.com/api/posts/
```

---

## セキュリティ

### Google Sign-in

- Google公式のID Token検証ライブラリを使用
- トークンの有効期限を自動チェック
- 署名検証により改ざんを防止
- 複数のClient ID（iOS/Android）に対応

### Sign in with Apple

- Appleの公開鍵を使用したJWT署名検証
- Client ID（Bundle ID/Service ID）とissuerの厳密な検証
- 複数のClient ID（iOS/Web）に対応
- トークンの有効期限を自動チェック
- 改ざん防止のための暗号学的検証

---

## エラーコード一覧

| HTTPステータス | エラーメッセージ | 説明 |
|----------------|------------------|------|
| 400 | `id_token is required` | Google: ID Tokenが提供されていません |
| 400 | `Email not found in token` | Google: トークンにメールアドレスが含まれていません |
| 400 | `identity_token and user_id are required` | Apple: 必須パラメータが不足しています |
| 401 | `Invalid token: ...` | トークンの検証に失敗しました（無効・期限切れ・改ざん等） |
| 401 | `user_id mismatch` | Apple: トークン内のuser_idとリクエストのuser_idが一致しません |
| 401 | `Failed to fetch Apple public keys: ...` | Apple: 公開鍵の取得に失敗しました |
| 401 | `Public key not found for the given kid` | Apple: トークンのkey IDに対応する公開鍵が見つかりません |

---

## よくある質問

### Q: トークンの有効期限は？

A: 現在、発行されたAPIトークンに有効期限はありません。トークンは明示的に削除されるまで有効です。

### Q: 同じユーザーが複数回ログインした場合は？

A: 既存のトークンが再利用されます。新しいトークンは発行されません。

### Q: GoogleとAppleの両方でログインした場合、同じユーザーとして扱われますか？

A: いいえ。GoogleとAppleは別々のアカウントとして扱われます。メールアドレスが同じでも、別のユーザーアカウントが作成されます。

### Q: Apple Sign-inで2回目のログイン時にメールアドレスが取得できない

A: これは正常な動作です。Appleは初回ログイン時のみメールアドレスと名前を提供します。サーバー側では初回ログイン時に保存したメールアドレスを使用します。

### Q: プライベートリレーメールは通常のメールアドレスと同じように使えますか？

A: はい。`@privaterelay.appleid.com`のメールアドレスは通常のメールアドレスと同様に機能します。ただし、Appleが中継するため、ユーザーが設定で無効化することができます。
