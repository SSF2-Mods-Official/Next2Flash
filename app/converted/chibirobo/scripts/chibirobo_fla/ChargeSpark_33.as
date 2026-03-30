package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ChargeSpark_33 extends MovieClip
    {

        public function ChargeSpark_33()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

