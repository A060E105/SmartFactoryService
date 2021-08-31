# SmartFactory
## markbook
[Configuration](#Configuration)

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