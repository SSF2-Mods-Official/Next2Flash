package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Dash_14 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Dash_14()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 9, this.frame10, 16, this.frame17, 24, this.frame25, 26, this.frame27, 36, this.frame37);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady())
            {
                this.self.playSound("simon_dashstart");
            };
        }

        internal function frame9():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_simon_step_02");
            };
        }

        internal function frame10():*
        {
            this.gotoAndStop("run");
        }

        internal function frame17():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_simon_step_01");
            };
        }

        internal function frame25():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_simon_step_02");
            };
        }

        internal function frame27():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame37():*
        {
            this.self.stancePlayFrame("run");
        }


    }
}

