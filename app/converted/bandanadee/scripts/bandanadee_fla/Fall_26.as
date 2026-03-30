package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Fall_26 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Fall_26()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame8():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

