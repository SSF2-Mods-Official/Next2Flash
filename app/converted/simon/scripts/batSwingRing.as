package
{
    import flash.display.MovieClip;

    public dynamic class batSwingRing extends MovieClip
    {

        public var stance:MovieClip;

        public function batSwingRing()
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

