package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_23 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var playsound:Number;
        public var audio:Number;
        public var newStats:*;

        public function DashAttack_23()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 16, this.frame17, 17, this.frame18, 22, this.frame23, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
            this.newStats = {
                "damage":5,
                "power":60,
                "kbConstant":80,
                "effectSound":"sw_brawl_hit_M"
            };
        }

        internal function frame6():*
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
            if ((root != null) && (parent != null))
            {
                this.self.playAttackSound(1);
            };
            if ((root != null) && (parent != null))
            {
                this.self.attachEffect("wind_wave", {
                    "x":this.self.flipX(35),
                    "y":-35,
                    "scaleX":0.8,
                    "scaleY":0.8,
                    "parentLock":true
                });
            };
            this.self.attachEffect("global_dust_heavy");
            this.self.setXSpeed(16, false);
        }

        internal function frame17():*
        {
            this.self.updateAttackStats({
                "xSpeedDecay":1,
                "refreshRate":420
            });
        }

        internal function frame18():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackBoxStats(1, this.newStats);
            this.self.updateAttackBoxStats(2, this.newStats);
        }

        internal function frame23():*
        {
            this.self.setXSpeed(0, false);
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

