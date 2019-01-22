# Python TitanGUI

A python based GUI for the CLI password manager Titan

## Requirements

The following librairies are required for the script to work :

+ pexpect
+ pyperclip

You can install them with these commands
```shell
python3.7 -m pip install pexpect
python3.7 -m pip install pyperclip 
```
This script also requires to have an existing Titan's password file

**Very Important**

Before using this script the following line of the script must be editted to match the absolute path of the Titan's password file

```python
DB_PATH: str = "/home/user/password_file"
```

## Usage

```shell
python3.7 TitanGUI.py
```


