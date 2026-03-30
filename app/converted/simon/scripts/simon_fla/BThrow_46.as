package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class BThrow_46 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var touchBox:MovieClip;
        public var self:SimonExt;
        public var playsound:Number;
        public var audio:Number;

        public function BThrow_46()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 13, this.frame14, 16, this.frame17, 19, this.frame20, 25, this.frame26, 28, this.frame29);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as SimonExt);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.swapDepthsWithGrabbedOpponent(true);
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
            this.self.playAttackSound(1);
        }

        internal function frame11():*
        {
            SSF2API.getCamera().shake(9);
        }

        internal function frame14():*
        {
            SSF2API.getCamera().shake(6);
        }

        internal function frame17():*
        {
            SSF2API.getCamera().shake(3);
        }

        internal function frame20():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_simon_step_02");
                };
            };
        }

        internal function frame26():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_s1");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_simon_step_01");
                };
            };
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }


    }
}

