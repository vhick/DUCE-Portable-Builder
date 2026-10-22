# DUCE Portable - Windows Test Checklist

Do this after GitHub Actions succeeds. Do not claim full portability until these tests pass.

1. Extract the downloaded application into `C:\PortableApps\DUCEPortable` (or any writable directory, including an external drive).
2. Run `DUCEPortable.exe`. It must open without a Python installation, administrator permission, driver, installation wizard or registry prompt.
3. Set a recognizable preference, close the app. Check `Data\duce-gui-settings.json` and `Data\duce.log` exist. Check there is **no** new `duce-gui-settings.json` beside the inner EXE in `App\DUCE\GUI\`.
4. If using course exports, confirm exported text files are in `Data\Courses\`.
5. Relaunch and confirm your settings persist. If using the CLI, run `DUCEPortable-CLI.cmd` and check `Data\duce-cli-settings.json`.
6. Move the complete folder to another writable directory and relaunch. Confirm settings follow it. Browser-cookie auto-login may require that you are already logged in on that PC.
7. Close the app and compare user AppData/LocalAppData/ProgramData paths before/after to check for newly written DUCE-specific files. Browser-cookie *reading* is expected. Antivirus/Windows transient traces are outside the scope of the app.
8. Build a newer upstream version, replace only App, Other and root launcher files, and verify Data remains unchanged.
9. Put the complete portable folder inside a PortableApps.com installation and refresh the menu. Confirm app name and upstream original icon appear.
10. Check live login and enrollment **only with your own Udemy account** and current valid coupons. Failed coupon sites or expired tokens are upstream/network issues, not necessarily portability issues.

If Windows SmartScreen warns about a newly compiled, unsigned file, review the GitHub Actions provenance and source before choosing to run. This package is unsigned; do not bypass security controls for an untrusted file.

## If a test fails

- GitHub build error: open Actions, failed run, then the first red step. Save the log.
- Window does not open: check `Data\LauncherLogs\launcher-errors.log` and `Data\duce.log`.
- An upstream code change causes patch rejection: inspect the changed base.py function rather than silently applying a risky fallback.
- Original icon unavailable: packaging intentionally fails rather than substituting a generic icon.
