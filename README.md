# Spring-Dash-Mod-Manager
A mod manager for Spring Dash

---

## How To Use the manager
- to use the software create a folder on the root of Spring Dash called "mods"
- inside this folder place any mods (make sure to maintain the name for example Mods/Easy-Snow/... and not have it be Mods/...)
- Run the program and click yes when steam asks to run with a modified pck

---

## How to use the developer tool
- on the first run it will recover the game project to a folder called "game-files" to be used with Godot v4.1.3 and generate a checksum with the original files
- this can be opened with said Godot version and edited however you please
- the next time you run the script it will compare the new files with the old ones and make your mod with the name developer-mod which can be used with the mod manager by moving it into the mods folder

---

## How it works
- the program takes all the mods in your mods folder and combines them into a folder called pak
- using GDRE tools this folder is patched into Spring Dash's pck file
- the game is launched using the modified pck as opposed to the original one

---

## Credits

This project uses portions of [GDRETools/gdsdecomp](https://github.com/GDRETools/gdsdecomp), created and maintained by @nikitalita and contributors, under the MIT License.
