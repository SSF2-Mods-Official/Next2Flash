package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Fall_43 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Fall_43()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame5():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

