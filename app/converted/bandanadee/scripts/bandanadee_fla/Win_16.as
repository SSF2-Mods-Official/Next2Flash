package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_16 extends MovieClip
    {

        public function Win_16()
        {
            super();
            addFrameScript(38, this.frame39, 44, this.frame45, 50, this.frame51, 70, this.frame71, 79, this.frame80, 89, this.frame90, 91, this.frame92, 97, this.frame98, 110, this.frame111, 111, this.frame112);
        }

        internal function frame39():*
        {
            SSF2API.playSound("bandanadee_step01");
        }

        internal function frame45():*
        {
            SSF2API.playSound("bandanadee_jump1");
        }

        internal function frame51():*
        {
            SSF2API.playSound("bandanadee_uspecSpin");
        }

        internal function frame71():*
        {
            SSF2API.playSound("bandanadee_land1");
        }

        internal function frame80():*
        {
            SSF2API.playSound("bandanadee_jump1");
        }

        internal function frame90():*
        {
            SSF2API.playSound("bandanadee_step01");
        }

        internal function frame92():*
        {
            SSF2API.playSound("bandanadee_step02");
        }

        internal function frame98():*
        {
            SSF2API.playSound("bandanadee_powersteal");
        }

        internal function frame111():*
        {
            stop();
        }

        internal function frame112():*
        {
            this.gotoAndPlay("stop");
        }


    }
}

