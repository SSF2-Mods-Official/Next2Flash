package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ChargeSpark_31 extends MovieClip
    {

        public function ChargeSpark_31()
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

