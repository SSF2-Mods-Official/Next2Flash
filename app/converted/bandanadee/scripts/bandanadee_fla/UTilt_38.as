package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class UTilt_38 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var playsound:Number;
        public var audio:Number;

        public function UTilt_38()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame4():*
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

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {"damage":7});
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

