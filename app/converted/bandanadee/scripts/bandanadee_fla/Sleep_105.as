package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Sleep_105 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Sleep_105()
        {
            super();
            addFrameScript(0, this.frame1, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playSound("fall_asleep");
            };
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}

