using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows.Forms;

static class Program
{
    [STAThread]
    static void Main(string[] args)
    {
        string baseDir = AppDomain.CurrentDomain.BaseDirectory;
        string runtime = Path.Combine(baseDir, "runtime");
        string exe = Path.Combine(runtime, "Next2Flash.exe");
        if (!File.Exists(exe))
        {
            MessageBox.Show(
                "Could not find runtime\\Next2Flash.exe next to this launcher.",
                "Next2Flash",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error);
            return;
        }

        var start = new ProcessStartInfo();
        start.FileName = exe;
        start.WorkingDirectory = runtime;
        start.UseShellExecute = false;
        start.Arguments = QuoteArgs(args);
        Process.Start(start);
    }

    static string QuoteArgs(string[] args)
    {
        var builder = new StringBuilder();
        foreach (string arg in args)
        {
            if (builder.Length > 0)
                builder.Append(' ');
            builder.Append(Quote(arg));
        }
        return builder.ToString();
    }

    static string Quote(string value)
    {
        if (value.IndexOfAny(new char[] { ' ', '\t', '"' }) < 0)
            return value;
        return "\"" + value.Replace("\"", "\\\"") + "\"";
    }
}
