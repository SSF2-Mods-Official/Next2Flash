package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class UAir_39 extends MovieClip
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

        public function UAir_39()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 8, this.frame9, 14, this.frame15, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame7():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame8():*
        {
            this.self.attachEffect("global_spark", {
                "scaleX":0.6,
                "scaleY":0.6,
                "x":this.self.flipX(12),
                "y":-145
            });
        }

        internal function frame9():*
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
        }

        internal function frame15():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("simon_land");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

