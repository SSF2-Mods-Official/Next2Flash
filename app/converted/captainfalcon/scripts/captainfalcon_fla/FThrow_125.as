package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class FThrow_125 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function FThrow_125()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7, 7, this.frame8, 9, this.frame10, 20, this.frame21);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.swapDepthsWithGrabbedOpponent(true);
            };
        }

        internal function frame2():*
        {
            this.self.playSound("cfalcon_kickwind");
        }

        internal function frame7():*
        {
            this.self.refreshAttackID();
            this.self.setXSpeed(3, false);
        }

        internal function frame8():*
        {
            SSF2API.getCamera().shake(9);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame10():*
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
            this.self.playSound("cfalcon_kickwind");
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}

