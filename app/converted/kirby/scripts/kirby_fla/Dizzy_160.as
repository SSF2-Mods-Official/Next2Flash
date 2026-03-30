package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_160 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function Dizzy_160()
        {
            super();
            addFrameScript(0, this.frame1, 37, this.frame38);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self && !this.self.getMetalStatus())
            {
                this.self.playSound("kirby_dizzy", true);
            };
        }

        internal function frame38():*
        {
            gotoAndStop("again");
        }


    }
}

