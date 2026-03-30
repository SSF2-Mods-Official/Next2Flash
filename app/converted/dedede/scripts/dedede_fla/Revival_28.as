package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Revival_28 extends MovieClip
    {

        public var self:DededeExt;

        public function Revival_28()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
            };
        }


    }
}

