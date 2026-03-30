package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Sleep_231 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Sleep_231()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("canStartRise", true);
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }


    }
}

