package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class UAir_115 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var playsound:Number;
        public var audio:Number;

        public function UAir_115()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 10, this.frame11, 17, this.frame18, 18, this.frame19, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame4():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame5():*
        {
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

        internal function frame11():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }

        internal function frame19():*
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

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

