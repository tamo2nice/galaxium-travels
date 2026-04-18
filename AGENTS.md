# AGENTS.md

このファイルは、このリポジトリでコードを扱う際のエージェント向けガイダンスを提供します。

## 変更履歴

### 2026-04-18: 座席クラス機能完成
**目的**: 座席クラス機能の3つの既知の問題を解決し、本番環境で安全に使用できるようにする

**実施した変更**:
1. **テストフィクスチャの更新**
   - `conftest.py`の`sample_flight_data`に座席クラスフィールド（`economy_price`, `business_price`, `galaxium_price`, `economy_seats`, `business_seats`, `galaxium_seats`）を追加
   - `sample_booking_data`に`seat_class`フィールドを追加
   - `test_services.py`と`test_rest.py`の全`Flight`および`Booking`オブジェクト作成箇所を更新

2. **シード在庫管理の修正**
   - `seed.py`で予約作成時に該当座席クラスの在庫を減算するロジックを追加
   - 在庫がある座席クラスのみから選択するよう修正
   - `status == "booked"`の場合のみ在庫を減らすよう条件分岐を追加

3. **フロントエンドUI価格表示の修正**
   - `BookingCard.tsx`で`flight.price`（レガシーのeconomy価格）から`booking.price_paid`（実際の支払額）に変更
   - 座席クラス情報の表示を追加（`Armchair`アイコンと座席クラス名）
   - `getSeatClassDisplay()`ヘルパー関数を使用

4. **ドキュメント更新**
   - README.mdから「Current Known Issues」セクションを削除
   - AGENTS.mdに本変更履歴を追加

**結果**:
- 全バックエンドテスト成功（29 passed, 0 failed）
- 座席クラス機能が本番環境デプロイ可能な状態に到達
- 在庫管理の整合性が保証される
- ユーザーが正確な価格情報を確認できる

## 重要な非標準パターン

### バックエンド (booking_system_backend/)
- **MCP サーバーは FastAPI アプリの前に作成必須**: `server.py` で MCP インスタンスを FastAPI より先に作成しないとライフサイクルの結合が失敗する
- **テストは monkeypatch で SessionLocal を上書き**: `conftest.py` で `db_module.SessionLocal` と `server.SessionLocal` の両方をパッチする必要がある
- **booking.book_flight() は name パラメータで検証**: user_id だけでなく name も必須で、DB の name と一致しない場合は NAME_MISMATCH エラーを返す
- **ErrorResponse は Union 型で返却**: サービス層の関数は `BookingOut | ErrorResponse` を返すため、呼び出し側で型チェックが必要
- **datetime は ISO 文字列として保存**: `booking_time` は `datetime.utcnow().isoformat()` で文字列として保存（SQLite の制約）

### フロントエンド (booking_system_frontend/)
- **API エラーは interceptor で ErrorResponse に変換**: axios interceptor がネットワークエラーを `ErrorResponse` 型に統一する
- **isErrorResponse() でレスポンス判定**: API レスポンスが成功かエラーかを `success === false` で判定するヘルパー関数を使用
- **型定義は snake_case**: バックエンドの Python スキーマに合わせて `flight_id`, `user_id` など snake_case を使用（TypeScript の慣例に反する）

## テスト実行

### バックエンド単体テスト
```bash
cd booking_system_backend
pytest                    # 全テスト実行
pytest tests/test_services.py  # サービス層のみ
pytest tests/test_rest.py      # REST API のみ
```

### フロントエンドビルド検証
```bash
cd booking_system_frontend
npm run build            # TypeScript コンパイル + Vite ビルド