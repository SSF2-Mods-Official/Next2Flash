package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Run_22 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Run_22()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 9, this.frame10, 16, this.frame17, 20, this.frame21, 22, this.frame23);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
                this.self.playSound("bandanadee_dashstart");
            };
        }

        internal function frame6():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame10():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_step01");
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
                this.self.playSound("bandanadee_step02");
            };
        }

        internal function frame21():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame23():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_fspecEnd");
            };
        }


    }
}

