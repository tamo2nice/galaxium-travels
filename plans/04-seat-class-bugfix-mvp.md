# 座席クラス機能完成 - MVP カード

## 📋 現状分析

### ターゲットユーザー
- **開発チーム**: テストを実行し、コードの品質を保証する
- **運用チーム**: 本番環境にデプロイし、システムを監視する
- **エンドユーザー**: 正確な価格と在庫情報で予約を行う

### 現在の課題
1. **テストの失敗**: バックエンドテストのフィクスチャが座席クラスフィールド（`economy_seats`, `business_seats`, `galaxium_seats`, `economy_price`, `business_price`, `galaxium_price`）を含んでいない
2. **在庫の不整合**: シードデータで予約を作成する際、該当する座席クラスの在庫を減らしていない
3. **UI表示の誤り**: フロントエンドの予約履歴で、Business/Galaxium予約が`price_paid`ではなくレガシーの`economy`価格を表示している

### 望ましい結果
- 全テストが成功する（100%パス率）
- デモデータの在庫数が予約数と正確に一致する
- ユーザーが予約履歴で正しい支払額を確認できる
- 本番環境にデプロイ可能な状態

### 制約
- 既存の機能を壊さない（後方互換性維持）
- データベーススキーマは変更しない（既に実装済み）
- 新機能は追加しない（バグ修正のみ）

---

## 🎯 MVP カード

### Goal
座席クラス機能を本番環境で安全に使用できるよう、3つの既知の問題を解決する

### User
- **開発チーム**: 信頼できるテストスイートで開発を継続したい
- **運用チーム**: 本番環境にデプロイできる安定したシステムが必要
- **エンドユーザー**: 正確な価格情報で予約を確認したい

### Pain
- **テスト失敗**: 座席クラスフィールドがないため、`Flight`と`Booking`のフィクスチャでテストが失敗する
- **在庫不整合**: シードデータの予約が在庫を減らさないため、デモが不正確で信頼性が低い
- **価格表示エラー**: UIが間違った価格を表示し、ユーザーを混乱させ、信頼を損なう

### In Scope
1. **バックエンドテストフィクスチャの更新**
   - `conftest.py`の`sample_flight_data`に座席クラスフィールドを追加
   - `sample_booking_data`に`seat_class`フィールドを追加
   - 全テストファイルで座席クラスフィールドを使用するよう更新

2. **シードデータの在庫管理修正**
   - `seed.py`で予約作成時に該当座席クラスの在庫を減算
   - 在庫が負にならないよう検証ロジックを追加
   - シード実行後の在庫数を検証

3. **フロントエンドUI価格表示の修正**
   - `BookingCard.tsx`で`price_paid`フィールドを使用
   - レガシーのeconomy価格フォールバックを削除
   - 座席クラス情報を表示に追加

4. **検証とドキュメント更新**
   - 全テストの実行と成功確認
   - README.mdから「Current Known Issues」セクションを削除
   - 変更内容をAGENTS.mdに記録

### Out of Scope
- 新機能の追加（座席クラスフィルタリング、アップグレード機能など）
- UIデザインの大幅な変更
- パフォーマンス最適化
- 追加の座席クラスの導入
- データベーススキーマの変更
- 既存APIエンドポイントの変更

---

## 📝 Top 5 ユーザーストーリー

### 1. テストフィクスチャの更新
**As a** バックエンド開発者  
**I want** 座席クラスフィールドを含む正しいテストフィクスチャ  
**So that** 全テストが成功し、コードの品質を保証できる

**Done when**:
- `conftest.py`の`sample_flight_data`が全座席クラスフィールドを含む
- `sample_booking_data`が`seat_class`フィールドを含む
- `pytest`が警告なしで100%成功する
- テストカバレッジが維持される

**Acceptance Criteria**:
```python
# sample_flight_data に以下が含まれる:
economy_seats, business_seats, galaxium_seats
economy_price, business_price, galaxium_price

# sample_booking_data に以下が含まれる:
seat_class: "economy" | "business" | "galaxium"
```

---

### 2. シード在庫管理の修正
**As a** システム管理者  
**I want** シードデータが正確な在庫数を反映する  
**So that** デモ環境が実際の動作を正しく示す

**Done when**:
- 予約作成時に該当座席クラスの在庫が減る
- 在庫が負にならない検証ロジックが動作する
- シード実行後、在庫数 = 初期値 - 予約数
- デモデータの整合性が保証される

**Acceptance Criteria**:
```python
# seed.py で予約作成時:
if seat_class == "economy":
    flight.economy_seats -= 1
elif seat_class == "business":
    flight.business_seats -= 1
elif seat_class == "galaxium":
    flight.galaxium_seats -= 1

# 在庫が0未満にならないことを確認
assert flight.economy_seats >= 0
```

---

### 3. UI価格表示の修正
**As a** エンドユーザー  
**I want** 予約履歴で実際に支払った金額を確認したい  
**So that** 自分の予約内容を正確に把握できる

**Done when**:
- `BookingCard.tsx`が`booking.price_paid`を表示
- Business/Galaxium予約が正しい価格を表示
- レガシーのeconomy価格フォールバックが削除される
- 座席クラス情報が表示される

**Acceptance Criteria**:
```typescript
// BookingCard.tsx で:
<div>Price: {formatCurrency(booking.price_paid)}</div>
<div>Class: {booking.seat_class}</div>

// レガシーコードを削除:
// ❌ flight?.price (economy fallback)
// ✅ booking.price_paid
```

