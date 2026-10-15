package next2flash.ffdec;

import com.jpexs.decompiler.flash.ReadOnlyTagList;
import com.jpexs.decompiler.flash.SWF;
import com.jpexs.decompiler.flash.tags.DefineSpriteTag;
import com.jpexs.decompiler.flash.tags.PlaceObject2Tag;
import com.jpexs.decompiler.flash.tags.PlaceObject3Tag;
import com.jpexs.decompiler.flash.tags.RemoveObject2Tag;
import com.jpexs.decompiler.flash.tags.ShowFrameTag;
import com.jpexs.decompiler.flash.tags.Tag;
import com.jpexs.decompiler.flash.timeline.Timelined;
import com.jpexs.decompiler.flash.types.MATRIX;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

/**
 * Adds, removes, and moves PlaceObject tags on an existing timeline (GPLv3).
 * Spec file, one operation per line:
 *   sprite &lt;id&gt;
 *   transform &lt;frame&gt; &lt;depth&gt; &lt;txPixels&gt; &lt;tyPixels&gt;
 *   remove &lt;frame&gt; &lt;depth&gt;
 *   add &lt;frame&gt; &lt;depth&gt; &lt;character&gt; &lt;txPixels&gt; &lt;tyPixels&gt;
 * Frames are 1-based. Sprite 0 is the main timeline.
 */
public final class PlaceEdit {
    private PlaceEdit() {}

    public static void run(String swfPath, String specPath) throws Exception {
        int spriteId = 0;
        List<String[]> ops = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(specPath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                String[] parts = line.split("\\s+");
                if (parts[0].equals("sprite")) {
                    spriteId = Integer.parseInt(parts[1]);
                } else {
                    ops.add(parts);
                }
            }
        }

        try (FileInputStream in = new FileInputStream(swfPath)) {
            SWF swf = new SWF(in, false);
            Timelined timeline = timeline(swf, spriteId);
            int applied = 0;
            for (String[] op : ops) {
                apply(swf, timeline, op);
                applied++;
            }
            try (FileOutputStream out = new FileOutputStream(swfPath)) {
                swf.saveTo(out);
            }
            System.out.println("places=" + applied);
        }
    }

    private static Timelined timeline(SWF swf, int spriteId) {
        if (spriteId == 0) {
            return swf;
        }
        DefineSpriteTag sprite = findSprite(swf.getTags(), spriteId);
        if (sprite == null) {
            throw new IllegalArgumentException("sprite " + spriteId);
        }
        return sprite;
    }

    private static DefineSpriteTag findSprite(ReadOnlyTagList tags, int spriteId) {
        for (Tag tag : tags) {
            if (tag instanceof DefineSpriteTag) {
                DefineSpriteTag sprite = (DefineSpriteTag) tag;
                if (sprite.getCharacterId() == spriteId) {
                    return sprite;
                }
                DefineSpriteTag nested = findSprite(sprite.getTags(), spriteId);
                if (nested != null) {
                    return nested;
                }
            }
        }
        return null;
    }

    private static void apply(SWF swf, Timelined timeline, String[] op) {
        String kind = op[0];
        int frame = Integer.parseInt(op[1]);
        int depth = Integer.parseInt(op[2]);
        ShowFrameTag show = showFrame(timeline, frame);
        if (kind.equals("transform")) {
            int tx = pixels(op[3]);
            int ty = pixels(op[4]);
            Tag place = findPlace(tagsBefore(timeline, show), depth);
            if (place instanceof PlaceObject2Tag) {
                PlaceObject2Tag tag = (PlaceObject2Tag) place;
                tag.matrix = moved(tag.matrix, tx, ty);
                tag.placeFlagHasMatrix = true;
                tag.setModified(true);
            } else if (place instanceof PlaceObject3Tag) {
                PlaceObject3Tag tag = (PlaceObject3Tag) place;
                tag.matrix = moved(tag.matrix, tx, ty);
                tag.placeFlagHasMatrix = true;
                tag.setModified(true);
            } else {
                PlaceObject2Tag tag = new PlaceObject2Tag(
                    swf, true, depth, -1, moved(null, tx, ty), null, -1, null, -1, null);
                SWF.addTagBefore(tag, show);
            }
        } else if (kind.equals("remove")) {
            Tag place = findPlace(tagsBefore(timeline, show), depth);
            if (place != null) {
                timeline.removeTag(place);
            }
            RemoveObject2Tag remove = new RemoveObject2Tag(swf);
            remove.depth = depth;
            remove.setModified(true);
            SWF.addTagBefore(remove, show);
        } else if (kind.equals("add")) {
            int character = Integer.parseInt(op[3]);
            int tx = pixels(op[4]);
            int ty = pixels(op[5]);
            PlaceObject2Tag tag = new PlaceObject2Tag(
                swf, false, depth, character, moved(null, tx, ty), null, -1, null, -1, null);
            SWF.addTagBefore(tag, show);
        } else {
            throw new IllegalArgumentException("place op " + kind);
        }
    }

    private static int pixels(String text) {
        return (int) Math.round(Double.parseDouble(text) * 20.0);
    }

    private static MATRIX moved(MATRIX current, int tx, int ty) {
        MATRIX matrix = current == null ? new MATRIX() : new MATRIX(current);
        matrix.translateX = tx;
        matrix.translateY = ty;
        return matrix;
    }

    private static ShowFrameTag showFrame(Timelined timeline, int frame) {
        int seen = 0;
        for (Tag tag : timeline.getTags()) {
            if (tag instanceof ShowFrameTag) {
                seen++;
                if (seen == frame) {
                    return (ShowFrameTag) tag;
                }
            }
        }
        throw new IllegalArgumentException("frame " + frame);
    }

    private static List<Tag> tagsBefore(Timelined timeline, ShowFrameTag show) {
        List<Tag> tags = new ArrayList<>();
        for (Tag tag : timeline.getTags()) {
            if (tag == show) {
                break;
            }
            if (tag instanceof ShowFrameTag) {
                tags.clear();
            } else {
                tags.add(tag);
            }
        }
        return tags;
    }

    private static Tag findPlace(List<Tag> tags, int depth) {
        Tag found = null;
        for (Tag tag : tags) {
            if (tag instanceof PlaceObject2Tag && ((PlaceObject2Tag) tag).depth == depth) {
                found = tag;
            } else if (tag instanceof PlaceObject3Tag && ((PlaceObject3Tag) tag).depth == depth) {
                found = tag;
            }
        }
        return found;
    }
}
