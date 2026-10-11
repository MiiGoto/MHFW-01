# MHFW-01 — Virtual Horizontal Flow Wrapper Rev A

Windows上で動く独立した横型ピロー包装機の仮想制御環境です。
**ST → MatIEC → native DLL → Beremiz runtime → 実UDP I/O → Python機械モデル**。
PythonでPLCロジックを代用していません。購入費用0円、実機出力なし。

## 起動

Windows x64のPowerShellで、リポジトリをcloneして無料ツールを取得します:

```powershell
git clone https://github.com/MiiGoto/MHFW-01.git
cd MHFW-01
.\scripts\setup.ps1
.\scripts\start_all.ps1
```

ブラウザで <http://127.0.0.1:8080> を開き、PLC I/O CONNECTED を確認して START。
必要なら RESET ALARM → START。STOPはPAUSEに入ります。
10× simulationを使う場合は停止中にチェックするか、起動時に `-Accelerated`。
停止は `scripts/stop_all.ps1`。プロセスの自動再起動・次Phaseの自動開始はありません。

## 個別起動・編集・試験

1. `scripts/build_plc.ps1` — STからPLCopenを生成し、Beremiz CLIでネイティブビルド。
2. 別のPowerShellで `scripts/start_plc.ps1` — LOCAL runtime起動、転送、実行。
3. さらに別のPowerShellで `scripts/start_simulation.ps1` — Python/HMI起動。
4. 終了時はHMIでSTOP後、各端末でCtrl+C。
5. `scripts/open_plc_ide.ps1` — 同じPLCopenプロジェクトをBeremiz IDEで開く。

試験はHMIを終了し、PLCだけ動かして `scripts/run_tests.ps1`。
PLCと機械の結合試験は実runtimeへのUDP通信を必須とし、Python単体試験とログを分離します。
試験のcold resetは仮想バッチ専用です。HMIにはcold-reset操作を公開していません。

新しいPCでは `scripts/setup.ps1` で公式無料アーカイブを取得・展開してからビルドします。
ネット接続、Windows x64、数GBの空き容量が必要です。管理者インストールは不要。
実行ポリシーで拒否された場合は、その組織/PCのポリシーに従って実行してください。
このプロジェクトはポリシーやファイアウォールの設定を変更しません。

## 操作とモデル

- AUTO / MANUAL連続ジョグ / SINGLE CYCLE、停止PAUSE、異常FAULT。
- 製品60×40×15 mm、袋120 mm、5～10 packs/minが初期値。
- レシピは停止中に変更。適用すると仮想バッチ・カウンタを初期化します。
- 動くコンベヤ、製品、フィルムロール/送り、フォーマー、センターシール、エンドジョー、カッター、排出、製品センサを表示。
- 包装完了した製品は青緑のフィルム袋とシール線で区別します。
- 異常原因を解除 → RESET → 新しいSTART。原因が残ればRESETを拒否します。
- 包装イベントは `logs/session.jsonl`。PLCカウンタはバッチ内の値で、電源断保持は未実装。

検証結果・A～J対応は [docs/virtual_commissioning.md](docs/virtual_commissioning.md)。
構成・I/O・同期制御・将来の実機移行は `docs/` を参照。

熱伝達、フィルムの実変形、シール強度、食品衛生、実機安全認証は検証対象外です。
PCのソフト停止は実機の安全認証済み非常停止ではありません。
参照: [フジキカイ公開製品情報](https://www.fujikikai-inc.co.jp/products)、[Beremiz公式](https://beremiz.org/)。
公開情報から機能段階のみを参考にした独立設計で、企業図面・内部仕様は使用していません。

公開用リポジトリの作成経緯・検証範囲は [docs/publication.md](docs/publication.md) を参照。
