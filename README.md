# Sheet Music Manager

![Screenshot from 2022-07-25 10-33-40](https://user-images.githubusercontent.com/20556684/180668575-91afa573-df3b-46fb-9b11-ac702db32d69.png)

A Python CLI to manage your sheet music library.

## Install

1. Download and install the package

```
git clone https://github.com/hugomiddeldorp/sheet_music_manager.git
cd sheet_music_manager
pip install .
```

2. Navigate to your sheet music folder
3. Run the command smm

## How to Use

The status bar at the bottom has all the useful commands.

In the search bar, you can type `:q` to quit and `:u` to update the library (_warning_: depending on the size of your library, the update might take a while as it looks up every single file for information on IMSLP)

Once you have loaded all your files, you can move your selection by using the arrows and open the file by pressing Enter.

You can edit an entry by pressing Ctrl-E on the current selection.
