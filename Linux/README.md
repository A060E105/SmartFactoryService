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

# Configuration
This is a smart factory configuration class, This class is a single instance, You can read and write configuration in any process.

## property
| name | return type |
|:---:|:---:|
| version | string |
| mic_1_name | string |
| mic_1_cali | string |
| mic_2_name | string |
| mic_2_cali | string |
| second | int |
| framerate | int |
| samples | int |
| sampwidth | int |
| channels | int |
| with_cut_file | bool |
| save_split_audio | bool |
| port | int |


## methods

### create(self)
```
Description:
    create configuration file content
```

### read(self)
```
Description:
    read configuration file
```

### save(self)
```
Description:
    save configuration to file
```



# All in One structure

## workflow
1. create UI
2. create a thread for the read USB serial port data in a QR Code scanner
3. show QR code in UI
4. hide QR code before recording, or after show 3~5 seconds do it.