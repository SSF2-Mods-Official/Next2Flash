package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_14 extends MovieClip
    {

        public function Win_14()
        {
            super();
            addFrameScript(67, this.frame68, 68, this.frame69);
        }

        internal function frame68():*
        {
            this.gotoAndStop("vacuum");
        }

        internal function frame69():*
        {
            this.gotoAndStop("loop");
        }


    }
}

