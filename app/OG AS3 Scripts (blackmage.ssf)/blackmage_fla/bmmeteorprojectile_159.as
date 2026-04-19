// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.bmmeteorprojectile_159

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

    public dynamic class bmmeteorprojectile_159 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var isOnGround:Boolean;
        public var character:*;
        public var temp:*;
        public var dmg:Number;
        public var charge:int;
        public var max:int;

        public function bmmeteorprojectile_159()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 13, this.frame14, 14, this.frame15, 27, this.frame28, 29, this.frame30, 30, this.frame31);
        }

        public function onGround(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.onGround);
            this.self.getMC().y = (this.self.getMC().y + 5);
            this.isOnGround = true;
        }

        public function toContinue(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.self.flip);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.toContinue);
            this.self.removeEventListener(SSF2Event.REVERSE, this.self.flip);
            this.self.stancePlayFrame("continue");
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.isOnGround = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.onGround);
            };
        }

        internal function frame3():*
        {
            this.self.stancePlayFrame("redo");
        }

        internal function frame4():*
        {
            this.temp = SSF2API.getProjectile(this);
            if (!this.self)
            {
                this.self = this.temp;
            };
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.onGround);
            this.dmg = this.self.getAttackBoxStat(1, "damage");
            this.charge = this.character.getGlobalVariable("BMageDSpecCharge");
            this.max = this.character.getAttackStat("chargetime_max");
            if (this.charge > this.max)
            {
                this.charge = this.max;
            };
            this.dmg = (this.dmg + ((this.charge / this.max) * 23));
            this.self.updateAttackBoxStats(1, {
                "damage":this.dmg,
                "effectSound":"brawl_fire_l"
            });
            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
            this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.self.flip);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
            this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
            this.self.addEventListener(SSF2Event.REVERSE, this.self.flip);
        }

        internal function frame5():*
        {
            if (this.isOnGround)
            {
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.removeEventListener(SSF2Event.HIT_WALL, this.toContinue);
                this.self.removeEventListener(SSF2Event.REVERSE, this.self.flip);
                this.self.stancePlayFrame("continue");
            };
        }

        internal function frame14():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame15():*
        {
            this.self.updateProjectileStats({
                "maxgravity":0,
                "canBePocketed":false,
                "canBeAbsorbed":true
            });
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.playSound("bombexplode");
        }

        internal function frame28():*
        {
            this.self.destroy();
        }

        internal function frame30():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame31():*
        {
            this.self = SSF2API.getProjectile(this);
            this.isOnGround = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.self.updateAttackBoxStats(1, {"effectSound":"brawl_fire_l"});
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.self.flip);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
                this.self.addEventListener(SSF2Event.REVERSE, this.self.flip);
                this.self.playSound("bmfire");
                this.self.stancePlayFrame("loop");
            };
        }


    }
}//package blackmage_fla

