package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Pitfall_135 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Pitfall_135()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (parent && SSF2API.isReady())
            {
                this.self.setGlobalVariable("jab", false);
            };
        }


    }
}

