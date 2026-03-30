package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class ufoWrapperMC_197 extends MovieClip
    {

        public var UFOSound:*;

        public function ufoWrapperMC_197()
        {
            super();
            addFrameScript(969, this.frame970);
        }

        internal function frame970():*
        {
            this.UFOSound = SSF2API.playSound("smashville_UFO");
        }


    }
}

