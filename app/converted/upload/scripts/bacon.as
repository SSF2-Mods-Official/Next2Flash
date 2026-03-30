package
{
    import flash.display.MovieClip;

    public dynamic class bacon extends MovieClip
    {

        public var stance:MovieClip;

        public function bacon()
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

