package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_17 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Walk_17()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 16, this.frame17, 26, this.frame27, 36, this.frame37, 46, this.frame47, 56, this.frame57);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady())
            {
            };
        }

        internal function frame7():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("gw_step1");
            };
        }

        internal function frame17():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("gw_step2");
            };
        }

        internal function frame27():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("beep_step_1");
            };
        }

        internal function frame37():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("gw_step2");
            };
        }

        internal function frame47():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("beep_step_1");
            };
        }

        internal function frame57():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

