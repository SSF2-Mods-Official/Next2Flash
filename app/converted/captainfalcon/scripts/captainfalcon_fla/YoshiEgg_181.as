package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class YoshiEgg_181 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:CaptainExt;

        public function YoshiEgg_181()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("tether", false);
                this.self.setGlobalVariable("nStoredLabel", null);
                this.self.setGlobalVariable("sStoredLabel", null);
            };
        }


    }
}

