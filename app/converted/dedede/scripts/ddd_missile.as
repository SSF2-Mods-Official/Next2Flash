package
{
    import flash.display.MovieClip;

    public dynamic class ddd_missile extends MovieClip
    {

        public var stance:MovieClip;

        public function ddd_missile()
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

