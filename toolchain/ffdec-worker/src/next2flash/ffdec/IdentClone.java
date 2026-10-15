package next2flash.ffdec;

import com.jpexs.decompiler.flash.ReadOnlyTagList;
import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.abc.ABC;
import com.jpexs.decompiler.flash.abc.avm2.AVM2ConstantPool;
import com.jpexs.decompiler.flash.configuration.Configuration;
import com.jpexs.decompiler.flash.tags.DefineEditTextTag;
import com.jpexs.decompiler.flash.tags.DefineSpriteTag;
import com.jpexs.decompiler.flash.tags.ExportAssetsTag;
import com.jpexs.decompiler.flash.tags.FrameLabelTag;
import com.jpexs.decompiler.flash.tags.SymbolClassTag;
import com.jpexs.decompiler.flash.tags.Tag;
import com.jpexs.decompiler.flash.tags.ABCContainerTag;
import com.jpexs.decompiler.flash.tags.base.PlaceObjectTypeTag;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * In-memory identifier dump/rewrite for cloned symbols. Avoids FFDec's
 * full SWF XML round-trip (tens of MB of shape records).
 */
public final class IdentClone {
    private IdentClone() {}

    public static void dump(String swfPath, String outPath) throws Exception {
        disableHeavyFfdecWork();
        try (FileInputStream in = new FileInputStream(swfPath)) {
            SWF swf = openSwf(in);
            Set<String> symbols = new LinkedHashSet<>();
            StringBuilder abcItems = new StringBuilder();
            walk(swf.getTags(), tag -> {
                if (tag instanceof SymbolClassTag) {
                    for (String name : ((SymbolClassTag) tag).names) {
                        if (name != null && !name.isEmpty()) {
                            symbols.add(name);
                        }
                    }
                } else if (tag instanceof ExportAssetsTag) {
                    for (String name : ((ExportAssetsTag) tag).names) {
                        if (name != null && !name.isEmpty()) {
                            symbols.add(name);
                        }
                    }
                } else if (tag instanceof ABCContainerTag) {
                    ABC abc = ((ABCContainerTag) tag).getABC();
                    if (abc == null || abc.constants == null) {
                        return;
                    }
                    AVM2ConstantPool pool = abc.constants;
                    for (int i = 1; i < pool.getStringCount(); i++) {
                        String s = pool.getString(i);
                        if (s != null && s.length() <= 256 && s.indexOf('\n') < 0) {
                            abcItems.append("<item>").append(xmlEscape(s)).append("</item>");
                        }
                    }
                }
            });

            try (Writer w = new OutputStreamWriter(
                    new BufferedOutputStream(new FileOutputStream(outPath)), StandardCharsets.UTF_8)) {
                w.write(abcItems.toString());
                w.write("<item type=\"SymbolClassTag\"><names>");
                for (String name : symbols) {
                    w.write("<item>");
                    w.write(xmlEscape(name));
                    w.write("</item>");
                }
                w.write("</names></item>");
            }
        }
    }

    public static void rewrite(String swfPath, String outPath, String pairsPath) throws Exception {
        disableHeavyFfdecWork();
        List<Pair> ident = new ArrayList<>();
        List<Pair> exact = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(new FileInputStream(pairsPath), StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                String[] parts = line.split("\t", 3);
                if (parts.length < 3) {
                    continue;
                }
                Pair p = new Pair(parts[1], parts[2]);
                if (p.from.isEmpty() || p.from.equals(p.to)) {
                    continue;
                }
                if (parts[0].equals("E")) {
                    exact.add(p);
                } else {
                    ident.add(p);
                }
            }
        }
        ident.sort((a, b) -> Integer.compare(b.from.length(), a.from.length()));
        Map<Character, List<Pair>> byFirst = new HashMap<>();
        for (Pair p : ident) {
            byFirst.computeIfAbsent(p.from.charAt(0), k -> new ArrayList<>()).add(p);
        }

