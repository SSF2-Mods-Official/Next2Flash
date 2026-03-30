package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_12 extends MovieClip
    {

        public var self:BlackMageExt;

        public function Win_12()
        {
            super();
            addFrameScript(0, this.frame1, 125, this.frame126);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame126():*
        {
            gotoAndPlay("loop");
        }


    }
}

