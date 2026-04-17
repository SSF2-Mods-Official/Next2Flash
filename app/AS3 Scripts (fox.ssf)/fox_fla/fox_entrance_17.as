// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_entrance_17

package fox_fla
{
    import flash.display.MovieClip;
    import flash.display.*;
    import flash.geom.*;
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

    public dynamic class fox_entrance_17 extends MovieClip 
    {

        public var self:FoxExt;

        public function fox_entrance_17()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 12, this.frame13, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame2():*
        {
            this.self.playSound("starFox_Entrance_sfx");
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
                SSF2API.getCamera().shake(3);
            }
            else
            {
                this.self.playSound("fox_landHeavy");
            };
            this.self.attachEffect("effect_land");
        }

        internal function frame31():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}//package fox_fla

