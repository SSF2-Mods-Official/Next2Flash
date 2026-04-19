package
{
    import flash.display.MovieClip;

    public dynamic class bm_dair_death extends MovieClip
    {

        public var stance:MovieClip;

        public function bm_dair_death()
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

