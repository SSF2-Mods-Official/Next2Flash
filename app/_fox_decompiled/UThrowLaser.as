package
{
    import flash.display.MovieClip;

    public dynamic class UThrowLaser extends MovieClip
    {

        public var stance:MovieClip;

        public function UThrowLaser()
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

