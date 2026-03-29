package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class ChargeSpark_27 extends MovieClip
    {

        public function ChargeSpark_27()
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

