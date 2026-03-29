package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Run_39 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Run_39()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 12, this.frame13, 13, this.frame14, 22, this.frame23, 23, this.frame24, 24, this.frame25, 25, this.frame26, 31, this.frame32);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_m1");
                }
                else
                {
                    this.self.playSound("falcon_footstep");
                };
            };
        }

        internal function frame7():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("falcon_footstep2");
            };
        }

        internal function frame13():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame14():*
        {
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
            this.self.playSound("cfalcon_run_start");
        }

        internal function frame23():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame24():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame25():*
        {
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
        }

        internal function frame26():*
        {
            this.self.playSound("cfalcon_dashturn");
        }

        internal function frame32():*
        {
            this.self.stancePlayFrame("run");
        }


    }
}

