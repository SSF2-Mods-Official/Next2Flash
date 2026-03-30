package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_15 extends MovieClip
    {

        public function Win_15()
        {
            super();
            addFrameScript(41, this.frame42, 45, this.frame46, 62, this.frame63, 89, this.frame90);
        }

        internal function frame42():*
        {
            SSF2API.playSound("lucario_win", true);
        }

        internal function frame46():*
        {
            SSF2API.playSound("lucario_swing_nair");
        }

        internal function frame63():*
        {
            SSF2API.playSound("lucario_taunt2");
        }

        internal function frame90():*
        {
            gotoAndStop("loop");
        }


    }
}

