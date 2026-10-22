# DUCE True Portable Builder v1.0 (Windows x64)

Builds [Discounted Udemy Course Enroller](https://github.com/techtanic/Discounted-Udemy-Course-Enroller) as a **manual, ZIP-only, PortableApps.com-Menu-compatible portable program**. This is an independent portable build, not the official upstream release.

## What the builder produces

```text
DUCEPortable/
├── DUCEPortable.exe                   <- launch the app here
├── DUCEPortable-CLI.cmd               <- optional command-line interface
├── App/
│   ├── AppInfo/
│   │   ├── appinfo.ini
│   │   ├── appicon.ico                  <- original upstream icon
│   │   ├── appicon.png
│   │   ├── appicon_16.png
│   │   └── appicon_32.png
│   └── DUCE/
│       ├── GUI/DUCE-GUI.exe + _internal/
│       └── CLI/DUCE-CLI.exe + _internal/
├── Data/                              <- your settings and exports, keep on upgrades
└── Other/
    ├── Help/USER-GUIDE.txt
    └── Source/                        <- patched upstream source, AGPL-3.0 license
```

The builder compiles original upstream source on a Windows GitHub-hosted runner, preserving the original upstream `.ico` and complete PyInstaller **onedir** dependencies. It does **not** use the developer's prebuilt EXE.

## How to run the builder (browser only)

1. On GitHub, make a **new empty public repository** such as `DUCE-Portable-Builder`. The new repository is for builder files, **not** a fork of the developer's app. If you prefer private, GitHub Actions may be subject to your account's limits.
2. Extract this builder ZIP on your computer. Upload **all its contents** to the root of your new GitHub repository, including the hidden `.github` folder. In the GitHub web interface choose **Add file → Upload files → Commit changes**.
3. Go to your repository's **Actions** tab. Enable Actions if GitHub prompts you.
4. Click **Build DUCE Portable (Manual)** on the left; choose **Run workflow**. Leave the `upstream_ref` field as **latest** for the most recent stable GitHub Release tag; an exact tag/commit/branch is also supported.
5. Open the completed run and download the **DUCE-Portable-Windows-x64** artifact under **Artifacts**. GitHub wraps its uploaded application ZIP inside another downloaded ZIP; extract that outer ZIP first.
6. Extract the inner `DUCEPortable_vX.Y.Z_Windows_x64.zip`. Open the `DUCEPortable` folder and double-click **DUCEPortable.exe**.
7. Optional: put the whole `DUCEPortable` folder beneath your PortableApps directory. The menu should detect it from `App/AppInfo/appinfo.ini` and the supplied original icons (refresh or restart the menu if needed).

**No Python installation is needed on the computer where you run the finished portable app.** GitHub compiles Python and its dependencies into the program.

## How to upgrade without losing your settings

1. Run the GitHub Action again to build the newer official version.
2. Close DUCE on the Windows PC and create a backup of its existing **Data** folder.
3. Extract the new application ZIP to a temporary location.
4. In the *existing* `DUCEPortable` folder, replace **App**, **Other**, **DUCEPortable.exe** and **DUCEPortable-CLI.cmd** with the corresponding updated files.
5. **Never replace or delete your existing Data folder.** Your settings, exports and logs will remain.
6. Reopen `DUCEPortable.exe`. Sign in again if the Udemy session expired or you've moved to another PC.

**Do not extract the whole new `DUCEPortable` folder over an existing installation with an overwrite-all option**, because that risks replacing the Data contents. Replace only the four items named above.

## Portability design and limits

- Settings (including saved login details if enabled) and program logs use `Data` through a guarded patch of upstream `base.py`.
- Relative output files (`Courses/`, `debug/`, `log.txt`, `error.html`) stay in `Data` because the launcher starts DUCE with `Data` as its working folder.
- Temporary files created through `TEMP` and `TMP` go under `Data/Temp`; known XDG caches go under `Data/Cache`. No installation, driver, service, scheduled task, registry integration, or admin rights are introduced by the builder or launcher.
- **Browser-cookie auto-login intentionally reads the installed browser's existing user profile** using upstream `rookiepy`. It cannot carry the browser's encrypted cookies from one Windows installation to another. The launcher does not overwrite `%APPDATA%`, `%LOCALAPPDATA%` or the actual browser profile because doing so would break this feature.
- Because dependencies and the Windows operating system may create ordinary caches or security logs, **zero host-side traces cannot be guaranteed**. This is an application-data-portable design, not a virtualized sandbox.
- Coupon providers, Udemy authentication, rate limits, and API responses are controlled externally. A successful build does not prove that live enrollment still works.
- If you choose to save a Udemy email/password, the upstream settings may contain those credentials in **plaintext JSON** under `Data`. Use a trusted/encrypted drive, or disable saving the password. Browser cookie extraction itself is sensitive.
- The automation respects nothing automatically: it is **manual only**. It does not start enrollment on its own, auto-register accounts, or run scheduled tasks.

## Builder checks

- Validates and stops on unrecognized upstream data path function changes.
- Checks Python syntax and simple direct Windows profile-write patterns.
- Confirms original icon (not generic), PortableApps metadata and program files.
- Includes the full patched upstream source under `Other/Source` and respects its AGPL-3.0 license notice.
- Runs the root portable launcher in `--self-test` mode to check its directory layout and `Data` folder permissions without logging in or enrolling.
- Pins Python 3.11 / PyInstaller 6.16.0 / Pillow 11.3.0 for reproducible build tooling; application requirements are installed from the selected upstream source version.

**Validation status:** builder scripts can be syntax and layout checked independently, but the Windows executable cannot be fully executed on a Linux-only authoring environment. Run the GitHub Action, then test the finished program on a Windows machine before treating portability as verified.

## License and attribution

Original application: © techtanic and contributors; [AGPL-3.0](https://github.com/techtanic/Discounted-Udemy-Course-Enroller/blob/master/LICENSE). Original icon: upstream `extra/DUCE-LOGO.ico`. This distribution does not claim official endorsement. The generated package includes the patched application source and the launcher source to facilitate AGPL compliance; comply with all source and attribution duties when redistributing.
