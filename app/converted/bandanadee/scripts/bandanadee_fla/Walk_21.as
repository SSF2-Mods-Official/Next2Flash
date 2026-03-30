package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_21 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var normalwalk:*;

        public function Walk_21()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 12, this.frame13, 20, this.frame21);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.normalwalk = true;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
            };
        }

        internal function frame3():*
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

        internal function frame13():*
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
            this.self.stancePlayFrame("startwalk");
        }


    }
}

