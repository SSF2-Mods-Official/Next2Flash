package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class FTilt_50 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function FTilt_50()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5, 7, this.frame8, 9, this.frame10, 11, this.frame12, 15, this.frame16);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
            };
        }

        internal function frame2():*
        {
            this.playsound = SSF2API.random();
            this.audio = this.self.getGlobalVariable("audio");
        }

        internal function frame4():*
        {
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(1);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 1);
                };
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(2);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 2);
                };
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(3);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 3);
                };
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                if ((root != null) && (parent != null))
                {
                    this.self.playVoiceSound(4);
                };
                if ((root != null) && (parent != null))
                {
                    this.self.setGlobalVariable("audio", 4);
                };
            };
            if ((root != null) && (parent != null))
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.attachEffect("global_dust_swirl");
            this.self.addEffectToList(this.self.attachEffect("trail_cfalcon_ftilt", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame8():*
        {
            this.self.setXSpeed(4, false);
        }

        internal function frame10():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            };
        }

        internal function frame12():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            };
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

