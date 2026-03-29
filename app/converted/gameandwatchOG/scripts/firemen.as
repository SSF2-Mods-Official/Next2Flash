package
{
    import flash.display.MovieClip;

    public dynamic class firemen extends MovieClip
    {

        public var stance:MovieClip;

        public function firemen()
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

