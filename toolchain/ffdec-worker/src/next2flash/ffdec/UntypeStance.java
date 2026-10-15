package next2flash.ffdec;

import com.jpexs.decompiler.flash.ReadOnlyTagList;
import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.abc.ABC;
import com.jpexs.decompiler.flash.abc.avm2.AVM2ConstantPool;
import com.jpexs.decompiler.flash.abc.types.ClassInfo;
import com.jpexs.decompiler.flash.abc.types.InstanceInfo;
import com.jpexs.decompiler.flash.abc.types.Multiname;
import com.jpexs.decompiler.flash.abc.types.Namespace;
import com.jpexs.decompiler.flash.abc.types.traits.Trait;
import com.jpexs.decompiler.flash.abc.types.traits.TraitSlotConst;
import com.jpexs.decompiler.flash.abc.types.traits.Traits;
import com.jpexs.decompiler.flash.configuration.Configuration;
import com.jpexs.decompiler.flash.tags.ABCContainerTag;
import com.jpexs.decompiler.flash.tags.DefineSpriteTag;
import com.jpexs.decompiler.flash.tags.Tag;

import java.io.FileInputStream;
import java.io.FileOutputStream;

/**
 * Retypes auto-declared stage instance slots that point at {@code *_fla.*}
 * timeline classes (e.g. {@code clip:Idle_3}) to {@code flash.display.MovieClip}.
 * Prevents AVM2 Error #1034 when the same instance name is a different
 * {@code _fla} class on another frame (CSS intro taunt).
 */
public final class UntypeStance {
    private UntypeStance() {}

    public static void run(String swfPath, String outPath) throws Exception {
        try {
            if (Configuration.autoDeobfuscate != null) {
                Configuration.autoDeobfuscate.set(Boolean.FALSE);
            }
            if (Configuration.autoDeobfuscateIdentifiers != null) {
                Configuration.autoDeobfuscateIdentifiers.set(Boolean.FALSE);
            }
        } catch (Throwable ignored) {
        }

        int changed = 0;
        try (FileInputStream in = new FileInputStream(swfPath)) {
            SWF swf = new SWF(in, true, false);
            changed = walk(swf.getTags());
            try (FileOutputStream out = new FileOutputStream(outPath)) {
                swf.saveTo(out);
            }
        }
        System.out.println("untyped-slots:" + changed);
    }

    private static int walk(ReadOnlyTagList tags) throws Exception {
        if (tags == null) {
            return 0;
        }
        int total = 0;
        for (Tag tag : tags) {
            if (tag instanceof ABCContainerTag) {
                ABC abc = ((ABCContainerTag) tag).getABC();
                int n = untypeAbc(abc);
                if (n > 0) {
                    tag.setModified(true);
                    total += n;
                }
            }
            if (tag instanceof DefineSpriteTag) {
                total += walk(((DefineSpriteTag) tag).getTags());
            }
        }
        return total;
    }

    static int untypeAbc(ABC abc) {
        if (abc == null || abc.constants == null || abc.instance_info == null) {
            return 0;
        }
        AVM2ConstantPool pool = abc.constants;
        int movieClipType = movieClipQName(pool);
        int count = 0;
        for (int i = 0; i < abc.instance_info.size(); i++) {
            InstanceInfo inst = abc.instance_info.get(i);
            if (inst == null || inst.deleted || isFlaTimelineClass(pool, inst)) {
                continue;
            }
            count += untypeTraits(abc, pool, inst.instance_traits, movieClipType);
            if (abc.class_info != null && i < abc.class_info.size()) {
                ClassInfo ci = abc.class_info.get(i);
                if (ci != null && !ci.deleted) {
                    count += untypeTraits(abc, pool, ci.static_traits, movieClipType);
                }
            }
        }
        return count;
    }

    private static int untypeTraits(ABC abc, AVM2ConstantPool pool, Traits traits, int movieClipType) {
        if (traits == null || traits.traits == null) {
            return 0;
        }
        int count = 0;
        for (Trait trait : traits.traits) {
            if (!(trait instanceof TraitSlotConst)) {
                continue;
            }
            TraitSlotConst slot = (TraitSlotConst) trait;
            if (!slot.isVar() || slot.type_index <= 0) {
                continue;
            }
            if (!isFlaType(pool, slot.type_index)) {
                continue;
            }
            slot.type_index = movieClipType;
            count++;
        }
        return count;
    }

    static boolean isFlaTimelineClass(AVM2ConstantPool pool, InstanceInfo inst) {
        if (inst.name_index <= 0) {
            return false;
        }
        return packageEndsWithFla(pool, inst.name_index);
    }

    static boolean isFlaType(AVM2ConstantPool pool, int multinameIndex) {
        return packageEndsWithFla(pool, multinameIndex);
    }

    private static boolean packageEndsWithFla(AVM2ConstantPool pool, int multinameIndex) {
        Multiname mn = pool.getMultiname(multinameIndex);
        if (mn == null) {
            return false;
        }
        Namespace ns = mn.getNamespace(pool);
        if (ns == null) {
            return false;
        }
        String pkg = ns.getRawName(pool);
        return pkg != null && pkg.endsWith("_fla");
    }

    private static int movieClipQName(AVM2ConstantPool pool) {
        int ns = pool.getNamespaceId(Namespace.KIND_PACKAGE, "flash.display", 0, true);
        int name = pool.getStringId("MovieClip", true);
        Multiname qn = Multiname.createQName(false, name, ns);
        return pool.getMultinameId(qn, true);
    }
}
