package
{
    import flash.display.MovieClip;

    public dynamic class landmasterLaser extends MovieClip
    {

        public var stance:MovieClip;

        public function landmasterLaser()
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

