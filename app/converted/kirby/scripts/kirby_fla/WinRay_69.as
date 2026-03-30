package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class WinRay_69 extends MovieClip
    {

        public function WinRay_69()
        {
            super();
            addFrameScript(48, this.frame49, 58, this.frame59, 76, this.frame77, 86, this.frame87, 96, this.frame97, 108, this.frame109, 109, this.frame110);
        }

        internal function frame49():*
        {
            SSF2API.playSound("kirby_jump1");
        }

        internal function frame59():*
        {
            SSF2API.playSound("kirby_land1");
        }

        internal function frame77():*
        {
            SSF2API.playSound("kirby_jump1");
        }

        internal function frame87():*
        {
            SSF2API.playSound("kirby_land1");
        }

        internal function frame97():*
        {
            SSF2API.playSound("kirby_powersteal");
            SSF2API.playSound("kirby_grunt2");
        }

        internal function frame109():*
        {
            stop();
        }

        internal function frame110():*
        {
            this.gotoAndPlay("stop");
        }


    }
}

