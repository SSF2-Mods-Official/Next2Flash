package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class BAir_117 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var playsound:Number;
        public var audio:Number;

        public function BAir_117()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 16, this.frame17, 20, this.frame21, 21, this.frame22, 27, this.frame28);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(-37),
                "y":-15,
                "parentLock":true
            });
            this.self.playAttackSound(1);
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

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "power":0,
                "kbConstant":112
            });
        }

        internal function frame17():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame28():*
        {
            this.self.endAttack();
        }


    }
}

