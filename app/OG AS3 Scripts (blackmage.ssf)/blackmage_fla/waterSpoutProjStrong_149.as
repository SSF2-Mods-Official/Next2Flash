// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.waterSpoutProjStrong_149

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

    public dynamic class waterSpoutProjStrong_149 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var newXSpeed:*;
        public var newYSpeed:*;
        public var character:*;

        public function waterSpoutProjStrong_149()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 7, this.frame8, 9, this.frame10, 10, this.frame11, 13, this.frame14, 17, this.frame18);
        }

        public function toContinue(_arg_1:*):*
        {
            this.self.stancePlayFrame("continue");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.toContinue);
        }

        public function toChibtinue(_arg_1:*):*
        {
            this.self.stancePlayFrame("chibtinue");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toChibtinue);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toChibtinue);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toChibtinue);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.toChibtinue);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.newXSpeed = 0;
            this.newYSpeed = 0;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.newXSpeed = (0.55 * this.character.getXSpeed());
                this.newYSpeed = ((0.55 * this.character.getYSpeed()) + this.self.getProjectileStat("yspeed"));
                this.self.setXSpeed(this.newXSpeed, true);
                this.self.setYSpeed(this.newYSpeed);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
            };
        }

        internal function frame4():*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame8():*
        {
            this.self.destroy();
        }

        internal function frame10():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame11():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toChibtinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toChibtinue);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toChibtinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.toChibtinue);
            };
        }

        internal function frame14():*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame18():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

