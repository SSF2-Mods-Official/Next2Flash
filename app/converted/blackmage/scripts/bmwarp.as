package
{
    import flash.display.MovieClip;

    public dynamic class bmwarp extends MovieClip
    {

        public var stance:MovieClip;

        public function bmwarp()
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

