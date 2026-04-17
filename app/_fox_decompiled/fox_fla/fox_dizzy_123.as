package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_dizzy_123 extends MovieClip
    {

        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_dizzy_123()
        {
            super();
            addFrameScript(0, this.frame1, 33, this.frame34);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("fox_dizzy", true);
                };
            };
        }

        internal function frame34():*
        {
            this.gotoAndStop("loop");
        }


    }
}

