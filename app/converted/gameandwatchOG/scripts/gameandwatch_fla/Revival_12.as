package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Revival_12 extends MovieClip
    {

        public var self:gameandwatchExt;

        public function Revival_12()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
            };
        }


    }
}

