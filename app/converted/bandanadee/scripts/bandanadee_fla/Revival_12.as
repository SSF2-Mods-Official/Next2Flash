package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Revival_12 extends MovieClip
    {

        public var stance:MovieClip;
        public var self:BandanaDeeExt;

        public function Revival_12()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
            };
        }


    }
}

