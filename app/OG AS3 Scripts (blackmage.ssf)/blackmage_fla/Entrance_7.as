// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Entrance_7

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.*;
    import flash.display.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class Entrance_7 extends MovieClip 
    {

        public var self:BlackMageExt;

        public function Entrance_7()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 6, this.frame7, 8, this.frame9, 10, this.frame11, 12, this.frame13, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame3():*
        {
            this.self.playSound("menumove");
        }

        internal function frame5():*
        {
            this.self.playSound("menumove");
        }

        internal function frame7():*
        {
            this.self.playSound("menumove");
        }

        internal function frame9():*
        {
            this.self.playSound("menumove");
        }

        internal function frame11():*
        {
            this.self.playSound("menumove");
        }

        internal function frame13():*
        {
            this.self.playSound("bm_Entrance_last");
        }

        internal function frame40():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}//package blackmage_fla

