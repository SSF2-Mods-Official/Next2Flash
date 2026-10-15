package next2flash.ffdec;

import com.jpexs.decompiler.flash.console.CommandLineArgumentParser;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * Long-lived FFDec CLI worker (GPLv3). Keeps one JVM warm and runs successive
 * CommandLineArgumentParser commands from stdin so a caller avoids
 * ~1s+ JVM startup per call.
 *
 * Protocol (UTF-8, one command per line):
 *   READY          — worker greeting on startup
 *   PING           — replies PONG
 *   EXIT / QUIT    — replies BYE and exits
 *   &lt;ffdec args&gt;   — same argv as {@code java -jar ffdec.jar …}
 *                    replies OK or ERR &lt;message&gt;
 */
public final class FfdecWorker {
    private FfdecWorker() {}

    public static void main(String[] args) throws Exception {
        System.setProperty("java.awt.headless", "true");
        System.setProperty("java.net.preferIPv4Stack", "true");
        mirrorStartupProperties();
        setToolProperty("worker", "true");

        PrintStream ctrl = System.out;
        BufferedReader in = new BufferedReader(
            new InputStreamReader(System.in, StandardCharsets.UTF_8));

        ctrl.println("READY");
        ctrl.flush();

        String line;
        while ((line = in.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) {
                continue;
            }
            if (line.equalsIgnoreCase("PING")) {
                ctrl.println("PONG");
                ctrl.flush();
                continue;
            }
            if (line.equalsIgnoreCase("EXIT") || line.equalsIgnoreCase("QUIT")) {
                ctrl.println("BYE");
                ctrl.flush();
                break;
            }

            String[] cmdArgs;
            try {
                cmdArgs = splitArgs(line);
            } catch (IllegalArgumentException ex) {
                ctrl.println("ERR bad-args " + sanitize(ex.getMessage()));
                ctrl.flush();
                continue;
            }

            ByteArrayOutputStream sink = new ByteArrayOutputStream();
            PrintStream capture = new PrintStream(sink, true, StandardCharsets.UTF_8);
            PrintStream prevOut = System.out;
            PrintStream prevErr = System.err;
            System.setOut(capture);
            System.setErr(capture);
            try {
                if (cmdArgs.length >= 3 && "-identdump".equalsIgnoreCase(cmdArgs[0])) {
                    IdentClone.dump(cmdArgs[1], cmdArgs[2]);
                } else if (cmdArgs.length >= 4 && "-identrewrite".equalsIgnoreCase(cmdArgs[0])) {
                    IdentClone.rewrite(cmdArgs[1], cmdArgs[2], cmdArgs[3]);
                } else if (cmdArgs.length >= 3 && "-untypestance".equalsIgnoreCase(cmdArgs[0])) {
                    UntypeStance.run(cmdArgs[1], cmdArgs[2]);
                } else if (cmdArgs.length >= 3 && "-placeedit".equalsIgnoreCase(cmdArgs[0])) {
                    PlaceEdit.run(cmdArgs[1], cmdArgs[2]);
                } else {
                    cmdArgs = applyToolDashD(cmdArgs);
                    CommandLineArgumentParser.parseArguments(cmdArgs);
                }
                ctrl.println("OK");
            } catch (SecurityException se) {
                String msg = se.getMessage() == null ? "" : se.getMessage();
                if (msg.startsWith("blocked-exit:0")) {
                    ctrl.println("OK");
                } else if (msg.startsWith("blocked-exit:")) {
                    ctrl.println("ERR exit-" + msg.substring("blocked-exit:".length()));
                } else {
                    ctrl.println("ERR " + sanitize(msg));
                }
            } catch (Throwable t) {
                ctrl.println("ERR " + sanitize(t.toString()));
            } finally {
                System.setOut(prevOut);
                System.setErr(prevErr);
                capture.close();
                String captured = sink.toString(StandardCharsets.UTF_8);
                for (String xflLine : captured.split("\r?\n")) {
                    if (xflLine.contains("[XFL]"))
                        prevErr.println(xflLine);
                }
            }
            ctrl.flush();
        }
    }

    /** Minimal shell-style splitter supporting double quotes. */
    static String[] splitArgs(String line) {
        List<String> out = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean inQuote = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == '"') {
                inQuote = !inQuote;
                continue;
            }
            if (!inQuote && Character.isWhitespace(c)) {
                if (cur.length() > 0) {
                    out.add(cur.toString());
                    cur.setLength(0);
                }
                continue;
            }
            cur.append(c);
        }
        if (inQuote) {
            throw new IllegalArgumentException("unclosed quote");
        }
        if (cur.length() > 0) {
            out.add(cur.toString());
        }
        return out.toArray(new String[0]);
    }

    static final String PROP_PREFIX = "n2f.";
    /** Older callers and the patched FFDec library still use this prefix. */
    static final String LEGACY_PROP_PREFIX = "ssf2mm.";

    static void setToolProperty(String key, String value) {
        System.setProperty(PROP_PREFIX + key, value);
        System.setProperty(LEGACY_PROP_PREFIX + key, value);
    }

    static void mirrorStartupProperties() {
        for (String name : System.getProperties().stringPropertyNames()) {
            String key = toolKey(name);
            if (key != null) {
                setToolProperty(key, System.getProperty(name));
            }
        }
    }

    static String toolKey(String name) {
        if (name.startsWith(PROP_PREFIX)) {
            return name.substring(PROP_PREFIX.length());
        }
        if (name.startsWith(LEGACY_PROP_PREFIX)) {
            return name.substring(LEGACY_PROP_PREFIX.length());
        }
        return null;
    }

    static String[] applyToolDashD(String[] args) {
        List<String> out = new ArrayList<>();
        for (String a : args) {
            int eq = a.indexOf('=');
            String key = a.startsWith("-D") && eq > 2 ? toolKey(a.substring(2, eq)) : null;
            if (key != null && !key.isEmpty()) {
                setToolProperty(key, a.substring(eq + 1));
            } else {
                out.add(a);
            }
        }
        return out.toArray(new String[0]);
    }

    private static String sanitize(String s) {
        if (s == null) {
            return "";
        }
        return s.replace('\r', ' ').replace('\n', ' ');
    }
}
