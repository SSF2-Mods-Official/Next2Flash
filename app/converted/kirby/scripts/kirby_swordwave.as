package
{
    import flash.display.MovieClip;

    public dynamic class kirby_swordwave extends MovieClip
    {

        public var stance:a;

        public function kirby_swordwave()
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

