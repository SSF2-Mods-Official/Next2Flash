// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_airB_65

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

    public dynamic class fox_airB_65 extends MovieClip 
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

        public function fox_airB_65()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 4, this.frame5, 12, this.frame13, 19, this.frame20, 20, this.frame21, 26, this.frame27);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame2():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame3():*
        {
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
            this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":10,
                "hitStun":3,
                "effectSound":"brawl_kick_m"
            });
        }

        internal function frame13():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }

        internal function frame21():*
        {
            this.self.updateAttackStats({"cancelWhenAirborne":true});
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("fox_landHeavy");
            };
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

