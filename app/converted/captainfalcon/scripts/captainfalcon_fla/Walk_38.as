package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_38 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Walk_38()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 15, this.frame16);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }

        internal function frame7():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("falcon_footstep");
            };
        }

        internal function frame16():*
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


    }
}

