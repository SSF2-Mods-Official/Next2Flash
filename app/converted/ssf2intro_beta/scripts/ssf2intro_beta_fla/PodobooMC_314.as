package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class PodobooMC_314 extends MovieClip
    {

        public function PodobooMC_314()
        {
            super();
            addFrameScript(1, this.frame2, 12, this.frame13, 31, this.frame32, 42, this.frame43, 60, this.frame61, 70, this.frame71);
        }

        internal function frame2():*
        {
            SSF2API.playSound("podoboo_land");
        }

        internal function frame13():*
        {
            SSF2API.playSound("podoboo_jump");
        }

        internal function frame32():*
        {
            SSF2API.playSound("podoboo_land");
        }

        internal function frame43():*
        {
            SSF2API.playSound("podoboo_jump");
        }

        internal function frame61():*
        {
            SSF2API.playSound("podoboo_land");
        }

        internal function frame71():*
        {
            SSF2API.playSound("podoboo_jump");
        }


    }
}

