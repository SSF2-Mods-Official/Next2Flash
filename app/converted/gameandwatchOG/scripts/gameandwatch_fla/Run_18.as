package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Run_18 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Run_18()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 6, this.frame7, 10, this.frame11, 14, this.frame15, 15, this.frame16, 21, this.frame22);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady())
            {
                this.self.playSound("gw_dash");
            };
        }

        internal function frame6():*
        {
            this.self.stancePlayFrame("run");
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

        internal function frame11():*
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

        internal function frame15():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame16():*
        {
            this.self.playSound("gw_dash_stop");
        }

        internal function frame22():*
        {
            this.self.stancePlayFrame("run");
        }


    }
}

