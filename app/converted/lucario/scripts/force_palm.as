package
{
    import flash.display.MovieClip;

    public dynamic class force_palm extends MovieClip
    {

        public var stance:MovieClip;

        public function force_palm()
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

