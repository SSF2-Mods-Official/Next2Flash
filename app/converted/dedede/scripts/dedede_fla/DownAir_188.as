package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class DownAir_188 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var playsound:Number;
        public var audio:Number;

        public function DownAir_188()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 7, this.frame8, 8, this.frame9, 9, this.frame10, 17, this.frame18, 23, this.frame24, 24, this.frame25, 32, this.frame33);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame2():*
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
        }

        internal function frame8():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame9():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_ll");
        }

        internal function frame10():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(5),
                "y":45,
                "scaleX":2,
                "scaleY":2,
                "parentLock":true
            });
        }

        internal function frame18():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }

        internal function frame25():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_landHeavy");
                };
            };
            SSF2API.getCamera().shake(3);
        }

        internal function frame33():*
        {
            this.self.endAttack();
        }


    }
}

