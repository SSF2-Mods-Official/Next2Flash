package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class NAir_38 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var playsound:Number;
        public var audio:Number;

        public function NAir_38()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 11, this.frame12, 23, this.frame24, 26, this.frame27, 27, this.frame28, 32, this.frame33);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && this.self && SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
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
            this.self.playAttackSound(1);
            this.self.setLandingLag(true);
        }

        internal function frame12():*
        {
            this.self.updateAttackBoxStats(1, {"damage":7});
            this.self.updateAttackBoxStats(2, {"damage":7});
            this.self.updateAttackBoxStats(3, {"damage":7});
            this.self.updateAttackBoxStats(4, {"damage":7});
        }

        internal function frame24():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }

        internal function frame28():*
        {
            SSF2API.getCamera().shake(2);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("simon_land");
                };
            };
        }

        internal function frame33():*
        {
            this.self.endAttack();
        }


    }
}

