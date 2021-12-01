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
