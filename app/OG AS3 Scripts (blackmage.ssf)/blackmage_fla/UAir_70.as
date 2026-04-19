// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.UAir_70

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

    public dynamic class UAir_70 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function UAir_70()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 6, this.frame7, 8, this.frame9, 10, this.frame11, 12, this.frame13, 15, this.frame16, 16, this.frame17, 22, this.frame23);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((this.self) && (SSF2API.isReady())))
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.fireProjectile("waterspout_strong");
            this.self.setLandingLag(true);
            this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.self.fireProjectile("waterspout");
        }

        internal function frame7():*
        {
            this.self.fireProjectile("waterspout");
        }

        internal function frame9():*
        {
            this.self.fireProjectile("waterspout_strong");
        }

        internal function frame11():*
        {
        }

        internal function frame13():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("blackmage_landHeavy");
            };
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

