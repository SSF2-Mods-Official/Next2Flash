package
{
    import flash.display.MovieClip;

    public dynamic class kirby_starbullet extends MovieClip
    {

        public var stance:MovieClip;

        public function kirby_starbullet()
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

