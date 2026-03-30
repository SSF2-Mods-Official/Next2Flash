package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class FThrow_44 extends MovieClip
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
        public var enemy:Object;

        public function FThrow_44()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 8, this.frame9, 10, this.frame11, 21, this.frame22);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as SimonExt);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.swapDepthsWithGrabbedOpponent(false);
            };
            this.enemy = null;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.enemy = this.self.getGrabbedOpponents()[0];
                this.self.swapDepths(this.enemy);
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame6():*
        {
            this.enemy.flip();
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame9():*
        {
            this.self.swapDepths(this.enemy);
            this.enemy.flip();
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
            this.self.swapDepths(this.enemy);
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.shakeCamera(9);
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

        internal function frame22():*
        {
            this.self.endAttack();
        }


    }
}

