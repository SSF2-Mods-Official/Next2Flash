package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_ledgeattack_117 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var playsound:Number;
        public var audio:Number;

        public function fox_ledgeattack_117()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 9, this.frame10, 11, this.frame12, 12, this.frame13, 16, this.frame17, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame5():*
        {
            this.self.playSound("fox_jump01");
        }

        internal function frame10():*
        {
            this.self.setXSpeed(8.25, false);
            this.self.setYSpeed(-6);
        }

        internal function frame12():*
        {
            this.self.attachEffect("global_dust_light");
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

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("fox_landHeavy");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

