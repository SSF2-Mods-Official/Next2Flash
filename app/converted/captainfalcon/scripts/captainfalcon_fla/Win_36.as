package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_36 extends MovieClip
    {

        public function Win_36()
        {
            super();
            addFrameScript(45, this.frame46, 69, this.frame70, 70, this.frame71);
        }

        internal function frame46():*
        {
            SSF2API.playSound("fPunchCharge");
        }

        internal function frame70():*
        {
            stop();
        }

        internal function frame71():*
        {
            this.gotoAndStop("stop");
        }


    }
}

