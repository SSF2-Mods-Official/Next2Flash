package
{
    import flash.display.MovieClip;

    public dynamic class global_sparkle extends MovieClip
    {

        public function global_sparkle()
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
            gotoAndStop("end");
        }


    }
}

