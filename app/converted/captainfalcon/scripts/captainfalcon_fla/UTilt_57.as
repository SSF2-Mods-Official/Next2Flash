package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class UTilt_57 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function UTilt_57()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 20, this.frame21);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame5():*
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
            this.self.attachEffect("global_spark", {"y":-80});
            this.self.playAttackSound(1);
        }

        internal function frame8():*
        {
            this.self.setXSpeed(3, false);
            this.self.playAttackSound(2);
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_utilt", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame9():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame10():*
        {
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            };
            this.self.setXSpeed(0);
        }

        internal function frame11():*
        {
            this.self.playAttackSound(3);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

