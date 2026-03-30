package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_walking_26 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_walking_26()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 15, this.frame16, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }

        internal function frame6():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("fox_footstep");
            };
        }

        internal function frame16():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("fox_footstep2");
            };
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

