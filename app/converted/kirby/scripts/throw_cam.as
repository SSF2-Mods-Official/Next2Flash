package
{
    import flash.display.MovieClip;

    public dynamic class throw_cam extends MovieClip
    {

        public var stance:throw_cam2;

        public function throw_cam()
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

