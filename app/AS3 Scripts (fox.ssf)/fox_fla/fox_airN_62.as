// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_airN_62

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

    public dynamic class fox_airN_62 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var playsound:Number;
        public var audio:Number;

        public function fox_airN_62()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 18, this.frame19, 21, this.frame22, 22, this.frame23, 26, this.frame27);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                if (((SSF2API.isReady()) && (this.self)))
                {
                    this.playsound = SSF2API.random();
                    this.audio = this.self.getGlobalVariable("audio");
                };
            };
            if (((this.self) && (SSF2API.isReady())))
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            if (((this.self) && (SSF2API.isReady())))
            {
                this.self.attachEffect("global_dust_blast", {
                    "x":this.self.flipX(30),
                    "y":-5,
                    "parentLock":true
                });
            };
            this.self.playAttackSound(1);
            if ((((this.playsound > 0.2) && (this.playsound <= 0.4)) && (!(this.audio == 1))))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((((this.playsound > 0.4) && (this.playsound <= 0.6)) && (!(this.audio == 2))))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((((this.playsound > 0.6) && (this.playsound <= 0.8)) && (!(this.audio == 3))))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((((this.playsound > 0.8) && (this.playsound <= 1)) && (!(this.audio == 4))))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
        }

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":9,
                "power":0,
                "hitStun":2,
                "effectSound":"brawl_kick_m"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":9,
                "power":0,
                "hitStun":2,
                "effectSound":"brawl_kick_m"
            });
        }

        internal function frame19():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }

        internal function frame23():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("fox_landLight");
            };
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

