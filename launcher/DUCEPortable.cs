using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;

// Small .NET Framework launcher. No .NET SDK/runtime download needed on a
// normal Windows 10/11 machine with .NET Framework 4.x enabled.
// Launches the original DUCE application without modifying browser profiles.
class DUCEPortableLauncher
{
    [STAThread]
    static int Main(string[] args)
    {
        string root = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        string guiExe = Path.Combine(root, @"App\DUCE\GUI\DUCE-GUI.exe");
        string cliExe = Path.Combine(root, @"App\DUCE\CLI\DUCE-CLI.exe");
        string data = Path.Combine(root, "Data");
        string logDir = Path.Combine(data, "LauncherLogs");
        bool cli = args.Length > 0 && (args[0].Equals("--cli", StringComparison.OrdinalIgnoreCase));
        bool selfTest = args.Length > 0 && args[0].Equals("--self-test", StringComparison.OrdinalIgnoreCase);
        string target = cli ? cliExe : guiExe;

        try
        {
            if (!File.Exists(guiExe) || !File.Exists(cliExe))
                throw new FileNotFoundException("A DUCE program file is missing. Extract the complete portable ZIP, including App and its subfolders.");
            if (!File.Exists(Path.Combine(root, @"App\AppInfo\appinfo.ini")))
                throw new FileNotFoundException("PortableApps metadata is missing. Extract the full ZIP.");
            Directory.CreateDirectory(data);
            Directory.CreateDirectory(logDir);
            Directory.CreateDirectory(Path.Combine(data, "Temp"));
            Directory.CreateDirectory(Path.Combine(data, "Cache"));

            // For CI verification; doesn't open the application or access Udemy.
            if (selfTest)
            {
                File.WriteAllText(Path.Combine(logDir, "self-test.txt"), "Portable launcher files and writable Data directory OK" + Environment.NewLine);
                return 0;
            }

            ProcessStartInfo start = new ProcessStartInfo(target);
            start.UseShellExecute = false;
            start.WorkingDirectory = data;   // Relative log.txt, Courses, debug and error.html stay in Data.
            start.EnvironmentVariables["DUCE_PORTABLE_DATA_DIR"] = data;
            start.EnvironmentVariables["TEMP"] = Path.Combine(data, "Temp");
            start.EnvironmentVariables["TMP"] = Path.Combine(data, "Temp");
            start.EnvironmentVariables["XDG_CACHE_HOME"] = Path.Combine(data, "Cache");
            start.EnvironmentVariables["PYTHONNOUSERSITE"] = "1";
            if (cli && args.Length > 1)
            {
                StringBuilder passed = new StringBuilder();
                for (int i = 1; i < args.Length; i++)
                {
                    if (passed.Length > 0) passed.Append(" ");
                    passed.Append(QuoteArg(args[i]));
                }
                start.Arguments = passed.ToString();
            }

            using (Process p = Process.Start(start))
            {
                if (p == null) throw new Exception("Windows did not launch DUCE.");
                p.WaitForExit();
                return p.ExitCode;
            }
        }
        catch (Exception ex)
        {
            try
            {
                Directory.CreateDirectory(logDir);
                File.AppendAllText(Path.Combine(logDir, "launcher-errors.log"), DateTime.Now.ToString("s") + "  " + ex + Environment.NewLine);
            }
            catch { /* The intended drive may be read-only or disconnected. */ }
            MessageBox.Show(ex.Message, "DUCE Portable - Launch error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    // Windows-compatible quoting of command-line arguments.
    private static string QuoteArg(string arg)
    {
        if (arg.Length > 0 && arg.IndexOfAny(new char[] { ' ', '\t', '"' }) < 0) return arg;
        StringBuilder sb = new StringBuilder("\"");
        int backslashes = 0;
        foreach (char c in arg)
        {
            if (c == '\\') { backslashes++; continue; }
            if (c == '"')
            {
                sb.Append('\\', backslashes * 2 + 1);
                sb.Append('"');
                backslashes = 0;
                continue;
            }
            sb.Append('\\', backslashes);
            backslashes = 0;
            sb.Append(c);
        }
        sb.Append('\\', backslashes * 2);
        sb.Append('"');
        return sb.ToString();
    }
}
