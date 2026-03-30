package
{
    import flash.display.MovieClip;

    public dynamic class star_mc extends MovieClip
    {

        public var stance:MovieClip;

        public function star_mc()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            stop();
        }


    }
}

