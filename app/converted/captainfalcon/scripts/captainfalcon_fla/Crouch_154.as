package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_154 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Crouch_154()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }

        internal function frame4():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame5():*
        {
            gotoAndStop("loop");
        }


    }
}

