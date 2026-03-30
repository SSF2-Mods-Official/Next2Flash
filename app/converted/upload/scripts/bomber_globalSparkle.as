package
{
    import flash.display.MovieClip;

    public dynamic class bomber_globalSparkle extends MovieClip
    {

        public function bomber_globalSparkle()
        {
            super();
            addFrameScript(7, this.frame8, 8, this.frame9);
        }

        internal function frame8():*
        {
            stop();
            parent.removeChild(this);
        }

        internal function frame9():*
        {
            gotoAndPlay("end");
        }


    }
}