        try (FileInputStream in = new FileInputStream(swfPath)) {
            SWF swf = openSwfForRewrite(in);
            walk(swf.getTags(), tag -> applyTag(tag, ident, exact, byFirst));
            try (FileOutputStream out = new FileOutputStream(outPath)) {
                swf.saveTo(out);
            }
        }
    }

    private static void applyTag(Tag tag, List<Pair> ident, List<Pair> exact, Map<Character, List<Pair>> byFirst) {
        boolean changed = false;
        if (tag instanceof SymbolClassTag) {
            SymbolClassTag sc = (SymbolClassTag) tag;
            for (int i = 0; i < sc.names.size(); i++) {
                String next = rewriteValue(sc.names.get(i), ident, exact, byFirst);
                if (next != null) {
                    sc.names.set(i, next);
                    changed = true;
                }
            }
        } else if (tag instanceof ExportAssetsTag) {
            ExportAssetsTag ex = (ExportAssetsTag) tag;
            for (int i = 0; i < ex.names.size(); i++) {
                String next = rewriteValue(ex.names.get(i), ident, exact, byFirst);
                if (next != null) {
                    ex.names.set(i, next);
                    changed = true;
                }
            }
        } else if (tag instanceof FrameLabelTag) {
            FrameLabelTag fl = (FrameLabelTag) tag;
            String next = rewriteValue(fl.name, ident, exact, byFirst);
            if (next != null) {
                fl.name = next;
                changed = true;
            }
        } else if (tag instanceof PlaceObjectTypeTag) {
            PlaceObjectTypeTag po = (PlaceObjectTypeTag) tag;
            String inst = rewriteValue(po.getInstanceName(), ident, exact, byFirst);
            if (inst != null) {
                po.setInstanceName(inst);
                changed = true;
            }
            String cls = rewriteValue(po.getClassName(), ident, exact, byFirst);
            if (cls != null) {
                po.setClassName(cls);
                changed = true;
            }
        } else if (tag instanceof DefineEditTextTag) {
            DefineEditTextTag et = (DefineEditTextTag) tag;
            String vn = rewriteValue(et.variableName, ident, exact, byFirst);
            if (vn != null) {
                et.variableName = vn;
                changed = true;
            }
            String it = rewriteValue(et.initialText, ident, exact, byFirst);
            if (it != null) {
                et.initialText = it;
                changed = true;
            }
        } else if (tag instanceof ABCContainerTag) {
            ABC abc = ((ABCContainerTag) tag).getABC();
            if (abc != null && abc.constants != null) {
                AVM2ConstantPool pool = abc.constants;
                for (int i = 1; i < pool.getStringCount(); i++) {
                    String next = rewriteValue(pool.getString(i), ident, exact, byFirst);
                    if (next != null) {
                        pool.setString(i, next);
                        changed = true;
                    }
                }
            }
        }
        if (changed) {
            tag.setModified(true);
        }
    }

    private static String rewriteValue(String value, List<Pair> ident, List<Pair> exact, Map<Character, List<Pair>> byFirst) {
        if (value == null || value.isEmpty()) {
            return null;
        }
        String next = value;
        boolean exactHit = false;
        for (Pair p : exact) {
            if (next.equals(p.from)) {
                next = p.to;
                exactHit = true;
            }
        }
        // Exact rows are displayName/GUID. Identifier rewrite after that
        // turns "Prefix Name" into "Prefix PrefixName".
        if (!exactHit) {
            next = rewriteIdentifiers(next, ident, byFirst);
        }
        return next.equals(value) ? null : next;
    }

    static String rewriteIdentifiers(String content, List<Pair> pairs) {
        Map<Character, List<Pair>> byFirst = new HashMap<>();
        if (pairs != null) {
            for (Pair p : pairs) {
                if (p.from == null || p.from.isEmpty()) {
                    continue;
                }
                byFirst.computeIfAbsent(p.from.charAt(0), k -> new ArrayList<>()).add(p);
            }
        }
        return rewriteIdentifiers(content, pairs, byFirst);
    }

    static String rewriteIdentifiers(String content, List<Pair> pairs, Map<Character, List<Pair>> byFirst) {
        if (content == null || content.isEmpty() || pairs == null || pairs.isEmpty()) {
            return content;
        }
        StringBuilder sb = new StringBuilder(content.length() + 16);
        int pos = 0;
        while (pos < content.length()) {
            boolean matched = false;
            List<Pair> cands = byFirst.get(content.charAt(pos));
            if (cands != null) {
                for (Pair p : cands) {
                    if (identifierMatchesAt(content, pos, p.from)) {
                        sb.append(p.to);
                        pos += p.from.length();
                        matched = true;
                        break;
                    }
                }
            }
            if (!matched) {
                sb.append(content.charAt(pos));
                pos++;
            }
        }
        return sb.toString();
    }

    static boolean identifierMatchesAt(String text, int index, String token) {
        if (index < 0 || token == null || token.isEmpty() || index + token.length() > text.length()) {
            return false;
        }
        if (!text.regionMatches(index, token, 0, token.length())) {
            return false;
        }
        if (index > 0 && isAsciiAlnum(text.charAt(index - 1))) {
            return false;
        }
        if (isInsideProtectedBgmId(text, index, token)) {
            return false;
        }
        int after = index + token.length();
        if (after >= text.length()) {
            return true;
        }
        return isIdentifierRightBoundaryOk(token, text.charAt(after));
    }

    private static boolean isInsideProtectedBgmId(String text, int index, String token) {
        if (token.regionMatches(true, 0, "bgm_", 0, 4)) {
            return false;
        }
        int start = index;
        while (start > 0) {
            char c = text.charAt(start - 1);
            if (!(isAsciiAlnum(c) || c == '_')) {
                break;
            }
            start--;
        }
        return index - start >= 4 && text.regionMatches(true, start, "bgm_", 0, 4);
    }

    private static boolean isIdentifierRightBoundaryOk(String token, char next) {
        int letters = 0;
        int upper = 0;
        int lower = 0;
        for (int i = 0; i < token.length(); i++) {
            char c = token.charAt(i);
            if (c >= 'A' && c <= 'Z') {
                letters++;
                upper++;
            } else if (c >= 'a' && c <= 'z') {
                letters++;
                lower++;
            }
        }
        boolean allUpper = letters > 0 && upper == letters;
        boolean allLower = letters > 0 && lower == letters;
        if (allUpper || allLower || upper == 0) {
            return !isAsciiAlnum(next);
        }
        if (upper > 0 && lower > 0) {
            return next < 'a' || next > 'z';
        }
        return !isAsciiAlnum(next);
    }

    private static boolean isAsciiAlnum(char c) {
        return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
    }

    private static SWF openSwf(FileInputStream in) throws Exception {
        // Lazy read for ident dump only (no save).
        return new SWF(in, true, true);
    }

    private static SWF openSwfForRewrite(FileInputStream in) throws Exception {
        // Full parse before save so embedded sounds/shapes stay valid.
        return new SWF(in, true, false);
    }

    private static void disableHeavyFfdecWork() {
        try {
            if (Configuration.autoDeobfuscate != null) {
                Configuration.autoDeobfuscate.set(Boolean.FALSE);
            }
            if (Configuration.autoDeobfuscateIdentifiers != null) {
                Configuration.autoDeobfuscateIdentifiers.set(Boolean.FALSE);
            }
        } catch (Throwable ignored) {
            // Older FFDec jars may not expose these items.
        }
    }

    private static void walk(ReadOnlyTagList tags, TagConsumer consumer) throws Exception {
        if (tags == null) {
            return;
        }
        for (Tag tag : tags) {
            consumer.accept(tag);
            if (tag instanceof DefineSpriteTag) {
                walk(((DefineSpriteTag) tag).getTags(), consumer);
            }
        }
    }

    private static String xmlEscape(String value) {
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }

    @FunctionalInterface
    private interface TagConsumer {
        void accept(Tag tag) throws Exception;
    }

    static final class Pair {
        final String from;
        final String to;

        Pair(String from, String to) {
            this.from = from;
            this.to = to;
        }
    }
}