---

### 4. テスト実行と検証
**As a** 品質保証エンジニア  
**I want** 全テストが成功することを確認したい  
**So that** 本番環境へのデプロイが安全であることを保証できる

**Done when**:
- `pytest`が全テスト成功（0 failed）
- `npm run build`がエラーなしで完了
- 手動テストで3つの座席クラスが正しく動作
- 既存機能が壊れていないことを確認

**Acceptance Criteria**:
```bash
# バックエンド
cd booking_system_backend
pytest  # 全テスト成功

# フロントエンド
cd booking_system_frontend
npm run build  # ビルド成功
```

---

### 5. ドキュメント更新
**As a** プロジェクトマネージャー  
**I want** ドキュメントが最新状態であることを確認したい  
**So that** チームが正確な情報に基づいて作業できる

**Done when**:
- README.mdから「Current Known Issues」セクションが削除される
- AGENTS.mdに修正内容が記録される
- 変更履歴が明確に文書化される
- 次の開発者が問題なく作業を継続できる

**Acceptance Criteria**:
```markdown
# README.md から削除:
### Current Known Issues
- Backend tests still contain fixtures...
- Seed data can create bookings...
- Booking history UI can still show...

# AGENTS.md に追加:
## 2026-04-18: 座席クラス機能完成
- テストフィクスチャ更新
- シード在庫管理修正
- UI価格表示修正
```

---

## 📊 成功指標

### Primary Metric
**テスト成功率**: 100%（現在は座席クラス関連で失敗）

**測定方法**:
```bash
pytest --tb=short
# Expected: X passed, 0 failed
```

### Secondary Metrics
1. **在庫整合性**: 100%
   - 測定: シード実行後、全フライトで `初期在庫 - 予約数 = 現在在庫`
   
2. **UI価格表示正確性**: 100%
   - 測定: 全予約カードで `表示価格 === booking.price_paid`

3. **ビルド成功率**: 100%
   - 測定: `npm run build` がエラーなしで完了

### Guardrail Metrics
- **既存機能の動作**: 100%（後方互換性維持）
- **API レスポンス時間**: 変化なし（パフォーマンス劣化なし）
- **データベース整合性**: 100%（データ破損なし）

---

## ⚠️ リスク & 未解決の質問

### Technical Risks
1. **テスト修正時のロジック破壊**
   - **リスク**: 既存のテストロジックを誤って変更する可能性
   - **軽減策**: 変更前に全テストを実行し、ベースラインを確立
   - **影響**: Medium
   - **確率**: Low

2. **シード在庫管理の副作用**
   - **リスク**: 在庫減算ロジックが既存データに予期しない影響を与える
   - **軽減策**: テスト環境で十分に検証してから本番適用
   - **影響**: Medium
   - **確率**: Low

3. **UI変更によるレイアウト崩れ**
   - **リスク**: 価格表示の変更が他のUI要素に影響する
   - **軽減策**: ブラウザテストで視覚的に確認
   - **影響**: Low
   - **確率**: Very Low

### Business Risks
1. **デプロイ遅延**
   - **リスク**: 修正に予想以上の時間がかかる
   - **軽減策**: タイムボックスを設定（最大4時間）
   - **影響**: Low
   - **確率**: Low

### Unresolved Questions
1. **既存の本番データベースは存在するか？**
   - **重要度**: High
   - **影響**: マイグレーション戦略の決定に必要
   - **回答期限**: 実装開始前

2. **テスト修正の優先順位は？**
   - **重要度**: Medium
   - **オプション**: 
     - A) services → REST → 統合
     - B) 失敗しているテストから順に
   - **推奨**: B（失敗しているテストから）

3. **シードデータの予約数は調整すべきか？**
   - **重要度**: Low
   - **現状**: 20件の予約
   - **検討**: 在庫不足を避けるため減らすべきか？

---

## 📅 実装計画

### Phase 1: バックエンド修正（1-2時間）
1. テストフィクスチャの更新（30分）
2. シード在庫管理の修正（45分）
3. バックエンドテストの実行と検証（15分）

### Phase 2: フロントエンド修正（30分-1時間）
1. BookingCard.tsx の価格表示修正（20分）
2. 型定義の確認（10分）
3. ビルドテストと視覚確認（20分）

### Phase 3: 統合テストとドキュメント（30分）
1. エンドツーエンドテスト（15分）
2. ドキュメント更新（10分）
3. 最終レビュー（5分）

**総所要時間**: 2-4時間

---

## ✅ 完了条件（Definition of Done）

- [ ] 全バックエンドテストが成功（pytest 100%）
- [ ] フロントエンドビルドが成功（npm run build）
- [ ] シードデータの在庫数が予約数と一致
- [ ] 予約履歴UIが正しい価格を表示
- [ ] README.mdから既知の問題セクションが削除
- [ ] AGENTS.mdに変更内容が記録
- [ ] コードレビュー完了
- [ ] 本番環境デプロイ準備完了

---

## 🔄 次のステップ

このMVPが完了したら、以下の機能開発に進むことができます：

1. **座席クラスフィルタリング** - ユーザーが希望する座席クラスでフライトを絞り込む
2. **予約確認メール** - 予約完了時に確認メールを送信
3. **管理者ダッシュボード** - フライトと予約を管理するUI
4. **決済統合** - 実際の支払い処理を実装

---

**作成日**: 2026-04-18  
**優先度**: Critical  
**所要時間**: 2-4時間  
**依存関係**: なし（独立して実装可能）