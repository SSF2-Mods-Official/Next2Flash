// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.FAir_71

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

    public dynamic class FAir_71 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var playsound:Number;

        public function FAir_71()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 10, this.frame11, 13, this.frame14, 14, this.frame15, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((this.self) && (SSF2API.isReady())))
            {
                this.playsound = SSF2API.random();
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            if ((((this.self.isFacingRight()) && (this.self.getXSpeed() < 8)) || ((!(this.self.isFacingRight())) && (this.self.getXSpeed() > -8))))
            {
                this.self.setXSpeed(8, false);
            };
            this.self.playSound("bm_chocobocut");
            if (this.playsound > 0.9)
            {
                this.self.playSound("chocobo3");
            }
            else
            {
                if (this.playsound > 0.7)
                {
                    this.self.playSound("chocobo2");
                }
                else
                {
                    if (this.playsound > 0.4)
                    {
                        this.self.playSound("chocobo");
                    };
                };
            };
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(28),
                "y":-28,
                "parentLock":true
            });
        }

        internal function frame11():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }

        internal function frame15():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("blackmage_landLight");
            };
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

