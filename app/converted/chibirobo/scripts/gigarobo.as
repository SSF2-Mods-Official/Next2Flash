package
{
    import flash.display.MovieClip;

    public dynamic class gigarobo extends MovieClip
    {

        public var stance:MovieClip;

        public function gigarobo()
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

