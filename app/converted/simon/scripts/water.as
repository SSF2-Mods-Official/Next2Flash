package
{
    import flash.display.MovieClip;

    public dynamic class water extends MovieClip
    {

        public var stance:MovieClip;

        public function water()
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

