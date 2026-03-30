package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Revival_8 extends MovieClip
    {

        public var self:BlackMageExt;

        public function Revival_8()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
            };
        }


    }
}

