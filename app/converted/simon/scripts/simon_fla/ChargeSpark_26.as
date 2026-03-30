package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class ChargeSpark_26 extends MovieClip
    {

        public function ChargeSpark_26()
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

