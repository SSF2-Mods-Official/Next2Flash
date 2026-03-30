package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class _1_1_212 extends MovieClip
    {

        public var bg_doomship:MovieClip;

        public function _1_1_212()
        {
            super();
            addFrameScript(149, this.frame150);
        }

        internal function frame150():*
        {
            if (SSF2API.randomInteger(1, 24) > 22)
            {
                if (SSF2API.randomInteger(1, 4) != 4)
                {
                    this.bg_doomship.visible = true;
                }
                else
                {
                    this.bg_doomship.visible = false;
                };
            };
        }


    }
}

