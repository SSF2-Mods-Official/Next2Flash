package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class BThrow_127 extends MovieClip
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

        public function BThrow_127()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 5, this.frame6, 10, this.frame11, 12, this.frame13, 24, this.frame25);
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

        internal function frame3():*
        {
            this.self.swapDepthsWithGrabbedOpponent(false);
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

        internal function frame6():*
        {
            SSF2API.getCamera().shake(1);
        }

        internal function frame11():*
        {
            this.self.swapDepthsWithGrabbedOpponent(true);
            this.self.refreshAttackID();
        }

        internal function frame13():*
        {
            SSF2API.getCamera().shake(9);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

