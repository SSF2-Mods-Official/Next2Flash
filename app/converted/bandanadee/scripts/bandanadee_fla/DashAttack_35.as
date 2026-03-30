package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_35 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var cooldown:int;
        public var didCooldown:Boolean;
        public var playsound:Number;
        public var audio:Number;

        public function DashAttack_35()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 6, this.frame7, 7, this.frame8, 8, this.frame9, 10, this.frame11, 19, this.frame20, 23, this.frame24, 26, this.frame27, 31, this.frame32);
        }

        public function doCooldown(_arg_1:*=null):void
        {
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.doCooldown);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.doCooldown);
            this.didCooldown = true;
            this.self.createTimer(this.cooldown, 1, this.doSecondHit);
        }

        public function doSecondHit(_arg_1:*=null):void
        {
            this.self.updateAttackBoxStats(1, {
                "direction":50,
                "damage":7,
                "kbConstant":80
            });
            this.self.updateAttackBoxStats(2, {
                "direction":50,
                "damage":7,
                "kbConstant":80
            });
            this.self.refreshAttackID();
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.cooldown = 4;
            this.didCooldown = false;
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.doCooldown);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.doCooldown);
            };
        }

        internal function frame2():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame3():*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.6));
        }

        internal function frame7():*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 1.3));
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("bandanadee_fspecEnd");
            };
        }

        internal function frame8():*
        {
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
            this.self.playAttackSound(1);
            this.self.unnattachFromGround();
            this.self.setYSpeed(-6);
            this.self.setXSpeed(10, false);
            this.self.playSound("bandanadee_uspecSpin");
        }

        internal function frame9():*
        {
            this.self.setLandingLag(true);
            this.self.updateAttackBoxStats(1, {"power":50});
            this.self.updateAttackBoxStats(2, {"power":50});
        }

        internal function frame11():*
        {
            if (!this.didCooldown)
            {
                this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.doCooldown);
                this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.doCooldown);
                this.doSecondHit();
            };
        }

        internal function frame20():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }

        internal function frame27():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}

