# SmartFactory
## markbook
[Configuration](#Configuration)

[User Interface](#user-interface)

# pyarmor

第一次先使用這個指令來產生`pytransform`這個資料夾：
```bash
$ pyarmor obfuscate <filename>
```

每個.py檔都執行過一次下方這個指令，以防止多線程找不到模組的問題
```bash
$ pyarmor obfuscate --restrict 1 --exact --no-runtime <filename>
```

# Version

## 2.5.0
新增功能：
* 錄音完成後先將 wav 轉成 mp3 ，再將 mp3 轉回 wav ，並覆蓋之前的 wav 檔。

## 2.4.3
新增功能：
* 顯示每張圖片的 density 和 thresholds 。

## 2.4.2
新增功能：
* 可於設定檔中設定 AI 分析的 density 和 thresholds 的數值。

## 2.4.1
新增功能：
* 可於設定檔中設定 Spectrogram 中的 vmin 和 vmax 數值。

修復問題：
* AI 分析中，抓不到正確圖片路徑的問題。

## 2.4.0
新增功能：
* 使用新的模型架構(KDE model)。

## 2.3.7
新增功能：
* 將麥克風預設輸入音量調整至 80% 。
* 可於設定檔中設定 Spectrogram 中的 hopsize 數值。

## 2.3.6
新增功能：
* 使用 `nircmdc.exe` 來設定麥克風輸入音量。

## 2.3.5
新增功能：
* 設定麥克風輸入音量。

## 2.3.3
新增功能：
* 可於設定檔中設定 picture_width, picture_height, freq_split_list 和 binsize 的數值。

## 2.3.2
修復問題：
* 錯誤訊息的編碼

## 2.3.1
新增功能：
* 取得麥克風校正值會同時拿到舊的校正值與新的校正值

## 2.3.0
新增功能：
* 麥克風校正 API 拆分成兩隻
    * 取得麥克風校正值
    * 設定麥克風校正值
* window_client_ui 麥克風校正後會詢問是否儲存該校正值

## 2.2.0
新增功能：
* 錄音時間調整
* 麥克風校正前先做 A-weighting 處理

## 1.4.2
新增功能：
* 修改掛載行動硬碟方式。

## 1.4.1
新增功能：
* 錄音出現錯誤時會拋出例外處理，並回傳麥克風錯誤的代碼。

## 1.4.0
新增功能：
* 啟動程式時自動掛載行動硬碟，若掛載失敗將跳出錯誤提醒。

## 1.3.5
新增功能：
* 移除另外儲存cali音檔功能

修復問題：
* 麥克風校正數值不正確

## 1.3.4
新增功能：
* 儲存cali音檔

修復問題：
* 聲音太小是因為做了麥克風校正，為了比對便將校正前後的音檔個別儲存，有校正的音檔名稱後面會加上cali。


## 1.3.2
新增功能：
* 使用設定檔來設定delay時間


## 1.3.1
新增功能：
* 增加delay時間


## 1.3.0
新增功能：
* 顯示錯誤訊息
* 顯示分析結果
* 新增CSV檔的資料夾
* 將分析完的音檔備份至同CSV檔名的資料夾內，裡面有NG/OK資料夾，會依據分析結果進行備份。
