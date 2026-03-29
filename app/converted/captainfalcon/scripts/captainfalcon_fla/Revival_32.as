package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Revival_32 extends MovieClip
    {

        public var stance:MovieClip;
        public var self:CaptainExt;

        public function Revival_32()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
            };
        }


    }
}

