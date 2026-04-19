// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.BThrow_79

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

    public dynamic class BThrow_79 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;

        public function BThrow_79()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 23, this.frame24);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.xframe = null;
        }

        internal function frame3():*
        {
            SSF2API.getCamera().shake(2);
            this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.xframe = "attack";
        }

        internal function frame6():*
        {
            SSF2API.getCamera().shake(2);
        }

        internal function frame7():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame8():*
        {
            SSF2API.getCamera().shake(4);
        }

        internal function frame9():*
        {
            this.self.fireProjectile("bthrowrock");
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

