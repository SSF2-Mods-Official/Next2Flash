package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DThrow_126 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:CaptainExt;
        public var playsound:Number;
        public var audio:Number;

        public function DThrow_126()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 8, this.frame9, 9, this.frame10, 10, this.frame11, 22, this.frame23);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.swapDepthsWithGrabbedOpponent(false);
            };
        }

        internal function frame2():*
        {
            this.self.playSound("cfalcon_kickwind");
        }

        internal function frame9():*
        {
            this.self.setXSpeed(3, false);
        }

        internal function frame10():*
        {
            SSF2API.getCamera().shake(9);
        }

        internal function frame11():*
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
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}

