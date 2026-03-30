package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class RevivalPlatform_11 extends MovieClip
    {

        public var stance:MovieClip;
        public var self:LucarioExt;

        public function RevivalPlatform_11()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
                this.self.setIntangibility(false);
            };
        }


    }
}

