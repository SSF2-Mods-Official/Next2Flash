// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemHeavyShoot_94

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

    public dynamic class ItemHeavyShoot_94 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function ItemHeavyShoot_94()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

