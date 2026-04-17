package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class groundRef_mc_13 extends MovieClip
    {

        public var self:FoxExt;

        public function groundRef_mc_13()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.visible = false;
        }


    }
}

