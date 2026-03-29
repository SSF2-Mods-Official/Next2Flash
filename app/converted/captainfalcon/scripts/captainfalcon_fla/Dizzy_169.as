package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_169 extends MovieClip
    {

        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Dizzy_169()
        {
            super();
            addFrameScript(0, this.frame1, 20, this.frame21);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("cfalcon_dizzy", true);
                };
            };
        }

        internal function frame21():*
        {
            this.gotoAndStop("loop");
        }


    }
}

